"""Typed errors and safe user-facing messages for the InvestKit Runtime."""

from __future__ import annotations

from .security import SENSITIVE_VALUE_RE


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
    redacted = SENSITIVE_VALUE_RE.sub("[REDACTED]", message)
    printable = "".join(
        character if character.isprintable() else " " for character in redacted
    )
    return " ".join(printable.split())[:limit]
