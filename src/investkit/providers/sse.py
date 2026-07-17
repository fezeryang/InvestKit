"""Official SSE announcement lookup and conservative research-bundle acquisition."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from typing import Any, Mapping, Protocol
from urllib.parse import parse_qs, urlencode, urlsplit
import urllib.error
import urllib.request

from ..errors import InvestKitError
from .guangfa import normalize_a_share_symbol


QUERY_ENDPOINT = "https://query.sse.com.cn/security/stock/queryCompanyBulletin.do"
PROFILE_ENDPOINT = "https://query.sse.com.cn/commonQuery.do"
PROFILE_SQL_ID = "COMMON_SSE_ZQPZ_GP_GPLB_C"
STATIC_DISCLOSURE_ORIGIN = "https://static.sse.com.cn"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
TIMEOUT_SECONDS = 10.0


class SseAccessError(InvestKitError):
    """Raised when official SSE lookup is unavailable or not permitted."""


class SseResponseError(InvestKitError):
    """Raised when the SSE response is malformed or ambiguous."""


class SseTransport(Protocol):
    def get(
        self,
        *,
        url: str,
        headers: dict[str, str],
        timeout: float,
        max_bytes: int,
    ) -> bytes: ...


class SseAnnouncementClient:
    """Read public official announcement metadata after explicit network consent."""

    def __init__(self, *, allow_network: bool, transport: SseTransport | None = None) -> None:
        if not allow_network:
            raise SseAccessError("SSE network access requires explicit permission")
        self._transport = transport or UrllibSseTransport()

    def acquire_bundle(self, symbol: str) -> dict[str, Any]:
        normalized = normalize_a_share_symbol(symbol)
        if normalized.market != "SH":
            raise ValueError("SSE provider supports .SH securities only")
        query = urlencode(
            {
                "isPagination": "true",
                "productId": normalized.code,
                "keyWord": "",
                "securityType": "0101,120100,020100,020200,120200",
                "pageHelp.pageSize": "50",
                "pageHelp.pageNo": "1",
                "pageHelp.beginPage": "1",
                "pageHelp.cacheSize": "1",
                "pageHelp.endPage": "1",
            }
        )
        try:
            announcement_payload = self._transport.get(
                url=f"{QUERY_ENDPOINT}?{query}",
                headers={
                    "Accept": "application/json",
                    "Referer": "https://www.sse.com.cn/",
                    "User-Agent": "InvestKit/0.3 official-disclosure-research",
                },
                timeout=TIMEOUT_SECONDS,
                max_bytes=MAX_RESPONSE_BYTES,
            )
            profile_query = urlencode(
                {
                    "isPagination": "false",
                    "sqlId": PROFILE_SQL_ID,
                    "productid": normalized.code,
                }
            )
            profile_payload = self._transport.get(
                url=f"{PROFILE_ENDPOINT}?{profile_query}",
                headers={
                    "Accept": "application/json",
                    "Referer": (
                        "https://www.sse.com.cn/assortment/stock/list/info/company/"
                        f"index.shtml?COMPANY_CODE={normalized.code}"
                    ),
                    "User-Agent": "InvestKit/0.3 official-disclosure-research",
                },
                timeout=TIMEOUT_SECONDS,
                max_bytes=MAX_RESPONSE_BYTES,
            )
        except Exception as error:
            raise SseAccessError("SSE official lookup failed") from error
        value = _strict_object(announcement_payload)
        page = value.get("pageHelp")
        rows = page.get("data") if isinstance(page, Mapping) else None
        if not isinstance(rows, list) or not rows:
            raise SseResponseError("SSE returned no matching security announcements")
        announcements = _announcements(rows, normalized.code)
        if not announcements:
            raise SseResponseError("SSE returned no valid matching announcements")
        names = {item["security_name"] for item in announcements}
        if len(names) != 1:
            raise SseResponseError("SSE security identity is ambiguous")
        short_name = names.pop()
        profile = _profile(_strict_object(profile_payload), normalized.code, short_name)
        return _bundle(normalized.canonical, normalized.code, profile, announcements)


class UrllibSseTransport:
    def get(
        self,
        *,
        url: str,
        headers: dict[str, str],
        timeout: float,
        max_bytes: int,
    ) -> bytes:
        parsed = urlsplit(url)
        query_endpoint = urlsplit(QUERY_ENDPOINT)
        profile_endpoint = urlsplit(PROFILE_ENDPOINT)
        if (
            parsed.scheme != "https"
            or parsed.hostname != query_endpoint.hostname
            or parsed.port is not None
            or parsed.path not in {query_endpoint.path, profile_endpoint.path}
            or not parsed.query
            or parsed.fragment
        ):
            raise SseAccessError("SSE endpoint is not allowlisted")
        if parsed.path == profile_endpoint.path:
            try:
                values = parse_qs(parsed.query, strict_parsing=True)
            except ValueError as error:
                raise SseAccessError("SSE profile query is invalid") from error
            if (
                set(values) != {"isPagination", "sqlId", "productid"}
                or values["isPagination"] != ["false"]
                or values["sqlId"] != [PROFILE_SQL_ID]
                or len(values["productid"]) != 1
                or not re.fullmatch(r"6[0-9]{5}", values["productid"][0])
            ):
                raise SseAccessError("SSE profile query is not allowlisted")
        request = urllib.request.Request(url, headers=headers, method="GET")
        opener = urllib.request.build_opener(_NoRedirect())
        try:
            with opener.open(request, timeout=timeout) as response:
                if response.status != 200:
                    raise SseAccessError("SSE returned a non-success status")
                payload = response.read(max_bytes + 1)
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            raise SseAccessError("SSE network request failed") from error
        if len(payload) > max_bytes:
            raise SseResponseError("SSE response exceeds the allowed boundary")
        return payload


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects so the exact official host boundary cannot drift."""

    def redirect_request(
        self,
        request: Any,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def _announcements(rows: list[Any], code: str) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, Mapping) or row.get("SECURITY_CODE") != code:
            continue
        name = _text(row.get("SECURITY_NAME"), "security name")
        title = _text(row.get("TITLE"), "announcement title", limit=500)
        date = _text(row.get("SSEDATE"), "announcement date")
        path = _text(row.get("URL"), "announcement path", limit=1000)
        if not re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", date):
            continue
        if not path.startswith("/disclosure/") or not path.endswith(".pdf") or ".." in path:
            continue
        result.append(
            {
                "security_name": name,
                "title": title,
                "publication_date": date,
                "path": path,
                "bulletin_type": str(row.get("BULLETIN_TYPE") or "公告"),
            }
        )
    return result[:50]


