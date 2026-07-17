"""Mode-aware, read-only doctor contracts for imported and legacy tasks."""

from __future__ import annotations

import contextlib
from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Mapping
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MICROSOFT_FIXTURE = REPOSITORY_ROOT / "fixtures/acceptance/microsoft-fy2025.json"
IMPORTED_QUESTION = (
    "What does Microsoft FY2025 filing evidence support about financial "
    "durability and risk?"
)
EXPECTED_STEPS = (
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


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected a JSON object in {path}")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _status(check: Any) -> str:
    value = getattr(check, "status", "")
    return str(getattr(value, "value", value)).upper()


def _check_text(check: Any) -> str:
    return " ".join(
        str(getattr(check, field, "")) for field in ("name", "message")
    ).lower()


def _project_state(root: Path) -> dict[str, tuple[int, int, str, bytes]]:
    """Capture file set, mode, mtime, type/target, and regular-file bytes."""

    result: dict[str, tuple[int, int, str, bytes]] = {}
    for directory, directory_names, file_names in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        for name in sorted([*directory_names, *file_names]):
            path = directory_path / name
            relative = path.relative_to(root).as_posix()
            metadata = path.lstat()
            if path.is_symlink():
                kind = "symlink:" + os.readlink(path)
                payload = b""
            elif path.is_file():
                kind = "file"
                payload = path.read_bytes()
            elif path.is_dir():
                kind = "directory"
                payload = b""
            else:
                kind = "special"
                payload = b""
            result[relative] = (
                metadata.st_mode,
                metadata.st_mtime_ns,
                kind,
                payload,
            )
    return result


class ImportedDoctorContractTests(unittest.TestCase):
    """Exercise D1-D13 against one pinned completed Microsoft task."""

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._base_temporary_directory = tempfile.TemporaryDirectory(
            prefix="investkit-imported-doctor-base-"
        )
        base_root = Path(cls._base_temporary_directory.name)
        cls.base_project = base_root / "project"
        cls.base_project.mkdir()

        from investkit.initializer import initialize_project
        from investkit.research.workflow import run_demo_research, run_research

        initialized = initialize_project(cls.base_project, source_root=REPOSITORY_ROOT)
        if initialized.exit_code:
            raise AssertionError(f"base initialization failed: {initialized!r}")
        input_path = cls.base_project / "inputs/microsoft-fy2025.json"
        input_path.parent.mkdir()
        shutil.copy2(MICROSOFT_FIXTURE, input_path)
        imported = run_research(
            cls.base_project,
            REPOSITORY_ROOT,
            input_path=input_path,
            question=IMPORTED_QUESTION,
        )
        if imported.status != "completed":
            raise AssertionError(f"base imported workflow failed: {imported!r}")
        demo = run_demo_research(cls.base_project, REPOSITORY_ROOT)
        if demo.status != "completed":
            raise AssertionError(f"base demo workflow failed: {demo!r}")
        cls.imported_task_id = imported.task_id
        cls.demo_task_id = demo.task_id

    @classmethod
    def tearDownClass(cls) -> None:
        cls._base_temporary_directory.cleanup()

    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="investkit-imported-doctor-test-"
        )
        self.temp_root = Path(self._temporary_directory.name)
        self.project_root = self.temp_root / "project"
        shutil.copytree(
            self.base_project,
            self.project_root,
            copy_function=shutil.copy2,
            symlinks=True,
        )
        self.task_path = (
            self.project_root / "workspace/research" / self.imported_task_id
        )
        self.demo_task_path = (
            self.project_root / "workspace/research" / self.demo_task_id
        )

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def doctor(self):
        from investkit.doctor import run_doctor

        return run_doctor(self.project_root, source_root=REPOSITORY_ROOT)

    def assert_check(self, report: Any, status: str, *fragments: str) -> None:
        matches = [
            check
            for check in report.checks
            if _status(check) == status
            and all(fragment.lower() in _check_text(check) for fragment in fragments)
        ]
        self.assertTrue(
            matches,
            "no matching diagnostic; got:\n"
            + "\n".join(
                f"{_status(check)} {_check_text(check)}" for check in report.checks
            ),
        )

    def _update_artifact_hash(self, task_path: Path, relative_path: str) -> None:
        task_file = task_path / "task.json"
        task = _read_json(task_file)
        hashes = task.get("artifact_hashes")
        if not isinstance(hashes, dict):
            raise AssertionError("task has no artifact hash mapping")
        hashes[relative_path] = _sha256(task_path / relative_path)
        _write_json(task_file, task)

    def _coordinate_snapshot_hash(self) -> None:
        snapshot = self.task_path / "input/research-bundle.json"
        task_file = self.task_path / "task.json"
        task = _read_json(task_file)
        digest = _sha256(snapshot)
        task["input"]["sha256"] = digest
        task["artifact_hashes"]["input/research-bundle.json"] = digest
        _write_json(task_file, task)

    def _coordinate_snapshot_freshness(self, freshness: str) -> None:
        """Update one completed task consistently except for its evidence age."""

        from investkit.filesystem import stable_json_bytes
        from investkit.providers.file import FileProvider

        snapshot = self.task_path / "input/research-bundle.json"
        task_file = self.task_path / "task.json"
        task = _read_json(task_file)
        bundle = _read_json(snapshot)
        old_digest = str(task["input"]["sha256"])
        for source in bundle["sources"]:
            source["freshness"] = freshness
        metadata_sources = bundle["operations"]["get_source_metadata"]["data"][
            "sources"
        ]
        for source in metadata_sources:
            source["freshness"] = freshness

        snapshot.write_bytes(stable_json_bytes(bundle))
        provider = FileProvider(self.project_root, snapshot)
        new_digest = provider.bundle_sha256
        task["input"]["sha256"] = new_digest
        task["artifact_hashes"]["input/research-bundle.json"] = new_digest

        sources_path = self.task_path / "sources.json"
        sources = _read_json(sources_path)
        sources["sources"] = deepcopy(list(provider.bundle["sources"]))
        _write_json(sources_path, sources)
        task["artifact_hashes"]["sources.json"] = _sha256(sources_path)

        identity = provider.identify_security(str(task["security_query"]))
        security_id = str(identity["security_id"])
        records = {
            "data/security-identity.json": identity,
            "data/source-metadata.json": provider.get_source_metadata(security_id),
            "data/security-profile.json": provider.get_security_profile(security_id),
            "data/financial-statements.json": provider.get_financial_statements(
                security_id
            ),
            "data/price-history.json": provider.get_price_history(security_id),
            "data/valuation-inputs.json": provider.get_valuation_inputs(security_id),
            "data/peer-comparables.json": provider.get_peer_comparables(security_id),
            "data/earnings-history.json": provider.get_earnings_history(security_id),
            "data/catalyst-events.json": provider.get_catalyst_events(security_id),
        }
        for relative_path, record in records.items():
            path = self.task_path / relative_path
            _write_json(path, record)
            task["artifact_hashes"][relative_path] = _sha256(path)

        report_path = self.task_path / "report.md"
        report_path.write_text(
            report_path.read_text(encoding="utf-8").replace(
                old_digest,
                new_digest,
            ),
            encoding="utf-8",
        )
        task["artifact_hashes"]["report.md"] = _sha256(report_path)
        _write_json(task_file, task)

    def _make_incomplete(self, status: str) -> None:
        if status not in {"created", "running", "failed"}:
            raise AssertionError(status)
        task_file = self.task_path / "task.json"
        plan_file = self.task_path / "plan.json"
        run_log_file = self.task_path / "run-log.json"
        task = _read_json(task_file)
        plan = _read_json(plan_file)

        for path in (self.task_path / "capabilities").glob("*"):
            path.unlink()
        for path in (self.task_path / "data").glob("*"):
            path.unlink()
        (self.task_path / "report.md").unlink()
        for name, empty in (
            (
                "sources.json",
                {"input_mode": "imported", "schema_version": "1.0", "sources": []},
            ),
            (
                "assumptions.json",
                {
                    "assumptions": [],
                    "input_mode": "imported",
                    "schema_version": "1.0",
                },
            ),
            (
                "findings.json",
                {
                    "capabilities": {},
                    "findings": [],
                    "input_mode": "imported",
                    "schema_version": "1.0",
                },
            ),
            (
                "risks.json",
                {
                    "input_mode": "imported",
                    "risks": [],
                    "schema_version": "1.0",
                    "unknowns": [],
                    "warnings": [],
                },
            ),
        ):
            _write_json(self.task_path / name, empty)

        for index, step in enumerate(plan["steps"]):
            step.clear()
            step.update(
                {
                    "id": EXPECTED_STEPS[index],
                    "output": f"capabilities/{EXPECTED_STEPS[index]}.json",
                    "status": "pending",
                }
            )
        task.update(
            {
                "artifact_hashes": {},
                "completed_steps": [],
                "current_step": None,
                "data": [],
                "outcome": None,
                "status": status,
            }
        )
        events: list[dict[str, Any]] = [
            {
                "event": "task",
                "input_mode": "imported",
                "status": "created",
                "timestamp": task["created_at"],
            }
        ]
        if status in {"running", "failed"}:
            task["current_step"] = EXPECTED_STEPS[0]
            plan["steps"][0]["status"] = status
            events.extend(
                [
                    {
                        "event": "task",
                        "input_mode": "imported",
                        "status": "running",
                        "timestamp": task["updated_at"],
                    },
                    {
                        "event": "step",
                        "status": "running",
                        "step": EXPECTED_STEPS[0],
                        "timestamp": task["updated_at"],
                    },
                ]
            )
        if status == "failed":
            task["outcome"] = {"error": "controlled failure", "status": "failed"}
            events.append(
                {
                    "error": "controlled failure",
                    "event": "step",
                    "status": "failed",
                    "step": EXPECTED_STEPS[0],
                    "timestamp": task["updated_at"],
                }
            )
        _write_json(task_file, task)
        _write_json(plan_file, plan)
        _write_json(run_log_file, {"events": events, "task_id": self.imported_task_id})

    def _make_demo_task_legacy_shaped(self) -> None:
        task_file = self.demo_task_path / "task.json"
        task = _read_json(task_file)
        for field in ("input", "input_mode", "security_query"):
            task.pop(field, None)
        plan_file = self.demo_task_path / "plan.json"
        plan = _read_json(plan_file)
        plan.pop("input_mode", None)
        _write_json(plan_file, plan)
        for name in ("sources.json", "assumptions.json", "findings.json", "risks.json"):
            path = self.demo_task_path / name
            value = _read_json(path)
            value.pop("input_mode", None)
            _write_json(path, value)
        for path in (self.demo_task_path / "capabilities").glob("*.json"):
            value = _read_json(path)
            method = value.get("method")
            if isinstance(method, dict):
                method.pop("input_mode", None)
            _write_json(path, value)
        for relative_path in list(task["artifact_hashes"]):
            task["artifact_hashes"][relative_path] = _sha256(
                self.demo_task_path / relative_path
            )
        _write_json(task_file, task)

    def test_d1_completed_microsoft_task_passes_with_historical_warning(self) -> None:
        report = self.doctor()

        self.assertEqual(report.exit_code, 0, report)
        self.assert_check(report, "PASS", self.imported_task_id)
        self.assert_check(report, "WARN", self.imported_task_id, "stale")

    def test_d1_old_evidence_warns_even_when_freshness_label_says_current(self) -> None:
        self._coordinate_snapshot_freshness("current")

        report = self.doctor()

        self.assertEqual(report.exit_code, 0, report)
        self.assert_check(report, "PASS", self.imported_task_id)
        self.assert_check(report, "WARN", self.imported_task_id, "stale", "date")

    def test_d2_missing_snapshot_fails_safely(self) -> None:
        (self.task_path / "input/research-bundle.json").unlink()

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "snapshot")

    def test_d2_raw_snapshot_hash_mismatch_fails_safely(self) -> None:
        snapshot = self.task_path / "input/research-bundle.json"
        snapshot.write_bytes(snapshot.read_bytes() + b" ")

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "snapshot", "hash")

    def test_d3_schema_validation_is_independent_of_coordinated_hashes(self) -> None:
        snapshot = self.task_path / "input/research-bundle.json"
        bundle = _read_json(snapshot)
        bundle["schema_version"] = "99.0"
        _write_json(snapshot, bundle)
        self._coordinate_snapshot_hash()

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "bundle", "schema")

    def test_d4_persisted_registry_must_equal_snapshot_registry(self) -> None:
        path = self.task_path / "sources.json"
        sources = _read_json(path)
        sources["sources"][0]["title"] = "Coordinated but false source title"
        _write_json(path, sources)
        self._update_artifact_hash(self.task_path, "sources.json")

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "registry")

    def test_d5_capability_source_join_is_enforced_after_hash_update(self) -> None:
        relative = "capabilities/financial-statement-analysis.json"
        path = self.task_path / relative
        capability = _read_json(path)
        capability["facts"][0]["source_ids"] = ["unresolved-source"]
        source_ids: list[str] = []
        for field in ("facts", "findings", "risks"):
            for record in capability[field]:
                for source_id in record.get("source_ids", []):
                    if source_id not in source_ids:
                        source_ids.append(source_id)
        capability["source_ids"] = source_ids
        _write_json(path, capability)
        self._update_artifact_hash(self.task_path, relative)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "source")

    def test_d6_provider_record_must_equal_snapshot_operation(self) -> None:
        relative = "data/financial-statements.json"
        path = self.task_path / relative
        record = _read_json(path)
        record["currency"] = "EUR"
        _write_json(path, record)
        self._update_artifact_hash(self.task_path, relative)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "provider", "data")

    def test_d7_imported_report_cannot_be_relabeled_fictional(self) -> None:
        relative = "report.md"
        path = self.task_path / relative
        text = path.read_text(encoding="utf-8")
        text = text.replace("## Imported Data Declaration", "## Demo Data Declaration")
        text += "\nThis is fictional demo material.\n"
        path.write_text(text, encoding="utf-8")
        self._update_artifact_hash(self.task_path, relative)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "report", "mode")

    def test_d7_imported_report_requires_non_guarantee_disclosure(self) -> None:
        relative = "report.md"
        path = self.task_path / relative
        text = path.read_text(encoding="utf-8")
        text = text.replace("not independently fetch, verify, or guarantee", "reviewed")
        text = text.replace("not independently guaranteed", "reviewed")
        path.write_text(text, encoding="utf-8")
        self._update_artifact_hash(self.task_path, relative)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "report", "disclosure")

    def test_d7_imported_report_rejects_raw_markup_injection(self) -> None:
        relative = "report.md"
        path = self.task_path / relative
        path.write_text(
            path.read_text(encoding="utf-8") + "\n<script>alert(1)</script>\n",
            encoding="utf-8",
        )
        self._update_artifact_hash(self.task_path, relative)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "report", "unsafe")

    def test_d7_imported_report_rejects_chinese_action_language(self) -> None:
        relative = "report.md"
        path = self.task_path / relative
        path.write_text(
            path.read_text(encoding="utf-8") + "\n建议买入该股票。\n",
            encoding="utf-8",
        )
        self._update_artifact_hash(self.task_path, relative)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "report", "action")

    def test_report_language_boundary_does_not_reject_best_buy_name(self) -> None:
        from investkit.doctor import IMPORTED_REPORT_RESTRICTED_RE

        self.assertIsNone(
            IMPORTED_REPORT_RESTRICTED_RE.search(
                "Company: Best Buy Co., Inc.; evidence remains incomplete."
            )
        )
        self.assertIsNotNone(
            IMPORTED_REPORT_RESTRICTED_RE.search(
                "The analyst should buy the stock immediately."
            )
        )

    def test_d8_legacy_demo_is_accepted_but_imported_relabel_is_not(self) -> None:
        self._make_demo_task_legacy_shaped()

        healthy = self.doctor()

        self.assertEqual(healthy.exit_code, 0, healthy)
        self.assert_check(healthy, "PASS", self.demo_task_id)

        relative = "report.md"
        path = self.demo_task_path / relative
        text = path.read_text(encoding="utf-8").replace(
            "## Demo Data Declaration", "## Imported Data Declaration"
        )
        path.write_text(text, encoding="utf-8")
        self._update_artifact_hash(self.demo_task_path, relative)

        corrupted = self.doctor()

        self.assertNotEqual(corrupted.exit_code, 0)
        self.assert_check(corrupted, "FAIL", self.demo_task_id, "report", "mode")

    def test_d9_symlinked_input_directory_is_rejected_without_following(self) -> None:
        input_directory = self.task_path / "input"
        outside = self.temp_root / "outside-input"
        outside.mkdir()
        sentinel = outside / "research-bundle.json"
        sentinel.write_bytes((input_directory / "research-bundle.json").read_bytes())
        shutil.rmtree(input_directory)
        input_directory.symlink_to(outside, target_is_directory=True)
        before = sentinel.read_bytes()

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(
            report,
            "FAIL",
            self.imported_task_id,
            "filesystem",
            "symlink",
        )
        self.assertEqual(sentinel.read_bytes(), before)

    def test_d9_unexpected_task_symlink_is_rejected_without_following(self) -> None:
        sentinel = self.temp_root / "outside-sentinel.json"
        sentinel.write_text('{"outside": true}\n', encoding="utf-8")
        before = sentinel.read_bytes()
        (self.task_path / "unexpected.json").symlink_to(sentinel)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(
            report,
            "FAIL",
            self.imported_task_id,
            "filesystem",
            "symlink",
        )
        self.assertEqual(sentinel.read_bytes(), before)

    def test_d9_unexpected_task_fifo_is_rejected_without_opening(self) -> None:
        fifo = self.task_path / "unexpected.json"
        os.mkfifo(fifo)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(
            report,
            "FAIL",
            self.imported_task_id,
            "filesystem",
            "special",
        )

    def test_d10_credentials_fail_without_value_disclosure(self) -> None:
        fake_secret = "sk-test-NOT-REAL-0123456789abcdefghijklmnop"
        snapshot = self.task_path / "input/research-bundle.json"
        bundle = _read_json(snapshot)
        bundle["api_key"] = fake_secret
        _write_json(snapshot, bundle)
        self._coordinate_snapshot_hash()

        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            report = self.doctor()
            from investkit.cli import main

            with contextlib.chdir(self.project_root):
                exit_code = main(["doctor"])

        self.assertNotEqual(report.exit_code, 0)
        self.assertNotEqual(exit_code, 0)
        self.assertNotIn(fake_secret, repr(report))
        self.assertNotIn(fake_secret, stdout.getvalue() + stderr.getvalue())
        self.assert_check(report, "FAIL", "sensitive")

    def test_d10_report_credentials_fail_without_value_disclosure(self) -> None:
        fake_secret = "sk-test-NOT-REAL-9876543210abcdefghijklmnop"
        path = self.task_path / "report.md"
        path.write_text(
            path.read_text(encoding="utf-8") + f"\napi_key: {fake_secret}\n",
            encoding="utf-8",
        )
        self._update_artifact_hash(self.task_path, "report.md")

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assertNotIn(fake_secret, repr(report))
        self.assert_check(report, "FAIL", "sensitive")

    def test_d10_common_tokens_fail_after_artifact_hash_coordination(self) -> None:
        tokens = (
            "gh" + "p_NOTREAL0123456789abcdefghijklmnop",
            "github_" + "pat_NOTREAL_0123456789abcdefghijklmnop",
            "xo" + "xb-NOTREAL0123456789-abcdefghijklmnop",
            "gl" + "pat-NOTREAL0123456789abcdefghijkl",
            "np" + "m_NOTREAL0123456789abcdefghijklmnop",
            "sk_" + "live_NOTREAL0123456789abcdefghijklmnop",
            "AI" + "zaNOTREAL0123456789abcdefghijklmnop",
            "ya" + "29.NOTREAL0123456789abcdefghijklmnop",
            "S" + "G.NOTREAL0123456789abcdef.NOTREAL0123456789abcdefghijklmnop",
            "AKIA" + "0123456789ABCDEF",
            "ey" + "Jub3RyZWFsIjoiYSJ9.eyJub3RyZWFsIjoiYiJ9.NOTREALSIGNATURE123456789",
        )
        path = self.task_path / "report.md"
        original = path.read_text(encoding="utf-8")
        for token in tokens:
            with self.subTest(prefix=token.split("_")[0].split("-")[0]):
                path.write_text(original + f"\n{token}\n", encoding="utf-8")
                self._update_artifact_hash(self.task_path, "report.md")

                report = self.doctor()

                self.assertNotEqual(report.exit_code, 0)
                self.assertNotIn(token, repr(report))
                self.assert_check(report, "FAIL", "sensitive")

    def test_task_json_duplicate_keys_fail_closed(self) -> None:
        path = self.task_path / "task.json"
        task = _read_json(path)
        text = path.read_text(encoding="utf-8").rstrip()
        path.write_text(
            text[:-1]
            + f',\n  "id": {json.dumps(task["id"])}\n}}\n',
            encoding="utf-8",
        )

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "corrupt")

    def test_task_json_nonfinite_number_fails_closed(self) -> None:
        path = self.task_path / "task.json"
        text = path.read_text(encoding="utf-8").rstrip()
        path.write_text(
            text[:-1] + ',\n  "diagnostic_probe": NaN\n}\n',
            encoding="utf-8",
        )

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "corrupt")

    def test_task_json_oversize_payload_fails_closed(self) -> None:
        path = self.task_path / "task.json"
        task = _read_json(path)
        task["diagnostic_padding"] = "x" * (2 * 1024 * 1024)
        _write_json(path, task)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "corrupt")

    def _assert_incomplete_warns(self, status: str) -> None:
        self._make_incomplete(status)

        report = self.doctor()

        self.assertEqual(report.exit_code, 0, report)
        self.assert_check(report, "WARN", self.imported_task_id, status)

    def test_d11_valid_created_imported_task_warns_without_failure(self) -> None:
        self._assert_incomplete_warns("created")

    def test_d11_valid_running_imported_task_warns_without_failure(self) -> None:
        self._assert_incomplete_warns("running")

    def test_d11_valid_failed_imported_task_warns_without_failure(self) -> None:
        self._assert_incomplete_warns("failed")

    def test_d11_non_prefix_incomplete_state_fails(self) -> None:
        self._make_incomplete("created")
        plan_path = self.task_path / "plan.json"
        plan = _read_json(plan_path)
        plan["steps"][1]["status"] = "completed"
        _write_json(plan_path, plan)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_check(report, "FAIL", self.imported_task_id, "prefix")

    def test_d12_doctor_preserves_file_set_bytes_modes_and_mtimes(self) -> None:
        before = _project_state(self.project_root)

        report = self.doctor()

        after = _project_state(self.project_root)
        self.assertEqual(report.exit_code, 0, report)
        self.assertEqual(after, before)

    def test_d13_doctor_preserves_completed_resume_immutability(self) -> None:
        from investkit.research.workflow import resume_research

        report = self.doctor()
        self.assertEqual(report.exit_code, 0, report)
        before = {
            path.relative_to(self.task_path).as_posix(): path.read_bytes()
            for path in self.task_path.rglob("*")
            if path.is_file()
        }

        resumed = resume_research(
            self.project_root,
            self.imported_task_id,
            REPOSITORY_ROOT,
        )

        self.assertEqual(resumed.status, "completed")
        after = {
            path.relative_to(self.task_path).as_posix(): path.read_bytes()
            for path in self.task_path.rglob("*")
            if path.is_file()
        }
        self.assertEqual(set(after), set(before))
        for relative_path, payload in before.items():
            if relative_path != "run-log.json":
                self.assertEqual(after[relative_path], payload, relative_path)


if __name__ == "__main__":
    unittest.main()
