"""Wheel delivery regression for the self-contained offline CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import venv


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BUILD_INPUTS = (
    "agents",
    "fixtures",
    "packages",
    "schemas",
    "skills",
    "specs",
    "src",
    "workflows",
    "workspace-template",
    "README.md",
    "pyproject.toml",
)

RUNTIME_SKILLS = {
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


class WheelInstallContractTests(unittest.TestCase):
    def test_wheel_install_runs_the_fresh_project_flow_without_checkout_assets(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="investkit-wheel-test-") as temporary:
            temporary_root = Path(temporary)
            build_root = temporary_root / "build-input"
            build_root.mkdir()
            for relative_name in BUILD_INPUTS:
                source = REPOSITORY_ROOT / relative_name
                target = build_root / relative_name
                if source.is_dir():
                    shutil.copytree(
                        source,
                        target,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.egg-info"),
                    )
                else:
                    shutil.copy2(source, target)

            wheel_root = temporary_root / "wheel"
            wheel_root.mkdir()
            build = self._run(
                (
                    sys.executable,
                    "-m",
                    "pip",
                    "wheel",
                    "--no-build-isolation",
                    "--no-deps",
                    "--wheel-dir",
                    str(wheel_root),
                    str(build_root),
                ),
                cwd=temporary_root,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            wheels = list(wheel_root.glob("investkit-*.whl"))
            self.assertEqual(len(wheels), 1)
            self.assertTrue(wheels[0].name.startswith("investkit-0.3.0-"))

            environment_root = temporary_root / "environment"
            venv.EnvBuilder(with_pip=True).create(environment_root)
            bin_directory = "Scripts" if os.name == "nt" else "bin"
            python = environment_root / bin_directory / (
                "python.exe" if os.name == "nt" else "python"
            )
            investkit = environment_root / bin_directory / (
                "investkit.exe" if os.name == "nt" else "investkit"
            )
            install = self._run(
                (
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--no-index",
                    "--no-deps",
                    str(wheels[0]),
                ),
                cwd=temporary_root,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            self.assertTrue(investkit.is_file())

            project_root = temporary_root / "fresh-project"
            project_root.mkdir()
            initialized = self._run((str(investkit), "init"), cwd=project_root)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            config = json.loads(
                (project_root / ".investkit/config.json").read_text(encoding="utf-8")
            )
            self.assertEqual(config["investkit_version"], "0.3.0")
            delivered_source = Path(config["source_root"])
            self.assertTrue(delivered_source.is_dir())
            self.assertEqual(delivered_source.name, "investkit")
            self.assertEqual(delivered_source.parent.name, "share")
            self.assertFalse(str(delivered_source).startswith(str(build_root)))
            for relative_asset in (
                "schemas/research-bundle-v1.schema.json",
                "schemas/research-bundle-v1.template.json",
            ):
                with self.subTest(asset=relative_asset):
                    delivered_asset = delivered_source / relative_asset
                    self.assertTrue(delivered_asset.is_file(), relative_asset)
                    self.assertEqual(
                        delivered_asset.read_bytes(),
                        (build_root / relative_asset).read_bytes(),
                    )
            installed = {
                path.name
                for path in (project_root / ".agents/skills").iterdir()
                if path.is_dir()
            }
            self.assertEqual(installed, RUNTIME_SKILLS)

            imported_input = project_root / "inputs/microsoft-fy2025.json"
            imported_input.parent.mkdir()
            shutil.copy2(
                build_root / "fixtures/acceptance/microsoft-fy2025.json",
                imported_input,
            )
            # From this point the installed wheel plus the analyst-supplied bundle
            # are the only Runtime inputs.  No checkout asset may satisfy discovery.
            shutil.rmtree(build_root)

            diagnosed = self._run((str(investkit), "doctor"), cwd=project_root)
            self.assertEqual(diagnosed.returncode, 0, diagnosed.stdout + diagnosed.stderr)
            demo = self._run(
                (str(investkit), "demo", "research"),
                cwd=project_root,
            )
            self.assertEqual(demo.returncode, 0, demo.stdout + demo.stderr)
            match = re.search(r"\bdemo-[A-Za-z0-9_-]+", demo.stdout)
            self.assertIsNotNone(match, demo.stdout)
            assert match is not None
            task_id = match.group(0)
            capability_root = project_root / "workspace/research" / task_id / "capabilities"
            self.assertEqual(
                {path.stem for path in capability_root.glob("*.json")},
                RUNTIME_SKILLS,
            )
            resumed = self._run(
                (str(investkit), "demo", "research", "--resume", task_id),
                cwd=project_root,
            )
            self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)

            imported = self._run(
                (
                    str(investkit),
                    "research",
                    "--input",
                    "inputs/microsoft-fy2025.json",
                    "--question",
                    "What does the supplied FY2025 filing support about financial quality and risk?",
                ),
                cwd=project_root,
            )
            self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
            imported_match = re.search(r"\bresearch-[A-Za-z0-9_-]+", imported.stdout)
            self.assertIsNotNone(imported_match, imported.stdout)
            assert imported_match is not None
            imported_task_id = imported_match.group(0)
            imported_task_root = (
                project_root / "workspace/research" / imported_task_id
            )
            imported_report = (imported_task_root / "report.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Microsoft Corporation", imported_report)
            self.assertIn("user-supplied", imported_report.lower())
            self.assertIn("not independently", imported_report.lower())
            self.assertNotIn("fictional", imported_report.lower())

            before_imported_resume = {
                path.relative_to(imported_task_root).as_posix(): path.read_bytes()
                for path in imported_task_root.rglob("*")
                if path.is_file()
            }

            resumed_imported = self._run(
                (str(investkit), "research", "--resume", imported_task_id),
                cwd=project_root,
            )
            self.assertEqual(
                resumed_imported.returncode,
                0,
                resumed_imported.stdout + resumed_imported.stderr,
            )
            after_imported_resume = {
                path.relative_to(imported_task_root).as_posix(): path.read_bytes()
                for path in imported_task_root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(set(after_imported_resume), set(before_imported_resume))
            for relative, content in before_imported_resume.items():
                if relative != "run-log.json":
                    self.assertEqual(after_imported_resume[relative], content, relative)
            self.assertNotEqual(
                after_imported_resume["run-log.json"],
                before_imported_resume["run-log.json"],
            )
            diagnosed_after_resume = self._run(
                (str(investkit), "doctor"), cwd=project_root
            )
            self.assertEqual(
                diagnosed_after_resume.returncode,
                0,
                diagnosed_after_resume.stdout + diagnosed_after_resume.stderr,
            )
            dependency_check = self._run(
                (str(python), "-m", "pip", "check"),
                cwd=project_root,
            )
            self.assertEqual(
                dependency_check.returncode,
                0,
                dependency_check.stdout + dependency_check.stderr,
            )

    @staticmethod
    def _run(arguments: tuple[str, ...], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment.update(
            {
                "PIP_DISABLE_PIP_VERSION_CHECK": "1",
                "PIP_NO_INDEX": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
            }
        )
        return subprocess.run(
            arguments,
            cwd=cwd,
            env=environment,
            capture_output=True,
            check=False,
            text=True,
            timeout=60,
        )


if __name__ == "__main__":
    unittest.main()
