"""Filesystem boundary, hashing, and create-once helpers."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
from typing import Any

from .errors import FilesystemBoundaryError
from .models import FileAction


@dataclass(frozen=True)
class AtomicReplacement:
    """One staged, caller-derived replacement with commit-time preconditions."""

    root: Path
    relative_path: str
    destination: Path
    staged_path: Path
    expected_existing_sha256: frozenset[str]
    allow_missing: bool


def resolved_root(value: str | Path, *, require_directory: bool = True) -> Path:
    root = Path(value).expanduser().resolve()
    if require_directory and not root.is_dir():
        raise FilesystemBoundaryError(f"directory does not exist: {root}")
    return root


def resolve_within(root: Path, relative_path: str | Path) -> Path:
    root = root.expanduser().resolve()
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise FilesystemBoundaryError("relative path escapes its approved root")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise FilesystemBoundaryError("path contains an unsafe symlink")
    path = current.resolve()
    if not path.is_relative_to(root):
        raise FilesystemBoundaryError("path escapes its approved root")
    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(128 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def create_once(root: Path, relative_path: str | Path, content: bytes) -> FileAction:
    """Create a file exclusively, or classify an identical/conflicting file."""

    path = resolve_within(root, relative_path)
    display_path = Path(relative_path).as_posix()
    if path.exists():
        if not path.is_file():
            return FileAction("WARN", display_path, "path exists and is not a file")
        try:
            existing = path.read_bytes()
        except OSError:
            return FileAction("WARN", display_path, "existing file cannot be read")
        if existing == content:
            return FileAction("SKIP", display_path, "identical InvestKit file exists")
        return FileAction("WARN", display_path, "existing file differs; preserved")

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        file_descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return create_once(root, relative_path, content)
    try:
        with os.fdopen(file_descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return FileAction("CREATE", display_path, "created")


def stage_atomic_replacement(
    root: Path,
    relative_path: str | Path,
    content: bytes,
    *,
    expected_existing_sha256: frozenset[str],
    allow_missing: bool = False,
) -> AtomicReplacement:
    """Stage bytes beside a safely derived destination without replacing it."""

    destination = resolve_within(root, relative_path)
    display_path = Path(relative_path).as_posix()
    destination.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.investkit-",
        dir=destination.parent,
    )
    staged_path = Path(temporary_name)
    try:
        os.fchmod(file_descriptor, 0o600)
        with os.fdopen(file_descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        try:
            os.close(file_descriptor)
        except OSError:
            pass
        staged_path.unlink(missing_ok=True)
        raise
    return AtomicReplacement(
        root=root.resolve(),
        relative_path=display_path,
        destination=destination,
        staged_path=staged_path,
        expected_existing_sha256=expected_existing_sha256,
        allow_missing=allow_missing,
    )


def commit_atomic_replacement(replacement: AtomicReplacement) -> None:
    """Atomically commit a stage if its owned-file precondition still holds."""

    destination = resolve_within(
        replacement.root, replacement.relative_path
    )
    if destination != replacement.destination:
        raise FilesystemBoundaryError("atomic replacement destination changed")
    current_digest = _regular_file_digest(destination)
    if current_digest is None:
        if not replacement.allow_missing:
            raise FilesystemBoundaryError(
                "atomic replacement target unexpectedly missing"
            )
    elif current_digest not in replacement.expected_existing_sha256:
        raise FilesystemBoundaryError(
            "atomic replacement target changed after preflight"
        )
    os.replace(replacement.staged_path, destination)
    directory_descriptor = os.open(destination.parent, os.O_RDONLY)
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)


def discard_atomic_replacement(replacement: AtomicReplacement) -> None:
    """Remove an uncommitted stage without touching its destination."""

    replacement.staged_path.unlink(missing_ok=True)


def _regular_file_digest(path: Path) -> str | None:
    """Hash one regular file without following a final-component symlink."""

    try:
        path_stat = os.lstat(path)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise FilesystemBoundaryError(
            "atomic replacement target is unsafe or inaccessible"
        ) from error
    if not stat.S_ISREG(path_stat.st_mode):
        raise FilesystemBoundaryError(
            "atomic replacement target is not a regular file"
        )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        file_descriptor = os.open(path, flags)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise FilesystemBoundaryError(
            "atomic replacement target is unsafe or inaccessible"
        ) from error
    try:
        file_stat = os.fstat(file_descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            raise FilesystemBoundaryError(
                "atomic replacement target is not a regular file"
            )
        digest = hashlib.sha256()
        while True:
            chunk = os.read(file_descriptor, 128 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        return digest.hexdigest()
    finally:
        os.close(file_descriptor)
