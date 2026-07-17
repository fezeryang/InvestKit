"""Offline security contracts for the first-party Guangfa adapter boundary."""

from __future__ import annotations

import json
import os
import unittest
from unittest import mock


class RecordingTransport:
    def __init__(self, response: bytes | None = None) -> None:
        if response is None:
            response = '{"data":{"compName":"上海飞科电器股份有限公司"}}'.encode("utf-8")
        self.response = response
        self.calls: list[dict[str, object]] = []

    def post(self, *, url: str, headers: dict[str, str], body: bytes, timeout: float, max_bytes: int) -> bytes:
        self.calls.append(
            {"url": url, "headers": headers, "body": body, "timeout": timeout, "max_bytes": max_bytes}
        )
        return self.response


class FailingTransport(RecordingTransport):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def post(self, **kwargs: object) -> bytes:
        del kwargs
        raise OSError(self.message)


class GuangfaAdapterTests(unittest.TestCase):
    def test_provider_package_preserves_existing_public_exports(self) -> None:
        from investkit import providers

        self.assertTrue(
            {
                "DemoProvider",
                "FileProvider",
                "GuangfaClient",
                "Provider",
                "ProviderRecord",
                "normalize_a_share_symbol",
            }.issubset(set(providers.__all__))
        )

    def test_symbol_normalization_is_exchange_qualified_and_strict(self) -> None:
        from investkit.providers.guangfa import normalize_a_share_symbol

        symbol = normalize_a_share_symbol("603868.SH")
        self.assertEqual(symbol.canonical, "603868.SH")
        self.assertEqual(symbol.code, "603868")
        self.assertEqual(symbol.market, "SH")
        self.assertEqual(symbol.vendor_code, "SH603868")
        for invalid in ("603868", "SH603868", "603868.SZ", "000001.SH", "../603868.SH"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                normalize_a_share_symbol(invalid)

    def test_credentials_and_network_permission_are_required_before_transport(self) -> None:
        from investkit.providers.guangfa import GuangfaClient, ProviderAccessError

        transport = RecordingTransport()
        with self.assertRaises(ProviderAccessError):
            GuangfaClient(api_key=None, allow_network=True, transport=transport)
        with self.assertRaises(ProviderAccessError):
            GuangfaClient(api_key="test-secret", allow_network=False, transport=transport)
        self.assertEqual(transport.calls, [])

    def test_f10_call_uses_allowlisted_endpoint_tool_and_bounded_transport(self) -> None:
        from investkit.providers.guangfa import ENDPOINT, GuangfaClient

        transport = RecordingTransport()
        client = GuangfaClient(api_key="test-secret", allow_network=True, transport=transport)
        result = client.stock_f10("603868.SH")
        self.assertEqual(result["data"]["compName"], "上海飞科电器股份有限公司")
        self.assertEqual(len(transport.calls), 1)
        call = transport.calls[0]
        self.assertEqual(call["url"], ENDPOINT)
        self.assertEqual(call["headers"]["Authorization"], "Bearer test-secret")
        payload = json.loads(call["body"])
        self.assertEqual(
            payload,
            {
                "service_name": "wechat_f10",
                "tool_name": "f10_basic_post",
                "args": {"code": "603868", "market": "SH"},
            },
        )
        self.assertLessEqual(call["timeout"], 10.0)
        self.assertLessEqual(call["max_bytes"], 2 * 1024 * 1024)

    def test_environment_factory_and_errors_never_disclose_secret_values(self) -> None:
        from investkit.providers.guangfa import GuangfaClient, ProviderAccessError

        secret = "".join(("gf", "_live_super_", "secret_123456789"))
        with mock.patch.dict(os.environ, {"GF_SKILLS_APIKEY": secret}, clear=True):
            client = GuangfaClient.from_environment(
                allow_network=True,
                transport=FailingTransport(f"failed Authorization: Bearer {secret}"),
            )
        with self.assertRaises(ProviderAccessError) as caught:
            client.stock_f10("603868.SH")
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn(secret, repr(client))

    def test_financial_comparison_requires_two_same_asset_symbols(self) -> None:
        from investkit.providers.guangfa import GuangfaClient

        transport = RecordingTransport()
        client = GuangfaClient(
            api_key="test-secret", allow_network=True, transport=transport
        )
        client.compare_financials(
            "603868.SH", peer_symbol="002032.SZ", year="2025", report_type=12
        )
        payload = json.loads(transport.calls[0]["body"])
        self.assertEqual(
            payload["args"]["stock_codes"], ["SH603868", "SZ002032"]
        )

    def test_registered_market_etf_and_fund_tools_use_fixed_vendor_contracts(self) -> None:
        from investkit.providers.guangfa import GuangfaClient

        transport = RecordingTransport()
        client = GuangfaClient(
            api_key="test-secret", allow_network=True, transport=transport
        )
        client.dragon_tiger_list(date=20260313, market="sh")
        client.etf_rank(rank_type=1, page=0, size=20)
        client.etf_search(track_type="行业", one_track_name="科技", limit=20)
        client.etf_super_fund(flow_type="大幅流入")
        client.fund_detail("519002")
        client.fund_investment(
            "001643",
            balance=1000,
            start_date="20200101",
            end_date="20250101",
            frequency="0",
            strategies=[
                {
                    "prodAIRationType": "4",
                    "prodIndexType": "0",
                    "prodAverageType": "0",
                    "expectIncomeRatio": "0.2",
                }
            ],
        )
        payloads = [json.loads(call["body"]) for call in transport.calls]
        self.assertEqual(
            [(item["service_name"], item["tool_name"]) for item in payloads],
            [
                ("lhb", "lhb_aborttrade_market_date_get"),
                ("etf_rank", "finance-api_product_etf_rank_get"),
                ("etf_search", "finance_api_inclusive_etf_list_get"),
                ("etf-super-fund", "gfmiddle_eits_super_fund_etf_superfund_get"),
                ("jijin_info", "finance-api_product_fund_detail_get"),
                ("fund_invest", "finance_api_product_invest_compute_post"),
            ],
        )
        self.assertEqual(payloads[0]["args"], {"date": 20260313, "market": "sh"})
        self.assertEqual(payloads[1]["args"]["size"], 20)
        self.assertEqual(payloads[2]["args"]["trakType"], "行业")
        self.assertEqual(payloads[3]["args"], {"type": "大幅流入"})
        self.assertEqual(payloads[4]["args"], {"tradeCode": "519002"})
        self.assertEqual(payloads[5]["args"]["balance"], 1000)

    def test_registered_market_etf_and_fund_tools_reject_invalid_parameters(self) -> None:
        from investkit.providers.guangfa import GuangfaClient

        client = GuangfaClient(
            api_key="test-secret", allow_network=True, transport=RecordingTransport()
        )
        invalid_calls = (
            lambda: client.dragon_tiger_list(date=20261340, market="sh"),
            lambda: client.etf_rank(rank_type=99, size=20),
            lambda: client.etf_search(track_type="行业", limit=1001),
            lambda: client.etf_super_fund(flow_type="未知"),
            lambda: client.fund_detail("../../x"),
            lambda: client.fund_investment(
                "001643",
                balance=-1,
                start_date="20250101",
                end_date="20200101",
                frequency="0",
                strategies=[],
            ),
        )
        for call in invalid_calls:
            with self.subTest(call=call), self.assertRaises(ValueError):
                call()

    def test_duplicate_nonfinite_and_oversized_responses_fail_closed(self) -> None:
        from investkit.providers.guangfa import GuangfaClient, ProviderResponseError

        responses = (
            b'{"data":{},"data":{}}',
            b'{"data":NaN}',
            b"{" + b'"padding":"' + (b"x" * (2 * 1024 * 1024)) + b'"}',
        )
        for response in responses:
            client = GuangfaClient(
                api_key="test-secret",
                allow_network=True,
                transport=RecordingTransport(response),
            )
            with self.subTest(size=len(response)), self.assertRaises(ProviderResponseError):
                client.stock_f10("603868.SH")


if __name__ == "__main__":
    unittest.main()
