"""Deterministic first-party investment research capabilities."""

from .analysis import run_capability
from .catalog import INVESTMENT_CORE_SKILLS, RUNTIME_SKILLS
from .contracts import build_capability_result, validate_capability_result

__all__ = [
    "INVESTMENT_CORE_SKILLS",
    "RUNTIME_SKILLS",
    "build_capability_result",
    "run_capability",
    "validate_capability_result",
]
