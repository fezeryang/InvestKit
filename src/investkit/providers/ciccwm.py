"""Permission-gated clean-room client for reviewed CICCWM data APIs.

This module implements only the observed request contract. It does not import or
execute vendor package code and deliberately omits its telemetry and TLS changes.
"""

from __future__ import annotations

from datetime import datetime
import json
import os
import re
from typing import Any, Mapping, Protocol
import urllib.error
import urllib.request

from ..errors import InvestKitError
from .guangfa import normalize_a_share_symbol


ENDPOINT = "https://skill.ciccwm.com/zzt/ext/fcgi/common.fcgi"
API_KEY_ENV = "CICCWM_API_KEY"
TIMEOUT_SECONDS = 8.0
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class CiccwmAccessError(InvestKitError):
    """Raised when credential, permission, or network access is unavailable."""


class CiccwmResponseError(InvestKitError):
    """Raised when a vendor response violates the bounded JSON contract."""


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


class CiccwmClient:
    """Allowlisted read-only client shared by the six reviewed data packages."""

    def __init__(
        self,
        *,
        api_key: str | None,
        allow_network: bool,
        transport: JsonTransport | None = None,
    ) -> None:
        if (
            not isinstance(api_key, str)
            or not api_key.strip()
            or not api_key.strip().isascii()
        ):
            raise CiccwmAccessError(f"{API_KEY_ENV} is not configured")
        if not allow_network:
            raise CiccwmAccessError("CICCWM network access requires explicit permission")
        self._api_key = api_key.strip()
        self._transport = transport or UrllibTransport()

    def __repr__(self) -> str:
        return "CiccwmClient(endpoint='skill.ciccwm.com', credential='[REDACTED]')"

    @classmethod
    def from_environment(
        cls,
        *,
        allow_network: bool,
        transport: JsonTransport | None = None,
    ) -> "CiccwmClient":
        return cls(
            api_key=os.environ.get(API_KEY_ENV),
            allow_network=allow_network,
            transport=transport,
        )

    def market_info(self, symbol: str) -> Mapping[str, Any]:
        stock = normalize_a_share_symbol(symbol)
        tdx_param = {
            "Head": {"Target": 0},
            "Setcode": "1" if stock.market == "SH" else "0",
            "Code": stock.code,
            "HasProInfo": 1,
            "HasHQInfo": 1,
            "HasExtInfo": 1,
            "HasCwInfo": 1,
        }
        return self._call(
            "SkillTdxQuotationQueryCommon",
            {
                "entry": "HQServ.PBHQInfo",
                "tdx_param": json.dumps(tdx_param, ensure_ascii=False, separators=(",", ":")),
            },
        )

    def market_history(self, symbol: str, *, days: int = 60) -> Mapping[str, Any]:
        stock = normalize_a_share_symbol(symbol)
        if isinstance(days, bool) or not 2 <= days <= 250:
            raise ValueError("market history days must be between 2 and 250")
        tdx_param = {
            "Head": {"Target": 0},
            "Setcode": "1" if stock.market == "SH" else "0",
            "Code": stock.code,
            "Period": 4,
            "WantNum": days,
        }
        return self._call(
            "SkillTdxQuotationQueryCommon",
            {
                "entry": "HQServ.PBFXT",
                "tdx_param": json.dumps(tdx_param, ensure_ascii=False, separators=(",", ":")),
            },
        )

    def stock_finance(
        self, symbol: str, *, statement: str, year: str
    ) -> Mapping[str, Any]:
        stock = normalize_a_share_symbol(symbol)
        actions = {"indicators": 48571, "income": 48572, "cashflow": 48573, "balance": 48574}
        if statement not in actions:
            raise ValueError("financial statement type is unsupported")
        if not isinstance(year, str) or re.fullmatch(r"20[0-9]{2}", year) is None:
            raise ValueError("financial statement year must be YYYY")
        request = {
            "action": actions[statement],
            "gpcode": stock.code,
            "qtime": "12",
            "gtype": 1 if stock.market == "SH" else 0,
        }
        return self._call(
            "SkillEQuoteZhongzhuoF10Common",
            {"req_json": json.dumps(request, ensure_ascii=False, separators=(",", ":"))},
        )

    def hot_news(self, *, page: int = 1, size: int = 10) -> Mapping[str, Any]:
        if isinstance(page, bool) or page < 1 or isinstance(size, bool) or not 1 <= size <= 100:
            raise ValueError("hot-news pagination is invalid")
        return self._call(
            "SkillEInformationTopicSecendPage",
            {"page_num": page, "page_size": size, "type": 1, "scene": "1"},
        )

    def etf_hot(self, *, page: int = 1) -> Mapping[str, Any]:
        if isinstance(page, bool) or not 1 <= page <= 1000:
            raise ValueError("ETF ranking page is invalid")
        return self._call("SkillMCSearchHotList", {"type": 2001, "page_num": page})

    def dragon_tiger_list(self, *, date: str) -> Mapping[str, Any]:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except (TypeError, ValueError) as error:
            raise ValueError("dragon-tiger date must be YYYY-MM-DD") from error
        return self._call("SkillEQuoteLhbStockInfo", {"req_type": "1", "req_date": date})

    def fund_detail(self, product_id: str) -> Mapping[str, Any]:
        if not isinstance(product_id, str) or re.fullmatch(r"[0-9]{6,32}", product_id) is None:
            raise ValueError("fund product id must contain 6 to 32 digits")
        return self._call(
            "SkillCmdFmQryFundProductInfo",
            {"product_id": product_id, "need_wealth_article": 1},
        )

    def fund_search(
        self, keyword: str, *, page: int = 1, size: int = 10
    ) -> Mapping[str, Any]:
        if (
            not isinstance(keyword, str)
            or keyword != keyword.strip()
            or not 1 <= len(keyword) <= 80
        ):
            raise ValueError("fund search keyword is invalid")
        if isinstance(page, bool) or page < 1 or isinstance(size, bool) or not 1 <= size <= 20:
            raise ValueError("fund search pagination is invalid")
        return self._call(
            "SkillCmdFmSearchFund",
            {"keyword": keyword, "recpage": page, "reccnt": size, "search_type": 1},
        )

    def _call(self, cmdname: str, param: Mapping[str, Any]) -> Mapping[str, Any]:
        body = json.dumps(
            {"cmdname": cmdname, "param": dict(param)},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        try:
            response = self._transport.post(
                url=ENDPOINT,
                headers={
                    "Cookie": f"apiKey={self._api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "InvestKit/0.1",
                },
                body=body,
                timeout=TIMEOUT_SECONDS,
                max_bytes=MAX_RESPONSE_BYTES,
            )
        except Exception as error:
            raise CiccwmAccessError("CICCWM request failed without a usable response") from error
        if not isinstance(response, bytes) or len(response) > MAX_RESPONSE_BYTES:
            raise CiccwmResponseError("CICCWM response exceeds the allowed boundary")
        try:
            value = json.loads(
                response.decode("utf-8", errors="strict"),
                object_pairs_hook=_unique_object,
                parse_constant=_reject_constant,
            )
        except (UnicodeError, json.JSONDecodeError, ValueError) as error:
            raise CiccwmResponseError("CICCWM response is not strict UTF-8 JSON") from error
        if not isinstance(value, dict):
            raise CiccwmResponseError("CICCWM response must be a JSON object")
        if value.get("ret") == 5002:
            raise CiccwmAccessError("CICCWM rejected the configured credential")
        if value.get("ret") not in {0, "0"}:
            code = value.get("ret")
            raise CiccwmResponseError(f"CICCWM service returned business error code {code}")
        return value


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        del req, fp, code, msg, headers, newurl
        return None


class UrllibTransport:
    """Bounded HTTPS transport with redirects disabled."""

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
            raise CiccwmAccessError("CICCWM endpoint is not allowlisted")
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        opener = urllib.request.build_opener(_NoRedirect())
        try:
            with opener.open(request, timeout=timeout) as response:
                if response.status != 200:
                    raise CiccwmAccessError("CICCWM service returned a non-success status")
                length = response.headers.get("Content-Length")
                if length is not None and int(length) > max_bytes:
                    raise CiccwmResponseError("CICCWM response exceeds the allowed boundary")
                payload = response.read(max_bytes + 1)
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            raise CiccwmAccessError("CICCWM network request failed") from error
        if len(payload) > max_bytes:
            raise CiccwmResponseError("CICCWM response exceeds the allowed boundary")
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
