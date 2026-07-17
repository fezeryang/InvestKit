"""Permission-gated first-party client for reviewed Guangfa API adaptations.

The catalog still controls whether these operations are selectable. Merely importing
this module does not approve a candidate or perform network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import os
import re
from typing import Any, Mapping, Protocol
import urllib.error
import urllib.request

from ..errors import InvestKitError


ENDPOINT = "https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call"
API_KEY_ENV = "GF_SKILLS_APIKEY"
TIMEOUT_SECONDS = 8.0
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
_SYMBOL_RE = re.compile(r"^(?P<code>[0-9]{6})\.(?P<market>SH|SZ)$")


class ProviderAccessError(InvestKitError):
    """Raised before or during an unavailable credentialed provider call."""


class ProviderResponseError(InvestKitError):
    """Raised when a vendor response violates the bounded JSON contract."""


@dataclass(frozen=True)
class AShareSymbol:
    canonical: str
    code: str
    market: str
    vendor_code: str


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


def normalize_a_share_symbol(value: str) -> AShareSymbol:
    """Validate an exchange-qualified common A-share symbol."""

    if not isinstance(value, str) or value != value.strip():
        raise ValueError("symbol must use six digits plus .SH or .SZ")
    match = _SYMBOL_RE.fullmatch(value.upper())
    if match is None:
        raise ValueError("symbol must use six digits plus .SH or .SZ")
    code = match.group("code")
    market = match.group("market")
    if (market == "SH" and not code.startswith("6")) or (
        market == "SZ" and not code.startswith(("0", "3"))
    ):
        raise ValueError("symbol code and exchange are inconsistent")
    return AShareSymbol(
        canonical=f"{code}.{market}",
        code=code,
        market=market,
        vendor_code=f"{market}{code}",
    )


class GuangfaClient:
    """Small allowlisted client with separate credential and network gates."""

    def __init__(
        self,
        *,
        api_key: str | None,
        allow_network: bool,
        transport: JsonTransport | None = None,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ProviderAccessError(f"{API_KEY_ENV} is not configured")
        if not allow_network:
            raise ProviderAccessError("Guangfa network access requires explicit permission")
        self._api_key = api_key
        self._transport = transport or UrllibTransport()

    def __repr__(self) -> str:
        return "GuangfaClient(endpoint='mcp-api.gf.com.cn', credential='[REDACTED]')"

    @classmethod
    def from_environment(
        cls,
        *,
        allow_network: bool,
        transport: JsonTransport | None = None,
    ) -> GuangfaClient:
        return cls(
            api_key=os.environ.get(API_KEY_ENV),
            allow_network=allow_network,
            transport=transport,
        )

    def stock_f10(self, symbol: str) -> Mapping[str, Any]:
        normalized = normalize_a_share_symbol(symbol)
        return self._call(
            service_name="wechat_f10",
            tool_name="f10_basic_post",
            args={"code": normalized.code, "market": normalized.market},
        )

    def stock_valuation(self, symbol: str) -> Mapping[str, Any]:
        normalized = normalize_a_share_symbol(symbol)
        return self._call(
            service_name="quant",
            tool_name="common_basic_post",
            args={"stock_codes": [normalized.vendor_code]},
        )

    def compare_financials(
        self,
        symbol: str,
        *,
        peer_symbol: str,
        year: str,
        report_type: int = 12,
    ) -> Mapping[str, Any]:
        normalized = normalize_a_share_symbol(symbol)
        peer = normalize_a_share_symbol(peer_symbol)
        if peer.canonical == normalized.canonical:
            raise ValueError("financial comparison requires two distinct securities")
        if not re.fullmatch(r"20[0-9]{2}", year) or report_type not in {1, 6, 9, 12}:
            raise ValueError("financial comparison period is invalid")
        return self._call(
            service_name="quant",
            tool_name="compare_indicator_post",
            args={
                "report_type": report_type,
                "stock_codes": [normalized.vendor_code, peer.vendor_code],
                "year": year,
            },
        )

    def dragon_tiger_list(self, *, date: int, market: str) -> Mapping[str, Any]:
        value = str(date)
        try:
            datetime.strptime(value, "%Y%m%d")
        except ValueError as error:
            raise ValueError("dragon-tiger date must be YYYYMMDD") from error
        if market not in {"sh", "sz"}:
            raise ValueError("dragon-tiger market must be sh or sz")
        return self._call(
            service_name="lhb",
            tool_name="lhb_aborttrade_market_date_get",
            args={"date": date, "market": market},
        )

    def etf_rank(
        self,
        *,
        rank_type: int,
        page: int = 0,
        size: int = 10,
        same_index_filter: int | None = None,
    ) -> Mapping[str, Any]:
        if rank_type not in {1, 2, 3, 4, 12, 13}:
            raise ValueError("ETF rank type is unsupported")
        if isinstance(page, bool) or page < 0 or isinstance(size, bool) or not 1 <= size <= 100:
            raise ValueError("ETF rank pagination is invalid")
        args: dict[str, Any] = {"type": rank_type, "page": page, "size": size}
        if same_index_filter is not None:
            if same_index_filter not in {0, 1}:
                raise ValueError("same-index filter must be 0 or 1")
            args["sameIndexFilter"] = same_index_filter
        return self._call(
            service_name="etf_rank",
            tool_name="finance-api_product_etf_rank_get",
            args=args,
        )

    def etf_search(
        self,
        *,
        track_type: str | None = None,
        one_track_name: str | None = None,
        search: str | None = None,
        limit: int = 20,
        sort: str | None = None,
    ) -> Mapping[str, Any]:
        if isinstance(limit, bool) or not 1 <= limit <= 100:
            raise ValueError("ETF search limit is invalid")
        args: dict[str, Any] = {"start": 0, "limit": limit, "addRealTimeRoc": 1}
        for key, value in (
            ("trakType", track_type),
            ("oneTrakName", one_track_name),
            ("search", search),
            ("sort", sort),
        ):
            if value is None:
                continue
            if not isinstance(value, str) or not value.strip() or len(value) > 80:
                raise ValueError("ETF search text parameter is invalid")
            args[key] = value.strip()
        return self._call(
            service_name="etf_search",
            tool_name="finance_api_inclusive_etf_list_get",
            args=args,
        )

    def etf_super_fund(self, *, flow_type: str) -> Mapping[str, Any]:
        if flow_type not in {"大幅流入", "大幅流出", "持续流入", "持续流出"}:
            raise ValueError("ETF super-fund flow type is unsupported")
        return self._call(
            service_name="etf-super-fund",
            tool_name="gfmiddle_eits_super_fund_etf_superfund_get",
            args={"type": flow_type},
        )

    def fund_detail(self, trade_code: str) -> Mapping[str, Any]:
        if not isinstance(trade_code, str) or not re.fullmatch(r"[0-9]{6}", trade_code):
            raise ValueError("fund trade code must contain six digits")
        return self._call(
            service_name="jijin_info",
            tool_name="finance-api_product_fund_detail_get",
            args={"tradeCode": trade_code},
        )

    def fund_investment(
        self,
        trade_code: str,
        *,
        balance: int | float,
        start_date: str,
        end_date: str,
        frequency: str,
        strategies: list[Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        if not re.fullmatch(r"[0-9]{6}", trade_code):
            raise ValueError("fund trade code must contain six digits")
        if isinstance(balance, bool) or not isinstance(balance, (int, float)) or not 0 < balance <= 1_000_000:
            raise ValueError("fund investment balance is invalid")
        try:
            start = datetime.strptime(start_date, "%Y%m%d")
            end = datetime.strptime(end_date, "%Y%m%d")
        except ValueError as error:
            raise ValueError("fund investment dates must be YYYYMMDD") from error
        if start >= end or frequency not in {"0", "1", "2", "3"}:
            raise ValueError("fund investment period or frequency is invalid")
        if not isinstance(strategies, list) or not 1 <= len(strategies) <= 5:
            raise ValueError("fund investment requires one to five strategies")
        allowed_strategy_keys = {
            "prodAIRationType",
            "prodIndexType",
            "prodAverageType",
            "expectIncomeRatio",
            "backRate",
            "lockPeriod",
        }
        normalized: list[dict[str, Any]] = []
        for strategy in strategies:
            if not isinstance(strategy, Mapping) or not strategy or not set(strategy).issubset(allowed_strategy_keys):
                raise ValueError("fund investment strategy is invalid")
            normalized.append(dict(strategy))
        return self._call(
            service_name="fund_invest",
            tool_name="finance_api_product_invest_compute_post",
            args={
                "tradeCode": trade_code,
                "balance": balance,
                "rate": frequency,
                "startDate": start_date,
                "endDate": end_date,
                "enFundDate": "1",
                "strategyList": normalized,
            },
        )

    def _call(
        self,
        *,
        service_name: str,
        tool_name: str,
        args: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        body = json.dumps(
            {"service_name": service_name, "tool_name": tool_name, "args": dict(args)},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        try:
            response = self._transport.post(
                url=ENDPOINT,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body=body,
                timeout=TIMEOUT_SECONDS,
                max_bytes=MAX_RESPONSE_BYTES,
            )
        except Exception as error:
            raise ProviderAccessError("Guangfa request failed without a usable response") from error
        if not isinstance(response, bytes) or len(response) > MAX_RESPONSE_BYTES:
            raise ProviderResponseError("Guangfa response exceeds the allowed boundary")
        try:
            value = json.loads(
                response.decode("utf-8", errors="strict"),
                object_pairs_hook=_unique_object,
                parse_constant=_reject_constant,
            )
        except (UnicodeError, json.JSONDecodeError, ValueError) as error:
            raise ProviderResponseError("Guangfa response is not strict UTF-8 JSON") from error
        if not isinstance(value, dict):
            raise ProviderResponseError("Guangfa response must be a JSON object")
        return value


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        del req, fp, code, msg, headers, newurl
        return None


class UrllibTransport:
    """Bounded HTTPS transport; instantiated only after explicit client gates."""

    def post(
        self,
        *,
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout: float,
        max_bytes: int,
    ) -> bytes:
        if url != ENDPOINT:
            raise ProviderAccessError("Guangfa endpoint is not allowlisted")
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        opener = urllib.request.build_opener(_NoRedirect())
        try:
            with opener.open(request, timeout=timeout) as response:
                if response.status != 200:
                    raise ProviderAccessError("Guangfa service returned a non-success status")
                length = response.headers.get("Content-Length")
                if length is not None and int(length) > max_bytes:
                    raise ProviderResponseError("Guangfa response exceeds the allowed boundary")
                payload = response.read(max_bytes + 1)
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            raise ProviderAccessError("Guangfa network request failed") from error
        if len(payload) > max_bytes:
            raise ProviderResponseError("Guangfa response exceeds the allowed boundary")
        return payload


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate response key")
        value[key] = child
    return value


def _reject_constant(value: str) -> Any:
    del value
    raise ValueError("non-finite response number")
