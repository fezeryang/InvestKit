"""Allowlisted Skill discovery and deterministic trigger evaluation."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Mapping

from investkit.assets import default_source_root, resolve_source_root


INVESTMENT_CORE_SKILLS = (
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
)
RUNTIME_SKILLS = ("security-identification", *INVESTMENT_CORE_SKILLS)


_TRIGGER_TERMS: dict[str, tuple[str, ...]] = {
    "security-identification": (
        "identify security",
        "resolve ticker",
        "security identity",
        "which listed company",
        "isin",
    ),
    "company-deep-research": (
        "company deep research",
        "company deep dive",
        "company dossier",
        "management and capital allocation",
        "company overview",
    ),
    "business-model-analysis": (
        "business model",
        "revenue model",
        "unit economics",
        "order to cash",
        "value proposition",
    ),
    "financial-statement-analysis": (
        "financial statement",
        "three statement",
        "balance sheet",
        "cash flow statement",
        "income statement",
    ),
    "earnings-quality-analysis": (
        "earnings quality",
        "cash conversion",
        "accrual",
        "revenue recognition quality",
        "one-off earnings",
    ),
    "valuation-analysis": (
        "valuation analysis",
        "discounted cash flow",
        "dcf",
        "intrinsic value",
        "sensitivity analysis",
    ),
    "comps-analysis": (
        "comps analysis",
        "comparable companies",
        "peer multiples",
        "trading multiples",
        "relative valuation",
    ),
    "earnings-analysis": (
        "earnings analysis",
        "earnings review",
        "earnings preview",
        "earnings surprise",
        "guidance versus actual",
    ),
    "investment-thesis": (
        "investment thesis",
        "bull base bear thesis",
        "thesis pillars",
        "falsifiable thesis",
        "variant perception",
    ),
    "bear-case-analysis": (
        "bear case",
        "counter thesis",
        "red team the thesis",
        "thesis killer",
        "adverse causal",
    ),
    "catalyst-analysis": (
        "catalyst analysis",
        "catalyst calendar",
        "event catalyst",
        "regulatory decision",
        "monitorable event",
    ),
    "source-verification": (
        "source verification",
        "verify sources",
        "citation audit",
        "evidence quality",
        "fact check sources",
    ),
    "investment-report": (
        "investment report",
        "research report",
        "initiating coverage report",
        "ic memo",
        "assemble the report",
    ),
}


def discover_skill_files(source_root: Path, skill_name: str) -> tuple[Path, ...]:
    """Return regular, contained files for one explicitly allowlisted Skill."""

    _require_skill(skill_name)
    root = resolve_source_root(source_root)
    skill_root = root / "skills" / skill_name
    if skill_root.is_symlink() or not skill_root.is_dir():
        raise ValueError(f"approved Skill source is missing or unsafe: {skill_name}")
    resolved_skill_root = skill_root.resolve()
    if not resolved_skill_root.is_relative_to(root):
        raise ValueError("Skill source escapes the approved first-party root")

    files: list[Path] = []
    for path in sorted(skill_root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Skill source contains an unsafe symlink: {path.name}")
        if not path.is_file():
            continue
        resolved = path.resolve()
        if not resolved.is_relative_to(resolved_skill_root):
            raise ValueError("Skill file escapes its approved Skill root")
        files.append(path)
    if skill_root / "SKILL.md" not in files:
        raise ValueError(f"approved Skill is missing SKILL.md: {skill_name}")
    return tuple(files)


def evaluate_trigger(question: str, skill_name: str) -> bool:
    """Evaluate governed Eval metadata first, then use a conservative rule table."""

    _require_skill(skill_name)
    normalized = _normalize(question)
    if not normalized:
        return False

    eval_decision = _eval_file_decision(normalized, skill_name)
    if eval_decision is not None:
        return eval_decision
    return any(term in normalized for term in _TRIGGER_TERMS[skill_name])


def _eval_file_decision(question: str, skill_name: str) -> bool | None:
    try:
        source_root = default_source_root()
        path = source_root / "skills" / skill_name / "references" / "trigger-evals.json"
        if path.is_symlink() or not path.is_file():
            return None
        resolved = path.resolve()
        skill_root = (source_root / "skills" / skill_name).resolve()
        if not resolved.is_relative_to(skill_root):
            return None
        with path.open("r", encoding="utf-8") as stream:
            payload = json.load(stream)
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(payload, Mapping):
        return None
    cases = payload.get("cases")
    if not isinstance(cases, list):
        return None
    for case in cases:
        if not isinstance(case, Mapping) or _normalize(case.get("question")) != question:
            continue
        excluded = case.get("excluded_skills", [])
        expected = case.get("expected_skills", [])
        if isinstance(excluded, list) and skill_name in excluded:
            return False
        if isinstance(expected, list):
            return skill_name in expected
    return None


def _require_skill(skill_name: str) -> None:
    if skill_name not in RUNTIME_SKILLS:
        raise KeyError(f"unapproved first-party Skill: {skill_name}")


def _normalize(value: Any) -> str:
    text = str(value or "").casefold()
    return re.sub(r"\s+", " ", text).strip()
