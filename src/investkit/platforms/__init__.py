"""Supported InvestKit host-platform adapters."""

from .base import PlatformAdapter
from .codex import CodexAdapter

__all__ = ["CodexAdapter", "PlatformAdapter"]
