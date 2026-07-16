"""Codex project adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .base import PlatformAdapter


class CodexAdapter(PlatformAdapter):
    @property
    def name(self) -> str:
        return "codex"

    @property
    def installation_target(self) -> str:
        return ".agents/skills"

    @property
    def configuration_path(self) -> str:
        return ".agents/investkit.json"

    def configuration(self, installed_skills: list[str]) -> Mapping[str, Any]:
        return {
            "host_platform": self.name,
            "installation_target": self.installation_target,
            "installed_skills": list(installed_skills),
            "managed_by": "investkit",
            "schema_version": "1.0",
        }

    def detect_project(self, project_root: str | Path) -> bool:
        return bool(self.describe(project_root)["detected"])

    def describe(self, project_root: str | Path) -> Mapping[str, Any]:
        project = Path(project_root).expanduser().resolve()
        agents_state = _directory_state(project / ".agents")
        target_state = _directory_state(project / self.installation_target)
        detected = (
            project.is_dir()
            and agents_state in {"missing", "directory"}
            and target_state in {"missing", "directory"}
        )
        return {
            "agents_path_state": agents_state,
            "configuration_path": self.configuration_path,
            "detected": detected,
            "host_platform": self.name,
            "installation_target": self.installation_target,
            "project_exists": project.is_dir(),
            "project_root": str(project),
            "target_path_state": target_state,
        }


def _directory_state(path: Path) -> str:
    if path.is_symlink():
        return "unsafe-symlink"
    if not path.exists():
        return "missing"
    return "directory" if path.is_dir() else "conflict"
