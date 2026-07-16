"""Idempotent, create-once InvestKit project initialization."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from . import __version__
from .assets import (
    CORE_SKILLS,
    REQUIRED_SPECS,
    SPEC_VERSION_RE,
    complete_source_root,
    default_source_root,
    discover_skill_files,
    source_directories,
    source_file,
)
from .errors import AssetValidationError, InvestKitError, safe_error_message
from .filesystem import create_once, resolve_within, resolved_root, stable_json_bytes
from .models import FileAction, InitializationResult
from .platforms.codex import CodexAdapter


def initialize_project(
    project_root: str | Path,
    *,
    source_root: str | Path | None = None,
) -> InitializationResult:
    """Initialize a Codex project without overwriting any existing file."""

    try:
        return _initialize_project(project_root, source_root)
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
    actions: list[FileAction] = []

    skill_sources: list[tuple[str, Path, Path, bytes]] = []
    for skill_name in CORE_SKILLS:
        skill_root = source / "skills" / skill_name
        for path in discover_skill_files(source, skill_name):
            skill_sources.append(
                (skill_name, path, path.relative_to(skill_root), path.read_bytes())
            )

    spec_records = _spec_records(source)
    workspace_readme = source_file(
        source, Path("workspace-template") / "README.md"
    ).read_bytes()
    initialized_at = _existing_initialized_at(project) or _utc_now()

    mappings: list[dict[str, Any]] = []
    for skill_name, source_path, skill_relative, content in skill_sources:
        source_relative = source_path.relative_to(source).as_posix()
        target_relative = (
            Path(adapter.installation_target) / skill_name / skill_relative
        ).as_posix()
        digest = hashlib.sha256(content).hexdigest()
        action = create_once(project, target_relative, content)
        actions.append(action)
        mappings.append(
            {
                "kind": "skill",
                "source": source_relative,
                "source_sha256": digest,
                "target": target_relative,
                "target_sha256": digest,
            }
        )

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

    source_directory_records = source_directories(source)
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
    adapter_config = adapter.configuration(list(CORE_SKILLS))
    actions.extend(
        (
            create_once(
                project,
                adapter.configuration_path,
                stable_json_bytes(adapter_config),
            ),
            create_once(project, ".investkit/config.json", stable_json_bytes(config)),
        )
    )
    if any(action.action == "WARN" for action in actions):
        return InitializationResult(exit_code=1, actions=tuple(actions))
    actions.append(
        create_once(
            project,
            ".investkit/install-manifest.json",
            stable_json_bytes(manifest),
        )
    )
    exit_code = int(any(action.action == "WARN" for action in actions))
    return InitializationResult(exit_code=exit_code, actions=tuple(actions))


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


def _existing_initialized_at(project_root: Path) -> str | None:
    path = resolve_within(project_root, ".investkit/config.json")
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict) or value.get("managed_by") != "investkit":
        return None
    timestamp = value.get("initialized_at")
    return str(timestamp) if isinstance(timestamp, str) and timestamp.endswith("Z") else None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _bounded_message(error: BaseException) -> str:
    return safe_error_message(error, limit=300)
