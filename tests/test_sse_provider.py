"""Offline contracts for official SSE symbol lookup and bundle acquisition."""

from __future__ import annotations

import json
import os
from pathlib import Path
import contextlib
import io
from unittest import mock
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class SseTransport:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def get(self, *, url: str, headers: dict[str, str], timeout: float, max_bytes: int) -> bytes:
        self.calls.append({"url": url, "headers": headers, "timeout": timeout, "max_bytes": max_bytes})
        if "commonQuery.do" in url:
            return json.dumps(
                {
                    "result": [
                        {
                            "COMPANY_CODE": "603868",
                            "COMPANY_ABBR": "飞科电器",
                            "FULLNAME": "上海飞科电器股份有限公司",
                            "FULL_NAME_IN_ENGLISH": "Shanghai Flyco Electrical Appliance Co., Ltd",
                            "CSRC_GREAT_CODE_DESC": "电气机械和器材制造业",
                            "CSRC_CODE_DESC": "制造业",
                            "AREA_NAME_DESC": "上海",
                            "COMPANY_ADDRESS": "上海市松江区广富林东路555号",
                            "LEGAL_REPRESENTATIVE": "李丐腾",
                            "WWW_ADDRESS": "www.flyco.com",
                            "QIANYI_DATE": "2026-06-10 17:18:04",
                        }
                    ]
                },
                ensure_ascii=False,
            ).encode("utf-8")
        return json.dumps(
            {
                "pageHelp": {
                    "data": [
                        {
                            "SECURITY_CODE": "603868",
                            "SECURITY_NAME": "飞科电器",
                            "SSEDATE": "2026-04-29",
                            "TITLE": "飞科电器2025年年度报告",
                            "URL": "/disclosure/listedinfo/announcement/c/new/2026-04-29/603868_20260429_HKU6.pdf",
                            "BULLETIN_TYPE": "年报",
                        },
                        {
                            "SECURITY_CODE": "603868",
                            "SECURITY_NAME": "飞科电器",
                            "SSEDATE": "2026-04-29",
                            "TITLE": "飞科电器2026年第一季度报告",
                            "URL": "/disclosure/listedinfo/announcement/c/new/2026-04-29/603868_20260429_YLAC.pdf",
                            "BULLETIN_TYPE": "第一季度季报",
                        },
                    ]
                }
            },
            ensure_ascii=False,
        ).encode("utf-8")


