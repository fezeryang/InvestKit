"""Host-platform adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Mapping


class PlatformAdapter(ABC):
    """Describe how governed first-party assets map into one host platform."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable platform identifier."""

    @property
    @abstractmethod
    def installation_target(self) -> str:
        """Project-relative Skill installation target."""

    @property
    @abstractmethod
    def configuration_path(self) -> str:
        """Project-relative adapter configuration path."""

    @abstractmethod
    def configuration(self, installed_skills: list[str]) -> Mapping[str, Any]:
        """Return InvestKit-owned adapter configuration."""

    @abstractmethod
    def detect_project(self, project_root: str | Path) -> bool:
        """Return whether the project can safely host this adapter."""

    @abstractmethod
    def describe(self, project_root: str | Path) -> Mapping[str, Any]:
        """Describe the adapter and its non-mutating project detection state."""
