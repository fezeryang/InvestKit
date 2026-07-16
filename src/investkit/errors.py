"""Typed errors and safe user-facing messages for the InvestKit Runtime."""

from __future__ import annotations

import re


_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|secret|password|"
    r"credential|private[_-]?key)\s*[:=]\s*[^\s,;]+"
)
_BARE_SECRET_RE = re.compile(
    r"(?i)(?:\bsk-[A-Za-z0-9_-]{16,}|\bbearer\s+[A-Za-z0-9._-]{12,}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)


class InvestKitError(RuntimeError):
    """Base class for expected, user-actionable Runtime failures."""


class FilesystemBoundaryError(InvestKitError):
    """Raised when a path leaves an approved root."""


class AssetValidationError(InvestKitError):
    """Raised when a required first-party asset is missing or invalid."""


class InitializationError(InvestKitError):
    """Raised when a project cannot be initialized without data loss."""


def safe_error_message(error: BaseException, *, limit: int = 500) -> str:
    """Return a bounded printable message with common credential values removed."""

    message = str(error).strip() or error.__class__.__name__
    redacted = _SECRET_ASSIGNMENT_RE.sub(r"\1=[REDACTED]", message)
    redacted = _BARE_SECRET_RE.sub("[REDACTED]", redacted)
    printable = "".join(
        character if character.isprintable() else " " for character in redacted
    )
    return " ".join(printable.split())[:limit]
