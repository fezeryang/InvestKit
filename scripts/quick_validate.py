#!/usr/bin/env python3
"""Read-only structural validation for the complete first-party Skill set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping


EXPECTED_SKILLS = (
    "security-identification",
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
REQUIRED_SECTIONS = (
    "Objective",
    "Responsibility Boundary",
    "Positive Triggers",
    "Near-Miss Negative Triggers",
    "Inputs",
    "Missing-Data Behavior",
    "Used Specs",
    "Analytical Procedure",
    "Output Contract",
    "Source Requirements",
    "Risk and Non-Advice Boundaries",
    "Non-Applicable Cases",
    "Composition",
    "Evals",
)
FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
OPENAI_FIELD_RE = re.compile(
    r'^  (?P<key>display_name|short_description|default_prompt):\s+"(?P<value>[^"]+)"$'
)
GOVERNED_FILES = frozenset(
    {
        "SKILL.md",
        "agents/openai.yaml",
        "references/method-contract.md",
        "references/trigger-evals.json",
    }
)
GOVERNED_DIRECTORIES = frozenset({"agents", "references"})


class ValidationError(ValueError):
    """Raised when a governed Skill violates the local source contract."""


def validate_skill(skill_dir: Path) -> None:
    """Validate one canonical Skill without importing or executing its content."""

    if skill_dir.is_symlink() or not skill_dir.is_dir():
        raise ValidationError(f"unsafe or missing Skill directory: {skill_dir}")
    skill_dir = skill_dir.resolve()
    _validate_governed_tree(skill_dir)
    skill_file = _regular_file(skill_dir, Path("SKILL.md"))
    text = skill_file.read_text(encoding="utf-8")
    frontmatter = _frontmatter(text)
    name = skill_dir.name
    if frontmatter.get("name") != name:
        raise ValidationError(f"{name}: frontmatter name does not match directory")
    description = frontmatter.get("description", "")
    if "Use when" not in description or "Do not use" not in description:
        raise ValidationError(f"{name}: description needs positive and negative triggers")
    for section in REQUIRED_SECTIONS:
        if not re.search(rf"(?m)^#{{2,3}} {re.escape(section)}\s*$", text):
            raise ValidationError(f"{name}: missing section {section}")
    if not re.search(r"(?im)^Version:\s*[0-9]+(?:\.[0-9]+){1,2}\s*$", text):
        raise ValidationError(f"{name}: missing semantic Skill version")

    agent_path = _regular_file(skill_dir, Path("agents/openai.yaml"))
    method_path = _regular_file(skill_dir, Path("references/method-contract.md"))
    eval_path = _regular_file(skill_dir, Path("references/trigger-evals.json"))
    for target in LINK_RE.findall(text):
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        _regular_file(skill_dir, Path(target.split("#", 1)[0]))
    _validate_openai_agent(name, agent_path)
    _validate_method_contract(name, method_path)
    _validate_trigger_evals(name, eval_path)


def _validate_governed_tree(skill_dir: Path) -> None:
    files: set[str] = set()
    directories: set[str] = set()
    for path in skill_dir.rglob("*"):
        relative = path.relative_to(skill_dir).as_posix()
        if path.is_symlink():
            raise ValidationError(f"{skill_dir.name}: unsafe symlinked tree entry: {relative}")
        if path.is_file():
            files.add(relative)
        elif path.is_dir():
            directories.add(relative)
        else:
            raise ValidationError(f"{skill_dir.name}: unsafe tree entry: {relative}")
    if files != GOVERNED_FILES or directories != GOVERNED_DIRECTORIES:
        raise ValidationError(
            f"{skill_dir.name}: governed tree must contain exactly the four delivery files"
        )


def _validate_openai_agent(skill_name: str, path: Path) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise ValidationError(f"{skill_name}: invalid openai agent metadata") from error
    if len(lines) != 4 or lines[0] != "interface:":
        raise ValidationError(f"{skill_name}: invalid openai agent metadata")
    values: dict[str, str] = {}
    for line in lines[1:]:
        match = OPENAI_FIELD_RE.fullmatch(line)
        if match is None or match.group("key") in values:
            raise ValidationError(f"{skill_name}: invalid openai agent metadata")
        values[match.group("key")] = match.group("value").strip()
    if (
        set(values) != {"display_name", "short_description", "default_prompt"}
        or not all(values.values())
        or f"${skill_name}" not in values["default_prompt"]
    ):
        raise ValidationError(f"{skill_name}: invalid openai agent metadata")


def _validate_method_contract(skill_name: str, path: Path) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ValidationError(f"{skill_name}: invalid method contract") from error
    if not content.strip():
        raise ValidationError(f"{skill_name}: method contract must not be empty")


def _frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if match is None:
        raise ValidationError("SKILL.md has no valid frontmatter block")
    values: dict[str, str] = {}
    for line in match.group("body").splitlines():
        key, separator, value = line.partition(":")
        if not separator or not key.strip() or not value.strip():
            raise ValidationError("frontmatter entries must be single-line key/value pairs")
        normalized = key.strip()
        if normalized in values:
            raise ValidationError(f"duplicate frontmatter field: {normalized}")
        values[normalized] = value.strip()
    if set(values) != {"name", "description"}:
        raise ValidationError("frontmatter must contain only name and description")
    return values


def _regular_file(root: Path, relative: Path) -> Path:
    if relative.is_absolute() or ".." in relative.parts:
        raise ValidationError(f"path escapes the Skill directory: {relative}")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValidationError(f"unsafe symlinked Skill file: {relative}")
    resolved = current.resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValidationError(f"missing regular Skill file: {relative}")
    return resolved


def _validate_trigger_evals(skill_name: str, path: Path) -> None:
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValidationError(f"{skill_name}: invalid trigger Evals") from error
    if (
        not isinstance(payload, Mapping)
        or payload.get("schema_version") != "1.0"
        or payload.get("skill") != skill_name
    ):
        raise ValidationError(f"{skill_name}: trigger Eval identity is invalid")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) < 4:
        raise ValidationError(f"{skill_name}: at least four trigger Evals are required")
    identifiers: set[str] = set()
    positives = 0
    near_misses = 0
    for case in cases:
        if not isinstance(case, Mapping):
            raise ValidationError(f"{skill_name}: trigger Eval case must be an object")
        identifier = case.get("id")
        question = case.get("question")
        expected = case.get("expected_skills")
        excluded = case.get("excluded_skills")
        if (
            not isinstance(identifier, str)
            or not identifier.strip()
            or identifier in identifiers
            or not isinstance(question, str)
            or not question.strip()
            or not isinstance(expected, list)
            or not all(isinstance(value, str) for value in expected)
            or not isinstance(excluded, list)
            or not all(isinstance(value, str) for value in excluded)
        ):
            raise ValidationError(f"{skill_name}: malformed or duplicate trigger Eval")
        identifiers.add(identifier)
        positives += int(skill_name in expected and skill_name not in excluded)
        near_misses += int(skill_name in excluded and skill_name not in expected)
    if positives < 2 or near_misses < 2:
        raise ValidationError(
            f"{skill_name}: requires at least two positive and two near-miss Evals"
        )


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate exactly the 13 governed InvestKit Runtime Skills."
    )
    parser.add_argument(
        "skill_dirs",
        nargs="*",
        type=Path,
        help="Canonical Skill directories; defaults to the repository skills root.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    repository_root = Path(__file__).resolve().parents[1]
    skill_dirs = args.skill_dirs or [
        repository_root / "skills" / name for name in EXPECTED_SKILLS
    ]
    resolved_names = tuple(path.name for path in skill_dirs)
    if len(skill_dirs) != len(EXPECTED_SKILLS) or set(resolved_names) != set(EXPECTED_SKILLS):
        print(
            "FAIL expected exactly the 13 governed Runtime Skill directories",
            file=sys.stderr,
        )
        return 1
    by_name = {path.name: path for path in skill_dirs}
    try:
        for name in EXPECTED_SKILLS:
            validate_skill(by_name[name])
            print(f"PASS {name}")
    except (OSError, UnicodeError, ValidationError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    print(f"PASS validated exactly {len(EXPECTED_SKILLS)} governed Skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
