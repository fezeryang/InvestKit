"""Permission-gated, first-party boundary for the reviewed Eastmoney MX API."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from typing import Any, Mapping, Protocol
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from ..errors import InvestKitError
from .guangfa import normalize_a_share_symbol


ENDPOINT = "https://mkapi2.dfcfs.com/finskillshub/api/claw/query"
API_KEY_ENV = "MX_APIKEY"
TIMEOUT_SECONDS = 8.0
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_QUERY_BYTES = 4096
MAX_TABLES = 32
MAX_ROWS = 10_000
MAX_COLUMNS = 256
_YEAR_RE = re.compile(r"^20[0-9]{2}$")


class EastmoneyAccessError(InvestKitError):
    """Raised when credential or explicit network permission is unavailable."""


class EastmoneyResponseError(InvestKitError):
    """Raised when the vendor response is outside the conservative contract."""


class JsonTransport(Protocol):
    def post(
        self,
        *,
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout: float,
        max_bytes: int,
    ) -> bytes: ...


@dataclass(frozen=True)
class MxTable:
    title: str
    rows: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class MxQueryResult:
    security_name: str
    security_code: str
    tables: tuple[MxTable, ...]


class EastmoneyMxClient:
    """Expose fixed research queries; arbitrary user text is never sent upstream."""

    def __init__(
        self,
        *,
        api_key: str | None,
        allow_network: bool,
        transport: JsonTransport | None = None,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise EastmoneyAccessError(f"{API_KEY_ENV} is not configured")
        if not allow_network:
            raise EastmoneyAccessError("Eastmoney network access requires explicit permission")
        self._api_key = api_key
        self._transport = transport or UrllibTransport()

    def __repr__(self) -> str:
        return "EastmoneyMxClient(endpoint='mkapi2.dfcfs.com', credential='[REDACTED]')"

    @classmethod
    def from_environment(
        cls, *, allow_network: bool, transport: JsonTransport | None = None
    ) -> "EastmoneyMxClient":
        return cls(
            api_key=os.environ.get(API_KEY_ENV),
            allow_network=allow_network,
            transport=transport,
        )

    def company_profile(self, symbol: str) -> MxQueryResult:
        return self._query(symbol, "company")

    def financial_statements(self, symbol: str) -> MxQueryResult:
        return self._query(symbol, "financial")

    def valuation_snapshot(self, symbol: str) -> MxQueryResult:
        return self._query(symbol, "valuation")

    def _query(self, symbol: str, query_kind: str) -> MxQueryResult:
        normalized = normalize_a_share_symbol(symbol)
        query_text = _query_text(normalized.canonical, query_kind)
        body = json.dumps(
            {"toolQuery": query_text}, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        if len(body) > MAX_QUERY_BYTES:
            raise EastmoneyAccessError("Eastmoney query exceeds the allowed boundary")
        try:
            payload = self._transport.post(
                url=ENDPOINT,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "apikey": self._api_key,
                },
                body=body,
                timeout=TIMEOUT_SECONDS,
                max_bytes=MAX_RESPONSE_BYTES,
            )
        except Exception as error:
            raise EastmoneyAccessError("Eastmoney request failed without a usable response") from error
        value = _strict_object(payload)
        return _parse_result(value, normalized.canonical)


def _query_text(symbol: str, query_kind: str) -> str:
    if query_kind == "company":
        return f"查询股票{symbol}的公司基本资料、主营业务、行业分类、管理层和主要股东，返回结构化数据表"
    if query_kind == "financial":
        return f"查询股票{symbol}最近五年年度财务报表和关键财务指标，返回结构化数据表"
    if query_kind == "valuation":
        return f"查询股票{symbol}最新行情、市值、估值指标、现金和有息负债，返回结构化数据表"
    raise ValueError("unsupported Eastmoney query kind")


def _parse_result(value: Mapping[str, Any], canonical_symbol: str) -> MxQueryResult:
    if value.get("status") != 0:
        raise EastmoneyResponseError("Eastmoney returned an unsuccessful status")
    data = value.get("data")
    if not isinstance(data, Mapping):
        raise EastmoneyResponseError("Eastmoney response data is invalid")
    nested = data.get("data")
    if isinstance(nested, Mapping):
        root = nested.get("searchDataResultDTO")
        if isinstance(root, Mapping):
            data = root
    raw_tags = data.get("entityTagDTOList")
    security_name = data.get("securityName")
    security_code = data.get("securityCode")
    if isinstance(raw_tags, list):
        tags = [tag for tag in raw_tags if isinstance(tag, Mapping)]
        if len(tags) != 1:
            raise EastmoneyResponseError("Eastmoney security identity is ambiguous")
        security_name = tags[0].get("fullName")
        security_code = tags[0].get("secuCode")
    if not isinstance(security_name, str) or not security_name.strip():
        raise EastmoneyResponseError("Eastmoney response has no security identity")
    if not isinstance(security_code, str) or not _same_symbol(security_code, canonical_symbol):
        raise EastmoneyResponseError("Eastmoney security identity does not match the request")
    raw_tables = data.get("dataTableDTOList")
    if not isinstance(raw_tables, list) or not raw_tables or len(raw_tables) > MAX_TABLES:
        raise EastmoneyResponseError("Eastmoney response has no bounded data tables")
    tables = tuple(_parse_table(item) for item in raw_tables)
    if not tables:
        raise EastmoneyResponseError("Eastmoney response has no usable data tables")
    return MxQueryResult(security_name.strip(), canonical_symbol, tables)


def _same_symbol(value: str, canonical: str) -> bool:
    if value == canonical:
        return True
    code, market = canonical.split(".")
    return value in {code, f"{market}{code}"}


def _parse_table(value: Any) -> MxTable:
    if not isinstance(value, Mapping):
        raise EastmoneyResponseError("Eastmoney table is invalid")
    title = value.get("title") or value.get("inputTitle") or value.get("entityName")
    if not isinstance(title, str) or not title.strip() or len(title) > 200:
        raise EastmoneyResponseError("Eastmoney table title is invalid")
    table = value.get("table")
    if not isinstance(table, Mapping):
        raise EastmoneyResponseError("Eastmoney table payload is invalid")
    dates = table.get("headName")
    if not isinstance(dates, list) or not dates or len(dates) > MAX_ROWS:
        raise EastmoneyResponseError("Eastmoney table periods are invalid")
    name_map = value.get("nameMap")
    if not isinstance(name_map, Mapping):
        name_map = {}
    order = value.get("indicatorOrder")
    keys = list(order) if isinstance(order, list) else [key for key in table if key != "headName"]
    keys = [key for key in keys if key != "headName"]
    if len(keys) > MAX_COLUMNS:
        raise EastmoneyResponseError("Eastmoney table has too many columns")
    fields: list[tuple[Any, str]] = []
    for key in keys:
        label = name_map.get(key, name_map.get(str(key), key))
        if not isinstance(label, str) or not label.strip() or len(label) > 200:
            raise EastmoneyResponseError("Eastmoney table column label is invalid")
        fields.append((key, label.strip()))
    rows: list[Mapping[str, Any]] = []
    for index, period in enumerate(dates):
        if not isinstance(period, (str, int, float)) or isinstance(period, bool):
            raise EastmoneyResponseError("Eastmoney table period is invalid")
        row: dict[str, Any] = {"period": str(period)}
        for key, label in fields:
            values = table.get(key)
            if not isinstance(values, list) or index >= len(values):
                row[label] = None
                continue
            candidate = values[index]
            if isinstance(candidate, (dict, list, bool)):
                raise EastmoneyResponseError("Eastmoney table values must be scalar")
            row[label] = candidate
        rows.append(row)
    return MxTable(title.strip(), tuple(rows))


def _strict_object(payload: bytes) -> dict[str, Any]:
    if not isinstance(payload, bytes) or len(payload) > MAX_RESPONSE_BYTES:
        raise EastmoneyResponseError("Eastmoney response exceeds the allowed boundary")
    try:
        value = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise EastmoneyResponseError("Eastmoney response is not strict UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise EastmoneyResponseError("Eastmoney response must be a JSON object")
    return value


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        del req, fp, code, msg, headers, newurl
        return None


class UrllibTransport:
    def post(
        self,
        *,
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout: float,
        max_bytes: int,
    ) -> bytes:
        parsed = urlsplit(url)
        endpoint = urlsplit(ENDPOINT)
        if (
            parsed.scheme != "https"
            or parsed.hostname != endpoint.hostname
            or parsed.port is not None
            or parsed.path != endpoint.path
            or parsed.query
            or parsed.fragment
        ):
            raise EastmoneyAccessError("Eastmoney endpoint is not allowlisted")
        if len(body) > MAX_QUERY_BYTES:
            raise EastmoneyAccessError("Eastmoney request exceeds the allowed boundary")
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        opener = urllib.request.build_opener(_NoRedirect())
        try:
            with opener.open(request, timeout=timeout) as response:
                if response.status != 200:
                    raise EastmoneyAccessError("Eastmoney returned a non-success status")
                length = response.headers.get("Content-Length")
                if length is not None and int(length) > max_bytes:
                    raise EastmoneyResponseError("Eastmoney response exceeds the allowed boundary")
                payload = response.read(max_bytes + 1)
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            raise EastmoneyAccessError("Eastmoney network request failed") from error
        if len(payload) > max_bytes:
            raise EastmoneyResponseError("Eastmoney response exceeds the allowed boundary")
        return payload


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
