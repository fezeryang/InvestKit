"""End-to-end CLI contract for official identity plus broker evidence fusion."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tests.test_provider_fusion import (
    _cicc_financials,
    _cicc_history,
    _cicc_lhb,
    _cicc_market,
    _cicc_news,
    _gf_f10,
    _gf_financial,
    _gf_valuation,
)
from tests.test_sse_provider import SseTransport


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class FusedSymbolCliTests(unittest.TestCase):
    def test_symbol_without_peer_uses_ready_guangfa_target_valuation(self) -> None:
        from investkit.cli import main
        from investkit.initializer import initialize_project
        from investkit.providers.sse import SseAnnouncementClient

        base_bundle = SseAnnouncementClient(
            allow_network=True, transport=SseTransport()
        ).acquire_bundle("603868.SH")

        class FakeSse:
            def __init__(self, *, allow_network: bool) -> None:
                self.allow_network = allow_network

            def acquire_bundle(self, symbol: str) -> dict[str, object]:
                return base_bundle

        class FakeGuangfa:
            @classmethod
            def from_environment(cls, *, allow_network: bool) -> "FakeGuangfa":
                return cls()

            def stock_f10(self, symbol: str) -> dict[str, object]:
                return _gf_f10()

            def stock_valuation(self, symbol: str) -> dict[str, object]:
                return _gf_valuation(
                    "SH603868", "飞科电器", 134.43, 25.8652, 4.0767
                )

        with tempfile.TemporaryDirectory(prefix="investkit-gf-target-cli-") as temp:
            project = Path(temp) / "project"
            project.mkdir()
            self.assertEqual(
                initialize_project(project, source_root=REPOSITORY_ROOT).exit_code, 0
            )
            stdout = io.StringIO()
            stderr = io.StringIO()
            previous = Path.cwd()
            try:
                os.chdir(project)
                with mock.patch.dict(
                    os.environ,
                    {"GF_SKILLS_APIKEY": "test-secret"},
                    clear=True,
                ), mock.patch(
                    "investkit.cli.load_provider_environment", return_value=()
                ), mock.patch(
                    "investkit.cli.SseAnnouncementClient", FakeSse
                ), mock.patch(
                    "investkit.cli.GuangfaClient", FakeGuangfa
                ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    code = main(
                        [
                            "research",
                            "--symbol",
                            "603868.SH",
                            "--question",
                            "分析飞科电器的行业相对估值、基本面和风险。",
                            "--allow-network",
                        ]
                    )
            finally:
                os.chdir(previous)
            self.assertEqual((code, stderr.getvalue()), (0, ""))
            task_id = stdout.getvalue().split("research task: ", 1)[1].splitlines()[0]
            task = project / "workspace" / "research" / task_id
            report = (task / "report.md").read_text(encoding="utf-8")
            valuation = json.loads(
                (task / "capabilities/valuation-analysis.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(valuation["status"], "completed")
            self.assertEqual(valuation["method"]["name"], "market-relative-valuation")
            self.assertIn("Industry PE TTM comparison", report)
            self.assertNotIn("test-secret", report)

    def test_symbol_and_peer_run_fuses_sources_and_persists_all_capabilities(self) -> None:
        from investkit.cli import main
        from investkit.initializer import initialize_project
        from investkit.providers.sse import SseAnnouncementClient

        base_bundle = SseAnnouncementClient(
            allow_network=True, transport=SseTransport()
        ).acquire_bundle("603868.SH")

        class FakeSse:
            def __init__(self, *, allow_network: bool) -> None:
                self.allow_network = allow_network

            def acquire_bundle(self, symbol: str) -> dict[str, object]:
                self.symbol = symbol
                return base_bundle

        class FakeGuangfa:
            @classmethod
            def from_environment(cls, *, allow_network: bool) -> "FakeGuangfa":
                instance = cls()
                instance.allow_network = allow_network
                return instance

            def stock_f10(self, symbol: str) -> dict[str, object]:
                return _gf_f10()

            def stock_valuation(self, symbol: str) -> dict[str, object]:
                if symbol == "603868.SH":
                    return _gf_valuation("SH603868", "飞科电器", 134.43, 25.8652, 4.0767)
                return _gf_valuation("SZ002032", "苏泊尔", 610.0, 18.0, 5.2)

            def compare_financials(
                self, symbol: str, *, peer_symbol: str, year: str, report_type: int
            ) -> dict[str, object]:
                return _gf_financial(year, 14.1 if year == "2024" else 15.39, 32.0)

        class FakeCiccwm:
            @classmethod
            def from_environment(cls, *, allow_network: bool) -> "FakeCiccwm":
                instance = cls()
                instance.allow_network = allow_network
                return instance

            def market_info(self, symbol: str) -> dict[str, object]:
                return _cicc_market()

            def market_history(self, symbol: str, *, days: int) -> dict[str, object]:
                self.days = days
                return _cicc_history()

            def stock_finance(self, symbol: str, *, statement: str, year: str) -> dict[str, object]:
                return _cicc_financials()[statement]

            def hot_news(self, *, page: int, size: int) -> dict[str, object]:
                return _cicc_news()

            def dragon_tiger_list(self, *, date: str) -> dict[str, object]:
                return _cicc_lhb()

        with tempfile.TemporaryDirectory(prefix="investkit-fusion-cli-") as temp:
            project = Path(temp) / "project"
            project.mkdir()
            self.assertEqual(
                initialize_project(project, source_root=REPOSITORY_ROOT).exit_code, 0
            )
            stdout = io.StringIO()
            stderr = io.StringIO()
            previous = Path.cwd()
            try:
                os.chdir(project)
                with mock.patch.dict(
                    os.environ,
                    {
                        "GF_SKILLS_APIKEY": "test-secret",
                        "CICCWM_API_KEY": "test-ciccwm-secret",
                    },
                    clear=True,
                ), mock.patch(
                    "investkit.cli.load_provider_environment", return_value=()
                ), mock.patch(
                    "investkit.cli.SseAnnouncementClient", FakeSse
                ), mock.patch(
                    "investkit.cli.GuangfaClient", FakeGuangfa
                ), mock.patch(
                    "investkit.cli.CiccwmClient", FakeCiccwm
                ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    code = main(
                        [
                            "research",
                            "--symbol",
                            "603868.SH",
                            "--peer",
                            "002032.SZ",
                            "--question",
                            "完整分析飞科电器的基本面、财务质量、相对估值和风险。",
                            "--allow-network",
                        ]
                    )
            finally:
                os.chdir(previous)
            self.assertEqual((code, stderr.getvalue()), (0, ""))
            task_id = stdout.getvalue().split("research task: ", 1)[1].splitlines()[0]
            task = project / "workspace" / "research" / task_id
            report = (task / "report.md").read_text(encoding="utf-8")
            task_record = json.loads((task / "task.json").read_text(encoding="utf-8"))
            self.assertIn("gf-603868-f10", report)
            self.assertIn("ciccwm-603868-market", report)
            self.assertIn("苏泊尔", report)
            self.assertNotIn("&#x27;", report)
            self.assertNotIn("&quot;", report)
            self.assertEqual(report.count("bounded history is suitable"), 1)
            self.assertEqual(task_record["input"]["acquisition_mode"], "official_live")
            self.assertEqual(len(list((task / "capabilities").glob("*.json"))), 13)
            prices = json.loads((task / "data" / "price-history.json").read_text(encoding="utf-8"))
            self.assertEqual(prices["latest_price"], 31.0)
            catalysts = json.loads((task / "data" / "catalyst-events.json").read_text(encoding="utf-8"))
            self.assertEqual(len(catalysts["events"]), 2)
            thesis = json.loads(
                (task / "capabilities" / "investment-thesis.json").read_text(encoding="utf-8")
            )
            market_context = thesis["method"]["market_context"]
            self.assertAlmostEqual(market_context["available_period_return"], 31.0 / 29.5 - 1.0)
            self.assertEqual(market_context["observation_count"], 2)


if __name__ == "__main__":
    unittest.main()
