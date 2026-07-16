"""Small immutable result models shared by Runtime commands."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DiagnosticStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class FileAction:
    action: str
    path: str
    message: str = ""


@dataclass(frozen=True)
class InitializationResult:
    exit_code: int
    actions: tuple[FileAction, ...]


@dataclass(frozen=True)
class DiagnosticCheck:
    name: str
    status: DiagnosticStatus
    message: str


@dataclass(frozen=True)
class DoctorReport:
    checks: tuple[DiagnosticCheck, ...]

    @property
    def exit_code(self) -> int:
        return int(any(check.status is DiagnosticStatus.FAIL for check in self.checks))
