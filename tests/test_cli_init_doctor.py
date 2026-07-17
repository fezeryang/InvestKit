"""Contract tests for the InvestKit CLI, initialization, and diagnostics.

These tests intentionally exercise only first-party repository assets. They do
not inspect, import, copy, or execute material under third_party/ or adapted/.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
from typing import Any, Iterable, Mapping
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

FIRST_PARTY_SOURCE_DIRECTORIES = (
    "skills",
    "agents",
    "workflows",
    "specs",
    "schemas",
    "packages",
    "workspace-template",
    "fixtures",
)

FORBIDDEN_SOURCE_FRAGMENTS = ("third_party/raw", "adapted/skills")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
STATUS_LINE_RE = re.compile(
    r"^\s*\[?(PASS|WARN|FAIL)\]?(?:\s|:|-)" , re.MULTILINE
)


def _runtime_api():
    """Import lazily so unittest still collects the complete RED suite."""

    from investkit.cli import build_parser, main
    from investkit.doctor import run_doctor
    from investkit.initializer import initialize_project

    return build_parser, main, initialize_project, run_doctor


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise AssertionError(f"expected a JSON object in {path}")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized_relative_path(value: str) -> str:
    return PurePosixPath(value.replace("\\", "/")).as_posix()


def _status_value(check: Any) -> str:
    status = getattr(check, "status", "")
    return str(getattr(status, "value", status)).upper()


def _check_text(check: Any) -> str:
    return " ".join(
        str(getattr(check, field, "")) for field in ("name", "message")
    ).lower()


class RuntimeTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="investkit-runtime-test-"
        )
        self.temp_root = Path(self._temporary_directory.name)
        self.project_root = self.temp_root / "project"
        self.project_root.mkdir()

    def tearDown(self) -> None:
        # A writability test deliberately removes permissions. Restore them so
        # TemporaryDirectory can clean up even when an assertion fails.
        workspace = self.project_root / "workspace"
        if workspace.exists():
            workspace.chmod(0o700)
        self._temporary_directory.cleanup()

    def initialize(
        self,
        *,
        project_root: Path | None = None,
        source_root: Path = REPOSITORY_ROOT,
    ) -> Any:
        _, _, initialize_project, _ = _runtime_api()
        project = project_root or self.project_root
        result = initialize_project(project, source_root=source_root)
        self.assertEqual(
            result.exit_code,
            0,
            f"initialization failed: {result!r}",
        )
        return result

    def doctor(
        self,
        *,
        project_root: Path | None = None,
        source_root: Path = REPOSITORY_ROOT,
    ) -> Any:
        _, _, _, run_doctor = _runtime_api()
        return run_doctor(project_root or self.project_root, source_root=source_root)

    def invoke_main(
        self,
        *arguments: str,
        project_root: Path | None = None,
    ) -> tuple[int, str, str]:
        _, main, _, _ = _runtime_api()
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            contextlib.chdir(project_root or self.project_root),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            try:
                exit_code = main(list(arguments))
            except SystemExit as error:
                exit_code = int(error.code or 0)
        self.assertIsInstance(exit_code, int)
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def copy_first_party_source(self) -> Path:
        source_root = self.temp_root / "source"
        source_root.mkdir()
        for directory_name in FIRST_PARTY_SOURCE_DIRECTORIES:
            source = REPOSITORY_ROOT / directory_name
            if source.exists():
                shutil.copytree(source, source_root / directory_name)
        return source_root

    def assert_report_has(
        self,
        report: Any,
        status: str,
        *message_fragments: str,
    ) -> None:
        matching = [
            check
            for check in report.checks
            if _status_value(check) == status
            and all(fragment.lower() in _check_text(check) for fragment in message_fragments)
        ]
        self.assertTrue(
            matching,
            "no matching diagnostic; got:\n"
            + "\n".join(
                f"{_status_value(check)} {_check_text(check)}"
                for check in report.checks
            ),
        )


class CliContractTests(RuntimeTestCase):
    def test_parser_exposes_only_the_runnable_vertical_slice(self) -> None:
        build_parser, _, _, _ = _runtime_api()
        parser = build_parser()

        self.assertIsInstance(parser, argparse.ArgumentParser)
        help_text = parser.format_help().lower()
        for command in ("init", "doctor", "demo"):
            self.assertIn(command, help_text)

        command_actions = [
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ]
        self.assertEqual(len(command_actions), 1)
        choices = set(command_actions[0].choices)
        self.assertTrue({"init", "doctor", "demo"}.issubset(choices))
        self.assertTrue({"add", "update", "uninstall"}.isdisjoint(choices))

        # The required nested demo command and resume option must be parseable.
        parser.parse_args(["demo", "research"])
        parser.parse_args(["demo", "research", "--resume", "task-123"])

    def test_help_is_successful_and_lifecycle_placeholders_are_not(self) -> None:
        help_code, help_stdout, help_stderr = self.invoke_main("--help")
        self.assertEqual(help_code, 0)
        self.assertIn("init", help_stdout.lower())
        self.assertIn("doctor", help_stdout.lower())
        self.assertNotIn("traceback", (help_stdout + help_stderr).lower())

        for command in ("add", "update", "uninstall"):
            with self.subTest(command=command):
                code, stdout, stderr = self.invoke_main(command)
                self.assertNotEqual(code, 0)
                combined = (stdout + stderr).lower()
                self.assertNotIn("success", combined)
                self.assertNotIn("traceback", combined)


class InitContractTests(RuntimeTestCase):
    def test_codex_adapter_detects_and_describes_an_empty_project(self) -> None:
        from investkit.platforms.codex import CodexAdapter

        adapter = CodexAdapter()
        description = adapter.describe(self.project_root)

        self.assertTrue(adapter.detect_project(self.project_root))
        self.assertTrue(description["detected"])
        self.assertEqual(description["host_platform"], "codex")
        self.assertEqual(description["installation_target"], ".agents/skills")
        self.assertEqual(description["agents_path_state"], "missing")

    def test_init_preserves_a_file_occupying_the_codex_directory(self) -> None:
        _, _, initialize_project, _ = _runtime_api()
        agents_path = self.project_root / ".agents"
        sentinel = "user-owned path\n"
        agents_path.write_text(sentinel, encoding="utf-8")

        result = initialize_project(self.project_root, source_root=REPOSITORY_ROOT)

        self.assertNotEqual(result.exit_code, 0)
        self.assertEqual(agents_path.read_text(encoding="utf-8"), sentinel)
        self.assertFalse((self.project_root / ".investkit").exists())
        self.assertFalse((self.project_root / "workspace").exists())

    def test_init_populates_an_empty_project(self) -> None:
        code, stdout, stderr = self.invoke_main("init")

        self.assertEqual(code, 0, stderr)
        self.assertIn("CREATE", stdout)
        self.assertNotIn("Traceback", stdout + stderr)
        for required_path in (
            ".investkit/config.json",
            ".investkit/install-manifest.json",
            ".agents/investkit.json",
            "workspace/README.md",
        ):
            self.assertTrue((self.project_root / required_path).is_file(), required_path)
        self.assertTrue((self.project_root / "workspace/research").is_dir())

        config = _read_json(self.project_root / ".investkit/config.json")
        self.assertIsInstance(config.get("investkit_version"), str)
        self.assertTrue(config["investkit_version"])
        self.assertEqual(config.get("host_platform"), "codex")
        self.assertEqual(
            _normalized_relative_path(config.get("installation_target", "")),
            ".agents/skills",
        )
        self.assertEqual(
            _normalized_relative_path(config.get("workspace_path", "")),
            "workspace",
        )
        self.assertEqual(set(config.get("installed_skills", [])), CORE_SKILLS)
        self.assertTrue(config.get("initialized_at", "").endswith("Z"))
        self.assertTrue(config.get("source_root"))
        source_directories = config.get("source_directories", {})
        self.assertIsInstance(source_directories, dict)
        self.assertTrue({"skills", "specs", "workflows"}.issubset(source_directories))

        adapter = _read_json(self.project_root / ".agents/investkit.json")
        self.assertEqual(
            adapter.get("host_platform", adapter.get("platform")),
            "codex",
        )
        self.assertEqual(adapter.get("managed_by"), "investkit")

        installed = {
            child.name
            for child in (self.project_root / ".agents/skills").iterdir()
            if child.is_dir() and (child / "SKILL.md").is_file()
        }
        self.assertEqual(installed, CORE_SKILLS)

    def test_init_is_idempotent_and_reports_skips(self) -> None:
        self.initialize()
        owned_paths = [
            self.project_root / ".investkit/config.json",
            self.project_root / ".investkit/install-manifest.json",
            self.project_root / ".agents/investkit.json",
            *sorted((self.project_root / ".agents/skills").glob("*/SKILL.md")),
        ]
        before = {path.relative_to(self.project_root): path.read_bytes() for path in owned_paths}

        code, stdout, stderr = self.invoke_main("init")

        self.assertEqual(code, 0, stderr)
        self.assertIn("SKIP", stdout)
        after = {path.relative_to(self.project_root): path.read_bytes() for path in owned_paths}
        self.assertEqual(after, before)

    def test_init_preserves_a_conflicting_user_file(self) -> None:
        user_skill = self.project_root / ".agents/skills/company-deep-research/SKILL.md"
        user_skill.parent.mkdir(parents=True)
        sentinel = "# User-owned file\nDO NOT OVERWRITE\n"
        user_skill.write_text(sentinel, encoding="utf-8")

        code, stdout, stderr = self.invoke_main("init")

        self.assertNotEqual(code, 0)
        self.assertEqual(user_skill.read_text(encoding="utf-8"), sentinel)
        self.assertIn("WARN", stdout + stderr)
        self.assertNotIn("Traceback", stdout + stderr)

    def test_manifest_records_complete_verified_source_to_target_mappings(self) -> None:
        self.initialize()
        manifest = _read_json(self.project_root / ".investkit/install-manifest.json")
        mappings = manifest.get("mappings")
        self.assertIsInstance(mappings, list)
        assert isinstance(mappings, list)

        skill_mappings = {
            PurePosixPath(_normalized_relative_path(mapping["source"])).parts[-2]: mapping
            for mapping in mappings
            if mapping.get("kind") == "skill"
            and _normalized_relative_path(mapping.get("source", "")).endswith("/SKILL.md")
        }
        self.assertEqual(set(skill_mappings), CORE_SKILLS)

        source_root = Path(manifest.get("source_root", REPOSITORY_ROOT)).resolve()
        for skill_name, mapping in skill_mappings.items():
            with self.subTest(skill=skill_name):
                source_relative = _normalized_relative_path(mapping["source"])
                target_relative = _normalized_relative_path(mapping["target"])
                self.assertEqual(source_relative, f"skills/{skill_name}/SKILL.md")
                self.assertEqual(
                    target_relative,
                    f".agents/skills/{skill_name}/SKILL.md",
                )
                self.assertRegex(mapping.get("source_sha256", ""), HASH_RE)
                self.assertRegex(mapping.get("target_sha256", ""), HASH_RE)
                self.assertEqual(
                    mapping["source_sha256"],
                    _sha256(source_root / source_relative),
                )
                self.assertEqual(
                    mapping["target_sha256"],
                    _sha256(self.project_root / target_relative),
                )
                self.assertEqual(mapping["source_sha256"], mapping["target_sha256"])

        specs = manifest.get("specs")
        self.assertIsInstance(specs, list)
        assert isinstance(specs, list)
        spec_names = {
            PurePosixPath(_normalized_relative_path(record["path"])).name
            for record in specs
        }
        self.assertEqual(spec_names, REQUIRED_SPECS)
        for record in specs:
            self.assertTrue(record.get("version"))
            self.assertRegex(record.get("sha256", ""), HASH_RE)

    def test_init_never_records_or_installs_a_forbidden_source(self) -> None:
        self.initialize()
        owned_state = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                self.project_root / ".investkit/config.json",
                self.project_root / ".investkit/install-manifest.json",
                self.project_root / ".agents/investkit.json",
            )
        ).replace("\\", "/").lower()

        for fragment in FORBIDDEN_SOURCE_FRAGMENTS:
            self.assertNotIn(fragment, owned_state)
        installed_names = {
            path.parent.name
            for path in (self.project_root / ".agents/skills").glob("*/SKILL.md")
        }
        self.assertEqual(installed_names, CORE_SKILLS)

    def test_init_rejects_complete_trees_below_forbidden_source_boundaries(self) -> None:
        _, _, initialize_project, _ = _runtime_api()
        for relative_root in ("third_party/raw/forged", "adapted/skills/forged"):
            with self.subTest(source=relative_root):
                forged_source = self.temp_root / relative_root
                forged_source.mkdir(parents=True)
                for directory_name in FIRST_PARTY_SOURCE_DIRECTORIES:
                    source = REPOSITORY_ROOT / directory_name
                    if source.exists():
                        shutil.copytree(source, forged_source / directory_name)
                project = self.temp_root / ("project-" + relative_root.split("/")[0])
                project.mkdir()

                result = initialize_project(project, source_root=forged_source)

                self.assertNotEqual(result.exit_code, 0)
                self.assertFalse((project / ".agents").exists())
                self.assertFalse((project / ".investkit").exists())


class DoctorContractTests(RuntimeTestCase):
    def test_healthy_environment_has_only_pass_or_warn_and_exits_zero(self) -> None:
        self.initialize()

        report = self.doctor()

        self.assertEqual(report.exit_code, 0)
        self.assertGreaterEqual(len(report.checks), 14)
        statuses = {_status_value(check) for check in report.checks}
        self.assertTrue(statuses.issubset({"PASS", "WARN", "FAIL"}))
        self.assertIn("PASS", statuses)
        self.assertNotIn("FAIL", statuses)

        code, stdout, stderr = self.invoke_main("doctor")
        self.assertEqual(code, 0, stderr)
        self.assertRegex(stdout, STATUS_LINE_RE)
        self.assertIn("PASS", stdout)
        self.assertNotIn("FAIL", stdout)

    def test_unmanaged_codex_skill_is_a_warning_and_warnings_exit_zero(self) -> None:
        self.initialize()
        unmanaged = self.project_root / ".agents/skills/user-owned/SKILL.md"
        unmanaged.parent.mkdir(parents=True)
        unmanaged.write_text("# User-owned Skill\n", encoding="utf-8")

        report = self.doctor()

        self.assertEqual(report.exit_code, 0)
        self.assert_report_has(report, "WARN", "user-owned")
        code, stdout, stderr = self.invoke_main("doctor")
        self.assertEqual(code, 0, stderr)
        self.assertIn("WARN", stdout)
        self.assertNotIn("FAIL", stdout)

    def test_missing_installed_skill_is_a_critical_failure(self) -> None:
        self.initialize()
        missing = self.project_root / ".agents/skills/company-deep-research/SKILL.md"
        missing.unlink()

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", "company-deep-research")

    def test_missing_required_spec_is_a_critical_failure(self) -> None:
        source_root = self.copy_first_party_source()
        self.initialize(source_root=source_root)
        (source_root / "specs/source-policy.md").unlink()

        report = self.doctor(source_root=source_root)

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", "source-policy")

    def test_missing_required_workflow_is_reported_as_a_critical_failure(self) -> None:
        source_root = self.copy_first_party_source()
        self.initialize(source_root=source_root)
        (source_root / "workflows/company-deep-dive.json").unlink()

        report = self.doctor(source_root=source_root)

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", "workflow")

    def test_invalid_demo_metadata_is_a_critical_provider_failure(self) -> None:
        source_root = self.copy_first_party_source()
        self.initialize(source_root=source_root)
        fixture_path = source_root / "fixtures/demo/aurora-lantern-works.json"
        fixture = _read_json(fixture_path)
        fixture["currency"] = ""
        _write_json(fixture_path, fixture)

        report = self.doctor(source_root=source_root)

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", "provider")

    def test_corrupt_mapping_or_hash_is_a_critical_failure(self) -> None:
        self.initialize()
        manifest_path = self.project_root / ".investkit/install-manifest.json"
        manifest = _read_json(manifest_path)
        manifest["mappings"][0]["target_sha256"] = "0" * 64
        _write_json(manifest_path, manifest)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        failed_text = " ".join(
            _check_text(check)
            for check in report.checks
            if _status_value(check) == "FAIL"
        )
        self.assertRegex(failed_text, r"mapping|hash|checksum")
        code, stdout, stderr = self.invoke_main("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("FAIL", stdout + stderr)

    def test_unwritable_workspace_is_a_critical_failure(self) -> None:
        self.initialize()
        workspace = self.project_root / "workspace"
        workspace.chmod(0o555)
        try:
            report = self.doctor()
        finally:
            workspace.chmod(0o700)

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", "workspace", "writ")

    def test_unexpected_third_party_installation_marker_is_a_failure(self) -> None:
        self.initialize()
        rogue = self.project_root / ".agents/skills/unapproved-source"
        rogue.mkdir(parents=True)
        (rogue / "SKILL.md").write_text("# Unapproved source\n", encoding="utf-8")
        _write_json(
            rogue / ".investkit-source.json",
            {
                "managed_by": "investkit",
                "source": "third_party/raw/unapproved/SKILL.md",
                "approval": "unapproved",
            },
        )

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        failed_text = " ".join(
            _check_text(check)
            for check in report.checks
            if _status_value(check) == "FAIL"
        )
        self.assertRegex(failed_text, r"third.party|unapproved|forbidden")

    def test_secret_detection_fails_without_echoing_the_secret(self) -> None:
        self.initialize()
        config_path = self.project_root / ".investkit/config.json"
        config = _read_json(config_path)
        fake_secret = "sk-test-NOT-REAL-0123456789abcdefghijklmnop"
        config["api_key"] = fake_secret
        _write_json(config_path, config)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", "sensitive")
        self.assertNotIn(fake_secret, repr(report))
        code, stdout, stderr = self.invoke_main("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("FAIL", stdout + stderr)
        self.assertNotIn(fake_secret, stdout + stderr)

    def test_corrupt_task_record_is_a_critical_failure(self) -> None:
        self.initialize()
        corrupt_task = self.project_root / "workspace/research/corrupt-task/task.json"
        corrupt_task.parent.mkdir(parents=True)
        corrupt_task.write_text('{"status": "running",', encoding="utf-8")

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", "corrupt-task")

    def test_noncompleted_tasks_require_valid_plan_and_run_log_state(self) -> None:
        self.initialize()
        research_root = self.project_root / "workspace/research"
        for status in ("running", "failed"):
            task_id = f"corrupt-{status}-task"
            task_root = research_root / task_id
            task_root.mkdir()
            _write_json(
                task_root / "task.json",
                {
                    "id": task_id,
                    "outcome": (
                        {"error": "controlled failure", "status": "failed"}
                        if status == "failed"
                        else None
                    ),
                    "skills": sorted(CORE_SKILLS),
                    "specs": sorted(REQUIRED_SPECS),
                    "status": status,
                    "workflow": {
                        "id": "company-deep-dive",
                        "version": "0.2.0",
                    },
                },
            )
            _write_json(
                task_root / "plan.json",
                {
                    "steps": [],
                    "version": "0.2.0",
                    "workflow": "company-deep-dive",
                },
            )
            _write_json(
                task_root / "run-log.json", {"events": [], "task_id": task_id}
            )

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", "corrupt-running-task")
        self.assert_report_has(report, "FAIL", "corrupt-failed-task")

    def test_symlinked_skill_and_task_paths_are_rejected_without_following(self) -> None:
        self.initialize()
        outside_skill = self.temp_root / "outside-skill"
        outside_skill.mkdir()
        (outside_skill / "SKILL.md").write_text("# Outside\n", encoding="utf-8")
        installed_skill = self.project_root / ".agents/skills/company-deep-research"
        shutil.rmtree(installed_skill)
        installed_skill.symlink_to(outside_skill, target_is_directory=True)

        outside_task = self.temp_root / "outside-task"
        outside_task.mkdir()
        (outside_task / "task.json").write_text(
            '{"id":"linked-task","status":"completed"}\n',
            encoding="utf-8",
        )
        linked_task = self.project_root / "workspace/research/linked-task"
        linked_task.symlink_to(outside_task, target_is_directory=True)

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", "symlink")
        self.assert_report_has(report, "FAIL", "linked-task", "symlink")

    def test_completed_task_with_missing_report_is_a_critical_failure(self) -> None:
        self.initialize()
        from investkit.research.workflow import run_demo_research

        result = run_demo_research(self.project_root, REPOSITORY_ROOT)
        (result.task_path / "report.md").unlink()

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", result.task_id, "report.md")

    def test_completed_task_with_schema_valid_report_mutation_fails_hash(self) -> None:
        self.initialize()
        from investkit.research.workflow import run_demo_research

        result = run_demo_research(self.project_root, REPOSITORY_ROOT)
        with (result.task_path / "report.md").open("a", encoding="utf-8") as stream:
            stream.write("\n<!-- benign post-completion mutation -->\n")

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", result.task_id, "hash", "report.md")
        self.assertNotIn("benign post-completion mutation", repr(report))

    def test_secret_in_owned_markdown_fails_without_echoing_value(self) -> None:
        self.initialize()
        from investkit.research.workflow import run_demo_research

        result = run_demo_research(self.project_root, REPOSITORY_ROOT)
        fake_secret = "sk-test-NOT-REAL-0123456789abcdefghijklmnop"
        with (result.task_path / "report.md").open("a", encoding="utf-8") as stream:
            stream.write(f"\napi_key: {fake_secret}\n")

        report = self.doctor()

        self.assertNotEqual(report.exit_code, 0)
        self.assert_report_has(report, "FAIL", "sensitive")
        self.assertNotIn(fake_secret, repr(report))
        code, stdout, stderr = self.invoke_main("doctor")
        self.assertNotEqual(code, 0)
        self.assertNotIn(fake_secret, stdout + stderr)


if __name__ == "__main__":
    unittest.main()