class SseProviderTests(unittest.TestCase):
    def test_lookup_requires_explicit_network_permission(self) -> None:
        from investkit.providers.sse import SseAccessError, SseAnnouncementClient

        with self.assertRaises(SseAccessError):
            SseAnnouncementClient(allow_network=False, transport=SseTransport())

    def test_real_symbol_shape_resolves_official_identity_and_reports(self) -> None:
        from investkit.providers.sse import SseAnnouncementClient

        transport = SseTransport()
        bundle = SseAnnouncementClient(allow_network=True, transport=transport).acquire_bundle(
            "603868.SH"
        )
        self.assertEqual(bundle["security"]["security_id"], "SSE:603868")
        self.assertEqual(bundle["security"]["ticker"], "603868.SH")
        self.assertEqual(bundle["security"]["legal_name"], "上海飞科电器股份有限公司")
        self.assertEqual(bundle["market"], "SSE")
        self.assertEqual(len(bundle["sources"]), 3)
        self.assertTrue(all(source["publisher"] == "上海证券交易所" for source in bundle["sources"]))
        announcement_sources = [
            source
            for source in bundle["sources"]
            if source["source_type"] == "official-exchange-announcement"
        ]
        self.assertTrue(all(source["locator"].startswith("https://static.sse.com.cn/") for source in announcement_sources))
        profile = bundle["operations"]["get_security_profile"]["data"]
        self.assertIn("李丐腾", profile["management"]["summary"])
        self.assertIn("电气机械和器材制造业", profile["competitive_context"]["summary"])
        self.assertEqual(len(transport.calls), 2)
        self.assertIn("productId=603868", transport.calls[0]["url"])
        self.assertIn("COMMON_SSE_ZQPZ_GP_GPLB_C", transport.calls[1]["url"])
        self.assertLessEqual(transport.calls[0]["max_bytes"], 2 * 1024 * 1024)

    def test_transport_rejects_non_allowlisted_endpoints_and_redirects(self) -> None:
        from investkit.providers.sse import SseAccessError, UrllibSseTransport, _NoRedirect

        with self.assertRaises(SseAccessError):
            UrllibSseTransport().get(
                url="https://example.com/security/stock/queryCompanyBulletin.do?productId=603868",
                headers={},
                timeout=1.0,
                max_bytes=1024,
            )
        with self.assertRaises(SseAccessError):
            UrllibSseTransport().get(
                url="https://query.sse.com.cn/commonQuery.do?isPagination=false&sqlId=UNAPPROVED&productid=603868",
                headers={},
                timeout=1.0,
                max_bytes=1024,
            )
        handler = _NoRedirect()
        self.assertIsNone(
            handler.redirect_request(
                request=None,
                fp=None,
                code=302,
                msg="Found",
                headers={},
                newurl="https://example.com/redirected",
            )
        )

    def test_acquired_bundle_passes_the_existing_provider_contract_and_runs_all_stages(self) -> None:
        from investkit.initializer import initialize_project
        from investkit.providers.file import FileProvider
        from investkit.providers.sse import SseAnnouncementClient
        from investkit.research.workflow import run_research_bundle
        import tempfile

        bundle = SseAnnouncementClient(allow_network=True, transport=SseTransport()).acquire_bundle(
            "603868.SH"
        )
        with tempfile.TemporaryDirectory(prefix="investkit-sse-e2e-") as temp:
            project = Path(temp) / "project"
            project.mkdir()
            self.assertEqual(initialize_project(project, source_root=REPOSITORY_ROOT).exit_code, 0)
            provider = FileProvider.from_mapping(bundle, origin="provider:sse:603868.SH")
            result = run_research_bundle(
                project,
                REPOSITORY_ROOT,
                provider=provider,
                question="完整分析飞科电器的基本面、财务、估值、风险与催化剂。",
                acquisition_mode="official_live",
            )
            self.assertEqual(result.status, "completed")
            capability_files = sorted((result.task_path / "capabilities").glob("*.json"))
            self.assertEqual(len(capability_files), 13)
            identity = json.loads((result.task_path / "data/security-identity.json").read_text(encoding="utf-8"))
            self.assertEqual(identity["ticker"], "603868.SH")
            report = result.report_path.read_text(encoding="utf-8")
            self.assertIn("上海飞科电器股份有限公司", report)
            self.assertIn("603868.SH", report)
            self.assertIn("Official Live Data Declaration", report)
            self.assertNotIn("user-supplied imported data", report)

    def test_cli_symbol_mode_runs_the_full_workflow_through_the_sse_adapter(self) -> None:
        from investkit.cli import main
        from investkit.initializer import initialize_project
        from investkit.providers.sse import SseAnnouncementClient
        import tempfile

        bundle = SseAnnouncementClient(
            allow_network=True, transport=SseTransport()
        ).acquire_bundle("603868.SH")

        class FakeClient:
            def __init__(self, *, allow_network: bool) -> None:
                self.allow_network = allow_network

            def acquire_bundle(self, symbol: str) -> dict[str, object]:
                self.symbol = symbol
                return bundle

        with tempfile.TemporaryDirectory(prefix="investkit-sse-cli-") as temp:
            project = Path(temp) / "project"
            project.mkdir()
            self.assertEqual(initialize_project(project, source_root=REPOSITORY_ROOT).exit_code, 0)
            stdout = io.StringIO()
            stderr = io.StringIO()
            previous = Path.cwd()
            try:
                os.chdir(project)
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    denied_code = main(
                        [
                            "research",
                            "--symbol",
                            "603868.SH",
                            "--question",
                            "完整分析飞科电器。",
                        ]
                    )
                self.assertEqual(denied_code, 1)
                self.assertIn("explicit network permission", stderr.getvalue())
                self.assertEqual(list((project / "workspace/research").iterdir()), [])
                stdout.seek(0)
                stdout.truncate(0)
                stderr.seek(0)
                stderr.truncate(0)
                with mock.patch("investkit.cli.SseAnnouncementClient", FakeClient), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    code = main(
                        [
                            "research",
                            "--symbol",
                            "603868.SH",
                            "--question",
                            "完整分析飞科电器。",
                            "--allow-network",
                        ]
                    )
            finally:
                os.chdir(previous)
            self.assertEqual((code, stderr.getvalue()), (0, ""))
            self.assertIn("[PASS] symbol research task:", stdout.getvalue())
            task_directories = list((project / "workspace/research").iterdir())
            self.assertEqual(len(task_directories), 1)
            self.assertEqual(len(list((task_directories[0] / "capabilities").glob("*.json"))), 13)
            from investkit.doctor import run_doctor

            doctor = run_doctor(project, source_root=REPOSITORY_ROOT)
            task_checks = [
                check
                for check in doctor.checks
                if task_directories[0].name in check.name
            ]
            self.assertEqual(doctor.exit_code, 0, doctor)
            self.assertTrue(task_checks)
            self.assertTrue(all(check.status.value == "PASS" for check in task_checks))


if __name__ == "__main__":
    unittest.main()
