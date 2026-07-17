"""Contracts for multi-provider evidence fusion in symbol research."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tests.test_sse_provider import SseTransport


def _gf_f10(name: str = "上海飞科电器股份有限公司") -> dict[str, object]:
    return {
        "data": {
            "errcode": 0,
            "errmsg": "",
            "data": {
                "compName": name,
                "boardName": "主板",
                "businessScope": "剃须刀及配件,家用电器及配件,金属制品的研发,制造,加工",
                "industries": "制造业",
                "listDate": "20160418",
            },
        }
    }


def _gf_valuation(code: str, name: str, market_cap: float, pe: float, pb: float) -> dict[str, object]:
    return {
        "retcode": 0,
        "msg": "ok",
        "data": {
            "retcode": 0,
            "msg": "ok",
            "data": [
                {
                    "stock_code": code,
                    "stock_name": name,
                    "basic": {"list_date": "2016-04-18", "total_marketcap": market_cap},
                    "valuation": {
                        "pettm": pe,
                        "pb": pb,
                        "pettm_avg": 78.1434,
                        "pb_avg": 3.984,
                        "pettm_percent": 31.27,
                        "pb_percent": 0.48,
                        "trade_date": "2026-07-16",
                    },
                }
            ],
        },
    }


def _gf_financial(year: str, target_roe: float, peer_roe: float) -> dict[str, object]:
    return {
        "data": {
            "retcode": 0,
            "msg": "ok",
            "data": {
                "year": year,
                "report_type": 12,
                "data": [
                    {
                        "stock_code": "SH603868",
                        "stock_name": "飞科电器",
                        "end_date": f"{year}-12-31",
                        "report_type": 12,
                        "roe": target_roe,
                        "sale_gross_rate": 56.7,
                        "net_profit2totalincome": 13.2,
                        "cashflow_oper2income": 1.13,
                        "net_cashflow_oper2net_profit": 1.71,
                        "liablity2asset": 16.45,
                        "operate_income_yoy": -6.9,
                        "net_profit_yoy": 11.84,
                    },
                    {
                        "stock_code": "SZ002032",
                        "stock_name": "苏泊尔",
                        "end_date": f"{year}-12-31",
                        "report_type": 12,
                        "roe": peer_roe,
                        "sale_gross_rate": 24.8,
                        "net_profit2totalincome": 9.2,
                        "cashflow_oper2income": 1.17,
                        "net_cashflow_oper2net_profit": 1.26,
                        "liablity2asset": 52.9,
                        "operate_income_yoy": 1.54,
                        "net_profit_yoy": -6.72,
                    },
                ],
            },
        }
    }


def _cicc_market(*, code: str = "603868", name: str = "飞科电器") -> dict[str, object]:
    return {
        "ret": 0,
        "rsp": {
            "ret_code": 0,
            "data": json.dumps(
                {
                    "BaseInfo": {"Code": code, "Name": name, "Setcode": 1},
                    "HQInfo": {
                        "HQDate": "20260716",
                        "HQTime": "150000",
                        "Open": 30.0,
                        "MaxP": 31.2,
                        "MinP": 29.8,
                        "Close": 29.9,
                        "Now": 31.0,
                        "Volume": "123456",
                        "Amount": 3812336,
                    },
                    "ExtInfo": {"ZSZ": 135.04, "SYL": 25.9},
                }
            ),
        },
    }


def _cicc_history(*, code: str = "603868") -> dict[str, object]:
    return {
        "ret": 0,
        "rsp": {
            "ret_code": 0,
            "data": json.dumps(
                {
                    "Code": code,
                    "Setcode": 1,
                    "Period": 4,
                    "ListHead": {
                        "ItemHead": [
                            "Data", "Second", "Open", "High", "Low", "Close",
                            "Amount", "VolInStock", "Volume", "Settle", "up", "down",
                        ]
                    },
                    "ListItem": [
                        {"Item": ["20260715", "0", 29.0, 30.0, 28.8, 29.5, 1000, 0, 100, 0, 0, 0]},
                        {"Item": ["20260716", "0", 30.0, 31.2, 29.8, 31.0, 2000, 0, 200, 0, 0, 0]},
                    ],
                }
            ),
        },
    }


def _cicc_financials() -> dict[str, dict[str, object]]:
    rows = {
        "income": {"rq": "2025-12-31", "yysr": 4_500_000_000.0, "yycb": 2_000_000_000.0, "yylr": 900_000_000.0, "lrze": 920_000_000.0, "jlr": 780_000_000.0},
        "cashflow": {"rq": "2025-12-31", "jyxjje": 820_000_000.0, "tzxjje": -120_000_000.0, "czxjje": -400_000_000.0},
        "balance": {"rq": "2025-12-31", "zczj": 5_800_000_000.0, "fzhj": 950_000_000.0, "gdqyhj": 4_850_000_000.0, "hbzj": 1_200_000_000.0, "chjr": 700_000_000.0, "yszk": 300_000_000.0},
        "indicators": {"rq": "2025-12-31", "xsmll": 55.5, "jzcsyl": 16.2, "zcfzl": 16.4, "yysrzzl": -5.2, "jlrtbzzl": 8.1},
    }
    return {
        name: {"ret": 0, "rsp": {"ret_code": 0, "rsp_json": json.dumps([row])}}
        for name, row in rows.items()
    }


def _cicc_news() -> dict[str, object]:
    return {
        "ret": 0,
        "rsp": {
            "ret_code": 0,
            "content_list": [
                {
                    "id": "news-1",
                    "title": "飞科电器发布渠道调整公告",
                    "source": "中金财富资讯",
                    "pub_time": "2026-07-16 10:00:00",
                    "short_content": "公司渠道调整仍需观察后续收入和现金流影响。",
                    "detail_url": "https://example.invalid/news-1",
                    "stock_info": [{"stock_code": "603868", "stock_name": "飞科电器", "stock_market": "SH"}],
                },
                {
                    "id": "news-2",
                    "title": "无关市场新闻",
                    "source": "中金财富资讯",
                    "pub_time": "2026-07-16 09:00:00",
                    "stock_info": [{"stock_code": "000001", "stock_name": "平安银行", "stock_market": "SZ"}],
                },
            ],
        },
    }


def _cicc_lhb(*, code: str = "603868") -> dict[str, object]:
    return {
        "ret": 0,
        "rsp": {
            "ret_code": 0,
            "charts_info": {
                "overall_list": [
                    {
                        "secu_code": code,
                        "secu_name": "飞科电器",
                        "s_reason_type": "日涨幅偏离值",
                        "f_change_pct": 8.2,
                        "f_close_price": 31.0,
                        "f_income": 12000000.0,
                    }
                ],
                "jgqc_list": [],
                "yzby_list": [],
            },
        },
    }


class ProviderFusionTests(unittest.TestCase):
    def setUp(self) -> None:
        from investkit.providers.sse import SseAnnouncementClient

        self.base = SseAnnouncementClient(
            allow_network=True, transport=SseTransport()
        ).acquire_bundle("603868.SH")

    def test_fusion_builds_one_valid_bundle_with_cross_provider_lineage(self) -> None:
        from investkit.providers.file import FileProvider
        from investkit.providers.fusion import fuse_equity_research_bundle

        bundle = fuse_equity_research_bundle(
            self.base,
            f10_response=_gf_f10(),
            valuation_response=_gf_valuation("SH603868", "飞科电器", 134.43, 25.8652, 4.0767),
            peer_valuation_response=_gf_valuation("SZ002032", "苏泊尔", 610.0, 18.0, 5.2),
            financial_responses=[_gf_financial("2024", 14.1, 32.0), _gf_financial("2025", 15.39, 33.36)],
            peer_symbol="002032.SZ",
        )
        provider = FileProvider.from_mapping(bundle, origin="fusion:test")

        self.assertEqual(provider.bundle["security"]["ticker"], "603868.SH")
        self.assertGreaterEqual(len(provider.bundle["sources"]), 7)
        profile = provider.get_security_profile("SSE:603868")
        self.assertIn("剃须刀", profile["business_model"])
        statements = provider.get_financial_statements("SSE:603868")
        self.assertEqual([p["fiscal_year"] for p in statements["periods"]], ["2024", "2025"])
        self.assertEqual(statements["periods"][-1]["roe_percent"], 15.39)
        valuation = provider.get_valuation_inputs("SSE:603868")
        self.assertEqual(valuation["market_capitalization"], 134.43)
        self.assertEqual(valuation["price_to_earnings_ttm"], 25.8652)
        peers = provider.get_peer_comparables("SSE:603868")
        self.assertEqual(peers["peers"][0]["ticker"], "002032.SZ")
        self.assertAlmostEqual(peers["peers"][0]["price_to_earnings"], 18.0)
        self.assertTrue(
            any(source["publisher"] == "广发证券" for source in provider.bundle["sources"])
        )

    def test_guangfa_target_fusion_adds_relative_valuation_without_a_peer(self) -> None:
        from investkit.providers.file import FileProvider
        from investkit.providers.fusion import fuse_guangfa_target_bundle

        bundle = fuse_guangfa_target_bundle(
            self.base,
            f10_response=_gf_f10(),
            valuation_response=_gf_valuation(
                "SH603868", "飞科电器", 134.43, 25.8652, 4.0767
            ),
        )
        provider = FileProvider.from_mapping(bundle, origin="fusion:gf-target")

        profile = provider.get_security_profile("SSE:603868")
        self.assertIn("剃须刀", profile["business_model"])
        valuation = provider.get_valuation_inputs("SSE:603868")
        self.assertEqual(valuation["price_to_earnings_ttm"], 25.8652)
        self.assertEqual(valuation["industry_price_to_earnings_ttm"], 78.1434)
        reference = valuation["industry_valuation_reference"]
        self.assertEqual(reference["classification"], "制造业")
        self.assertIsNone(reference["sample_size"])
        self.assertAlmostEqual(
            reference["metrics"]["price_to_earnings_ttm"]["target_to_average"],
            25.8652 / 78.1434,
        )
        self.assertFalse(provider.get_peer_comparables("SSE:603868")["peers"])

    def test_relative_valuation_completes_without_manufacturing_dcf(self) -> None:
        from investkit.capabilities.analysis import run_capability
        from investkit.providers.file import FileProvider
        from investkit.providers.fusion import fuse_guangfa_target_bundle

        bundle = fuse_guangfa_target_bundle(
            self.base,
            f10_response=_gf_f10(),
            valuation_response=_gf_valuation(
                "SH603868", "飞科电器", 134.43, 25.8652, 4.0767
            ),
        )
        provider = FileProvider.from_mapping(bundle, origin="fusion:gf-target")
        valuation = provider.get_valuation_inputs("SSE:603868")
        result = run_capability(
            "valuation-analysis",
            {
                "input_mode": "imported",
                "valuation_inputs": valuation,
                "active_source_ids": valuation["source_ids"],
                "capability_results": {},
            },
        )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["method"]["name"], "market-relative-valuation")
        self.assertIsNone(result["method"]["target_value_range"])
        self.assertIn(
            "unknown-valuation-dcf",
            {item["id"] for item in result["unknowns"]},
        )
        self.assertTrue(
            all("guaranteed" not in item["statement"].lower() for item in result["findings"])
        )

    def test_fusion_rejects_identity_conflicts_and_unsuccessful_vendor_status(self) -> None:
        from investkit.providers.fusion import ProviderFusionError, fuse_equity_research_bundle

        cases = (
            {"f10_response": _gf_f10("错误公司")},
            {"valuation_response": {"retcode": 1, "msg": "failed", "data": None}},
        )
        for override in cases:
            arguments = {
                "f10_response": _gf_f10(),
                "valuation_response": _gf_valuation("SH603868", "飞科电器", 134.43, 25.8, 4.0),
                "peer_valuation_response": _gf_valuation("SZ002032", "苏泊尔", 610.0, 18.0, 5.2),
                "financial_responses": [_gf_financial("2024", 14.1, 32.0), _gf_financial("2025", 15.3, 33.0)],
                "peer_symbol": "002032.SZ",
            }
            arguments.update(override)
            with self.subTest(override=tuple(override)), self.assertRaises(ProviderFusionError):
                fuse_equity_research_bundle(deepcopy(self.base), **arguments)

    def test_ciccwm_fusion_adds_market_financial_and_relevant_event_evidence(self) -> None:
        from investkit.providers.file import FileProvider
        from investkit.providers.fusion import (
            fuse_ciccwm_research_bundle,
            fuse_equity_research_bundle,
        )

        gf_bundle = fuse_equity_research_bundle(
            self.base,
            f10_response=_gf_f10(),
            valuation_response=_gf_valuation("SH603868", "飞科电器", 134.43, 25.8652, 4.0767),
            peer_valuation_response=_gf_valuation("SZ002032", "苏泊尔", 610.0, 18.0, 5.2),
            financial_responses=[_gf_financial("2024", 14.1, 32.0), _gf_financial("2025", 15.39, 33.36)],
            peer_symbol="002032.SZ",
        )
        bundle = fuse_ciccwm_research_bundle(
            gf_bundle,
            market_info_response=_cicc_market(),
            market_history_response=_cicc_history(),
            financial_responses=_cicc_financials(),
            hot_news_response=_cicc_news(),
            dragon_tiger_response=_cicc_lhb(),
            dragon_tiger_date="2026-07-16",
        )
        provider = FileProvider.from_mapping(bundle, origin="fusion:ciccwm-test")

        prices = provider.get_price_history("SSE:603868")
        self.assertEqual(prices["latest_price"], 31.0)
        self.assertEqual(len(prices["observations"]), 2)
        statements = provider.get_financial_statements("SSE:603868")
        latest = statements["periods"][-1]
        self.assertEqual(latest["revenue"], 4_500_000_000.0)
        self.assertEqual(latest["cash_from_operations"], 820_000_000.0)
        self.assertEqual(latest["total_assets"], 5_800_000_000.0)
        catalysts = provider.get_catalyst_events("SSE:603868")
        self.assertEqual(len(catalysts["events"]), 2)
        self.assertTrue(all("603868" in event["event_id"] for event in catalysts["events"]))
        self.assertTrue(any(source["publisher"] == "中金财富" for source in bundle["sources"]))

    def test_ciccwm_fusion_rejects_market_identity_conflict(self) -> None:
        from investkit.providers.fusion import ProviderFusionError, fuse_ciccwm_research_bundle

        with self.assertRaises(ProviderFusionError):
            fuse_ciccwm_research_bundle(
                self.base,
                market_info_response=_cicc_market(code="000001", name="平安银行"),
                market_history_response=_cicc_history(code="000001"),
                financial_responses=_cicc_financials(),
                hot_news_response=_cicc_news(),
                dragon_tiger_response=_cicc_lhb(code="000001"),
                dragon_tiger_date="2026-07-16",
            )


if __name__ == "__main__":
    unittest.main()
