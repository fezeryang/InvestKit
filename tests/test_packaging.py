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
            delivered_source = Path(config["source_root"])
            self.assertTrue(delivered_source.is_dir())
            self.assertEqual(delivered_source.name, "investkit")
            self.assertEqual(delivered_source.parent.name, "share")
            self.assertFalse(str(delivered_source).startswith(str(build_root)))
            installed = {
                path.name
                for path in (project_root / ".agents/skills").iterdir()
                if path.is_dir()
            }
            self.assertEqual(installed, RUNTIME_SKILLS)

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
            diagnosed_after_resume = self._run(
                (str(investkit), "doctor"), cwd=project_root
            )
            self.assertEqual(
                diagnosed_after_resume.returncode,
                0,
                diagnosed_after_resume.stdout + diagnosed_after_resume.stderr,
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
