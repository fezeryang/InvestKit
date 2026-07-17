"""Read-only diagnostics for an initialized InvestKit project."""

from __future__ import annotations

from datetime import date, timedelta
import hashlib
import json
import math
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
from .catalog import load_asset_catalog
from .filesystem import resolve_within, resolved_root
from .models import DiagnosticCheck, DiagnosticStatus, DoctorReport
from .platforms.codex import CodexAdapter
from .providers.demo import DemoProvider
from .providers.file import (
    BundleInputError,
    BundleValidationError,
    FileProvider,
)
from .research.report import RESTRICTED_LANGUAGE_RE
from .research.tasks import TASK_ID_RE
from .security import contains_sensitive_key, contains_sensitive_value


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
IMPORTED_BUNDLE_PATH = "input/research-bundle.json"
DATA_OPERATION_PATHS = {
    "identify_security": "data/security-identity.json",
    "get_source_metadata": "data/source-metadata.json",
    "get_security_profile": "data/security-profile.json",
    "get_financial_statements": "data/financial-statements.json",
    "get_price_history": "data/price-history.json",
    "get_valuation_inputs": "data/valuation-inputs.json",
    "get_peer_comparables": "data/peer-comparables.json",
    "get_earnings_history": "data/earnings-history.json",
    "get_catalyst_events": "data/catalyst-events.json",
}
OPERATION_COMPLETION_STEPS = {
    "identify_security": "security-identification",
    "get_source_metadata": "security-identification",
    "get_security_profile": "company-deep-research",
    "get_financial_statements": "financial-statement-analysis",
    "get_price_history": "valuation-analysis",
    "get_valuation_inputs": "valuation-analysis",
    "get_peer_comparables": "comps-analysis",
    "get_earnings_history": "earnings-analysis",
    "get_catalyst_events": "catalyst-analysis",
}
IMPORTED_REPORT_RESTRICTED_RE = re.compile(
    r"(?im)(?:^|[.!?]\s+)(?:buy|sell|hold)\b|"
    r"\b(?:recommend(?:ation)?|rating|rated|should)\s+(?:is\s+|to\s+)?"
    r"(?:buy|sell|hold)\b|"
    r"\b(?:buy|sell|hold)\s+(?:the\s+)?(?:stock|shares|security)\b|"
    r"guaranteed (?:return|profit)|"
    r"risk-free return|price will|position size|stop loss|"
    r"(?:connect|access|use)\s+(?:a\s+)?brokerage|"
    r"(?:place|submit|execute)\s+(?:an?\s+)?order|"
    r"(?:transfer|send)\s+funds"
)
REPORT_INJECTION_RE = re.compile(
    r"(?i)<\s*/?\s*[a-z][^>\n]*>|javascript\s*:|data\s*:\s*text/html|"
    r"!?\[[^\]\n]*\]\s*\([^\n)]*\)"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MAX_OWNED_JSON_BYTES = 2 * 1024 * 1024
MAX_SENSITIVE_TEXT_BYTES = 2 * 1024 * 1024
IMPORTED_FRESHNESS_MAX_AGE_DAYS = 180


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
    checks.extend(_check_asset_catalog(source))
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
    checks.extend(_check_tasks(project))
    return DoctorReport(tuple(checks))


def _check_asset_catalog(source_root: Path) -> tuple[DiagnosticCheck, DiagnosticCheck]:
    """Validate catalog structure and report execution gates without network I/O."""

    try:
        catalog = load_asset_catalog(source_root)
    except Exception:
        return (
            _check(
                "Runtime asset catalog",
                DiagnosticStatus.FAIL,
                "catalog is missing, unsafe, malformed, or internally inconsistent",
            ),
            _check(
                "Asset execution gates",
                DiagnosticStatus.WARN,
                "execution gates cannot be evaluated until the catalog is valid",
            ),
        )
    first_party = sum(asset.origin == "first_party" for asset in catalog.assets)
    candidates = sum(asset.origin == "candidate" for asset in catalog.assets)
    catalog_check = _check(
        "Runtime asset catalog",
        DiagnosticStatus.PASS,
        f"catalog {catalog.catalog_version} contains {len(catalog.assets)} assets "
        f"({first_party} first-party, {candidates} candidates)",
    )
    credential_names = sorted(
        {name for asset in catalog.assets for name in asset.credentials}
    )
    missing_credentials = [name for name in credential_names if not os.environ.get(name)]
    unavailable_count = sum(asset.state != "ready" for asset in catalog.assets)
    details: list[str] = []
    if unavailable_count:
        details.append(f"{unavailable_count} assets are intentionally not ready")
    if missing_credentials:
        details.append("credentials not configured: " + ", ".join(missing_credentials))
    if details:
        gate_check = _check(
            "Asset execution gates",
            DiagnosticStatus.WARN,
            "; ".join(details),
        )
    else:
        gate_check = _check(
            "Asset execution gates",
            DiagnosticStatus.PASS,
            "all catalog execution gates are satisfied",
        )
    return catalog_check, gate_check


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
        value = _read_strict_json(path)
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
                marker = _read_strict_json(marker_path)
            except (
                OSError,
                UnicodeError,
                json.JSONDecodeError,
                OverflowError,
                RecursionError,
                TypeError,
                ValueError,
            ):
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
                try:
                    path.relative_to(research_root)
                except ValueError:
                    continue
                candidates.append(path)
    findings: list[str] = []
    uninspectable: list[str] = []
    for path in candidates:
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            continue
        except OSError:
            metadata = None
        try:
            relative = path.relative_to(project_root).as_posix()
        except ValueError:
            relative = "InvestKit-owned state"
        if metadata is None or not stat.S_ISREG(metadata.st_mode):
            uninspectable.append(relative)
            continue
        try:
            payload = _read_regular_bytes(path, MAX_SENSITIVE_TEXT_BYTES)
            text = payload.decode("utf-8", errors="strict")
        except (OSError, UnicodeError, ValueError):
            uninspectable.append(relative)
            continue
        value: Any = None
        if path.suffix == ".json":
            try:
                value = _strict_json_loads(text)
            except (
                json.JSONDecodeError,
                OverflowError,
                RecursionError,
                TypeError,
                ValueError,
            ):
                uninspectable.append(relative)
        if (
            (path.suffix == ".json" and _contains_sensitive(value))
            or contains_sensitive_value(text)
        ):
            findings.append(relative)
    findings = list(dict.fromkeys(findings))
    uninspectable = [
        value for value in dict.fromkeys(uninspectable) if value not in findings
    ]
    has_failures = bool(findings or uninspectable)
    if findings:
        message = "sensitive value detected in: " + ", ".join(findings)
    elif uninspectable:
        message = "owned state could not be safely inspected: " + ", ".join(
            uninspectable
        )
    else:
        message = "no likely credential values found in InvestKit-owned state"
    return _check(
        "sensitive information scan",
        DiagnosticStatus.FAIL if has_failures else DiagnosticStatus.PASS,
        message,
    )


def _check_tasks(project_root: Path) -> list[DiagnosticCheck]:
    """Return one safe, mode-aware diagnostic per durable research task."""

    try:
        research_root = resolve_within(project_root, "workspace/research")
    except Exception:
        return [
            _check(
                "research task records",
                DiagnosticStatus.FAIL,
                "research workspace escapes the project boundary",
            )
        ]
    if not research_root.is_dir():
        return [
            _check(
                "research task records",
                DiagnosticStatus.PASS,
                "no durable research tasks are present",
            )
        ]

    checks: list[DiagnosticCheck] = []
    try:
        entries = sorted(research_root.iterdir(), key=lambda path: path.name)
    except OSError:
        return [
            _check(
                "research task records",
                DiagnosticStatus.FAIL,
                "research workspace is inaccessible",
            )
        ]
    for entry in entries:
        task_name = _safe_name(entry.name)
        if entry.is_symlink():
            checks.append(
                _check(
                    f"research task {task_name}",
                    DiagnosticStatus.FAIL,
                    "task path is an unsafe symlink",
                )
            )
            continue
        if not entry.is_dir():
            continue
        try:
            task_path = entry.resolve()
        except OSError:
            task_path = entry
        if not task_path.is_relative_to(research_root):
            checks.append(
                _check(
                    f"research task {task_name}",
                    DiagnosticStatus.FAIL,
                    "task path escapes the research workspace",
                )
            )
            continue
        if not TASK_ID_RE.fullmatch(entry.name) or ".." in entry.name:
            checks.append(
                _check(
                    f"research task {task_name}",
                    DiagnosticStatus.FAIL,
                    "task ID is invalid",
                )
            )
            continue
        task_checks = _check_one_task(project_root, task_path, entry.name)
        checks.extend(task_checks)
    if not checks:
        checks.append(
            _check(
                "research task records",
                DiagnosticStatus.PASS,
                "no durable research tasks are present",
            )
        )
    return checks


def _check_one_task(
    project_root: Path,
    task_path: Path,
    task_id: str,
) -> list[DiagnosticCheck]:
    task_name = _safe_name(task_id)
    check_name = f"research task {task_name}"
    filesystem_problems = _task_filesystem_problems(task_path)
    if filesystem_problems:
        return [
            _check(
                check_name,
                DiagnosticStatus.FAIL,
                _bounded_problem_message(filesystem_problems),
            )
        ]
    task = _read_task_json(task_path, "task.json")
    if task is None:
        return [
            _check(check_name, DiagnosticStatus.FAIL, "task record is corrupt")
        ]
    status_value = task.get("status")
    if (
        task.get("id") != task_id
        or status_value not in {"created", "running", "failed", "completed"}
    ):
        return [
            _check(check_name, DiagnosticStatus.FAIL, "task record is invalid")
        ]
    status = str(status_value)
    explicit_mode = "input_mode" in task
    input_mode = task.get("input_mode", "demo")
    if input_mode not in {"demo", "imported"}:
        return [
            _check(check_name, DiagnosticStatus.FAIL, "task input mode is invalid")
        ]
    mode = str(input_mode)
    problems: list[str] = []
    warnings: list[str] = []

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
        problems.append("capability snapshots are invalid")

    plan = _read_task_json(task_path, "plan.json")
    run_log = _read_task_json(task_path, "run-log.json")
    problems.extend(_plan_problems(plan, status, task))
    problems.extend(_run_log_problems(run_log, task_id, status))
    if isinstance(plan, Mapping):
        plan_mode = plan.get("input_mode", "demo")
        if (explicit_mode and plan.get("input_mode") != mode) or (
            not explicit_mode and plan_mode != "demo"
        ):
            problems.append("plan input mode disagrees with the task")

    question = task.get("question")
    if not isinstance(question, str) or not question.strip():
        problems.append("research question is missing")
    elif not _question_artifact_matches(
        task_path,
        question,
        allow_legacy=not explicit_mode,
    ):
        problems.append("question artifact disagrees with the task")

    if isinstance(plan, Mapping):
        problems.extend(
            _capability_artifact_problems(task_path, status, plan)
        )
        completed_steps = _completed_plan_steps(plan)
    else:
        completed_steps = ()
    capability_values = _read_capability_values(task_path)
    if set(capability_values) != set(completed_steps):
        problems.append("capability artifacts do not equal the completed-step prefix")

    provider: FileProvider | None = None
    if mode == "imported":
        provider, imported_problems = _validate_imported_snapshot(
            project_root,
            task_path,
            task,
        )
        problems.extend(imported_problems)
        if provider is not None:
            warnings.extend(_imported_freshness_warnings(provider))
            problems.extend(
                _imported_state_problems(
                    task_path,
                    task,
                    provider,
                    completed_steps,
                    status,
                )
            )
            problems.extend(
                _imported_capability_problems(capability_values, provider)
            )
    else:
        problems.extend(
            _data_artifact_set_problems(
                task_path,
                task,
                completed_steps,
                status,
            )
        )

    problems.extend(
        _aggregate_artifact_problems(
            task_path,
            mode=mode,
            legacy=not explicit_mode,
            capability_values=capability_values,
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
            problems.append("failed outcome state is invalid")
    if status == "completed" and isinstance(plan, Mapping):
        completed_problems = _completed_task_problems(
            task_path,
            task_name,
            task,
            plan,
        )
        prefix = task_name + " "
        problems.extend(
            value[len(prefix) :] if value.startswith(prefix) else value
            for value in completed_problems
        )
        problems.extend(
            _report_mode_problems(
                task_path,
                task,
                mode=mode,
                provider=provider,
            )
        )

    if problems:
        return [
            _check(
                check_name,
                DiagnosticStatus.FAIL,
                _bounded_problem_message(problems),
            )
        ]

    checks = [
        _check(
            check_name,
            DiagnosticStatus.PASS,
            f"{status} {mode} task artifacts are valid",
        )
    ]
    if status != "completed":
        checks.append(
            _check(
                f"research task {task_name} lifecycle",
                DiagnosticStatus.WARN,
                f"task is valid but {status} and requires operator review",
            )
        )
    for warning in warnings:
        checks.append(
            _check(
                f"research task {task_name} freshness",
                DiagnosticStatus.WARN,
                warning,
            )
        )
    return checks


def _task_filesystem_problems(task_path: Path) -> list[str]:
    """Reject links and special files without following either kind."""

    problems: list[str] = []
    pending = [task_path]
    while pending:
        directory = pending.pop()
        try:
            with os.scandir(directory) as entries:
                children = sorted(entries, key=lambda entry: entry.name)
        except OSError:
            problems.append("task filesystem is inaccessible")
            continue
        for entry in children:
            try:
                metadata = entry.stat(follow_symlinks=False)
            except OSError:
                problems.append("task filesystem contains an unreadable entry")
                continue
            try:
                display = Path(entry.path).relative_to(task_path).as_posix()
            except ValueError:
                display = "unknown"
            safe_display = _safe_name(display)
            if stat.S_ISLNK(metadata.st_mode):
                problems.append(
                    f"task filesystem contains unsafe symlink: {safe_display}"
                )
            elif stat.S_ISDIR(metadata.st_mode):
                pending.append(Path(entry.path))
            elif not stat.S_ISREG(metadata.st_mode):
                problems.append(
                    f"task filesystem contains special file: {safe_display}"
                )
    return problems


def _bounded_problem_message(problems: list[str]) -> str:
    unique: list[str] = []
    for problem in problems:
        safe = str(problem).strip()
        if safe and safe not in unique:
            unique.append(safe)
    visible = unique[:8]
    message = "; ".join(visible)
    if len(unique) > len(visible):
        message += f"; {len(unique) - len(visible)} additional validation issue(s)"
    return message[:1600] or "task validation failed"


def _question_artifact_matches(
    task_path: Path,
    question: str,
    *,
    allow_legacy: bool,
) -> bool:
    artifact = _task_artifact(task_path, "question.md")
    if artifact is None or not artifact.is_file():
        return False
    try:
        raw = artifact.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    prefix = "# Research Question\n\n    "
    if raw.startswith(prefix) and raw.endswith("\n"):
        encoded = raw[len(prefix) : -1]
        if "\n" in encoded:
            return False
        try:
            decoded = json.loads(encoded)
        except json.JSONDecodeError:
            return False
        return (
            isinstance(decoded, str)
            and decoded == question
            and _safe_question_markdown(decoded) == raw
        )
    if allow_legacy:
        text = raw.strip()
        if text.startswith("# Research Question"):
            text = text[len("# Research Question") :].strip()
        return bool(text) and text == question
    return False


def _safe_question_markdown(question: str) -> str:
    encoded = json.dumps(question, ensure_ascii=False, allow_nan=False)
    for character, escape in (
        ("<", r"\u003c"),
        (">", r"\u003e"),
        ("!", r"\u0021"),
        ("[", r"\u005b"),
        ("]", r"\u005d"),
        ("&", r"\u0026"),
    ):
        encoded = encoded.replace(character, escape)
    return f"# Research Question\n\n    {encoded}\n"


def _completed_plan_steps(plan: Mapping[str, Any]) -> tuple[str, ...]:
    steps = plan.get("steps")
    if not isinstance(steps, list):
        return ()
    return tuple(
        str(step.get("id", ""))
        for step in steps
        if isinstance(step, Mapping) and step.get("status") == "completed"
    )


def _plan_problems(
    plan: Mapping[str, Any] | None,
    status: str,
    task: Mapping[str, Any] | None = None,
) -> list[str]:
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
    completed_prefix: list[str] = []
    encountered_incomplete = False
    for identifier, step_status in zip(identifiers, step_statuses):
        if step_status == "completed":
            if encountered_incomplete:
                return ["has a non-prefix completed workflow step"]
            completed_prefix.append(identifier)
        else:
            encountered_incomplete = True

    problems: list[str] = []
    active_status = "running" if status == "running" else "failed"
    if status == "created":
        if any(value != "pending" for value in step_statuses):
            problems.append("has plan state inconsistent with created status")
    elif status in {"running", "failed"}:
        active_indexes = [
            index for index, value in enumerate(step_statuses) if value == active_status
        ]
        if active_indexes != [len(completed_prefix)]:
            problems.append(f"has invalid {active_status} workflow position")
        if any(
            value != "pending"
            for value in step_statuses[len(completed_prefix) + 1 :]
        ):
            problems.append("has non-pending workflow state after the active step")
        forbidden = "failed" if status == "running" else "running"
        if forbidden in step_statuses:
            problems.append(f"has unexpected {forbidden} workflow state")
    elif status == "completed" and any(
        value != "completed" for value in step_statuses
    ):
        problems.append("has incomplete completed workflow state")

    if isinstance(task, Mapping):
        task_completed = task.get("completed_steps")
        if not isinstance(task_completed, list) or task_completed != completed_prefix:
            problems.append("completed-step manifest does not match the plan prefix")
        current_step = task.get("current_step")
        if status in {"created", "completed"}:
            if current_step is not None:
                problems.append("current step is inconsistent with task status")
        else:
            expected_current = (
                identifiers[len(completed_prefix)]
                if len(completed_prefix) < len(identifiers)
                else None
            )
            if current_step != expected_current:
                problems.append("current step does not match the active plan step")
        outcome = task.get("outcome")
        if status in {"created", "running"} and outcome is not None:
            problems.append("task outcome is present before completion")
        if status == "completed" and (
            not isinstance(outcome, Mapping)
            or outcome.get("status") != "completed"
            or outcome.get("report") != "report.md"
        ):
            problems.append("completed task outcome is invalid")
    return problems


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


def _validate_imported_snapshot(
    project_root: Path,
    task_path: Path,
    task: Mapping[str, Any],
) -> tuple[FileProvider | None, list[str]]:
    """Validate an imported snapshot without consulting its mutable origin."""

    record = task.get("input")
    if not isinstance(record, Mapping):
        return None, ["bundle snapshot input record is missing"]
    problems: list[str] = []
    allowed_fields = {"bundle_version", "origin", "sha256", "snapshot"}
    if set(record) not in {frozenset(allowed_fields), frozenset((*allowed_fields, "acquisition_mode"))}:
        problems.append("bundle snapshot input record fields are invalid")
    acquisition_mode = record.get("acquisition_mode", "user_imported")
    if acquisition_mode not in {"user_imported", "official_live"}:
        problems.append("bundle snapshot acquisition mode is invalid")
    if record.get("snapshot") != IMPORTED_BUNDLE_PATH:
        problems.append("bundle snapshot path is invalid")
    expected_hash = record.get("sha256")
    if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(expected_hash):
        problems.append("bundle snapshot hash record is invalid")
    bundle_version = record.get("bundle_version")
    if not isinstance(bundle_version, str) or not bundle_version.strip():
        problems.append("bundle snapshot version is missing")
    origin = record.get("origin")
    if not _safe_relative_metadata(origin):
        problems.append("bundle snapshot origin metadata is unsafe")
    if problems:
        return None, problems

    relative = Path(IMPORTED_BUNDLE_PATH)
    if _relative_path_has_symlink(task_path, relative):
        return None, ["bundle snapshot is missing or unsafe"]
    snapshot = _task_artifact(task_path, IMPORTED_BUNDLE_PATH)
    if snapshot is None or not snapshot.is_file():
        return None, ["bundle snapshot is missing or unsafe"]
    try:
        raw_digest = _sha256(snapshot)
    except OSError:
        return None, ["bundle snapshot is missing or unsafe"]
    if raw_digest != expected_hash:
        return None, ["bundle snapshot hash mismatch"]
    try:
        provider = FileProvider(project_root, snapshot)
    except BundleInputError:
        return None, ["bundle snapshot is unsafe or inaccessible"]
    except BundleValidationError:
        return None, ["bundle schema validation failed for the snapshot"]
    except Exception:
        return None, ["bundle snapshot validation failed safely"]
    if provider.bundle_sha256 != expected_hash:
        return None, ["bundle snapshot canonical hash mismatch"]
    if provider.bundle.get("bundle_version") != bundle_version:
        return None, ["bundle snapshot version disagrees with the task"]
    query = task.get("security_query")
    if not isinstance(query, str) or not query.strip():
        return None, ["imported security query is missing"]
    try:
        provider.identify_security(query)
    except Exception:
        return None, ["imported security query does not resolve to the snapshot"]
    return provider, []


def _safe_relative_metadata(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        return False
    normalized = value.replace("\\", "/")
    relative = Path(normalized)
    return not relative.is_absolute() and ".." not in relative.parts


def _imported_freshness_warnings(provider: FileProvider) -> list[str]:
    sources = provider.bundle.get("sources")
    if not isinstance(sources, list):
        return []
    warnings: list[str] = []
    if any(
        isinstance(source, Mapping)
        and re.search(
            r"(?i)stale|historical",
            str(source.get("freshness", "")),
        )
        for source in sources
    ):
        warnings.append("imported source registry contains historical/stale evidence")

    cutoff = date.today() - timedelta(days=IMPORTED_FRESHNESS_MAX_AGE_DAYS)
    dated_values: list[Any] = [provider.bundle.get("as_of_date")]
    for source in sources:
        if isinstance(source, Mapping):
            dated_values.extend(
                (source.get("as_of_date"), source.get("publication_date"))
            )
    if any(
        isinstance(value, str)
        and (parsed := _iso_date_or_none(value)) is not None
        and parsed < cutoff
        for value in dated_values
    ):
        warnings.append(
            "imported evidence is stale by date (older than the "
            f"{IMPORTED_FRESHNESS_MAX_AGE_DAYS}-day freshness window)"
        )
    return warnings


def _iso_date_or_none(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _imported_state_problems(
    task_path: Path,
    task: Mapping[str, Any],
    provider: FileProvider,
    completed_steps: tuple[str, ...],
    status: str,
) -> list[str]:
    problems = _data_artifact_set_problems(
        task_path,
        task,
        completed_steps,
        status,
    )
    completed = set(completed_steps)
    sources = _read_task_json(task_path, "sources.json")
    expected_sources = {
        "input_mode": "imported",
        "schema_version": "1.0",
        "sources": _deepcopy_json(provider.bundle.get("sources")),
    }
    if "security-identification" in completed:
        if sources != expected_sources:
            problems.append("persisted source registry differs from the bundle registry")
    elif sources != {
        "input_mode": "imported",
        "schema_version": "1.0",
        "sources": [],
    }:
        problems.append("source registry is ahead of the completed-step prefix")

    expected_records, record_error = _expected_imported_provider_records(
        provider,
        str(task.get("security_query", "")),
    )
    if record_error:
        problems.append(record_error)
        return problems
    for operation, relative_path in DATA_OPERATION_PATHS.items():
        required_step = OPERATION_COMPLETION_STEPS[operation]
        if required_step not in completed:
            continue
        actual = _read_task_json(task_path, relative_path)
        if actual != expected_records.get(operation):
            problems.append(
                "persisted provider data differs from the snapshot operation: "
                + relative_path
            )
    return problems


def _deepcopy_json(value: Any) -> Any:
    """Copy JSON-compatible values without exposing mutable Provider state."""

    if isinstance(value, Mapping):
        return {str(key): _deepcopy_json(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_deepcopy_json(child) for child in value]
    return value


def _expected_imported_provider_records(
    provider: FileProvider,
    query: str,
) -> tuple[dict[str, dict[str, Any]], str | None]:
    try:
        identity = provider.identify_security(query)
        security_id = str(identity.get("security_id", ""))
        records = {
            "identify_security": identity,
            "get_source_metadata": provider.get_source_metadata(security_id),
            "get_security_profile": provider.get_security_profile(security_id),
            "get_financial_statements": provider.get_financial_statements(security_id),
            "get_price_history": provider.get_price_history(security_id),
            "get_valuation_inputs": provider.get_valuation_inputs(security_id),
            "get_peer_comparables": provider.get_peer_comparables(security_id),
            "get_earnings_history": provider.get_earnings_history(security_id),
            "get_catalyst_events": provider.get_catalyst_events(security_id),
        }
    except Exception:
        return {}, "provider data could not be reconstructed from the snapshot"
    return {name: dict(value) for name, value in records.items()}, None


def _expected_data_paths(completed_steps: tuple[str, ...]) -> set[str]:
    completed = set(completed_steps)
    return {
        path
        for operation, path in DATA_OPERATION_PATHS.items()
        if OPERATION_COMPLETION_STEPS[operation] in completed
    }


def _data_artifact_set_problems(
    task_path: Path,
    task: Mapping[str, Any],
    completed_steps: tuple[str, ...],
    status: str,
) -> list[str]:
    expected = _expected_data_paths(completed_steps)
    problems: list[str] = []
    if _relative_path_has_symlink(task_path, Path("data")):
        return ["data directory is an unsafe symlink"]
    resolved = _task_artifact(task_path, "data")
    if resolved is None or not resolved.is_dir():
        return ["data directory is missing or unsafe"]
    actual: set[str] = set()
    try:
        entries = sorted((task_path / "data").iterdir(), key=lambda path: path.name)
    except OSError:
        return ["data directory is inaccessible"]
    for entry in entries:
        display = _safe_name(entry.name)
        if entry.is_symlink() or not entry.is_file() or entry.suffix != ".json":
            problems.append(f"data artifact is unsafe or unexpected: {display}")
            continue
        actual.add(f"data/{entry.name}")
    if actual != expected:
        problems.append("data artifacts do not equal the completed-step prefix")
    task_data = task.get("data")
    if status == "completed":
        if (
            not isinstance(task_data, list)
            or len(task_data) != len(expected)
            or set(task_data) != expected
        ):
            problems.append("completed task data manifest is incomplete or unexpected")
    elif task_data != []:
        problems.append("incomplete task data manifest must remain empty")
    return problems


def _read_capability_values(task_path: Path) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    if _relative_path_has_symlink(task_path, Path("capabilities")):
        return values
    root = _task_artifact(task_path, "capabilities")
    if root is None or not root.is_dir():
        return values
    try:
        entries = sorted((task_path / "capabilities").iterdir())
    except OSError:
        return values
    for entry in entries:
        if entry.is_symlink() or not entry.is_file() or entry.suffix != ".json":
            continue
        if entry.stem not in EXPECTED_WORKFLOW_STEPS:
            continue
        value = _read_task_json(task_path, f"capabilities/{entry.name}")
        if value is not None:
            values[entry.stem] = value
    return values


def _imported_capability_problems(
    capability_values: Mapping[str, Mapping[str, Any]],
    provider: FileProvider,
) -> list[str]:
    source_values = provider.bundle.get("sources")
    known_ids = {
        str(source.get("source_id"))
        for source in source_values
        if isinstance(source, Mapping) and source.get("source_id")
    } if isinstance(source_values, list) else set()
    operation_sources = provider.bundle.get("operations")
    relevant_operations = {
        "security-identification": ("identify_security",),
        "company-deep-research": ("get_security_profile",),
        "business-model-analysis": ("get_security_profile",),
        "financial-statement-analysis": ("get_financial_statements",),
        "earnings-quality-analysis": ("get_financial_statements",),
        "valuation-analysis": ("get_valuation_inputs", "get_price_history"),
        "comps-analysis": ("get_peer_comparables",),
        "earnings-analysis": ("get_earnings_history",),
        "catalyst-analysis": ("get_catalyst_events",),
    }
    problems: list[str] = []
    for capability, value in capability_values.items():
        method = value.get("method")
        if not isinstance(method, Mapping) or method.get("input_mode") != "imported":
            problems.append(f"capability method lacks imported mode: {capability}")
        referenced = {
            str(source_id) for source_id in value.get("source_ids", [])
        } if isinstance(value.get("source_ids"), list) else set()
        if not referenced.issubset(known_ids):
            problems.append(f"capability has unresolved source IDs: {capability}")
        for field in ("facts", "findings", "risks"):
            records = value.get(field)
            if not isinstance(records, list):
                continue
            for record in records:
                if not isinstance(record, Mapping):
                    continue
                record_ids = {
                    str(source_id) for source_id in record.get("source_ids", [])
                } if isinstance(record.get("source_ids"), list) else set()
                if not record_ids.issubset(known_ids):
                    problems.append(
                        f"capability record has unresolved source IDs: {capability}"
                    )
        operation_names = relevant_operations.get(capability)
        if operation_names and isinstance(operation_sources, Mapping):
            allowed: set[str] = set()
            for operation_name in operation_names:
                operation = operation_sources.get(operation_name)
                if isinstance(operation, Mapping) and isinstance(
                    operation.get("source_ids"), list
                ):
                    allowed.update(str(value) for value in operation["source_ids"])
            if not referenced.issubset(allowed):
                problems.append(
                    f"capability uses sources outside its operation evidence: {capability}"
                )
    return problems


def _aggregate_artifact_problems(
    task_path: Path,
    *,
    mode: str,
    legacy: bool,
    capability_values: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    assumptions = _read_task_json(task_path, "assumptions.json")
    findings = _read_task_json(task_path, "findings.json")
    risks = _read_task_json(task_path, "risks.json")
    if (
        not isinstance(assumptions, Mapping)
        or not isinstance(findings, Mapping)
        or not isinstance(risks, Mapping)
    ):
        return ["aggregate artifacts are missing, unsafe, or corrupt"]
    values = (assumptions, findings, risks)
    problems: list[str] = []
    for value in values:
        artifact_mode = value.get("input_mode")
        if legacy:
            if artifact_mode not in {None, "demo"}:
                problems.append("legacy aggregate artifact has an invalid mode")
        elif artifact_mode != mode:
            problems.append("aggregate artifact input mode disagrees with the task")
        if value.get("schema_version") != "1.0":
            problems.append("aggregate artifact schema version is invalid")

    expected_findings: list[dict[str, Any]] = []
    expected_assumptions: list[dict[str, Any]] = []
    expected_risks: list[dict[str, Any]] = []
    expected_unknowns: list[dict[str, Any]] = []
    expected_warnings: list[str] = []
    expected_index: dict[str, dict[str, Any]] = {}
    for capability in EXPECTED_WORKFLOW_STEPS:
        result = capability_values.get(capability)
        if not isinstance(result, Mapping):
            continue
        expected_index[capability] = {
            "artifact": f"capabilities/{capability}.json",
            "status": result.get("status"),
        }
        for field, destination in (
            ("findings", expected_findings),
            ("assumptions", expected_assumptions),
            ("risks", expected_risks),
            ("unknowns", expected_unknowns),
        ):
            records = result.get(field)
            if not isinstance(records, list):
                problems.append(f"capability aggregate records are invalid: {capability}")
                continue
            for record in records:
                if isinstance(record, Mapping):
                    destination.append({"capability": capability, **dict(record)})
        warnings = result.get("warnings")
        if isinstance(warnings, list):
            for warning in warnings:
                text = str(warning).strip()
                if text and text not in expected_warnings:
                    expected_warnings.append(text)

    if findings.get("capabilities") != expected_index:
        problems.append("findings capability index differs from persisted capabilities")
    if findings.get("findings") != expected_findings:
        problems.append("findings aggregate differs from persisted capabilities")
    if assumptions.get("assumptions") != expected_assumptions:
        problems.append("assumptions aggregate differs from persisted capabilities")
    if risks.get("risks") != expected_risks:
        problems.append("risks aggregate differs from persisted capabilities")
    if risks.get("unknowns") != expected_unknowns:
        problems.append("unknowns aggregate differs from persisted capabilities")
    if risks.get("warnings") != expected_warnings:
        problems.append("warnings aggregate differs from persisted capabilities")
    return problems


def _report_mode_problems(
    task_path: Path,
    task: Mapping[str, Any],
    *,
    mode: str,
    provider: FileProvider | None,
) -> list[str]:
    artifact = _task_artifact(task_path, "report.md")
    if artifact is None or not artifact.is_file():
        return ["report is missing or unsafe"]
    try:
        report = artifact.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ["report is corrupt"]
    lower = report.casefold()
    comparable = lower.replace("\\", "")
    problems: list[str] = []
    if REPORT_INJECTION_RE.search(report):
        problems.append("report contains unsafe markup or link injection")
    if RESTRICTED_LANGUAGE_RE.search(report) or IMPORTED_REPORT_RESTRICTED_RE.search(
        report
    ):
        problems.append("report contains action or return-promise language")
    if mode == "imported":
        input_record = task.get("input")
        official_live = (
            isinstance(input_record, Mapping)
            and input_record.get("acquisition_mode") == "official_live"
        )
        if official_live:
            if (
                "## official live data declaration" not in lower
                or "## imported data declaration" in lower
                or "## demo data declaration" in lower
                or "fictional" in lower
                or "aurora lantern" in lower
            ):
                problems.append("report mode is inconsistent with official live data")
            declaration = _markdown_section(report, "Official Live Data Declaration")
            disclosure = declaration.casefold()
            if (
                "official public sources" not in disclosure
                or "does not guarantee completeness" not in disclosure
            ):
                problems.append("report disclosure is incomplete for official live data")
        else:
            if (
                "## imported data declaration" not in lower
                or "## official live data declaration" in lower
                or "## demo data declaration" in lower
                or "fictional" in lower
                or "aurora lantern" in lower
            ):
                problems.append("report mode is inconsistent with imported data")
            declaration = _markdown_section(report, "Imported Data Declaration")
            independently_disclosed = bool(
                re.search(
                    r"not independently[^\n]{0,120}(?:guarantee|verify)",
                    declaration.casefold(),
                )
            )
            if "user-supplied" not in declaration.casefold() or not independently_disclosed:
                problems.append("report disclosure is incomplete for imported data")
        if provider is None:
            problems.append("report provenance cannot be checked without a valid bundle")
        else:
            security = provider.bundle.get("security")
            input_record = task.get("input")
            required_values: list[str] = []
            if isinstance(security, Mapping):
                required_values.extend(
                    str(security.get(field, ""))
                    for field in ("legal_name", "ticker", "security_id")
                )
            required_values.extend(
                [
                    str(task.get("question", "")),
                    str(provider.bundle.get("as_of_date", "")),
                    str(provider.bundle.get("bundle_version", "")),
                    str(input_record.get("sha256", ""))
                    if isinstance(input_record, Mapping)
                    else "",
                ]
            )
            for value in required_values:
                normalized = " ".join(value.split()).casefold().replace("\\", "")
                if not normalized or normalized not in comparable:
                    problems.append("report identity or persisted provenance is incomplete")
                    break
    else:
        if (
            "## demo data declaration" not in lower
            or "fictional" not in lower
            or "## imported data declaration" in lower
        ):
            problems.append("report mode is inconsistent with demo data")
    return problems


def _markdown_section(report: str, title: str) -> str:
    marker = f"## {title}"
    start = report.find(marker)
    if start < 0:
        return ""
    content_start = start + len(marker)
    end = report.find("\n## ", content_start)
    return report[content_start:] if end < 0 else report[content_start:end]


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
            if capability == "bear-case-analysis":
                thesis = values.get("investment-thesis")
                if isinstance(thesis, Mapping) and thesis.get("status") != "completed":
                    continue
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
    if task.get("input_mode", "demo") == "imported":
        expected_paths.add(IMPORTED_BUNDLE_PATH)
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
        value = _read_strict_json(artifact)
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        OverflowError,
        RecursionError,
        TypeError,
        ValueError,
    ):
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
        value = _read_strict_json(path)
    except FileNotFoundError:
        return {}, f"{relative_path} is missing"
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        OverflowError,
        RecursionError,
        RuntimeError,
        TypeError,
        ValueError,
    ):
        return {}, f"{relative_path} is corrupt or invalid"
    if not isinstance(value, dict):
        return {}, f"{relative_path} must contain a JSON object"
    return value, None


def _read_strict_json(path: Path) -> Any:
    payload = _read_regular_bytes(path, MAX_OWNED_JSON_BYTES)
    text = payload.decode("utf-8", errors="strict")
    return _strict_json_loads(text)


def _read_regular_bytes(path: Path, max_bytes: int) -> bytes:
    """Read one bounded regular file while refusing a symlink leaf."""

    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > max_bytes:
        raise ValueError("owned state is not a bounded regular file")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_size > max_bytes
            or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
        ):
            raise ValueError("owned state changed during inspection")
        chunks: list[bytes] = []
        remaining = max_bytes + 1
        while remaining:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > max_bytes:
            raise ValueError("owned state exceeds its size limit")
        return payload
    finally:
        os.close(descriptor)


def _strict_json_loads(text: str) -> Any:
    return json.loads(
        text,
        object_pairs_hook=_unique_json_object,
        parse_constant=_reject_json_constant,
        parse_float=_finite_json_float,
    )


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _reject_json_constant(_value: str) -> Any:
    raise ValueError("non-finite JSON constant is forbidden")


def _finite_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("non-finite JSON number is forbidden")
    return parsed


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
            if contains_sensitive_key(key) and child not in (None, "", [], {}):
                return True
            if _contains_sensitive(child):
                return True
        return False
    if isinstance(value, (list, tuple)):
        return any(_contains_sensitive(child) for child in value)
    return contains_sensitive_value(value)


def _check(
    name: str,
    status: DiagnosticStatus,
    message: str,
) -> DiagnosticCheck:
    return DiagnosticCheck(name=name, status=status, message=message)


def _safe_name(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]", "?", value)
    return sanitized[:96] or "unknown"
