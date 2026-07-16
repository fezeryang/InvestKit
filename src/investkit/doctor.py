"""Read-only diagnostics for an initialized InvestKit project."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any, Mapping

from . import __version__
from .assets import (
    CORE_SKILLS,
    REQUIRED_SPECS,
    SPEC_VERSION_RE,
    WORKFLOW_PATH,
    default_source_root,
    discover_skill_files,
    resolve_source_root,
    source_file,
)
from .capabilities.contracts import validate_capability_result
from .filesystem import resolve_within, resolved_root
from .models import DiagnosticCheck, DiagnosticStatus, DoctorReport
from .platforms.codex import CodexAdapter
from .providers.demo import DemoProvider
from .research.tasks import TASK_ID_RE


EXPECTED_WORKFLOW_STEPS = (
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
PROVIDER_METHODS = (
    "identify_security",
    "get_security_profile",
    "get_financial_statements",
    "get_price_history",
    "get_valuation_inputs",
    "get_source_metadata",
    "get_peer_comparables",
    "get_earnings_history",
    "get_catalyst_events",
)
PROVIDER_METADATA = {
    "as_of_date",
    "currency",
    "market",
    "source",
    "is_demo",
    "warnings",
}
SENSITIVE_KEY_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|private[_-]?key|secret|credential)"
)
SENSITIVE_VALUE_RE = re.compile(
    r"(?i)(?:\bsk-[A-Za-z0-9_-]{16,}|\bbearer\s+[A-Za-z0-9._-]{12,}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)
SENSITIVE_TEXT_ASSIGNMENT_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|"
    r"private[_-]?key|secret|credential)\s*[:=]\s*[^\s,;]{4,}"
)
FORBIDDEN_SOURCE_MARKERS = ("third_party/raw", "adapted/skills")
REQUIRED_COMPLETED_TASK_ARTIFACTS = (
    "task.json",
    "question.md",
    "plan.json",
    "loaded-specs.json",
    "installed-skills.json",
    "sources.json",
    "assumptions.json",
    "findings.json",
    "risks.json",
    "run-log.json",
    "report.md",
)
MANDATORY_COMPLETED_CAPABILITIES = frozenset(
    {"bear-case-analysis", "source-verification", "investment-report"}
)
IMMUTABLE_COMPLETED_TASK_ARTIFACTS = (
    "question.md",
    "plan.json",
    "loaded-specs.json",
    "installed-skills.json",
    "sources.json",
    "assumptions.json",
    "findings.json",
    "risks.json",
    "report.md",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def run_doctor(
    project_root: str | Path,
    *,
    source_root: str | Path | None = None,
) -> DoctorReport:
    """Return deterministic PASS/WARN/FAIL checks without repairing state."""

    checks: list[DiagnosticCheck] = []
    try:
        project = resolved_root(project_root)
    except Exception:
        return DoctorReport(
            (
                _check(
                    "project root",
                    DiagnosticStatus.FAIL,
                    "project root is missing or inaccessible",
                ),
            )
        )
    try:
        source = (
            default_source_root()
            if source_root is None
            else resolve_source_root(source_root)
        )
    except Exception:
        # Never inspect a rejected source candidate.  Diagnostics continue
        # against a known-missing path inside the selected project instead.
        source = project / ".investkit-unavailable-source"
        checks.append(
            _check(
                "first-party source root",
                DiagnosticStatus.FAIL,
                "first-party source root is missing or inaccessible",
            )
        )

    config, config_error = _read_object(project, ".investkit/config.json")
    manifest, manifest_error = _read_object(
        project, ".investkit/install-manifest.json"
    )
    adapter, adapter_error = _read_object(project, ".agents/investkit.json")
    codex_adapter = CodexAdapter()
    codex_environment = codex_adapter.describe(project)

    checks.append(
        _check(
            "InvestKit version",
            DiagnosticStatus.PASS
            if config.get("investkit_version") == __version__
            else DiagnosticStatus.FAIL,
            f"Runtime version {__version__}"
            if config.get("investkit_version") == __version__
            else "project configuration version is missing or incompatible",
        )
    )
    checks.append(
        _check(
            "project configuration",
            DiagnosticStatus.PASS
            if not config_error and config.get("managed_by") == "investkit"
            else DiagnosticStatus.FAIL,
            "configuration is valid"
            if not config_error and config.get("managed_by") == "investkit"
            else config_error or "configuration ownership marker is invalid",
        )
    )
    host_is_codex = (
        config.get("host_platform") == "codex"
        and adapter.get("host_platform", adapter.get("platform")) == "codex"
    )
    checks.append(
        _check(
            "host platform",
            DiagnosticStatus.PASS if host_is_codex else DiagnosticStatus.FAIL,
            "Codex adapter selected"
            if host_is_codex
            else "configured host platform is not the supported Codex adapter",
        )
    )
    adapter_valid = (
        not adapter_error
        and codex_adapter.detect_project(project)
        and adapter.get("managed_by") == "investkit"
        and adapter.get("installation_target") == ".agents/skills"
    )
    checks.append(
        _check(
            "Codex adapter configuration",
            DiagnosticStatus.PASS if adapter_valid else DiagnosticStatus.FAIL,
            "adapter configuration is valid"
            if adapter_valid
            else adapter_error
            or "adapter configuration or project environment is invalid "
            f"(agents={codex_environment['agents_path_state']}, "
            f"target={codex_environment['target_path_state']})",
        )
    )
    configured_source = config.get("source_root")
    source_matches = isinstance(configured_source, str) and Path(
        configured_source
    ).expanduser().resolve() == source
    checks.append(
        _check(
            "first-party source lineage",
            DiagnosticStatus.PASS if source_matches else DiagnosticStatus.FAIL,
            "configured source root matches diagnostics source"
            if source_matches
            else "configured source root does not match diagnostics source",
        )
    )

    try:
        workspace = resolve_within(project, "workspace")
        workspace_exists = workspace.is_dir()
    except Exception:
        workspace = None
        workspace_exists = False
    checks.append(
        _check(
            "workspace existence",
            DiagnosticStatus.PASS if workspace_exists else DiagnosticStatus.FAIL,
            "workspace directory exists"
            if workspace_exists
            else "workspace directory is missing",
        )
    )
    workspace_writable = (
        workspace is not None and workspace_exists and _mode_is_writable(workspace)
    )
    checks.append(
        _check(
            "workspace writability",
            DiagnosticStatus.PASS if workspace_writable else DiagnosticStatus.FAIL,
            "workspace is writable"
            if workspace_writable
            else "workspace is not writable",
        )
    )

    checks.append(_check_canonical_skills(source))
    installed_check, unmanaged_checks = _check_installed_skills(project)
    checks.append(installed_check)
    checks.extend(unmanaged_checks)
    checks.append(_check_manifest(manifest, manifest_error))
    checks.append(_check_mappings(project, source, manifest))
    checks.append(_check_specs(source, manifest))
    checks.append(_check_workflow(source))
    provider_check, fixture_check = _check_provider(source)
    checks.extend((provider_check, fixture_check))
    checks.append(_check_forbidden_state(project, config, manifest))
    checks.append(_check_sensitive_state(project))
    checks.append(_check_tasks(project))
    return DoctorReport(tuple(checks))


def _check_canonical_skills(source_root: Path) -> DiagnosticCheck:
    problems: list[str] = []
    file_count = 0
    for name in CORE_SKILLS:
        try:
            file_count += len(discover_skill_files(source_root, name))
        except Exception:
            problems.append(f"{name} is missing, unsafe, or incomplete")
    return _check(
        "first-party Skill source",
        DiagnosticStatus.FAIL if problems else DiagnosticStatus.PASS,
        "; ".join(problems)
        if problems
        else f"all {len(CORE_SKILLS)} allowlisted Skills and {file_count} governed files are present",
    )


def _check_installed_skills(
    project_root: Path,
) -> tuple[DiagnosticCheck, list[DiagnosticCheck]]:
    try:
        target = resolve_within(project_root, ".agents/skills")
    except Exception:
        return (
            _check(
                "Codex Skill installation target",
                DiagnosticStatus.FAIL,
                "Codex Skill target escapes the project boundary",
            ),
            [],
        )
    actual: set[str] = set()
    unsafe: list[str] = []
    if target.is_dir():
        for child in target.iterdir():
            display_name = _safe_name(child.name)
            if child.is_symlink():
                unsafe.append(display_name)
                continue
            try:
                resolved_child = child.resolve()
                skill_file = (resolved_child / "SKILL.md").resolve()
            except OSError:
                unsafe.append(display_name)
                continue
            if (
                resolved_child.is_dir()
                and resolved_child.is_relative_to(target)
                and skill_file.is_relative_to(resolved_child)
                and skill_file.is_file()
            ):
                actual.add(child.name)
    missing = [name for name in CORE_SKILLS if name not in actual]
    problems: list[str] = []
    if missing:
        problems.append("missing installed Skills: " + ", ".join(missing))
    if unsafe:
        problems.append("unsafe symlinked Skill paths: " + ", ".join(unsafe))
    primary = _check(
        "Codex Skill installation target",
        DiagnosticStatus.FAIL if problems else DiagnosticStatus.PASS,
        "; ".join(problems)
        if problems
        else "all required Skills are installed in .agents/skills",
    )
    extras = [
        _check(
            f"unmanaged Codex Skill {_safe_name(name)}",
            DiagnosticStatus.WARN,
            f"user-owned Skill {_safe_name(name)} is unmanaged and was preserved",
        )
        for name in sorted(actual - set(CORE_SKILLS))
    ]
    return primary, extras


def _check_manifest(
    manifest: Mapping[str, Any], error: str | None
) -> DiagnosticCheck:
    valid = (
        not error
        and manifest.get("managed_by") == "investkit"
        and isinstance(manifest.get("mappings"), list)
        and isinstance(manifest.get("specs"), list)
    )
    return _check(
        "installation manifest",
        DiagnosticStatus.PASS if valid else DiagnosticStatus.FAIL,
        "installation manifest structure is valid"
        if valid
        else error or "installation manifest structure is invalid",
    )


def _check_mappings(
    project_root: Path,
    source_root: Path,
    manifest: Mapping[str, Any],
) -> DiagnosticCheck:
    mappings = manifest.get("mappings")
    if not isinstance(mappings, list):
        return _check(
            "installation mapping checksums",
            DiagnosticStatus.FAIL,
            "mapping records are missing or corrupt",
        )
    problems: list[str] = []
    expected: dict[str, tuple[str, Path]] = {}
    for skill_name in CORE_SKILLS:
        try:
            skill_root = source_root / "skills" / skill_name
            for path in discover_skill_files(source_root, skill_name):
                source_relative = path.relative_to(source_root).as_posix()
                target_relative = (
                    Path(".agents/skills")
                    / skill_name
                    / path.relative_to(skill_root)
                ).as_posix()
                expected[source_relative] = (target_relative, path)
        except Exception:
            problems.append(f"{skill_name} canonical file discovery failed")

    by_source: dict[str, list[Mapping[str, Any]]] = {}
    for value in mappings:
        if not isinstance(value, Mapping):
            problems.append("mapping record is not an object")
            continue
        if value.get("kind") != "skill":
            continue
        source_value = str(value.get("source", "")).replace("\\", "/")
        by_source.setdefault(source_value, []).append(value)

    for source_value, records in by_source.items():
        if source_value not in expected:
            problems.append(
                f"unexpected governed Skill mapping: {_safe_name(source_value)}"
            )
        if len(records) != 1:
            problems.append(
                f"duplicate governed Skill mapping: {_safe_name(source_value)}"
            )

    for source_value, (expected_target, source_path) in expected.items():
        records = by_source.get(source_value, [])
        if len(records) != 1:
            if not records:
                problems.append(f"mapping missing: {_safe_name(source_value)}")
            continue
        mapping = records[0]
        target_value = str(mapping.get("target", "")).replace("\\", "/")
        if target_value != expected_target:
            problems.append(f"mapping path mismatch: {_safe_name(source_value)}")
            continue
        try:
            target_path = resolve_within(project_root, target_value)
            source_hash = _sha256(source_path)
            target_hash = _sha256(target_path)
        except (OSError, ValueError, RuntimeError):
            problems.append(f"mapping file missing or unsafe: {_safe_name(source_value)}")
            continue
        if (
            mapping.get("source_sha256") != source_hash
            or mapping.get("target_sha256") != target_hash
            or source_hash != target_hash
        ):
            problems.append(f"mapping hash/checksum mismatch: {_safe_name(source_value)}")
    return _check(
        "installation mapping checksums",
        DiagnosticStatus.FAIL if problems else DiagnosticStatus.PASS,
        "; ".join(problems)
        if problems
        else f"all {len(expected)} nested source-to-target mappings and hashes are verified",
    )


def _check_specs(source_root: Path, manifest: Mapping[str, Any]) -> DiagnosticCheck:
    records = manifest.get("specs")
    by_name: dict[str, Mapping[str, Any]] = {}
    if isinstance(records, list):
        for record in records:
            if isinstance(record, Mapping):
                by_name[Path(str(record.get("path", ""))).name] = record
    problems: list[str] = []
    for name in REQUIRED_SPECS:
        try:
            path = source_file(source_root, Path("specs") / name)
        except Exception:
            problems.append(f"{name} is missing")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            problems.append(f"{name} cannot be read")
            continue
        match = SPEC_VERSION_RE.search(text)
        record = by_name.get(name)
        digest = _sha256(path)
        if not match:
            problems.append(f"{name} has no version")
        elif record is None:
            problems.append(f"{name} manifest record is missing")
        elif record.get("version") != match.group(1) or record.get("sha256") != digest:
            problems.append(f"{name} version/checksum mismatch")
    return _check(
        "required research specs",
        DiagnosticStatus.FAIL if problems else DiagnosticStatus.PASS,
        "; ".join(problems)
        if problems
        else "all seven versioned research specs are verified",
    )


def _check_workflow(source_root: Path) -> DiagnosticCheck:
    try:
        path = source_file(source_root, WORKFLOW_PATH)
        value = json.loads(path.read_text(encoding="utf-8"))
        steps = value.get("steps", []) if isinstance(value, Mapping) else []
        identifiers = tuple(
            str(step.get("id", "")) if isinstance(step, Mapping) else str(step)
            for step in steps
        )
        valid = (
            isinstance(value, Mapping)
            and value.get("id") == "company-deep-dive"
            and bool(value.get("version"))
            and identifiers == EXPECTED_WORKFLOW_STEPS
            and tuple(value.get("skills", ())) == tuple(CORE_SKILLS)
            and all(
                isinstance(step, Mapping)
                and step.get("output") == f"capabilities/{step.get('id')}.json"
                for step in steps
            )
        )
    except Exception:
        valid = False
    return _check(
        "offline research workflow",
        DiagnosticStatus.PASS if valid else DiagnosticStatus.FAIL,
        "workflow identity, version, and ordered steps are valid"
        if valid
        else "required offline research workflow is missing or invalid",
    )


def _check_provider(source_root: Path) -> tuple[DiagnosticCheck, DiagnosticCheck]:
    try:
        provider = DemoProvider(asset_root=source_root)
        identity = provider.identify_security("demo")
        security_id = str(identity.get("security_id", ""))
        responses = [
            identity,
            provider.get_security_profile(security_id),
            provider.get_financial_statements(security_id),
            provider.get_price_history(security_id),
            provider.get_valuation_inputs(security_id),
            provider.get_source_metadata(security_id),
            provider.get_peer_comparables(security_id),
            provider.get_earnings_history(security_id),
            provider.get_catalyst_events(security_id),
        ]
        valid = all(_provider_response_is_valid(response) for response in responses)
    except Exception:
        responses = []
        valid = False
    provider_check = _check(
        "Demo Provider behavior",
        DiagnosticStatus.PASS if valid else DiagnosticStatus.FAIL,
        f"all {len(PROVIDER_METHODS)} offline Provider operations preserve required metadata"
        if valid
        else "Demo Provider or fixture behavior is invalid",
    )
    has_missing = any(_contains_none(response) for response in responses)
    warnings_are_actionable = any(
        re.search(r"(?i)missing|unknown|unavailable|not available", str(warning))
        for response in responses
        for warning in response.get("warnings", [])
    )
    fixture_valid = bool(responses) and has_missing and warnings_are_actionable
    fixture_check = _check(
        "demo fixture completeness",
        DiagnosticStatus.WARN if fixture_valid else DiagnosticStatus.FAIL,
        "fixture has explicit missing values and actionable warnings"
        if fixture_valid
        else "fixture does not expose missing values and actionable warnings",
    )
    return provider_check, fixture_check


def _provider_response_is_valid(response: Any) -> bool:
    if not isinstance(response, Mapping) or not PROVIDER_METADATA.issubset(response):
        return False
    if response.get("is_demo") is not True:
        return False
    if any(
        not isinstance(response.get(field), str) or not response.get(field)
        for field in ("as_of_date", "currency", "market", "source")
    ):
        return False
    if not response.get("fixture_version") and not response.get("retrieved_at"):
        return False
    warnings = response.get("warnings")
    return (
        isinstance(warnings, list)
        and bool(warnings)
        and all(isinstance(value, str) and value.strip() for value in warnings)
    )


def _check_forbidden_state(
    project_root: Path,
    config: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> DiagnosticCheck:
    problem: str | None = None
    serialized = json.dumps({"config": config, "manifest": manifest}).replace(
        "\\", "/"
    ).lower()
    if any(marker in serialized for marker in FORBIDDEN_SOURCE_MARKERS):
        problem = "forbidden third-party or draft source appears in owned state"
    try:
        skills_root = resolve_within(project_root, ".agents/skills")
    except Exception:
        skills_root = None
        problem = "Codex Skill installation target escapes the project boundary"
    if skills_root is not None and skills_root.is_dir():
        for child in skills_root.iterdir():
            display_name = _safe_name(child.name)
            if child.is_symlink():
                problem = f"unsafe symlinked installation path for {display_name}"
                break
            marker_path = child / ".investkit-source.json"
            if marker_path.is_symlink():
                problem = f"installation marker is an unsafe symlink for {display_name}"
                break
            if not marker_path.exists():
                continue
            try:
                marker_path = marker_path.resolve()
                if not marker_path.is_relative_to(skills_root):
                    problem = f"installation marker escapes the project for {display_name}"
                    break
            except OSError:
                problem = f"installation marker is inaccessible for {display_name}"
                break
            try:
                marker = json.loads(marker_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                problem = f"unapproved installation marker is corrupt for {display_name}"
                break
            marker_text = json.dumps(marker).replace("\\", "/").lower()
            if (
                any(value in marker_text for value in FORBIDDEN_SOURCE_MARKERS)
                or str(marker.get("approval", "")).lower() != "approved"
            ):
                problem = f"forbidden or unapproved installation marker for {display_name}"
                break
    return _check(
        "third-party installation boundary",
        DiagnosticStatus.FAIL if problem else DiagnosticStatus.PASS,
        problem or "no forbidden or unapproved InvestKit installation evidence found",
    )


def _check_sensitive_state(project_root: Path) -> DiagnosticCheck:
    candidates: list[Path] = []
    for relative_path in (
        ".investkit/config.json",
        ".investkit/install-manifest.json",
        ".agents/investkit.json",
    ):
        try:
            candidates.append(resolve_within(project_root, relative_path))
        except Exception:
            return _check(
                "sensitive information scan",
                DiagnosticStatus.FAIL,
                "InvestKit-owned state escapes the project boundary",
            )
    try:
        research_root = resolve_within(project_root, "workspace/research")
    except Exception:
        return _check(
            "sensitive information scan",
            DiagnosticStatus.FAIL,
            "research workspace escapes the project boundary",
        )
    if research_root.is_dir():
        for directory, child_directories, file_names in os.walk(
            research_root, followlinks=False
        ):
            directory_path = Path(directory)
            child_directories[:] = [
                name
                for name in child_directories
                if not (directory_path / name).is_symlink()
            ]
            for file_name in file_names:
                is_json = file_name.endswith(".json")
                is_owned_markdown = file_name in {"question.md", "report.md"}
                if not is_json and not is_owned_markdown:
                    continue
                path = directory_path / file_name
                if path.is_symlink():
                    continue
                resolved = path.resolve()
                if resolved.is_relative_to(research_root):
                    candidates.append(resolved)
    findings: list[str] = []
    for path in candidates:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
            value = json.loads(text) if path.suffix == ".json" else None
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if (
            (path.suffix == ".json" and _contains_sensitive(value))
            or SENSITIVE_VALUE_RE.search(text)
            or SENSITIVE_TEXT_ASSIGNMENT_RE.search(text)
        ):
            try:
                relative = path.relative_to(project_root).as_posix()
            except ValueError:
                relative = "InvestKit-owned state"
            findings.append(relative)
    return _check(
        "sensitive information scan",
        DiagnosticStatus.FAIL if findings else DiagnosticStatus.PASS,
        "sensitive value detected in: " + ", ".join(findings)
        if findings
        else "no likely credential values found in InvestKit-owned state",
    )


def _check_tasks(project_root: Path) -> DiagnosticCheck:
    problems: list[str] = []
    try:
        research_root = resolve_within(project_root, "workspace/research")
    except Exception:
        return _check(
            "research task records",
            DiagnosticStatus.FAIL,
            "research workspace escapes the project boundary",
        )
    if research_root.is_dir():
        for entry in sorted(research_root.iterdir(), key=lambda path: path.name):
            task_name = _safe_name(entry.name)
            if entry.is_symlink():
                problems.append(f"{task_name} is an unsafe symlinked task path")
                continue
            if not entry.is_dir():
                continue
            task_path = entry.resolve()
            if not task_path.is_relative_to(research_root):
                problems.append(f"{task_name} escapes the research workspace")
                continue
            if not TASK_ID_RE.fullmatch(entry.name) or ".." in entry.name:
                problems.append(f"{task_name} has an invalid task ID")
                continue
            task = _read_task_json(task_path, "task.json")
            if task is None:
                problems.append(f"{task_name} has a corrupt task record")
                continue
            if (
                not isinstance(task, Mapping)
                or task.get("id") != entry.name
                or task.get("status") not in {"created", "running", "failed", "completed"}
            ):
                problems.append(f"{task_name} has an invalid task record")
                continue
            status = str(task["status"])
            expected_skills = task.get("skills")
            expected_specs = task.get("specs")
            workflow = task.get("workflow")
            if (
                not isinstance(expected_skills, list)
                or not all(isinstance(value, str) for value in expected_skills)
                or len(expected_skills) != len(CORE_SKILLS)
                or set(expected_skills) != set(CORE_SKILLS)
                or not isinstance(expected_specs, list)
                or not all(isinstance(value, str) for value in expected_specs)
                or len(expected_specs) != len(REQUIRED_SPECS)
                or set(expected_specs) != set(REQUIRED_SPECS)
                or not isinstance(workflow, Mapping)
                or workflow.get("id") != "company-deep-dive"
                or not isinstance(workflow.get("version"), str)
                or not workflow.get("version")
            ):
                problems.append(f"{task_name} has invalid capability snapshots")
            plan = _read_task_json(task_path, "plan.json")
            run_log = _read_task_json(task_path, "run-log.json")
            plan_problems = _plan_problems(plan, status)
            run_log_problems = _run_log_problems(run_log, entry.name, status)
            problems.extend(f"{task_name} {problem}" for problem in plan_problems)
            problems.extend(f"{task_name} {problem}" for problem in run_log_problems)
            if not plan_problems and isinstance(plan, Mapping):
                problems.extend(
                    f"{task_name} {problem}"
                    for problem in _capability_artifact_problems(
                        task_path,
                        status,
                        plan,
                    )
                )
            if status == "failed":
                outcome = task.get("outcome")
                if (
                    not isinstance(outcome, Mapping)
                    or outcome.get("status") != "failed"
                    or not isinstance(outcome.get("error"), str)
                    or not outcome.get("error")
                ):
                    problems.append(f"{task_name} has invalid failed outcome state")
            if status == "completed" and not plan_problems:
                problems.extend(
                    _completed_task_problems(task_path, task_name, task, plan)
                )
    return _check(
        "research task records",
        DiagnosticStatus.FAIL if problems else DiagnosticStatus.PASS,
        "; ".join(problems)
        if problems
        else "research task records are structurally valid",
    )


def _plan_problems(plan: Mapping[str, Any] | None, status: str) -> list[str]:
    if not isinstance(plan, Mapping):
        return ["has corrupt plan.json"]
    steps = plan.get("steps")
    if (
        plan.get("workflow") != "company-deep-dive"
        or not isinstance(plan.get("version"), str)
        or not plan.get("version")
        or not isinstance(steps, list)
    ):
        return ["has corrupt plan.json"]
    identifiers = tuple(
        str(step.get("id", "")) if isinstance(step, Mapping) else ""
        for step in steps
    )
    if identifiers != EXPECTED_WORKFLOW_STEPS:
        return ["has invalid workflow steps in plan.json"]
    step_statuses = [
        step.get("status") if isinstance(step, Mapping) else None for step in steps
    ]
    if any(
        step_status not in {"pending", "running", "failed", "completed"}
        for step_status in step_statuses
    ):
        return ["has invalid step status in plan.json"]
    if status == "created" and any(value != "pending" for value in step_statuses):
        return ["has plan state inconsistent with created status"]
    if status == "failed" and "failed" not in step_statuses:
        return ["has no failed workflow step"]
    if status == "completed" and any(value != "completed" for value in step_statuses):
        return ["has incomplete completed workflow state"]
    return []


def _run_log_problems(
    run_log: Mapping[str, Any] | None,
    task_id: str,
    status: str,
) -> list[str]:
    if not isinstance(run_log, Mapping):
        return ["has corrupt run-log.json"]
    events = run_log.get("events")
    if run_log.get("task_id") != task_id or not isinstance(events, list) or not events:
        return ["has corrupt run-log.json"]
    if any(
        not isinstance(event, Mapping)
        or event.get("event") not in {"task", "step", "resume"}
        or not isinstance(event.get("status"), str)
        or not isinstance(event.get("timestamp"), str)
        or not event.get("timestamp")
        for event in events
    ):
        return ["has invalid run-log events"]
    required_status = {
        "created": "created",
        "running": "running",
        "failed": "failed",
        "completed": "completed",
    }[status]
    if not any(event.get("status") == required_status for event in events):
        return [f"has no {required_status} run-log event"]
    return []


def _capability_artifact_problems(
    task_path: Path,
    task_status: str,
    plan: Mapping[str, Any],
) -> list[str]:
    """Validate persisted capability envelopes without following task symlinks."""

    problems: list[str] = []
    steps_value = plan.get("steps", [])
    if not isinstance(steps_value, list):
        return problems
    step_statuses = {
        str(step.get("id", "")): str(step.get("status", ""))
        for step in steps_value
        if isinstance(step, Mapping)
    }
    required: set[str]
    if task_status == "completed":
        required = set(EXPECTED_WORKFLOW_STEPS)
    else:
        required = {
            name
            for name, status in step_statuses.items()
            if status == "completed"
        }

    lexical_root = task_path / "capabilities"
    capability_root = _task_artifact(task_path, "capabilities")
    if _relative_path_has_symlink(task_path, Path("capabilities")):
        return ["has an unsafe symlinked capabilities directory"]
    if capability_root is None or not capability_root.is_dir():
        return ["is missing capabilities directory"] if required else []

    values: dict[str, dict[str, Any]] = {}
    actual_names: set[str] = set()
    try:
        entries = sorted(lexical_root.iterdir(), key=lambda path: path.name)
    except OSError:
        return ["has an inaccessible capabilities directory"]
    for entry in entries:
        display_name = _safe_name(entry.name)
        if entry.is_symlink():
            problems.append(f"has unsafe symlinked capability artifact {display_name}")
            continue
        if not entry.is_file() or entry.suffix != ".json":
            problems.append(f"has unexpected capability artifact {display_name}")
            continue
        capability = entry.stem
        actual_names.add(capability)
        if capability not in CORE_SKILLS:
            problems.append(f"has unapproved capability artifact {display_name}")
            continue
        value = _read_task_json(task_path, f"capabilities/{entry.name}")
        if value is None:
            problems.append(f"has corrupt capability artifact {display_name}")
            continue
        try:
            validate_capability_result(value, expected=capability)
        except (TypeError, ValueError):
            problems.append(f"has invalid capability envelope {display_name}")
            continue
        values[capability] = value

        result_status = value.get("status")
        plan_status = step_statuses.get(capability)
        if plan_status == "completed" and result_status not in {"completed", "skipped"}:
            problems.append(
                f"has capability status inconsistent with completed step {capability}"
            )
        elif plan_status in {"pending", "running"} and result_status in {
            "completed",
            "skipped",
        }:
            problems.append(
                f"has capability artifact ahead of plan state for {capability}"
            )

    for capability in sorted(required - actual_names):
        problems.append(f"is missing capabilities/{capability}.json")

    if task_status == "completed":
        for capability in sorted(actual_names - set(EXPECTED_WORKFLOW_STEPS)):
            problems.append(f"has unexpected completed capability {capability}")
        for capability in sorted(MANDATORY_COMPLETED_CAPABILITIES):
            value = values.get(capability)
            if not isinstance(value, Mapping) or value.get("status") != "completed":
                problems.append(
                    f"requires completed mandatory capability {capability}"
                )

    referenced_ids = {
        str(source_id)
        for value in values.values()
        for source_id in value.get("source_ids", [])
        if isinstance(source_id, str) and source_id
    }
    if referenced_ids:
        sources = _read_task_json(task_path, "sources.json")
        records = sources.get("sources") if isinstance(sources, Mapping) else None
        known_ids = {
            str(record.get("source_id"))
            for record in records
            if isinstance(record, Mapping)
            and isinstance(record.get("source_id"), str)
            and record.get("source_id")
        } if isinstance(records, list) else set()
        unresolved = sorted(referenced_ids - known_ids)
        if unresolved:
            problems.append(
                "has unresolved capability source IDs: "
                + ", ".join(_safe_name(value) for value in unresolved)
            )
    return problems


def _completed_task_problems(
    task_path: Path,
    task_name: str,
    task: Mapping[str, Any],
    plan: Mapping[str, Any] | None,
) -> list[str]:
    problems: list[str] = []
    for relative_path in REQUIRED_COMPLETED_TASK_ARTIFACTS:
        artifact = _task_artifact(task_path, relative_path)
        if artifact is None or not artifact.is_file():
            problems.append(f"{task_name} is missing {relative_path}")
            continue
        if artifact.suffix == ".json" and _read_task_json(task_path, relative_path) is None:
            problems.append(f"{task_name} has corrupt {relative_path}")
        elif artifact.suffix == ".md":
            try:
                if not artifact.read_text(encoding="utf-8").strip():
                    problems.append(f"{task_name} has empty {relative_path}")
            except (OSError, UnicodeError):
                problems.append(f"{task_name} has corrupt {relative_path}")

    if isinstance(plan, Mapping):
        steps = plan.get("steps", [])
        identifiers = tuple(
            str(step.get("id", "")) if isinstance(step, Mapping) else ""
            for step in steps
        )
        if identifiers != EXPECTED_WORKFLOW_STEPS or any(
            not isinstance(step, Mapping) or step.get("status") != "completed"
            for step in steps
        ):
            problems.append(f"{task_name} has incomplete completed workflow state")

    outcome = task.get("outcome")
    if (
        not isinstance(outcome, Mapping)
        or outcome.get("status") != "completed"
        or outcome.get("report") != "report.md"
    ):
        problems.append(f"{task_name} has an invalid report reference")
    data_references = task.get("data")
    if not isinstance(data_references, list) or not data_references:
        problems.append(f"{task_name} has no data references")
    else:
        for reference in data_references:
            if (
                not isinstance(reference, str)
                or not reference.startswith("data/")
                or (artifact := _task_artifact(task_path, reference)) is None
                or not artifact.is_file()
                or _read_task_json(task_path, reference) is None
            ):
                problems.append(f"{task_name} has a broken or corrupt data reference")
                break
    data_directory = _task_artifact(task_path, "data")
    if data_directory is None or not data_directory.is_dir() or not any(
        not path.is_symlink() and path.is_file()
        for path in data_directory.glob("*.json")
    ):
        problems.append(f"{task_name} has no persisted data artifacts")
    problems.extend(
        f"{task_name} {problem}"
        for problem in _immutable_artifact_problems(task_path, task)
    )
    return problems


def _immutable_artifact_problems(
    task_path: Path,
    task: Mapping[str, Any],
) -> list[str]:
    """Compare a completed task's stored immutable artifact hashes."""

    expected_paths: set[str] = set(IMMUTABLE_COMPLETED_TASK_ARTIFACTS)
    expected_paths.update(
        f"capabilities/{capability}.json" for capability in EXPECTED_WORKFLOW_STEPS
    )
    data_references = task.get("data")
    if isinstance(data_references, list):
        expected_paths.update(
            value
            for value in data_references
            if isinstance(value, str) and value.startswith("data/")
        )
    stored = task.get("artifact_hashes")
    if not isinstance(stored, Mapping) or not stored:
        return ["has no immutable artifact hash manifest"]
    if set(stored) != expected_paths:
        return ["has an incomplete or unexpected immutable artifact hash manifest"]
    for relative_path in sorted(expected_paths):
        expected_digest = stored.get(relative_path)
        artifact = _task_artifact(task_path, relative_path)
        if (
            not isinstance(expected_digest, str)
            or not SHA256_RE.fullmatch(expected_digest)
            or artifact is None
            or not artifact.is_file()
        ):
            return [
                "has an invalid immutable artifact hash record for "
                + _safe_name(relative_path)
            ]
        try:
            actual_digest = _sha256(artifact)
        except OSError:
            return [
                "has an unreadable immutable artifact for "
                + _safe_name(relative_path)
            ]
        if actual_digest != expected_digest:
            return [
                "has an immutable artifact hash mismatch for "
                + _safe_name(relative_path)
            ]
    return []


