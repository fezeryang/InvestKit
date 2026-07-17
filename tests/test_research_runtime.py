"""Filesystem-first contracts for the offline research task Runtime."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import socket
import tempfile
from typing import Any, Iterable, Mapping
from unittest import mock
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

CORE_SKILLS = {
    "security-identification",
    "company-deep-research",
    "business-model-analysis",
    "financial-statement-analysis",
    "earnings-quality-analysis",
    "valuation-analysis",
    "comps-analysis",
    "earnings-analysis",
    "investment-thesis",
    "bear-case-analysis",
    "catalyst-analysis",
    "source-verification",
    "investment-report",
}

REQUIRED_SPECS = {
    "research-principles.md",
    "evidence-policy.md",
    "source-policy.md",
    "financial-data-policy.md",
    "valuation-policy.md",
    "risk-policy.md",
    "report-policy.md",
}

REQUIRED_TASK_PATHS = {
    "task.json",
    "question.md",
    "plan.json",
    "loaded-specs.json",
    "installed-skills.json",
    "data",
    "sources.json",
    "assumptions.json",
    "findings.json",
    "risks.json",
    "run-log.json",
    "report.md",
}

EXPECTED_WORKFLOW_STEPS = (
    "security-identification",
    "company-deep-research",
    "business-model-analysis",
    "financial-statement-analysis",
    "earnings-quality-analysis",
    "valuation-analysis",
    "comps-analysis",
    "earnings-analysis",
    "investment-thesis",
    "bear-case-analysis",
    "catalyst-analysis",
    "source-verification",
    "investment-report",
)

REPORT_SECTIONS = (
    "Research Subject",
    "Demo Data Declaration",
    "Data Date",
    "Executive Summary",
    "Company Overview",
    "Financial Analysis",
    "Earnings Quality",
    "Cash Flow and Balance Sheet Analysis",
    "Valuation Analysis",
    "Comparable Companies Analysis",
    "Earnings Analysis",
    "Investment Thesis",
    "Independent Bear Case",
    "Catalyst Analysis",
    "Positive Evidence",
    "Negative Evidence",
    "Primary Risks",
    "Assumptions",
    "Unknowns / To Verify",
    "Data Sources",
    "Used Skills",
    "Loaded Specs",
    "Generation Time",
    "Research Boundary",
)


def _runtime_api():
    from investkit.initializer import initialize_project
    from investkit.providers.demo import DemoProvider
    from investkit.research.workflow import resume_demo_research, run_demo_research

    return initialize_project, DemoProvider, run_demo_research, resume_demo_research


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def _records(value: Any, *keys: str) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, Mapping):
        for key in keys:
            candidate = value.get(key)
            if isinstance(candidate, list):
                return candidate
    return []


def _record_names(records: Iterable[Any]) -> set[str]:
    names: set[str] = set()
    for record in records:
        if isinstance(record, str):
            names.add(Path(record).name)
        elif isinstance(record, Mapping):
            value = record.get("name", record.get("id", record.get("path", "")))
            names.add(Path(str(value)).name)
    return names


def _normalize_step(value: Any) -> str:
    if isinstance(value, Mapping):
        value = value.get("id", value.get("name", ""))
    return re.sub(
        r"-+",
        "-",
        str(value).strip().lower().replace("_", " ").replace(" ", "-"),
    )


def _result_status(result: Any) -> str:
    return str(getattr(result, "status", "")).lower()


class ResearchRuntimeContractTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="investkit-research-test-"
        )
        self.project_root = Path(self._temporary_directory.name) / "project"
        self.project_root.mkdir()
        initialize_project, _, _, _ = _runtime_api()
        result = initialize_project(self.project_root, source_root=REPOSITORY_ROOT)
        self.assertEqual(result.exit_code, 0, result)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def run_demo(self, provider: Any = None) -> Any:
        _, _, run_demo_research, _ = _runtime_api()
        result = run_demo_research(
            self.project_root,
            REPOSITORY_ROOT,
            provider=provider,
        )
        self.assertTrue(getattr(result, "task_id", ""))
        return result

    def resume(self, task_id: str, provider: Any = None) -> Any:
        _, _, _, resume_demo_research = _runtime_api()
        return resume_demo_research(
            self.project_root,
            task_id,
            REPOSITORY_ROOT,
            provider=provider,
        )

    def task_path(self, result: Any) -> Path:
        return self.project_root / "workspace/research" / str(result.task_id)

    def test_demo_creates_a_complete_task_and_runs_the_ordered_workflow(self) -> None:
        result = self.run_demo()
        task_path = self.task_path(result)

        self.assertEqual(_result_status(result), "completed")
        self.assertTrue(task_path.is_dir())
        self.assertTrue(REQUIRED_TASK_PATHS.issubset({path.name for path in task_path.iterdir()}))
        self.assertTrue(any((task_path / "data").glob("*.json")))

        task = _read_json(task_path / "task.json")
        self.assertEqual(task.get("id"), result.task_id)
        self.assertEqual(task.get("status"), "completed")
        for field in (
            "created_at",
            "updated_at",
            "question",
            "workflow",
            "skills",
            "specs",
            "warnings",
            "outcome",
        ):
            self.assertIn(field, task)

        plan = _read_json(task_path / "plan.json")
        steps = tuple(
            _normalize_step(step) for step in _records(plan, "steps", "plan")
        )
        self.assertEqual(steps, EXPECTED_WORKFLOW_STEPS)

        run_log = _read_json(task_path / "run-log.json")
        events = _records(run_log, "events", "runs")
        serialized_events = json.dumps(events).lower()
        for status in ("created", "running", "completed"):
            self.assertIn(status, serialized_events)
        for step in EXPECTED_WORKFLOW_STEPS:
            self.assertIn(step, serialized_events.replace("_", "-"))

    def test_each_demo_has_a_unique_id_and_preserves_prior_tasks(self) -> None:
        first = self.run_demo()
        first_path = self.task_path(first)
        first_report = (first_path / "report.md").read_bytes()

        second = self.run_demo()

        self.assertNotEqual(first.task_id, second.task_id)
        self.assertTrue(first_path.is_dir())
        self.assertEqual((first_path / "report.md").read_bytes(), first_report)
        task_directories = {
            path.name
            for path in (self.project_root / "workspace/research").iterdir()
            if path.is_dir()
        }
        self.assertTrue({first.task_id, second.task_id}.issubset(task_directories))

    def test_task_records_exact_loaded_specs_and_installed_skills(self) -> None:
        result = self.run_demo()
        task_path = self.task_path(result)

        installed = _read_json(task_path / "installed-skills.json")
        self.assertEqual(_record_names(_records(installed, "skills", "installed")), CORE_SKILLS)

        loaded = _read_json(task_path / "loaded-specs.json")
        records = _records(loaded, "specs", "loaded_specs")
        self.assertEqual(_record_names(records), REQUIRED_SPECS)
        for record in records:
            with self.subTest(spec=record):
                self.assertIsInstance(record, Mapping)
                relative = str(record["path"]).replace("\\", "/")
                source = REPOSITORY_ROOT / relative
                self.assertTrue(source.is_file())
                self.assertTrue(record.get("version"))
                self.assertEqual(
                    record.get("sha256"),
                    hashlib.sha256(source.read_bytes()).hexdigest(),
                )

    def test_sources_assumptions_findings_risks_and_report_are_nonempty(self) -> None:
        result = self.run_demo()
        task_path = self.task_path(result)

        for name in ("sources.json", "assumptions.json", "findings.json", "risks.json"):
            with self.subTest(artifact=name):
                payload = _read_json(task_path / name)
                self.assertTrue(payload, f"{name} must contain durable research evidence")
        report = (task_path / "report.md").read_text(encoding="utf-8")
        self.assertTrue(report.strip())

    def test_report_has_all_sections_demo_disclosure_and_no_trade_instruction(self) -> None:
        result = self.run_demo()
        report = (self.task_path(result) / "report.md").read_text(encoding="utf-8")

        for section in REPORT_SECTIONS:
            with self.subTest(section=section):
                self.assertRegex(report, rf"(?im)^#+\s+{re.escape(section)}\s*$")
        self.assertRegex(report, r"(?i)fictional|demo data")
        self.assertRegex(report, r"(?i)not\s+(?:real-time|live)")
        self.assertNotRegex(
            report,
            r"(?i)(?:recommend(?:ation)?\s*:\s*(?:buy|sell)|"
            r"you should (?:buy|sell)|we recommend (?:buying|selling)|"
            r"guaranteed (?:return|profit)|risk-free return|price will)",
        )

    def test_completed_resume_appends_an_event_without_rewriting_artifacts(self) -> None:
        result = self.run_demo()
        task_path = self.task_path(result)
        immutable_paths = [
            task_path / "report.md",
            task_path / "sources.json",
            task_path / "assumptions.json",
            task_path / "findings.json",
            task_path / "risks.json",
            task_path / "loaded-specs.json",
            task_path / "installed-skills.json",
            *sorted((task_path / "data").glob("*.json")),
        ]
        before = {path.relative_to(task_path): path.read_bytes() for path in immutable_paths}
        run_log_before = (task_path / "run-log.json").read_bytes()

        resumed = self.resume(result.task_id)

        self.assertEqual(resumed.task_id, result.task_id)
        self.assertEqual(_result_status(resumed), "completed")
        after = {path.relative_to(task_path): path.read_bytes() for path in immutable_paths}
        self.assertEqual(after, before)
        run_log_after = (task_path / "run-log.json").read_bytes()
        self.assertNotEqual(run_log_after, run_log_before)
        self.assertIn("resume", run_log_after.decode("utf-8").lower())

    def test_corrupt_task_is_rejected_without_overwriting_completed_report(self) -> None:
        result = self.run_demo()
        task_path = self.task_path(result)
        report_before = (task_path / "report.md").read_bytes()
        (task_path / "task.json").write_text('{"status": "completed",', encoding="utf-8")

        with self.assertRaises(Exception) as raised:
            self.resume(result.task_id)

        self.assertRegex(str(raised.exception).lower(), r"corrupt|invalid|task")
        self.assertEqual((task_path / "report.md").read_bytes(), report_before)

    def test_completed_resume_rejects_materially_incomplete_findings(self) -> None:
        result = self.run_demo()
        task_path = self.task_path(result)
        report_before = (task_path / "report.md").read_bytes()
        (task_path / "findings.json").write_text(
            '{"schema_version":"1.0"}\n', encoding="utf-8"
        )

        with self.assertRaises(Exception) as raised:
            self.resume(result.task_id)

        self.assertRegex(str(raised.exception).lower(), r"incomplete|findings|task")
        self.assertEqual((task_path / "report.md").read_bytes(), report_before)

    def test_resume_rejects_external_symlinked_artifact_without_reading_it(self) -> None:
        result = self.run_demo()
        task_path = self.task_path(result)
        outside = self.project_root.parent / "outside-findings.json"
        outside_payload = b'{"secret":"outside sentinel"}\n'
        outside.write_bytes(outside_payload)
        findings = task_path / "findings.json"
        findings.unlink()
        findings.symlink_to(outside)

        with self.assertRaises(Exception):
            self.resume(result.task_id)

        self.assertEqual(outside.read_bytes(), outside_payload)

    def test_path_traversal_task_id_is_rejected(self) -> None:
        outside = self.project_root.parent / "escape-marker"
        with self.assertRaises(Exception):
            self.resume("../escape-marker")
        self.assertFalse(outside.exists())

    def test_task_store_refuses_non_finite_machine_json(self) -> None:
        from investkit.research.tasks import TaskStore

        store = TaskStore(self.project_root)
        task_path = store.create("research-non-finite-json")
        with self.assertRaises(ValueError):
            store.write_json(task_path, "non-finite.json", {"value": float("inf")})
        self.assertFalse((task_path / "non-finite.json").exists())

    def test_task_store_parent_swap_cannot_redirect_atomic_write(self) -> None:
        from investkit.research.tasks import TaskStore

        store = TaskStore(self.project_root)
        task_path = store.create("research-parent-swap")
        capabilities = task_path / "capabilities"
        original_capabilities = task_path / "capabilities.original"
        outside = self.project_root.parent / "outside-capabilities"
        outside.mkdir()
        original_artifact_path = store._artifact_path
        swapped = False

        def swap_after_preflight(path: Path, relative_path: str) -> Path:
            nonlocal swapped
            resolved = original_artifact_path(path, relative_path)
            if relative_path == "capabilities/probe.json" and not swapped:
                capabilities.rename(original_capabilities)
                capabilities.symlink_to(outside, target_is_directory=True)
                swapped = True
            return resolved

        with mock.patch.object(
            store,
            "_artifact_path",
            side_effect=swap_after_preflight,
        ):
            with self.assertRaises(Exception):
                store.write_json(
                    task_path,
                    "capabilities/probe.json",
                    {"must_remain": "inside the task"},
                )

        self.assertTrue(swapped, "the deterministic parent-swap probe did not run")
        self.assertFalse((outside / "probe.json").exists())
        self.assertFalse((original_capabilities / "probe.json").exists())

    def test_task_store_parent_swap_cannot_redirect_artifact_read(self) -> None:
        from investkit.research.tasks import CorruptTaskError, TaskStore

        store = TaskStore(self.project_root)
        task_path = store.create("research-read-parent-swap")
        store.write_json(task_path, "data/record.json", {"origin": "task"})
        data = task_path / "data"
        original_data = task_path / "data.original"
        outside = self.project_root.parent / "outside-data"
        outside.mkdir()
        outside_record = outside / "record.json"
        outside_record.write_text('{"origin":"outside sentinel"}\n', encoding="utf-8")
        outside_before = outside_record.read_bytes()
        original_artifact_path = store._artifact_path
        swapped = False

        def swap_after_preflight(path: Path, relative_path: str) -> Path:
            nonlocal swapped
            resolved = original_artifact_path(path, relative_path)
            if relative_path == "data/record.json" and not swapped:
                data.rename(original_data)
                data.symlink_to(outside, target_is_directory=True)
                swapped = True
            return resolved

        with mock.patch.object(
            store,
            "_artifact_path",
            side_effect=swap_after_preflight,
        ):
            with self.assertRaises(CorruptTaskError):
                store.read_json(task_path, "data/record.json")

        self.assertTrue(swapped, "the deterministic parent-swap probe did not run")
        self.assertEqual(outside_record.read_bytes(), outside_before)
        self.assertEqual(
            _read_json(original_data / "record.json"),
            {"origin": "task"},
        )

    def test_task_store_rejects_nonstandard_or_ambiguous_persisted_json(self) -> None:
        from investkit.research.tasks import CorruptTaskError, TaskStore

        store = TaskStore(self.project_root)
        task_path = store.create("research-strict-json")
        invalid_payloads = {
            "duplicate.json": '{"status":"running","status":"completed"}\n',
            "nan.json": '{"value":NaN}\n',
            "overflow.json": '{"value":1e9999}\n',
        }

        for name, payload in invalid_payloads.items():
            with self.subTest(artifact=name):
                store.write_text(task_path, name, payload)
                with self.assertRaises(CorruptTaskError):
                    store.read_json(task_path, name)

    def test_workflow_failure_persists_failed_state_and_run_log(self) -> None:
        _, DemoProvider, _, _ = _runtime_api()
        delegate = DemoProvider(asset_root=REPOSITORY_ROOT)

        class FailingProvider:
            def __getattr__(self, name: str) -> Any:
                return getattr(delegate, name)

            def get_financial_statements(self, security_id: str) -> Mapping[str, Any]:
                raise RuntimeError("controlled fixture failure")

        task_root = self.project_root / "workspace/research"
        before = {path.name for path in task_root.iterdir() if path.is_dir()}
        try:
            result = self.run_demo(provider=FailingProvider())
        except Exception:
            result = None
        after = {path.name for path in task_root.iterdir() if path.is_dir()}
        created = after - before
        self.assertEqual(len(created), 1)
        task_path = task_root / created.pop()
        task = _read_json(task_path / "task.json")
        self.assertEqual(task.get("status"), "failed")
        self.assertTrue((task_path / "run-log.json").is_file())
        run_log = json.dumps(_read_json(task_path / "run-log.json")).lower()
        self.assertIn("failed", run_log)
        self.assertIn("controlled fixture failure", run_log)
        if result is not None:
            self.assertEqual(_result_status(result), "failed")

    def test_failed_task_resumes_only_incomplete_steps_and_preserves_completed_data(
        self,
    ) -> None:
        _, DemoProvider, _, _ = _runtime_api()
        delegate = DemoProvider(asset_root=REPOSITORY_ROOT)

        class FailingProvider:
            def __getattr__(self, name: str) -> Any:
                return getattr(delegate, name)

            def get_financial_statements(self, security_id: str) -> Mapping[str, Any]:
                raise RuntimeError("controlled resumable failure")

        failed = self.run_demo(provider=FailingProvider())
        task_path = self.task_path(failed)
        identity_before = (task_path / "data/security-identity.json").read_bytes()
        profile_before = (task_path / "data/security-profile.json").read_bytes()

        resumed = self.resume(failed.task_id)

        self.assertEqual(_result_status(resumed), "completed")
        self.assertEqual(
            (task_path / "data/security-identity.json").read_bytes(), identity_before
        )
        self.assertEqual(
            (task_path / "data/security-profile.json").read_bytes(), profile_before
        )
        run_log = (task_path / "run-log.json").read_text(encoding="utf-8").lower()
        self.assertIn("resume-skipped", run_log)
        report = (task_path / "report.md").read_text(encoding="utf-8")
        self.assertNotIn("- Question: # Research Question", report)

    def test_workflow_failure_redacts_bare_secret_from_owned_state(self) -> None:
        _, DemoProvider, _, _ = _runtime_api()
        delegate = DemoProvider(asset_root=REPOSITORY_ROOT)
        fake_secret = "sk-test-NOT-REAL-0123456789abcdefghijklmnop"

        class SecretFailingProvider:
            def __getattr__(self, name: str) -> Any:
                return getattr(delegate, name)

            def get_financial_statements(self, security_id: str) -> Mapping[str, Any]:
                raise RuntimeError(f"provider rejected {fake_secret}")

        failed = self.run_demo(provider=SecretFailingProvider())
        serialized = "\n".join(
            path.read_text(encoding="utf-8")
            for path in self.task_path(failed).rglob("*")
            if path.is_file()
        )

        self.assertEqual(_result_status(failed), "failed")
        self.assertNotIn(fake_secret, serialized)
        self.assertIn("[REDACTED]", serialized)

    def test_normal_workflow_is_offline_and_writes_no_forbidden_runtime_state(self) -> None:
        with (
            mock.patch.object(
                socket,
                "create_connection",
                side_effect=AssertionError("network access is forbidden"),
            ),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=AssertionError("network access is forbidden"),
            ),
        ):
            result = self.run_demo()

        task_path = self.task_path(result)
        relative_paths = {
            path.relative_to(task_path).as_posix() for path in task_path.rglob("*")
        }
        serialized = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in task_path.rglob("*")
            if path.is_file()
        ).replace("\\", "/").lower()
        self.assertFalse(any(".trellis" in path for path in relative_paths))
        self.assertNotIn("third_party/raw", serialized)
        self.assertNotIn("adapted/skills", serialized)
        installed = {
            path.parent.name
            for path in (self.project_root / ".agents/skills").glob("*/SKILL.md")
        }
        self.assertEqual(installed, CORE_SKILLS)


if __name__ == "__main__":
    unittest.main()
