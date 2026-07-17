"""Offline contracts for the governed Eastmoney MX provider boundary."""

from __future__ import annotations

import json
import os
import unittest
from unittest import mock


def _response() -> bytes:
    return json.dumps(
        {
            "status": 0,
            "data": {
                "data": {
                    "searchDataResultDTO": {
                        "entityTagDTOList": [
                            {
                                "fullName": "上海飞科电器股份有限公司",
                                "secuCode": "603868.SH",
                                "entityTypeName": "A股",
                            }
                        ],
                        "dataTableDTOList": [
                            {
                                "title": "主要财务指标",
                                "entityName": "飞科电器",
                                "nameMap": {"revenue": "营业收入", "profit": "归母净利润"},
                                "indicatorOrder": ["revenue", "profit"],
                                "table": {
                                    "headName": ["2024", "2023"],
                                    "revenue": [4628000000, 5060000000],
                                    "profit": [1050000000, 1020000000],
                                },
                            }
                        ],
                    }
                }
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")


class RecordingTransport:
    def __init__(self, response: bytes | None = None) -> None:
        self.response = _response() if response is None else response
        self.calls: list[dict[str, object]] = []

    def post(
        self,
        *,
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout: float,
        max_bytes: int,
    ) -> bytes:
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "body": body,
                "timeout": timeout,
                "max_bytes": max_bytes,
            }
        )
        return self.response


class FailingTransport(RecordingTransport):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def post(self, **kwargs: object) -> bytes:
        del kwargs
        raise OSError(self.message)


class EastmoneyAdapterTests(unittest.TestCase):
    def test_provider_is_exported_without_replacing_existing_providers(self) -> None:
        from investkit import providers

        self.assertIn("EastmoneyMxClient", providers.__all__)
        self.assertIn("SseAnnouncementClient", providers.__all__)
        self.assertIn("GuangfaClient", providers.__all__)

    def test_credential_and_explicit_network_permission_precede_transport(self) -> None:
        from investkit.providers.eastmoney import EastmoneyAccessError, EastmoneyMxClient

        transport = RecordingTransport()
        with self.assertRaises(EastmoneyAccessError):
            EastmoneyMxClient(api_key=None, allow_network=True, transport=transport)
        with self.assertRaises(EastmoneyAccessError):
            EastmoneyMxClient(api_key="test-secret", allow_network=False, transport=transport)
        self.assertEqual(transport.calls, [])

    def test_financial_query_is_symbol_scoped_and_returns_normalized_tables(self) -> None:
        from investkit.providers.eastmoney import ENDPOINT, EastmoneyMxClient

        transport = RecordingTransport()
        client = EastmoneyMxClient(
            api_key="test-secret", allow_network=True, transport=transport
        )
        result = client.financial_statements("603868.SH")

        self.assertEqual(result.security_name, "上海飞科电器股份有限公司")
        self.assertEqual(result.security_code, "603868.SH")
        self.assertEqual(result.tables[0].title, "主要财务指标")
        self.assertEqual(
            result.tables[0].rows[0],
            {"period": "2024", "营业收入": 4628000000, "归母净利润": 1050000000},
        )
        self.assertEqual(len(transport.calls), 1)
        call = transport.calls[0]
        self.assertEqual(call["url"], ENDPOINT)
        self.assertEqual(call["headers"]["apikey"], "test-secret")
        self.assertEqual(call["headers"]["Content-Type"], "application/json")
        payload = json.loads(call["body"])
        self.assertEqual(set(payload), {"toolQuery"})
        self.assertIn("603868.SH", payload["toolQuery"])
        self.assertNotIn("test-secret", payload["toolQuery"])
        self.assertLessEqual(call["timeout"], 10.0)
        self.assertLessEqual(call["max_bytes"], 2 * 1024 * 1024)

    def test_only_fixed_research_templates_are_exposed(self) -> None:
        from investkit.providers.eastmoney import EastmoneyMxClient

        client = EastmoneyMxClient(
            api_key="test-secret", allow_network=True, transport=RecordingTransport()
        )
        self.assertFalse(hasattr(client, "query"))
        for method_name in ("company_profile", "financial_statements", "valuation_snapshot"):
            self.assertTrue(callable(getattr(client, method_name)))

    def test_environment_factory_and_failures_never_disclose_secret(self) -> None:
        from investkit.providers.eastmoney import EastmoneyAccessError, EastmoneyMxClient

        secret = "".join(("mx", "_live_super_", "secret_123456789"))
        with mock.patch.dict(os.environ, {"MX_APIKEY": secret}, clear=True):
            client = EastmoneyMxClient.from_environment(
                allow_network=True,
                transport=FailingTransport(f"failed apikey={secret}"),
            )
        with self.assertRaises(EastmoneyAccessError) as caught:
            client.company_profile("603868.SH")
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn(secret, repr(client))

    def test_malformed_ambiguous_and_oversized_responses_fail_closed(self) -> None:
        from investkit.providers.eastmoney import EastmoneyMxClient, EastmoneyResponseError

        ambiguous = json.dumps(
            {
                "status": 0,
                "data": {
                    "data": {
                        "searchDataResultDTO": {
                            "entityTagDTOList": [
                                {"fullName": "A", "secuCode": "603868.SH"},
                                {"fullName": "B", "secuCode": "603868.SH"},
                            ],
                            "dataTableDTOList": [],
                        }
                    }
                },
            }
        ).encode("utf-8")
        responses = (
            b'{"status":0,"status":0}',
            b'{"status":NaN}',
            ambiguous,
            b"{" + b'"padding":"' + (b"x" * (2 * 1024 * 1024)) + b'"}',
        )
        for response in responses:
            client = EastmoneyMxClient(
                api_key="test-secret",
                allow_network=True,
                transport=RecordingTransport(response),
            )
            with self.subTest(size=len(response)), self.assertRaises(EastmoneyResponseError):
                client.financial_statements("603868.SH")

    def test_direct_documented_table_location_is_supported_conservatively(self) -> None:
        from investkit.providers.eastmoney import EastmoneyMxClient

        payload = json.dumps(
            {
                "status": 0,
                "data": {
                    "securityName": "上海飞科电器股份有限公司",
                    "securityCode": "603868.SH",
                    "dataTableDTOList": [
                        {
                            "title": "估值",
                            "nameMap": {"pe": "市盈率"},
                            "table": {"headName": ["2026-07-17"], "pe": [18.2]},
                        }
                    ],
                },
            },
            ensure_ascii=False,
        ).encode("utf-8")
        client = EastmoneyMxClient(
            api_key="test-secret",
            allow_network=True,
            transport=RecordingTransport(payload),
        )
        result = client.valuation_snapshot("603868.SH")
        self.assertEqual(result.tables[0].rows[0]["市盈率"], 18.2)


if __name__ == "__main__":
    unittest.main()
