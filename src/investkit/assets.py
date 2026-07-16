"""Validated discovery of canonical and wheel-delivered first-party assets."""

from __future__ import annotations

from pathlib import Path
import re
import sysconfig
from typing import Iterable

from .errors import AssetValidationError, FilesystemBoundaryError


CORE_SKILLS = (
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
REQUIRED_SPECS = (
    "research-principles.md",
    "evidence-policy.md",
    "source-policy.md",
    "financial-data-policy.md",
    "valuation-policy.md",
    "risk-policy.md",
    "report-policy.md",
)
SOURCE_DIRECTORIES = (
    "skills",
    "agents",
    "workflows",
    "specs",
    "packages",
    "workspace-template",
    "fixtures",
)
FORBIDDEN_SOURCE_PATHS = (
    ("third_party", "raw"),
    ("adapted", "skills"),
)
WORKFLOW_PATH = Path("workflows/company-deep-dive.json")
FIXTURE_PATH = Path("fixtures/demo/aurora-lantern-works.json")
SPEC_VERSION_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?(?:spec\s+)?version(?:\*\*)?\s*"
    r"[:=-]\s*`?v?([0-9]+(?:\.[0-9]+){1,2})"
)


def default_source_root() -> Path:
    """Locate a complete source tree in a checkout or installed wheel prefix."""

    module_path = Path(__file__).resolve()
    candidates = (
        module_path.parents[2],
        *(parent / "share" / "investkit" for parent in module_path.parents[:6]),
        Path(sysconfig.get_path("data")) / "share" / "investkit",
    )
    for candidate in _unique_paths(candidates):
        try:
            root = complete_source_root(candidate)
        except AssetValidationError:
            continue
        return root
    raise AssetValidationError(
        "InvestKit first-party assets are unavailable; reinstall a complete wheel "
        "or run from the repository checkout"
    )


def resolve_source_root(value: str | Path) -> Path:
    """Resolve one explicitly approved first-party root without leaving it."""

    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise AssetValidationError("first-party source root is missing or inaccessible")
    if _has_forbidden_source_ancestry(root):
        raise AssetValidationError(
            "third-party and adapted trees cannot be first-party source roots"
        )
    return root


def complete_source_root(value: str | Path) -> Path:
    """Resolve a source root and require every asset needed by this slice."""

    root = resolve_source_root(value)
    if not _is_complete_source(root):
        raise AssetValidationError("first-party source root is incomplete")
    return root


def source_file(source_root: Path, relative_path: str | Path) -> Path:
    """Return one regular source file constrained below ``source_root``."""

    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise FilesystemBoundaryError("first-party asset path escapes its source root")
    root = source_root.expanduser().resolve()
    candidate = root / relative
    if _has_symlink_component(root, relative):
        raise FilesystemBoundaryError(
            "first-party asset path contains an unsafe symlink"
        )
    path = candidate.resolve()
    if not path.is_relative_to(root):
        raise FilesystemBoundaryError("first-party asset path escapes its source root")
    if not path.is_file():
        raise AssetValidationError(
            f"required first-party asset is missing: {relative.as_posix()}"
        )
    return path


def discover_skill_files(source_root: Path, skill_name: str) -> tuple[Path, ...]:
    """Return every regular file in one allowlisted first-party Skill tree.

    Discovery is deterministic and fails closed on symlinks, special files, or
    paths that escape the approved source root.  Merely adding a directory below
    ``skills/`` never makes it installable.
    """

    if skill_name not in CORE_SKILLS:
        raise AssetValidationError(f"unapproved first-party Skill: {skill_name}")

    root = resolve_source_root(source_root)
    relative_root = Path("skills") / skill_name
    if _has_symlink_component(root, relative_root):
        raise FilesystemBoundaryError(
            f"first-party Skill contains an unsafe symlink: {skill_name}"
        )
    skill_root = root / relative_root
    if not skill_root.is_dir():
        raise AssetValidationError(
            f"required first-party Skill is missing: {relative_root.as_posix()}"
        )

    files: list[Path] = []
    for candidate in sorted(skill_root.rglob("*")):
        relative = candidate.relative_to(root)
        if candidate.is_symlink() or _has_symlink_component(root, relative):
            raise FilesystemBoundaryError(
                f"first-party Skill contains an unsafe symlink: {relative.as_posix()}"
            )
        if candidate.is_dir():
            continue
        if not candidate.is_file():
            raise AssetValidationError(
                f"first-party Skill contains a non-regular file: {relative.as_posix()}"
            )
        resolved = candidate.resolve()
        if not resolved.is_relative_to(root):
            raise FilesystemBoundaryError(
                f"first-party Skill file escapes its source root: {relative.as_posix()}"
            )
        files.append(candidate)

    skill_entrypoint = skill_root / "SKILL.md"
    if skill_entrypoint not in files:
        raise AssetValidationError(
            f"required first-party asset is missing: {relative_root.as_posix()}/SKILL.md"
        )
    return tuple(files)


def source_directories(source_root: Path) -> dict[str, str]:
    """Return present approved source directories without following escapes."""

    present: dict[str, str] = {}
    for name in SOURCE_DIRECTORIES:
        path = (source_root / name).resolve()
        if path.is_relative_to(source_root) and path.is_dir():
            present[name] = name
    return present


def _is_complete_source(source_root: Path) -> bool:
    required = (
        *(Path("specs") / name for name in REQUIRED_SPECS),
        WORKFLOW_PATH,
        FIXTURE_PATH,
        Path("workspace-template/README.md"),
        Path("agents/README.md"),
        Path("packages/README.md"),
    )
    try:
        if not all(source_file(source_root, relative).is_file() for relative in required):
            return False
        return all(discover_skill_files(source_root, name) for name in CORE_SKILLS)
    except (AssetValidationError, FilesystemBoundaryError, OSError):
        return False


def _unique_paths(values: Iterable[Path]) -> tuple[Path, ...]:
    unique: list[Path] = []
    for value in values:
        resolved = value.expanduser().resolve()
        if resolved not in unique:
            unique.append(resolved)
    return tuple(unique)


def _has_forbidden_source_ancestry(path: Path) -> bool:
    parts = tuple(part.casefold() for part in path.parts)
    return any(
        parts[index : index + len(forbidden)] == forbidden
        for forbidden in FORBIDDEN_SOURCE_PATHS
        for index in range(len(parts) - len(forbidden) + 1)
    )


def _has_symlink_component(root: Path, relative: Path) -> bool:
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False
