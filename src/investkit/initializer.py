"""Idempotent, create-once InvestKit project initialization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any, NoReturn

from . import __version__
from .assets import (
    CORE_SKILLS,
    REQUIRED_SPECS,
    SPEC_VERSION_RE,
    SOURCE_DIRECTORIES,
    complete_source_root,
    default_source_root,
    discover_skill_files,
    source_directories,
    source_file,
)
from .errors import AssetValidationError, InvestKitError, safe_error_message
from .filesystem import (
    AtomicReplacement,
    commit_atomic_replacement,
    create_once,
    discard_atomic_replacement,
    resolve_within,
    resolved_root,
    stable_json_bytes,
    stage_atomic_replacement,
)
from .models import FileAction, InitializationResult
from .platforms.codex import CodexAdapter
from .security import contains_sensitive_key, contains_sensitive_value


_LEGACY_VERSION = "0.2.0"
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+(?:\.[0-9]+)?$")
_CURRENT_MIGRATION_RE = re.compile(r"^0\.3\.[0-9]+$")
# Release-pinned digests authenticate the two v0.2 ownership ledgers without
# depending on installation-specific fields such as source_root or timestamp.
# A manifest-provided per-file digest is not itself a trust anchor: an attacker
# who changes an owned file could otherwise update that digest in lockstep.
_LEGACY_MAPPING_LEDGER_SHA256 = (
    "f4b435bd8508c9da1b036e817ebcc0ed761af3ae7be0b060510d6a8e85023595"
)
_LEGACY_SPEC_LEDGER_SHA256 = (
    "db8ece84dfa2c91445b32319315b99ab9aa7fca52451c34c4c829ac61f52aac3"
)
_MAX_MACHINE_STATE_BYTES = 2 * 1024 * 1024
_MAX_MANAGED_FILE_BYTES = 8 * 1024 * 1024
_LEGACY_SKILL_FILES = (
    Path("SKILL.md"),
    Path("agents/openai.yaml"),
    Path("references/method-contract.md"),
    Path("references/trigger-evals.json"),
)
_MANIFEST_KEYS = frozenset(
    {
        "host_platform",
        "initialized_at",
        "installation_target",
        "investkit_version",
        "managed_by",
        "mappings",
        "schema_version",
        "source_directories",
        "source_root",
        "specs",
        "workspace_path",
    }
)
_MAPPING_KEYS = frozenset(
    {"kind", "source", "source_sha256", "target", "target_sha256"}
)
_SPEC_KEYS = frozenset({"path", "sha256", "version"})


@dataclass(frozen=True)
class _SkillAsset:
    source: str
    target: str
    content: bytes
    sha256: str


@dataclass(frozen=True)
class _DesiredState:
    skills: tuple[_SkillAsset, ...]
    config: bytes
    manifest: bytes
    adapter: bytes


@dataclass(frozen=True)
class _ProjectState:
    kind: str
    config_bytes: bytes | None = None
    config: dict[str, Any] | None = None
    manifest_bytes: bytes | None = None
    manifest: dict[str, Any] | None = None


@dataclass(frozen=True)
class _ReplacementPlan:
    path: str
    content: bytes
    expected_sha256: frozenset[str]
    allow_missing: bool


class _MigrationRejected(Exception):
    def __init__(self, actions: tuple[FileAction, ...]) -> None:
        super().__init__("safe initialization migration rejected")
        self.actions = actions


def initialize_project(
    project_root: str | Path,
    *,
    source_root: str | Path | None = None,
) -> InitializationResult:
    """Initialize a Codex project without overwriting any existing file."""

    try:
        return _initialize_project(project_root, source_root)
    except _MigrationRejected as error:
        return InitializationResult(exit_code=1, actions=error.actions)
    except (InvestKitError, OSError, UnicodeError, json.JSONDecodeError) as error:
        return InitializationResult(
            exit_code=1,
            actions=(FileAction("WARN", ".investkit", _bounded_message(error)),),
        )


def _initialize_project(
    project_root: str | Path,
    source_root: str | Path | None,
) -> InitializationResult:
    project = resolved_root(project_root)
    adapter = CodexAdapter()
    environment = adapter.describe(project)
    if not adapter.detect_project(project):
        agents_state = str(environment.get("agents_path_state", "unknown"))
        target_state = str(environment.get("target_path_state", "unknown"))
        return InitializationResult(
            exit_code=1,
            actions=(
                FileAction(
                    "WARN",
                    ".agents",
                    "Codex project environment is unsafe or occupied "
                    f"(agents={agents_state}, target={target_state}); preserved",
                ),
            ),
        )
    source = (
        default_source_root()
        if source_root is None
        else complete_source_root(source_root)
    )
    skill_assets: list[_SkillAsset] = []
    for skill_name in CORE_SKILLS:
        skill_root = source / "skills" / skill_name
        for path in discover_skill_files(source, skill_name):
            content = path.read_bytes()
            relative = path.relative_to(skill_root)
            skill_assets.append(
                _SkillAsset(
                    source=path.relative_to(source).as_posix(),
                    target=(
                        Path(adapter.installation_target) / skill_name / relative
                    ).as_posix(),
                    content=content,
                    sha256=hashlib.sha256(content).hexdigest(),
                )
            )

    spec_records = _spec_records(source)
    workspace_readme = source_file(
        source, Path("workspace-template") / "README.md"
    ).read_bytes()
    project_state = _classify_project_state(project)
    if project_state.kind == "fresh":
        initialized_at = _utc_now()
    else:
        state_document = (
            project_state.manifest
            if project_state.kind == "migration"
            else project_state.config
        )
        initialized_at = _validated_initialized_at(state_document)

    desired = _desired_state(
        adapter=adapter,
        source=source,
        source_directory_records=source_directories(source),
        initialized_at=initialized_at,
        skill_assets=tuple(skill_assets),
        spec_records=spec_records,
    )
    if project_state.kind == "migration":
        assert project_state.config_bytes is not None
        assert project_state.config is not None
        assert project_state.manifest_bytes is not None
        assert project_state.manifest is not None
        return _migrate_project(
            project,
            adapter,
            desired,
            project_state,
        )
    return _create_once_initialization(
        project,
        adapter,
        desired,
        workspace_readme,
        preserve_existing_workspace=project_state.kind == "current",
    )


def _desired_state(
    *,
    adapter: CodexAdapter,
    source: Path,
    source_directory_records: dict[str, str],
    initialized_at: str,
    skill_assets: tuple[_SkillAsset, ...],
    spec_records: list[dict[str, str]],
) -> _DesiredState:
    mappings = [
        {
            "kind": "skill",
            "source": asset.source,
            "source_sha256": asset.sha256,
            "target": asset.target,
            "target_sha256": asset.sha256,
        }
        for asset in skill_assets
    ]
    config = {
        "host_platform": adapter.name,
        "initialized_at": initialized_at,
        "installation_target": adapter.installation_target,
        "installed_skills": list(CORE_SKILLS),
        "investkit_version": __version__,
        "managed_by": "investkit",
        "manifest_path": ".investkit/install-manifest.json",
        "schema_version": "1.0",
        "source_directories": source_directory_records,
        "source_root": str(source),
        "workspace_path": "workspace",
    }
    manifest = {
        "host_platform": adapter.name,
        "initialized_at": initialized_at,
        "installation_target": adapter.installation_target,
        "investkit_version": __version__,
        "managed_by": "investkit",
        "mappings": mappings,
        "schema_version": "1.0",
        "source_directories": source_directory_records,
        "source_root": str(source),
        "specs": spec_records,
        "workspace_path": "workspace",
    }
    return _DesiredState(
        skills=skill_assets,
        config=stable_json_bytes(config),
        manifest=stable_json_bytes(manifest),
        adapter=stable_json_bytes(adapter.configuration(list(CORE_SKILLS))),
    )


def _create_once_initialization(
    project: Path,
    adapter: CodexAdapter,
    desired: _DesiredState,
    workspace_readme: bytes,
    *,
    preserve_existing_workspace: bool,
) -> InitializationResult:
    actions = [
        create_once(project, asset.target, asset.content)
        for asset in desired.skills
    ]
    workspace_readme_path = resolve_within(project, "workspace/README.md")
    if preserve_existing_workspace and workspace_readme_path.is_file():
        actions.append(
            FileAction(
                "SKIP",
                "workspace/README.md",
                "durable user workspace preserved",
            )
        )
    else:
        actions.append(create_once(project, "workspace/README.md", workspace_readme))
    research_path = resolve_within(project, "workspace/research")
    if research_path.exists() and not research_path.is_dir():
        actions.append(
            FileAction(
                "WARN",
                "workspace/research",
                "path exists and is not a directory; preserved",
            )
        )
    elif research_path.is_dir():
        actions.append(FileAction("SKIP", "workspace/research", "directory exists"))
    else:
        research_path.mkdir(parents=True)
        actions.append(FileAction("CREATE", "workspace/research", "created"))
    if any(action.action == "WARN" for action in actions):
        return InitializationResult(exit_code=1, actions=tuple(actions))

    actions.extend(
        (
            create_once(project, adapter.configuration_path, desired.adapter),
            create_once(project, ".investkit/config.json", desired.config),
        )
    )
    if any(action.action == "WARN" for action in actions):
        return InitializationResult(exit_code=1, actions=tuple(actions))
    actions.append(
        create_once(
            project,
            ".investkit/install-manifest.json",
            desired.manifest,
        )
    )
    return InitializationResult(
        exit_code=int(any(action.action == "WARN" for action in actions)),
        actions=tuple(actions),
    )


def _classify_project_state(project: Path) -> _ProjectState:
    investkit_directory = resolve_within(project, ".investkit")
    if investkit_directory.exists() and not investkit_directory.is_dir():
        _reject(
            ".investkit",
            "InvestKit machine-state directory is unsafe; migration not started",
        )
    config_result = _read_machine_json(
        project, ".investkit/config.json", missing_ok=True
    )
    manifest_result = _read_machine_json(
        project, ".investkit/install-manifest.json", missing_ok=True
    )
    if config_result is None and manifest_result is None:
        return _ProjectState(kind="fresh")
    if config_result is None:
        _reject(
            ".investkit/config.json",
            "incomplete InvestKit version state; migration not started",
        )
    if manifest_result is None:
        _reject(
            ".investkit/install-manifest.json",
            "incomplete InvestKit version state; migration not started",
        )
    assert config_result is not None
    assert manifest_result is not None
    config_bytes, config = config_result
    manifest_bytes, manifest = manifest_result
    config_version = config.get("investkit_version")
    manifest_version = manifest.get("investkit_version")
    if not isinstance(config_version, str) or not isinstance(manifest_version, str):
        _reject(
            ".investkit",
            "invalid InvestKit version state; migration not started",
        )
    if config_version == __version__ and manifest_version == __version__:
        return _ProjectState(
            kind="current",
            config_bytes=config_bytes,
            config=config,
            manifest_bytes=manifest_bytes,
            manifest=manifest,
        )
    if (
        _CURRENT_MIGRATION_RE.fullmatch(__version__)
        and manifest_version == _LEGACY_VERSION
        and config_version in {_LEGACY_VERSION, __version__}
    ):
        return _ProjectState(
            kind="migration",
            config_bytes=config_bytes,
            config=config,
            manifest_bytes=manifest_bytes,
            manifest=manifest,
        )
    _reject(
        ".investkit",
        "unsupported or mixed InvestKit version state; migration not started",
    )


def _migrate_project(
    project: Path,
    adapter: CodexAdapter,
    desired: _DesiredState,
    project_state: _ProjectState,
) -> InitializationResult:
    assert project_state.config_bytes is not None
    assert project_state.manifest_bytes is not None
    assert project_state.manifest is not None
    old_hashes, old_config = _validated_legacy_ledger(
        project_state.manifest_bytes,
        project_state.manifest,
        adapter,
    )
    conflicts: list[FileAction] = []
    plans: list[_ReplacementPlan] = []
    actions: list[FileAction] = []
    desired_by_target = {asset.target: asset for asset in desired.skills}

    for legacy_target in old_hashes:
        if legacy_target not in desired_by_target:
            _reject(
                ".investkit/install-manifest.json",
                "legacy ownership ledger is incompatible; migration not started",
            )

    for asset in desired.skills:
        legacy_digest = old_hashes.get(asset.target)
        try:
            current = _read_owned_regular(
                project,
                asset.target,
                missing_ok=legacy_digest is None,
                byte_limit=_MAX_MANAGED_FILE_BYTES,
            )
        except _MigrationRejected as error:
            conflicts.extend(error.actions)
            continue
        if current is None:
            plans.append(
                _ReplacementPlan(
                    path=asset.target,
                    content=asset.content,
                    expected_sha256=frozenset(),
                    allow_missing=True,
                )
            )
            actions.append(FileAction("CREATE", asset.target, "migration staged"))
            continue
        current_digest = hashlib.sha256(current).hexdigest()
        allowed = {asset.sha256}
        if legacy_digest is not None:
            allowed.add(legacy_digest)
        if current_digest not in allowed:
            conflicts.append(
                FileAction(
                    "WARN",
                    asset.target,
                    "managed file changed outside InvestKit; preserved",
                )
            )
        elif current == asset.content:
            actions.append(
                FileAction("SKIP", asset.target, "exact current file exists")
            )
        else:
            plans.append(
                _ReplacementPlan(
                    path=asset.target,
                    content=asset.content,
                    expected_sha256=frozenset(allowed),
                    allow_missing=False,
                )
            )
            actions.append(FileAction("UPDATE", asset.target, "migration staged"))

    adapter_result: tuple[bytes, dict[str, Any]] | None
    try:
        adapter_result = _read_machine_json(
            project,
            adapter.configuration_path,
            missing_ok=False,
        )
    except _MigrationRejected as error:
        conflicts.extend(error.actions)
        adapter_result = None
    if adapter_result is not None:
        adapter_bytes, _ = adapter_result
        old_adapter = _legacy_adapter_bytes(adapter)
        if adapter_bytes not in {old_adapter, desired.adapter}:
            conflicts.append(
                FileAction(
                    "WARN",
                    adapter.configuration_path,
                    "Codex adapter configuration changed; preserved",
                )
            )
        elif adapter_bytes == desired.adapter:
            actions.append(
                FileAction(
                    "SKIP",
                    adapter.configuration_path,
                    "exact adapter configuration exists",
                )
            )
        else:
            plans.append(
                _ReplacementPlan(
                    path=adapter.configuration_path,
                    content=desired.adapter,
                    expected_sha256=frozenset(
                        {
                            hashlib.sha256(old_adapter).hexdigest(),
                            hashlib.sha256(desired.adapter).hexdigest(),
                        }
                    ),
                    allow_missing=False,
                )
            )
            actions.append(
                FileAction(
                    "UPDATE",
                    adapter.configuration_path,
                    "migration staged",
                )
            )

    config_allowed = frozenset(
        {
            hashlib.sha256(old_config).hexdigest(),
            hashlib.sha256(desired.config).hexdigest(),
        }
    )
    if project_state.config_bytes not in {old_config, desired.config}:
        conflicts.append(
            FileAction(
                "WARN",
                ".investkit/config.json",
                "InvestKit configuration changed; preserved",
            )
        )
    elif project_state.config_bytes == desired.config:
        actions.append(
            FileAction("SKIP", ".investkit/config.json", "exact current config exists")
        )
    else:
        plans.append(
            _ReplacementPlan(
                path=".investkit/config.json",
                content=desired.config,
                expected_sha256=config_allowed,
                allow_missing=False,
            )
        )
        actions.append(
            FileAction("UPDATE", ".investkit/config.json", "migration staged")
        )

    if conflicts:
        return InitializationResult(exit_code=1, actions=tuple(conflicts))

    old_manifest_digest = hashlib.sha256(project_state.manifest_bytes).hexdigest()
    plans.append(
        _ReplacementPlan(
            path=".investkit/install-manifest.json",
            content=desired.manifest,
            expected_sha256=frozenset({old_manifest_digest}),
            allow_missing=False,
        )
    )
    actions.append(
        FileAction(
            "UPDATE",
            ".investkit/install-manifest.json",
            "migration committed",
        )
    )
    _commit_replacement_plans(project, plans)
    return InitializationResult(exit_code=0, actions=tuple(actions))


def _validated_legacy_ledger(
    manifest_bytes: bytes,
    manifest: dict[str, Any],
    adapter: CodexAdapter,
) -> tuple[dict[str, str], bytes]:
    if set(manifest) != _MANIFEST_KEYS:
        _reject_manifest()
    fixed_values = {
        "host_platform": adapter.name,
        "installation_target": adapter.installation_target,
        "investkit_version": _LEGACY_VERSION,
        "managed_by": "investkit",
        "schema_version": "1.0",
        "workspace_path": "workspace",
    }
    if any(manifest.get(key) != value for key, value in fixed_values.items()):
        _reject_manifest()
    initialized_at = manifest.get("initialized_at")
    source_root = manifest.get("source_root")
    source_directory_records = manifest.get("source_directories")
    if (
        not isinstance(initialized_at, str)
        or not _is_utc_timestamp(initialized_at)
        or not isinstance(source_root, str)
        or not source_root
        or len(source_root) > 4096
        or not source_root.isprintable()
        or not _valid_legacy_source_directories(source_directory_records)
    ):
        _reject_manifest()

    mappings = manifest.get("mappings")
    if not isinstance(mappings, list):
        _reject_manifest()
    expected_path_order = [
        (
            (Path("skills") / skill / relative).as_posix(),
            (Path(adapter.installation_target) / skill / relative).as_posix(),
        )
        for skill in CORE_SKILLS
        for relative in _LEGACY_SKILL_FILES
    ]
    expected_paths = set(expected_path_order)
    old_hashes: dict[str, str] = {}
    seen_sources: set[str] = set()
    observed_paths: list[tuple[str, str]] = []
    if len(mappings) != len(expected_paths):
        _reject_manifest()
    for record in mappings:
        if not isinstance(record, dict) or set(record) != _MAPPING_KEYS:
            _reject_manifest()
        source_path = record.get("source")
        target_path = record.get("target")
        source_digest = record.get("source_sha256")
        target_digest = record.get("target_sha256")
        if (
            record.get("kind") != "skill"
            or not isinstance(source_path, str)
            or not isinstance(target_path, str)
            or (source_path, target_path) not in expected_paths
            or source_path in seen_sources
            or not isinstance(source_digest, str)
            or not isinstance(target_digest, str)
            or not _HASH_RE.fullmatch(source_digest)
            or source_digest != target_digest
        ):
            _reject_manifest()
        seen_sources.add(source_path)
        old_hashes[target_path] = target_digest
        observed_paths.append((source_path, target_path))
    if (
        observed_paths != expected_path_order
        or seen_sources != {source for source, _ in expected_paths}
        or _ledger_sha256(mappings) != _LEGACY_MAPPING_LEDGER_SHA256
    ):
        _reject_manifest()

    specs = manifest.get("specs")
    if not isinstance(specs, list) or len(specs) != len(REQUIRED_SPECS):
        _reject_manifest()
    expected_specs = {f"specs/{name}" for name in REQUIRED_SPECS}
    seen_specs: set[str] = set()
    observed_specs: list[str] = []
    for record in specs:
        if not isinstance(record, dict) or set(record) != _SPEC_KEYS:
            _reject_manifest()
        path = record.get("path")
        digest = record.get("sha256")
        version = record.get("version")
        if (
            not isinstance(path, str)
            or path not in expected_specs
            or path in seen_specs
            or not isinstance(digest, str)
            or not _HASH_RE.fullmatch(digest)
            or not isinstance(version, str)
            or not _VERSION_RE.fullmatch(version)
        ):
            _reject_manifest()
        seen_specs.add(path)
        observed_specs.append(path)
    if (
        observed_specs != [f"specs/{name}" for name in REQUIRED_SPECS]
        or seen_specs != expected_specs
        or _ledger_sha256(specs) != _LEGACY_SPEC_LEDGER_SHA256
        or stable_json_bytes(manifest) != manifest_bytes
    ):
        _reject_manifest()

    old_config = stable_json_bytes(
        {
            "host_platform": adapter.name,
            "initialized_at": initialized_at,
            "installation_target": adapter.installation_target,
            "installed_skills": list(CORE_SKILLS),
            "investkit_version": _LEGACY_VERSION,
            "managed_by": "investkit",
            "manifest_path": ".investkit/install-manifest.json",
            "schema_version": "1.0",
            "source_directories": source_directory_records,
            "source_root": source_root,
            "workspace_path": "workspace",
        }
    )
    return old_hashes, old_config


def _ledger_sha256(records: list[Any]) -> str:
    return hashlib.sha256(stable_json_bytes(records)).hexdigest()


def _legacy_adapter_bytes(adapter: CodexAdapter) -> bytes:
    return stable_json_bytes(
        {
            "host_platform": adapter.name,
            "installation_target": adapter.installation_target,
            "installed_skills": list(CORE_SKILLS),
            "managed_by": "investkit",
            "schema_version": "1.0",
        }
    )


def _valid_legacy_source_directories(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    allowed = set(SOURCE_DIRECTORIES)
    required = {
        "skills",
        "agents",
        "workflows",
        "specs",
        "packages",
        "workspace-template",
        "fixtures",
    }
    return (
        required.issubset(value)
        and set(value).issubset(allowed)
        and all(isinstance(key, str) and item == key for key, item in value.items())
    )


def _commit_replacement_plans(
    project: Path, plans: list[_ReplacementPlan]
) -> None:
    staged: list[tuple[_ReplacementPlan, AtomicReplacement]] = []
    try:
        for plan in plans:
            replacement = stage_atomic_replacement(
                project,
                plan.path,
                plan.content,
                expected_existing_sha256=plan.expected_sha256,
                allow_missing=plan.allow_missing,
            )
            staged.append((plan, replacement))
    except BaseException:
        for _, replacement in staged:
            discard_atomic_replacement(replacement)
        raise

    try:
        for _, replacement in staged:
            commit_atomic_replacement(replacement)
    finally:
        for _, replacement in staged:
            discard_atomic_replacement(replacement)


def _read_machine_json(
    project: Path,
    relative_path: str,
    *,
    missing_ok: bool,
) -> tuple[bytes, dict[str, Any]] | None:
    content = _read_owned_regular(
        project,
        relative_path,
        missing_ok=missing_ok,
        byte_limit=_MAX_MACHINE_STATE_BYTES,
    )
    if content is None:
        return None
    try:
        text = content.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError, RecursionError):
        _reject(relative_path, "invalid or unsafe machine state; preserved")
    if not isinstance(value, dict) or _contains_secret_like(value):
        _reject(relative_path, "invalid or unsafe machine state; preserved")
    return content, value


def _read_owned_regular(
    project: Path,
    relative_path: str,
    *,
    missing_ok: bool,
    byte_limit: int,
) -> bytes | None:
    try:
        path = resolve_within(project, relative_path)
    except (InvestKitError, OSError):
        _reject(relative_path, "unsafe managed path; preserved")
    try:
        path_stat = os.lstat(path)
    except FileNotFoundError:
        if missing_ok:
            return None
        _reject(relative_path, "required managed file is missing; migration not started")
    except OSError:
        _reject(relative_path, "unsafe managed path; preserved")
    if not stat.S_ISREG(path_stat.st_mode) or path_stat.st_size > byte_limit:
        _reject(relative_path, "managed path is not a bounded regular file; preserved")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError:
        if missing_ok:
            return None
        _reject(relative_path, "required managed file is missing; migration not started")
    except OSError:
        _reject(relative_path, "unsafe managed path; preserved")
    try:
        file_stat = os.fstat(descriptor)
        if not stat.S_ISREG(file_stat.st_mode) or file_stat.st_size > byte_limit:
            _reject(relative_path, "managed path is not a bounded regular file; preserved")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(128 * 1024, byte_limit + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > byte_limit:
                _reject(relative_path, "managed file exceeds the safe size limit; preserved")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> NoReturn:
    raise ValueError("non-standard JSON constant")


def _contains_secret_like(value: Any) -> bool:
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                if contains_sensitive_key(key):
                    return True
                pending.append(item)
        elif isinstance(current, list):
            pending.extend(current)
        elif contains_sensitive_value(current):
            return True
    return False


def _validated_initialized_at(value: dict[str, Any] | None) -> str:
    if value is None:
        _reject(
            ".investkit",
            "invalid initialization timestamp; migration not started",
        )
    timestamp = value.get("initialized_at")
    if not isinstance(timestamp, str) or not _is_utc_timestamp(timestamp):
        _reject(
            ".investkit",
            "invalid initialization timestamp; migration not started",
        )
    return timestamp


def _is_utc_timestamp(value: str) -> bool:
    if not value.endswith("Z") or len(value) > 64:
        return False
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _reject_manifest() -> NoReturn:
    _reject(
        ".investkit/install-manifest.json",
        "legacy ownership ledger is invalid or incompatible; migration not started",
    )


def _reject(path: str, message: str) -> NoReturn:
    raise _MigrationRejected((FileAction("WARN", path, message),))


def _spec_records(source_root: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for name in REQUIRED_SPECS:
        relative_path = Path("specs") / name
        path = source_file(source_root, relative_path)
        text = path.read_text(encoding="utf-8")
        match = SPEC_VERSION_RE.search(text)
        if not match:
            raise AssetValidationError(f"required spec has no version: {name}")
        records.append(
            {
                "path": relative_path.as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "version": match.group(1),
            }
        )
    return records


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _bounded_message(error: BaseException) -> str:
    return safe_error_message(error, limit=300)