def _profile(value: Mapping[str, Any], code: str, short_name: str) -> dict[str, Any]:
    rows = value.get("result")
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], Mapping):
        raise SseResponseError("SSE returned an ambiguous company profile")
    row = rows[0]
    if row.get("COMPANY_CODE") != code or row.get("COMPANY_ABBR") != short_name:
        raise SseResponseError("SSE company profile does not match the announcement identity")
    return {
        "legal_name": _text(row.get("FULLNAME"), "company legal name"),
        "short_name": short_name,
        "english_name": _profile_text(row.get("FULL_NAME_IN_ENGLISH")),
        "industry": _profile_text(row.get("CSRC_GREAT_CODE_DESC")),
        "industry_group": _profile_text(row.get("CSRC_CODE_DESC")),
        "area": _profile_text(row.get("AREA_NAME_DESC")),
        "address": _profile_text(row.get("COMPANY_ADDRESS")),
        "legal_representative": _profile_text(row.get("LEGAL_REPRESENTATIVE")),
        "website": _profile_text(row.get("WWW_ADDRESS")),
        "profile_updated_at": _profile_text(row.get("QIANYI_DATE")),
    }


def _profile_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized or normalized == "-" or len(normalized) > 500:
        return None
    return normalized


def _bundle(symbol: str, code: str, profile: Mapping[str, Any], announcements: list[dict[str, str]]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    latest_date = max(item["publication_date"] for item in announcements)
    name = _text(profile.get("legal_name"), "company legal name", limit=500)
    short_name = _text(profile.get("short_name"), "company short name")
    sources: list[dict[str, Any]] = []
    for index, item in enumerate(announcements):
        sources.append(
            {
                "source_id": f"sse-{code}-announcement-{index + 1}",
                "publisher": "上海证券交易所",
                "title": item["title"],
                "source_type": "official-exchange-announcement",
                "locator": STATIC_DISCLOSURE_ORIGIN + item["path"],
                "publication_date": item["publication_date"],
                "as_of_date": item["publication_date"],
                "retrieved_at": now,
                "quality": "primary-authoritative-metadata",
                "freshness": "current-as-retrieved",
                "access_notes": "Public SSE announcement metadata; document contents were not parsed by this acquisition step.",
                "license_notes": "Public disclosure access verified; downstream reuse terms remain subject to SSE policy.",
            }
        )
    profile_source_id = f"sse-{code}-company-profile"
    profile_query = urlencode(
        {"isPagination": "false", "sqlId": PROFILE_SQL_ID, "productid": code}
    )
    sources.append(
        {
            "source_id": profile_source_id,
            "publisher": "上海证券交易所",
            "title": f"{name}公司概况",
            "source_type": "official-exchange-company-profile",
            "locator": f"{PROFILE_ENDPOINT}?{profile_query}",
            "publication_date": None,
            "as_of_date": now[:10],
            "retrieved_at": now,
            "quality": "primary-authoritative",
            "freshness": "current-as-retrieved",
            "access_notes": "Public SSE company profile retrieved through an allowlisted official query.",
            "license_notes": "Public disclosure access verified; downstream reuse terms remain subject to SSE policy.",
        }
    )
    source_ids = [source["source_id"] for source in sources]
    announcement_source_ids = [
        source["source_id"]
        for source in sources
        if source["source_type"] == "official-exchange-announcement"
    ]
    security = {
        "security_id": f"SSE:{code}",
        "ticker": symbol,
        "legal_name": name,
        "exchange": "Shanghai Stock Exchange",
        "aliases": [code, symbol, short_name, name],
    }
    limitations = "Official company profile and announcement metadata were acquired, but filing contents and financial tables were not parsed."
    gaps = _gap_operations(limitations)
    gaps["identify_security"] = {
        "data": dict(security),
        "source_ids": [profile_source_id, announcement_source_ids[0]],
        "warnings": ["Identity is supported by the official SSE company profile and announcement metadata."],
    }
    gaps["get_security_profile"] = {
        "data": {
            "name": name,
            "business_model": None,
            "segments": [],
            "products": [],
            "customers": None,
            "suppliers": None,
            "geographies": [profile["area"]] if profile.get("area") else [],
            "competitive_position": None,
            "business_risks": [],
            "revenue_model": None,
            "payer": None,
            "value_proposition": None,
            "revenue_components": {},
            "order_to_cash": None,
            "employee_count": None,
            "customer_concentration_percent": None,
            "management": {
                "summary": (
                    f"上交所公司概况列示法定代表人为{profile['legal_representative']}。"
                    if profile.get("legal_representative")
                    else None
                ),
                "tenure": None,
            },
            "capital_allocation": {},
            "competitive_context": {
                "summary": (
                    f"上交所公司概况的证监会行业分类为{profile['industry']}；未取得市场份额或同业比较证据。"
                    if profile.get("industry")
                    else None
                )
            },
            "research_drivers": [
                value
                for value in (
                    f"行业：{profile['industry']}" if profile.get("industry") else None,
                    f"地区：{profile['area']}" if profile.get("area") else None,
                )
                if value is not None
            ],
            "limitations": [limitations],
        },
        "source_ids": [profile_source_id],
        "warnings": [limitations],
    }
    gaps["get_source_metadata"] = {
        "data": {"sources": sources, "limitations": [limitations]},
        "source_ids": source_ids,
        "warnings": [limitations],
    }
    return {
        "schema_version": "1.0",
        "bundle_version": f"sse-{code}-{latest_date}-v1",
        "created_at": now,
        "retrieved_at": now,
        "as_of_date": latest_date,
        "currency": "CNY",
        "market": "SSE",
        "status": "imported",
        "warnings": [limitations, "Live lookup used public official metadata and made no claim about report contents."],
        "security": security,
        "sources": sources,
        "operations": gaps,
    }


def _gap_operations(limitation: str) -> dict[str, Any]:
    return {
        "identify_security": {},
        "get_security_profile": {},
        "get_financial_statements": {"data": {"accounting_basis": None, "period_type": None, "units": None, "periods": [], "limitations": [limitation]}, "source_ids": [], "warnings": [limitation]},
        "get_price_history": {"data": {"observations": [], "latest_price": None, "frequency": None, "limitations": [limitation]}, "source_ids": [], "warnings": [limitation]},
        "get_valuation_inputs": {"data": {"current_price": None, "market_capitalization": None, "enterprise_value": None, "forecast_unlevered_free_cash_flow": None, "wacc": None, "terminal_growth": None, "diluted_shares": None, "cash": None, "total_debt": None, "peer_ev_to_operating_income": None, "scenario_assumptions": None, "sensitivity_wacc_values": None, "sensitivity_terminal_growth_values": None, "units": None, "limitations": [limitation]}, "source_ids": [], "warnings": [limitation]},
        "get_source_metadata": {},
        "get_peer_comparables": {"data": {"peers": [], "selection_method": None, "period_alignment": None, "units": None, "limitations": [limitation]}, "source_ids": [], "warnings": [limitation]},
        "get_earnings_history": {"data": {"events": [], "transcript_available": None, "units": None, "limitations": [limitation]}, "source_ids": [], "warnings": [limitation]},
        "get_catalyst_events": {"data": {"events": [], "limitations": [limitation]}, "source_ids": [], "warnings": [limitation]},
    }


def _strict_object(payload: bytes) -> dict[str, Any]:
    if not isinstance(payload, bytes) or len(payload) > MAX_RESPONSE_BYTES:
        raise SseResponseError("SSE response exceeds the allowed boundary")
    try:
        value = json.loads(payload.decode("utf-8", errors="strict"), object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise SseResponseError("SSE response is not strict UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise SseResponseError("SSE response must be an object")
    return value


def _text(value: Any, label: str, *, limit: int = 200) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise SseResponseError(f"SSE {label} is invalid")
    return value.strip()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate response key")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    del value
    raise ValueError("non-finite response number")