def _read_task_json(task_path: Path, relative_path: str) -> dict[str, Any] | None:
    artifact = _task_artifact(task_path, relative_path)
    if artifact is None or not artifact.is_file():
        return None
    try:
        value = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _task_artifact(task_path: Path, relative_path: str) -> Path | None:
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    candidate = task_path / relative
    try:
        if _relative_path_has_symlink(task_path, relative):
            return None
        resolved = candidate.resolve()
    except OSError:
        return None
    return resolved if resolved.is_relative_to(task_path) else None


def _relative_path_has_symlink(root: Path, relative: Path) -> bool:
    current = root
    for part in relative.parts:
        current = current / part
        try:
            if current.is_symlink():
                return True
        except OSError:
            return True
    return False


def _read_object(root: Path, relative_path: str) -> tuple[dict[str, Any], str | None]:
    try:
        path = resolve_within(root, relative_path)
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, f"{relative_path} is missing"
    except (OSError, UnicodeError, json.JSONDecodeError, RuntimeError, ValueError):
        return {}, f"{relative_path} is corrupt or invalid"
    if not isinstance(value, dict):
        return {}, f"{relative_path} must contain a JSON object"
    return value, None


def _mode_is_writable(path: Path) -> bool:
    try:
        mode = stat.S_IMODE(path.stat().st_mode)
    except OSError:
        return False
    return bool(mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)) and os.access(
        path, os.W_OK
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _contains_none(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, Mapping):
        return any(_contains_none(child) for child in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_none(child) for child in value)
    return False


def _contains_sensitive(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if SENSITIVE_KEY_RE.search(str(key)) and child not in (None, "", [], {}):
                return True
            if _contains_sensitive(child):
                return True
        return False
    if isinstance(value, (list, tuple)):
        return any(_contains_sensitive(child) for child in value)
    return isinstance(value, str) and bool(SENSITIVE_VALUE_RE.search(value))


def _check(
    name: str,
    status: DiagnosticStatus,
    message: str,
) -> DiagnosticCheck:
    return DiagnosticCheck(name=name, status=status, message=message)


def _safe_name(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]", "?", value)
    return sanitized[:96] or "unknown"
