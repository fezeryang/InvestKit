"""Filesystem boundary, hashing, and create-once helpers."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .errors import FilesystemBoundaryError
from .models import FileAction


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
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
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
