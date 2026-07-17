"""Offline clean-room contracts for the CICCWM provider."""

from __future__ import annotations

import json
import unittest


class RecordingTransport:
    def __init__(self, response: bytes | None = None) -> None:
        self.calls: list[dict[str, object]] = []
        self.response = response or b'{"ret":0,"rsp":{"data":[]}}'

    def post(self, **kwargs: object) -> bytes:
        self.calls.append(dict(kwargs))
        return self.response


class CiccwmAdapterTests(unittest.TestCase):
    def test_six_read_only_packages_use_one_no_telemetry_boundary(self) -> None:
        from investkit.providers.ciccwm import CiccwmClient, ENDPOINT

        transport = RecordingTransport()
        client = CiccwmClient(
            api_key="test-secret", allow_network=True, transport=transport
        )
        client.market_info("603868.SH")
        client.market_history("603868.SH", days=60)
        client.stock_finance("603868.SH", statement="income", year="2025")
        client.hot_news(page=1, size=10)
        client.etf_hot(page=1)
        client.dragon_tiger_list(date="2026-03-13")
        client.fund_detail("519002")

        self.assertEqual(len(transport.calls), 7)
        self.assertTrue(all(call["url"] == ENDPOINT for call in transport.calls))
        self.assertTrue(all("webreport" not in str(call) for call in transport.calls))
        payloads = [json.loads(call["body"]) for call in transport.calls]
        self.assertEqual(
            [payload["cmdname"] for payload in payloads],
            [
                "SkillTdxQuotationQueryCommon",
                "SkillTdxQuotationQueryCommon",
                "SkillEQuoteZhongzhuoF10Common",
                "SkillEInformationTopicSecendPage",
                "SkillMCSearchHotList",
                "SkillEQuoteLhbStockInfo",
                "SkillCmdFmQryFundProductInfo",
            ],
        )
        history = json.loads(payloads[1]["param"]["tdx_param"])
        self.assertEqual(history["WantNum"], 60)
        self.assertEqual(history["Period"], 4)
        self.assertEqual(payloads[5]["param"]["req_date"], "2026-03-13")

    def test_fund_search_uses_fund_code_resolution_contract(self) -> None:
        from investkit.providers.ciccwm import CiccwmClient

        transport = RecordingTransport()
        client = CiccwmClient(api_key="secret", allow_network=True, transport=transport)
        client.fund_search("519002", page=1, size=10)
        payload = json.loads(transport.calls[0]["body"])
        self.assertEqual(payload["cmdname"], "SkillCmdFmSearchFund")
        self.assertEqual(
            payload["param"],
            {"keyword": "519002", "recpage": 1, "reccnt": 10, "search_type": 1},
        )

    def test_nonzero_vendor_result_is_not_misreported_as_success(self) -> None:
        from investkit.providers.ciccwm import CiccwmClient, CiccwmResponseError

        client = CiccwmClient(
            api_key="secret",
            allow_network=True,
            transport=RecordingTransport(b'{"ret":850210032,"msg":"invalid product"}'),
        )
        with self.assertRaises(CiccwmResponseError):
            client.fund_detail("519002")

    def test_credentials_permission_and_input_validation_fail_before_transport(self) -> None:
        from investkit.providers.ciccwm import CiccwmAccessError, CiccwmClient

        transport = RecordingTransport()
        with self.assertRaises(CiccwmAccessError):
            CiccwmClient(api_key=None, allow_network=True, transport=transport)
        with self.assertRaises(CiccwmAccessError):
            CiccwmClient(api_key="secret", allow_network=False, transport=transport)
        with self.assertRaises(CiccwmAccessError):
            CiccwmClient(api_key="secret：", allow_network=True, transport=transport)
        client = CiccwmClient(api_key="secret", allow_network=True, transport=transport)
        for call in (
            lambda: client.market_info("../../x"),
            lambda: client.stock_finance("603868.SH", statement="unknown", year="2025"),
            lambda: client.hot_news(page=0, size=1000),
            lambda: client.dragon_tiger_list(date="2026-99-99"),
            lambda: client.fund_detail("x"),
        ):
            with self.subTest(call=call), self.assertRaises(ValueError):
                call()
        self.assertEqual(transport.calls, [])


if __name__ == "__main__":
    unittest.main()
