"""Shared credential-pattern detection for every InvestKit trust boundary."""

from __future__ import annotations

import re


SENSITIVE_KEY_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|"
    r"private[_-]?key|secret|credential|authorization|"
    r"(?:^|[_-])token(?:$|[_-])|aws[_-]?(?:access[_-]?)?key(?:[_-]?id)?)"
)

# Explicit credential families plus contextual assignments.  Context-free generic
# entropy matching is intentionally avoided because task artifacts legitimately
# contain SHA-256 digests; a suspected value must have a recognizable credential
# prefix or a credential-like assignment label.
SENSITIVE_VALUE_RE = re.compile(
    r"(?i)(?:\bsk-[A-Za-z0-9_-]{16,}|"
    r"\bbearer\s+[A-Za-z0-9._~+/-]{12,}|"
    r"\bbasic\s+[A-Za-z0-9+/=]{8,}|"
    r"\bgh[pousr]_[A-Za-z0-9]{20,}|"
    r"\bgithub_pat_[A-Za-z0-9_]{20,}|"
    r"\b(?:xox[baprs]-|xapp-)[A-Za-z0-9-]{10,}|"
    r"\bglpat-[A-Za-z0-9_-]{16,}|"
    r"\b(?:sk|rk)_live_[A-Za-z0-9]{12,}|"
    r"\bnpm_[A-Za-z0-9]{16,}|"
    r"\bAIza[A-Za-z0-9_-]{20,}|"
    r"\bya29\.[A-Za-z0-9._-]{20,}|"
    r"\bSG\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|"
    r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|"
    r"\beyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\b|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|"
    r"private[_-]?key|secret|credential|authorization|token)"
    r"\s*[:=]\s*[^\s,;]{4,})"
)


def contains_sensitive_key(value: object) -> bool:
    """Return whether a field name denotes credential material."""

    return bool(SENSITIVE_KEY_RE.search(str(value)))


def contains_sensitive_value(value: object) -> bool:
    """Return whether text contains a recognized or contextual credential value."""

    return isinstance(value, str) and bool(SENSITIVE_VALUE_RE.search(value))
