"""Strict optional loading of project-local provider credential references."""

from __future__ import annotations

import os
from pathlib import Path
import stat

from .errors import InvestKitError


ALLOWED_PROVIDER_CREDENTIALS = frozenset(
    {
        "MX_APIKEY",
        "GF_SKILLS_APIKEY",
        "CICCWM_API_KEY",
        "GUOSEN_APIKEY",
    }
)
MAX_ENV_BYTES = 64 * 1024
MAX_VALUE_CHARS = 16 * 1024
PLACEHOLDER = "REQUIRED_API_KEY_UNKNOWN"


class ProviderEnvironmentError(InvestKitError):
    """Raised when a project .env file violates the credential boundary."""


def load_provider_environment(project_root: str | Path) -> tuple[str, ...]:
    """Load allowlisted values from a mode-600 regular `.env` without shell execution."""

    project = Path(project_root).resolve(strict=True)
    path = project / ".env"
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return ()
    except OSError as error:
        raise ProviderEnvironmentError("provider environment file is inaccessible") from error
    if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) & 0o077:
        raise ProviderEnvironmentError("provider environment file must be a private regular file (mode 600)")
    if metadata.st_size > MAX_ENV_BYTES:
        raise ProviderEnvironmentError("provider environment file exceeds the size limit")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if (
                not stat.S_ISREG(opened.st_mode)
                or stat.S_IMODE(opened.st_mode) & 0o077
                or opened.st_size > MAX_ENV_BYTES
            ):
                raise ProviderEnvironmentError("provider environment file changed or is unsafe")
            chunks: list[bytes] = []
            size = 0
            while True:
                chunk = os.read(
                    descriptor, min(8192, MAX_ENV_BYTES + 1 - size)
                )
                if not chunk:
                    break
                chunks.append(chunk)
                size += len(chunk)
                if size > MAX_ENV_BYTES:
                    raise ProviderEnvironmentError(
                        "provider environment file exceeds the size limit"
                    )
            payload = b"".join(chunks)
        finally:
            os.close(descriptor)
    except ProviderEnvironmentError:
        raise
    except OSError as error:
        raise ProviderEnvironmentError("provider environment file cannot be opened safely") from error
    if len(payload) > MAX_ENV_BYTES:
        raise ProviderEnvironmentError("provider environment file exceeds the size limit")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise ProviderEnvironmentError("provider environment file must be UTF-8") from error

    parsed: dict[str, str] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ProviderEnvironmentError(
                f"provider environment syntax is invalid at line {line_number}"
            )
        name, raw_value = line.split("=", 1)
        if name not in ALLOWED_PROVIDER_CREDENTIALS or name in parsed:
            raise ProviderEnvironmentError(
                f"provider environment variable is unsupported or duplicated at line {line_number}"
            )
        value = _value(raw_value, line_number)
        parsed[name] = value

    loaded: list[str] = []
    for name, value in parsed.items():
        if value == PLACEHOLDER or name in os.environ:
            continue
        os.environ[name] = value
        loaded.append(name)
    return tuple(sorted(loaded))


def _value(raw: str, line_number: int) -> str:
    if raw != raw.strip():
        raise ProviderEnvironmentError(
            f"provider environment value has edge whitespace at line {line_number}"
        )
    value = raw
    if len(value) >= 2 and value[0] in {"'", '"'}:
        if value[-1] != value[0]:
            raise ProviderEnvironmentError(
                f"provider environment quotes are invalid at line {line_number}"
            )
        value = value[1:-1]
    if (
        not value
        or len(value) > MAX_VALUE_CHARS
        or not value.isascii()
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise ProviderEnvironmentError(
            f"provider environment value is invalid at line {line_number}"
        )
    return value
