"""Safe, all-or-nothing v0.2 to v0.3 initialization migration contracts."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from unittest import mock
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected JSON object in {path}")
    return value


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _file_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }


def _stable_json_bytes(value: dict[str, object]) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


class V03MigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="investkit-v03-migration-"
        )
        self.temp_root = Path(self._temporary_directory.name)
        self.project_root = self.temp_root / "project"
        self.project_root.mkdir()
        self.source_root = self.temp_root / "source"
        self.source_root.mkdir()
        from investkit.assets import SOURCE_DIRECTORIES

        for name in SOURCE_DIRECTORIES:
            source = REPOSITORY_ROOT / name
            if source.is_dir():
                shutil.copytree(source, self.source_root / name)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def initialize_as(self, version: str):
        from investkit.initializer import initialize_project

        with mock.patch("investkit.initializer.__version__", version):
            return initialize_project(self.project_root, source_root=self.source_root)

    def create_v02_project(self) -> str:
        result = self.initialize_as("0.2.0")
        self.assertEqual(result.exit_code, 0, result)
        initialized_at = str(
            _read_json(self.project_root / ".investkit/config.json")["initialized_at"]
        )
        return initialized_at

    def test_machine_json_writer_rejects_non_finite_numbers(self) -> None:
        from investkit.filesystem import stable_json_bytes

        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    stable_json_bytes({"value": value})

    def test_pristine_v02_project_upgrades_owned_files_and_preserves_workspace(self) -> None:
        initialized_at = self.create_v02_project()
        # A genuine v0.2 delivery predates the governed schema directory.  Keep
        # the representative ledger/config metadata aligned with that baseline.
        for machine_path in (
            self.project_root / ".investkit/config.json",
            self.project_root / ".investkit/install-manifest.json",
        ):
            machine_state = _read_json(machine_path)
            source_directories = machine_state["source_directories"]
            assert isinstance(source_directories, dict)
            source_directories.pop("schemas", None)
            machine_state["source_root"] = "/retired/investkit-v02-assets"
            _write_json(machine_path, machine_state)
        legacy_task = self.project_root / "workspace/research/legacy-task/evidence.json"
        legacy_task.parent.mkdir()
        legacy_task.write_text('{"preserve":true}\n', encoding="utf-8")
        workspace_readme = self.project_root / "workspace/README.md"
        workspace_readme.write_text("# User workspace\n", encoding="utf-8")
        changed_skill = self.source_root / "skills/company-deep-research/SKILL.md"
        changed_skill.write_text(
            changed_skill.read_text(encoding="utf-8")
            + "\n<!-- v0.3 migration acceptance marker -->\n",
            encoding="utf-8",
        )
        new_v03_source = (
            self.source_root
            / "skills/company-deep-research/references/v03-migration-note.md"
        )
        new_v03_source.write_text("# New governed v0.3 file\n", encoding="utf-8")

        result = self.initialize_as("0.3.0")

        self.assertEqual(result.exit_code, 0, result)
        config = _read_json(self.project_root / ".investkit/config.json")
        manifest = _read_json(
            self.project_root / ".investkit/install-manifest.json"
        )
        self.assertEqual(config["investkit_version"], "0.3.0")
        self.assertEqual(manifest["investkit_version"], "0.3.0")
        self.assertEqual(config["initialized_at"], initialized_at)
        self.assertEqual(manifest["initialized_at"], initialized_at)
        self.assertEqual(
            (
                self.project_root
                / ".agents/skills/company-deep-research/SKILL.md"
            ).read_bytes(),
            changed_skill.read_bytes(),
        )
        self.assertEqual(
            (
                self.project_root
                / ".agents/skills/company-deep-research/references/v03-migration-note.md"
            ).read_bytes(),
            new_v03_source.read_bytes(),
        )
        self.assertEqual(legacy_task.read_text(encoding="utf-8"), '{"preserve":true}\n')
        self.assertEqual(workspace_readme.read_text(encoding="utf-8"), "# User workspace\n")
        self.assertTrue(any(action.action == "UPDATE" for action in result.actions))
        for owned_path in (
            self.project_root / ".investkit/config.json",
            self.project_root / ".investkit/install-manifest.json",
            self.project_root
            / ".agents/skills/company-deep-research/SKILL.md",
            self.project_root
            / ".agents/skills/company-deep-research/references/v03-migration-note.md",
        ):
            self.assertEqual(owned_path.stat().st_mode & 0o777, 0o600)

        before_repeat = _file_bytes(self.project_root)
        repeated = self.initialize_as("0.3.0")
        self.assertEqual(repeated.exit_code, 0, repeated)
        self.assertEqual(_file_bytes(self.project_root), before_repeat)

    def test_changed_owned_target_aborts_entire_upgrade_before_any_write(self) -> None:
        self.create_v02_project()
        first_source = self.source_root / "skills/company-deep-research/SKILL.md"
        first_source.write_text(
            first_source.read_text(encoding="utf-8") + "\n<!-- desired-v03-a -->\n",
            encoding="utf-8",
        )
        conflicting_source = self.source_root / "skills/valuation-analysis/SKILL.md"
        conflicting_source.write_text(
            conflicting_source.read_text(encoding="utf-8") + "\n<!-- desired-v03-b -->\n",
            encoding="utf-8",
        )
        conflict_target = (
            self.project_root / ".agents/skills/valuation-analysis/SKILL.md"
        )
        conflict_target.write_text("# user-owned conflict\n", encoding="utf-8")
        second_conflict = (
            self.project_root / ".agents/skills/comps-analysis/SKILL.md"
        )
        second_conflict.write_text("# second user-owned conflict\n", encoding="utf-8")
        before = _file_bytes(self.project_root)

        result = self.initialize_as("0.3.0")

        self.assertNotEqual(result.exit_code, 0)
        self.assertEqual(_file_bytes(self.project_root), before)
        self.assertTrue(
            any(
                action.action == "WARN"
                and action.path == ".agents/skills/valuation-analysis/SKILL.md"
                for action in result.actions
            )
        )
        self.assertTrue(
            any(
                action.action == "WARN"
                and action.path == ".agents/skills/comps-analysis/SKILL.md"
                for action in result.actions
            )
        )

    def test_forged_legacy_mapping_digest_cannot_reassign_owned_skill(self) -> None:
        self.create_v02_project()
        target_relative = ".agents/skills/company-deep-research/SKILL.md"
        target = self.project_root / target_relative
        target.write_bytes(
            target.read_bytes() + b"\n<!-- attacker-controlled replacement -->\n"
        )
        forged_digest = hashlib.sha256(target.read_bytes()).hexdigest()
        manifest_path = self.project_root / ".investkit/install-manifest.json"
        manifest = _read_json(manifest_path)
        mappings = manifest["mappings"]
        assert isinstance(mappings, list)
        matching = [
            mapping
            for mapping in mappings
            if isinstance(mapping, dict) and mapping.get("target") == target_relative
        ]
        self.assertEqual(len(matching), 1)
        matching[0]["source_sha256"] = forged_digest
        matching[0]["target_sha256"] = forged_digest
        _write_json(manifest_path, manifest)
        before = _file_bytes(self.project_root)

        result = self.initialize_as("0.3.0")

        self.assertNotEqual(result.exit_code, 0)
        self.assertEqual(_file_bytes(self.project_root), before)
        self.assertTrue(
            any(
                action.action == "WARN"
                and action.path == ".investkit/install-manifest.json"
                for action in result.actions
            )
        )

    def test_changed_config_adapter_or_manifest_is_preserved_without_partial_upgrade(self) -> None:
        for relative_path in (
            ".investkit/config.json",
            ".agents/investkit.json",
            ".investkit/install-manifest.json",
        ):
            with self.subTest(relative_path=relative_path):
                project = self.temp_root / ("project-" + Path(relative_path).name)
                project.mkdir()
                original_project = self.project_root
                self.project_root = project
                try:
                    self.create_v02_project()
                    path = project / relative_path
                    path.write_text(
                        path.read_text(encoding="utf-8") + "\n",
                        encoding="utf-8",
                    )
                    before = _file_bytes(project)
                    result = self.initialize_as("0.3.0")
                    self.assertNotEqual(result.exit_code, 0)
                    self.assertEqual(_file_bytes(project), before)
                    self.assertTrue(
                        any(
                            action.action == "WARN" and action.path == relative_path
                            for action in result.actions
                        )
                    )
                finally:
                    self.project_root = original_project

    def test_unsupported_or_mixed_version_state_is_non_destructive(self) -> None:
        self.create_v02_project()
        manifest_path = self.project_root / ".investkit/install-manifest.json"
        manifest = _read_json(manifest_path)
        manifest["investkit_version"] = "0.1.0"
        _write_json(manifest_path, manifest)
        before = _file_bytes(self.project_root)

        result = self.initialize_as("0.3.0")

        self.assertNotEqual(result.exit_code, 0)
        self.assertEqual(_file_bytes(self.project_root), before)
        self.assertRegex(
            " ".join(action.message for action in result.actions).lower(),
            r"version|incompatible|migration",
        )

    def test_forward_and_incomplete_version_states_are_non_destructive(self) -> None:
        for case in ("forward", "incomplete"):
            with self.subTest(case=case):
                project = self.temp_root / f"version-{case}"
                project.mkdir()
                original_project = self.project_root
                self.project_root = project
                try:
                    self.create_v02_project()
                    config_path = project / ".investkit/config.json"
                    manifest_path = project / ".investkit/install-manifest.json"
                    if case == "forward":
                        config = _read_json(config_path)
                        manifest = _read_json(manifest_path)
                        config["investkit_version"] = "9.0.0"
                        manifest["investkit_version"] = "9.0.0"
                        _write_json(config_path, config)
                        _write_json(manifest_path, manifest)
                    else:
                        manifest_path.unlink()
                    before = _file_bytes(project)

                    result = self.initialize_as("0.3.0")

                    self.assertNotEqual(result.exit_code, 0)
                    self.assertEqual(_file_bytes(project), before)
                    self.assertRegex(
                        " ".join(
                            action.message for action in result.actions
                        ).lower(),
                        r"version|incomplete|migration",
                    )
                finally:
                    self.project_root = original_project

    def test_interrupted_upgrade_accepts_only_exact_old_or_desired_bytes(self) -> None:
        initialized_at = self.create_v02_project()
        manifest_path = self.project_root / ".investkit/install-manifest.json"
        old_manifest = manifest_path.read_bytes()
        changed_source = self.source_root / "skills/company-deep-research/SKILL.md"
        changed_source.write_text(
            changed_source.read_text(encoding="utf-8")
            + "\n<!-- exact desired interrupted state -->\n",
            encoding="utf-8",
        )
        changed_target = (
            self.project_root / ".agents/skills/company-deep-research/SKILL.md"
        )
        changed_target.write_bytes(changed_source.read_bytes())
        config_path = self.project_root / ".investkit/config.json"
        desired_config = _read_json(config_path)
        desired_config["investkit_version"] = "0.3.0"
        config_path.write_bytes(_stable_json_bytes(desired_config))

        result = self.initialize_as("0.3.0")

        self.assertEqual(result.exit_code, 0, result)
        self.assertNotEqual(manifest_path.read_bytes(), old_manifest)
        self.assertEqual(
            _read_json(manifest_path)["investkit_version"], "0.3.0"
        )
        self.assertEqual(
            _read_json(config_path)["initialized_at"], initialized_at
        )
        self.assertEqual(changed_target.read_bytes(), changed_source.read_bytes())

    def test_manifest_is_the_final_commit_point_and_partial_retry_recovers(self) -> None:
        self.create_v02_project()
        manifest_path = self.project_root / ".investkit/install-manifest.json"
        old_manifest = manifest_path.read_bytes()
        changed_source = self.source_root / "skills/company-deep-research/SKILL.md"
        changed_source.write_text(
            changed_source.read_text(encoding="utf-8")
            + "\n<!-- atomic ordering marker -->\n",
            encoding="utf-8",
        )
        from investkit import initializer

        real_commit = initializer.commit_atomic_replacement
        attempted: list[str] = []

        def fail_at_config(replacement):
            attempted.append(replacement.relative_path)
            if replacement.relative_path == ".investkit/config.json":
                raise OSError("simulated atomic commit interruption")
            real_commit(replacement)

        with mock.patch.object(
            initializer,
            "commit_atomic_replacement",
            side_effect=fail_at_config,
        ):
            interrupted = self.initialize_as("0.3.0")

        self.assertNotEqual(interrupted.exit_code, 0)
        self.assertEqual(manifest_path.read_bytes(), old_manifest)
        self.assertNotIn(".investkit/install-manifest.json", attempted)
        self.assertFalse(
            [
                path
                for path in self.project_root.rglob("*")
                if ".investkit-" in path.name
            ]
        )

        committed: list[str] = []

        def record_commit(replacement):
            committed.append(replacement.relative_path)
            real_commit(replacement)

        with mock.patch.object(
            initializer,
            "commit_atomic_replacement",
            side_effect=record_commit,
        ):
            resumed = self.initialize_as("0.3.0")

        self.assertEqual(resumed.exit_code, 0, resumed)
        self.assertEqual(committed[-1], ".investkit/install-manifest.json")

    def test_missing_symlink_or_special_owned_target_is_rejected_before_writes(self) -> None:
        cases = ("missing", "symlink", "fifo")
        for case in cases:
            with self.subTest(case=case):
                project = self.temp_root / f"unsafe-target-{case}"
                project.mkdir()
                original_project = self.project_root
                self.project_root = project
                outside = self.temp_root / f"outside-{case}.txt"
                outside.write_text("outside sentinel\n", encoding="utf-8")
                try:
                    self.create_v02_project()
                    target = (
                        project
                        / ".agents/skills/company-deep-research/SKILL.md"
                    )
                    target.unlink()
                    if case == "symlink":
                        target.symlink_to(outside)
                    elif case == "fifo":
                        os.mkfifo(target)
                    before = _file_bytes(project)
                    result = self.initialize_as("0.3.0")
                    self.assertNotEqual(result.exit_code, 0)
                    self.assertEqual(_file_bytes(project), before)
                    self.assertEqual(
                        outside.read_text(encoding="utf-8"), "outside sentinel\n"
                    )
                    self.assertTrue(
                        any(
                            action.path
                            == ".agents/skills/company-deep-research/SKILL.md"
                            for action in result.actions
                        )
                    )
                finally:
                    self.project_root = original_project

    def test_malformed_duplicate_or_secret_machine_state_fails_safely(self) -> None:
        secret_value = "sk" + "-this-must-never-appear-1234567890"
        corruptions = {
            "malformed": b'{"investkit_version":"0.2.0"',
            "duplicate": (
                b'{"investkit_version":"0.2.0",'
                b'"investkit_version":"0.2.0"}\n'
            ),
            "secret": _stable_json_bytes(
                {
                    "investkit_version": "0.2.0",
                    "api_key": secret_value,
                }
            ),
        }
        for case, content in corruptions.items():
            with self.subTest(case=case):
                project = self.temp_root / f"bad-state-{case}"
                project.mkdir()
                original_project = self.project_root
                self.project_root = project
                try:
                    self.create_v02_project()
                    config_path = project / ".investkit/config.json"
                    config_path.write_bytes(content)
                    before = _file_bytes(project)
                    result = self.initialize_as("0.3.0")
                    self.assertNotEqual(result.exit_code, 0)
                    self.assertEqual(_file_bytes(project), before)
                    diagnostic = repr(result)
                    self.assertNotIn(secret_value, diagnostic)
                    self.assertTrue(
                        any(
                            action.path == ".investkit/config.json"
                            for action in result.actions
                        )
                    )
                finally:
                    self.project_root = original_project

    def test_manifest_mapping_attacks_are_rejected_without_path_following(self) -> None:
        def duplicate_mapping(manifest: dict[str, object]) -> None:
            mappings = manifest["mappings"]
            assert isinstance(mappings, list)
            mappings.append(dict(mappings[0]))

        def escaping_mapping(manifest: dict[str, object]) -> None:
            mappings = manifest["mappings"]
            assert isinstance(mappings, list)
            mapping = mappings[0]
            assert isinstance(mapping, dict)
            mapping["target"] = "../../outside-sentinel.txt"

        def invalid_digest(manifest: dict[str, object]) -> None:
            mappings = manifest["mappings"]
            assert isinstance(mappings, list)
            mapping = mappings[0]
            assert isinstance(mapping, dict)
            mapping["source_sha256"] = "not-a-sha256"

        def unknown_mapping(manifest: dict[str, object]) -> None:
            mappings = manifest["mappings"]
            assert isinstance(mappings, list)
            extra = dict(mappings[0])
            extra["source"] = "skills/unapproved/SKILL.md"
            extra["target"] = ".agents/skills/unapproved/SKILL.md"
            mappings.append(extra)

        def reordered_mappings(manifest: dict[str, object]) -> None:
            mappings = manifest["mappings"]
            assert isinstance(mappings, list)
            mappings.reverse()

        mutations = {
            "duplicate": duplicate_mapping,
            "escape": escaping_mapping,
            "digest": invalid_digest,
            "unknown": unknown_mapping,
            "reordered": reordered_mappings,
        }
        for case, mutate in mutations.items():
            with self.subTest(case=case):
                project = self.temp_root / f"bad-mapping-{case}"
                project.mkdir()
                original_project = self.project_root
                self.project_root = project
                outside = self.temp_root / "outside-sentinel.txt"
                outside.write_text("do not touch\n", encoding="utf-8")
                try:
                    self.create_v02_project()
                    manifest_path = project / ".investkit/install-manifest.json"
                    manifest = _read_json(manifest_path)
                    mutate(manifest)
                    _write_json(manifest_path, manifest)
                    before = _file_bytes(project)
                    result = self.initialize_as("0.3.0")
                    self.assertNotEqual(result.exit_code, 0)
                    self.assertEqual(_file_bytes(project), before)
                    self.assertEqual(outside.read_text(encoding="utf-8"), "do not touch\n")
                    self.assertNotIn("../", repr(result))
                    self.assertTrue(
                        any(
                            action.path == ".investkit/install-manifest.json"
                            for action in result.actions
                        )
                    )
                finally:
                    self.project_root = original_project

    def test_symlinked_machine_state_is_rejected_without_following_it(self) -> None:
        self.create_v02_project()
        config_path = self.project_root / ".investkit/config.json"
        outside = self.temp_root / "outside-config.json"
        outside_before = config_path.read_bytes()
        outside.write_bytes(outside_before)
        config_path.unlink()
        config_path.symlink_to(outside)
        manifest_before = (
            self.project_root / ".investkit/install-manifest.json"
        ).read_bytes()

        result = self.initialize_as("0.3.0")

        self.assertNotEqual(result.exit_code, 0)
        self.assertTrue(config_path.is_symlink())
        self.assertEqual(outside.read_bytes(), outside_before)
        self.assertEqual(
            (self.project_root / ".investkit/install-manifest.json").read_bytes(),
            manifest_before,
        )
        self.assertTrue(
            any(
                action.path == ".investkit/config.json"
                for action in result.actions
            )
        )


if __name__ == "__main__":
    unittest.main()
