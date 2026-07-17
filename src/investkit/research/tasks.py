"""Safe filesystem persistence for InvestKit research tasks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import stat
from typing import Any, Mapping
from uuid import uuid4

from investkit.errors import FilesystemBoundaryError, safe_error_message
from investkit.filesystem import resolve_within


TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,95}$")
MAX_TASK_ARTIFACT_BYTES = 8 * 1024 * 1024
_READ_CHUNK_BYTES = 128 * 1024


class ResearchTaskError(RuntimeError):
    """Base exception for persisted research-task failures."""


class InvalidTaskIdError(ResearchTaskError):
    """Raised when a task ID could escape or alias the task workspace."""


class CorruptTaskError(ResearchTaskError):
    """Raised when durable task state cannot be trusted or resumed."""


@dataclass(frozen=True)
class ResearchResult:
    """Public result returned by demo research operations."""

    task_id: str
    status: str
    task_path: Path
    report_path: Path | None = None
    error: str | None = None

    @property
    def exit_code(self) -> int:
        return 0 if self.status == "completed" else 1


def utc_now() -> str:
    """Return a UTC ISO-8601 timestamp with a ``Z`` suffix."""

    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def new_task_id(prefix: str = "demo") -> str:
    """Create a sortable task ID with collision-resistant entropy."""

    if prefix not in {"demo", "research"}:
        raise ValueError("unsupported research task ID prefix")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{prefix}-{timestamp}-{uuid4().hex[:10]}"


class TaskStore:
    """Read and atomically update task state below one project root."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).expanduser().resolve()
        if not self.project_root.is_dir():
            raise ResearchTaskError(
                f"project root does not exist: {self.project_root}"
            )
        self._require_safe_openat()
        project_metadata = self.project_root.stat(follow_symlinks=False)
        if not stat.S_ISDIR(project_metadata.st_mode):
            raise ResearchTaskError("project root is not a safe directory")
        self._project_identity = (
            project_metadata.st_dev,
            project_metadata.st_ino,
        )
        self.research_root = resolve_within(
            self.project_root, "workspace/research"
        )
        self.research_root.mkdir(parents=True, exist_ok=True)
        research_metadata = self.research_root.stat(follow_symlinks=False)
        if not stat.S_ISDIR(research_metadata.st_mode):
            raise ResearchTaskError("research workspace is not a safe directory")
        self._research_identity = (
            research_metadata.st_dev,
            research_metadata.st_ino,
        )

    def create(self, task_id: str) -> Path:
        """Create and return a new exclusive task directory."""

        task_path = self.task_path(task_id)
        research_descriptor = self._open_research_directory()
        try:
            try:
                os.mkdir(task_id, mode=0o700, dir_fd=research_descriptor)
            except FileExistsError as error:
                raise ResearchTaskError(
                    f"research task already exists: {task_id}"
                ) from error
            try:
                task_descriptor = os.open(
                    task_id,
                    self._directory_flags(),
                    dir_fd=research_descriptor,
                )
                try:
                    os.mkdir("data", mode=0o700, dir_fd=task_descriptor)
                    os.mkdir("capabilities", mode=0o700, dir_fd=task_descriptor)
                    os.fsync(task_descriptor)
                finally:
                    os.close(task_descriptor)
                os.fsync(research_descriptor)
            except OSError as error:
                raise ResearchTaskError(
                    f"research task could not be created safely: {task_id}"
                ) from error
        finally:
            os.close(research_descriptor)
        return task_path

    def task_path(self, task_id: str, *, require_exists: bool = False) -> Path:
        """Resolve a validated task ID without permitting path traversal."""

        if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id):
            raise InvalidTaskIdError("invalid research task ID")
        if ".." in task_id:
            raise InvalidTaskIdError("invalid research task ID")
        try:
            task_path = resolve_within(self.research_root, task_id)
        except FilesystemBoundaryError as error:
            raise InvalidTaskIdError(
                "research task ID escapes or aliases the workspace"
            ) from error
        if require_exists and not task_path.is_dir():
            raise ResearchTaskError(f"research task not found: {task_id}")
        return task_path

    def read_json(self, task_path: Path, relative_path: str) -> Any:
        """Read a JSON task artifact or raise an actionable corruption error."""

        try:
            text = self.read_text(task_path, relative_path)
            return json.loads(
                text,
                object_pairs_hook=_unique_json_object,
                parse_constant=_reject_json_constant,
                parse_float=_finite_json_float,
            )
        except CorruptTaskError:
            raise
        except (
            json.JSONDecodeError,
            OverflowError,
            RecursionError,
            TypeError,
            ValueError,
        ) as error:
            raise CorruptTaskError(
                f"corrupt or invalid task artifact: {relative_path}"
            ) from error

    def read_text(self, task_path: Path, relative_path: str) -> str:
        """Read a UTF-8 task text artifact."""

        try:
            return self._read_artifact_bytes(task_path, relative_path).decode(
                "utf-8",
                errors="strict",
            )
        except CorruptTaskError:
            raise
        except UnicodeError as error:
            raise CorruptTaskError(
                f"corrupt or invalid task artifact: {relative_path}"
            ) from error

    def write_json(
        self,
        task_path: Path,
        relative_path: str,
        payload: Any,
        *,
        overwrite: bool = True,
    ) -> Path:
        """Atomically write stable UTF-8 JSON inside a task directory."""

        text = (
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n"
        )
        return self.write_text(
            task_path,
            relative_path,
            text,
            overwrite=overwrite,
        )

    def write_text(
        self,
        task_path: Path,
        relative_path: str,
        text: str,
        *,
        overwrite: bool = True,
    ) -> Path:
        """Atomically write text inside a task directory."""

        path = self._artifact_path(task_path, relative_path)
        payload = text.encode("utf-8", errors="strict")
        if len(payload) > MAX_TASK_ARTIFACT_BYTES:
            raise ResearchTaskError(
                f"task artifact exceeds the maximum allowed size: {relative_path}"
            )
        parts = self._artifact_parts(relative_path)
        temporary_name = f".{parts[-1]}.{uuid4().hex}.tmp"
        parent_descriptor: int | None = None
        temporary_exists = False
        try:
            parent_descriptor = self._open_parent_directory(
                task_path,
                parts[:-1],
                create=True,
            )
            self._validate_write_target(
                parent_descriptor,
                parts[-1],
                relative_path,
                overwrite=overwrite,
            )
            temporary_descriptor = os.open(
                temporary_name,
                (
                    os.O_WRONLY
                    | os.O_CREAT
                    | os.O_EXCL
                    | os.O_NOFOLLOW
                    | getattr(os, "O_CLOEXEC", 0)
                ),
                0o600,
                dir_fd=parent_descriptor,
            )
            temporary_exists = True
            try:
                os.fchmod(temporary_descriptor, 0o600)
                self._write_all(temporary_descriptor, payload)
                os.fsync(temporary_descriptor)
            finally:
                os.close(temporary_descriptor)

            self._verify_parent_attached(
                task_path,
                parts[:-1],
                parent_descriptor,
            )
            if overwrite:
                os.replace(
                    temporary_name,
                    parts[-1],
                    src_dir_fd=parent_descriptor,
                    dst_dir_fd=parent_descriptor,
                )
                temporary_exists = False
            else:
                try:
                    os.link(
                        temporary_name,
                        parts[-1],
                        src_dir_fd=parent_descriptor,
                        dst_dir_fd=parent_descriptor,
                        follow_symlinks=False,
                    )
                except FileExistsError as error:
                    raise ResearchTaskError(
                        f"refusing to overwrite task artifact: {relative_path}"
                    ) from error
                os.unlink(temporary_name, dir_fd=parent_descriptor)
                temporary_exists = False
            os.fsync(parent_descriptor)
        except ResearchTaskError:
            raise
        except OSError as error:
            raise ResearchTaskError(
                f"task artifact could not be written safely: {relative_path}"
            ) from error
        finally:
            if parent_descriptor is not None:
                if temporary_exists:
                    try:
                        os.unlink(temporary_name, dir_fd=parent_descriptor)
                    except OSError:
                        pass
                os.close(parent_descriptor)
        return path

    def append_event(self, task_path: Path, event: Mapping[str, Any]) -> None:
        """Append one structured event to the durable run log."""

        if self.artifact_is_file(task_path, "run-log.json"):
            payload = self.read_json(task_path, "run-log.json")
            if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
                raise CorruptTaskError("corrupt or invalid task artifact: run-log.json")
        else:
            payload = {"task_id": task_path.name, "events": []}
        payload["events"].append(dict(event))
        self.write_json(task_path, "run-log.json", payload)

    def artifact_path(self, task_path: Path, relative_path: str) -> Path:
        """Resolve one task artifact for safe existence or directory checks."""

        return self._artifact_path(task_path, relative_path)

    def artifact_is_file(self, task_path: Path, relative_path: str) -> bool:
        """Return whether a constrained task artifact is a regular file."""

        self._artifact_path(task_path, relative_path)
        parts = self._artifact_parts(relative_path)
        parent_descriptor: int | None = None
        try:
            parent_descriptor = self._open_parent_directory(
                task_path,
                parts[:-1],
                create=False,
            )
            metadata = os.stat(
                parts[-1],
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            return stat.S_ISREG(metadata.st_mode)
        except FileNotFoundError:
            return False
        except ResearchTaskError:
            raise
        except OSError as error:
            raise CorruptTaskError(
                f"task artifact is unsafe or inaccessible: {relative_path}"
            ) from error
        finally:
            if parent_descriptor is not None:
                os.close(parent_descriptor)

    def _artifact_path(self, task_path: Path, relative_path: str) -> Path:
        task_name = self._validated_task_name(task_path)
        parts = self._artifact_parts(relative_path)
        try:
            return resolve_within(
                self.research_root,
                Path(task_name, *parts),
            )
        except FilesystemBoundaryError as error:
            raise InvalidTaskIdError(
                "task artifact path escapes or aliases the task directory"
            ) from error

    def _read_artifact_bytes(self, task_path: Path, relative_path: str) -> bytes:
        self._artifact_path(task_path, relative_path)
        parts = self._artifact_parts(relative_path)
        parent_descriptor: int | None = None
        file_descriptor: int | None = None
        try:
            parent_descriptor = self._open_parent_directory(
                task_path,
                parts[:-1],
                create=False,
            )
            file_descriptor = os.open(
                parts[-1],
                (
                    os.O_RDONLY
                    | os.O_NOFOLLOW
                    | getattr(os, "O_NONBLOCK", 0)
                    | getattr(os, "O_CLOEXEC", 0)
                ),
                dir_fd=parent_descriptor,
            )
            before = os.fstat(file_descriptor)
            if (
                not stat.S_ISREG(before.st_mode)
                or before.st_size > MAX_TASK_ARTIFACT_BYTES
            ):
                raise CorruptTaskError(
                    f"corrupt or invalid task artifact: {relative_path}"
                )
            chunks: list[bytes] = []
            size = 0
            while True:
                chunk = os.read(
                    file_descriptor,
                    min(
                        _READ_CHUNK_BYTES,
                        MAX_TASK_ARTIFACT_BYTES + 1 - size,
                    ),
                )
                if not chunk:
                    break
                chunks.append(chunk)
                size += len(chunk)
                if size > MAX_TASK_ARTIFACT_BYTES:
                    raise CorruptTaskError(
                        f"corrupt or invalid task artifact: {relative_path}"
                    )
            after = os.fstat(file_descriptor)
            if (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_mtime_ns,
            ) != (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
            ):
                raise CorruptTaskError(
                    f"task artifact changed while being read: {relative_path}"
                )
            return b"".join(chunks)
        except FileNotFoundError as error:
            raise CorruptTaskError(
                f"task is incomplete: missing {relative_path}"
            ) from error
        except CorruptTaskError:
            raise
        except ResearchTaskError:
            raise
        except OSError as error:
            raise CorruptTaskError(
                f"corrupt or invalid task artifact: {relative_path}"
            ) from error
        finally:
            if file_descriptor is not None:
                os.close(file_descriptor)
            if parent_descriptor is not None:
                os.close(parent_descriptor)

    def _open_research_directory(self) -> int:
        root_descriptor: int | None = None
        workspace_descriptor: int | None = None
        research_descriptor: int | None = None
        try:
            root_descriptor = os.open(
                self.project_root,
                self._directory_flags(),
            )
            self._require_identity(
                root_descriptor,
                self._project_identity,
                "project root changed after TaskStore initialization",
            )
            workspace_descriptor = os.open(
                "workspace",
                self._directory_flags(),
                dir_fd=root_descriptor,
            )
            research_descriptor = os.open(
                "research",
                self._directory_flags(),
                dir_fd=workspace_descriptor,
            )
            self._require_identity(
                research_descriptor,
                self._research_identity,
                "research workspace changed after TaskStore initialization",
            )
            result = research_descriptor
            research_descriptor = None
            return result
        except ResearchTaskError:
            raise
        except OSError as error:
            raise ResearchTaskError(
                "research workspace is unsafe or inaccessible"
            ) from error
        finally:
            if research_descriptor is not None:
                os.close(research_descriptor)
            if workspace_descriptor is not None:
                os.close(workspace_descriptor)
            if root_descriptor is not None:
                os.close(root_descriptor)

    def _open_task_directory(self, task_path: Path) -> int:
        task_name = self._validated_task_name(task_path)
        research_descriptor = self._open_research_directory()
        try:
            try:
                task_descriptor = os.open(
                    task_name,
                    self._directory_flags(),
                    dir_fd=research_descriptor,
                )
            except FileNotFoundError as error:
                raise ResearchTaskError(
                    f"research task not found: {task_name}"
                ) from error
            except OSError as error:
                raise InvalidTaskIdError(
                    "task path is unsafe or inaccessible"
                ) from error
            return task_descriptor
        finally:
            os.close(research_descriptor)

    def _open_parent_directory(
        self,
        task_path: Path,
        parent_parts: tuple[str, ...],
        *,
        create: bool,
    ) -> int:
        current_descriptor = self._open_task_directory(task_path)
        try:
            for part in parent_parts:
                if create:
                    try:
                        os.mkdir(part, mode=0o700, dir_fd=current_descriptor)
                    except FileExistsError:
                        pass
                next_descriptor = os.open(
                    part,
                    self._directory_flags(),
                    dir_fd=current_descriptor,
                )
                os.close(current_descriptor)
                current_descriptor = next_descriptor
            result = current_descriptor
            current_descriptor = -1
            return result
        finally:
            if current_descriptor >= 0:
                os.close(current_descriptor)

    def _verify_parent_attached(
        self,
        task_path: Path,
        parent_parts: tuple[str, ...],
        expected_descriptor: int,
    ) -> None:
        verification_descriptor = self._open_parent_directory(
            task_path,
            parent_parts,
            create=False,
        )
        try:
            expected = os.fstat(expected_descriptor)
            actual = os.fstat(verification_descriptor)
            if (expected.st_dev, expected.st_ino) != (actual.st_dev, actual.st_ino):
                raise ResearchTaskError(
                    "task artifact parent changed during atomic write"
                )
        finally:
            os.close(verification_descriptor)

    @staticmethod
    def _validate_write_target(
        parent_descriptor: int,
        name: str,
        relative_path: str,
        *,
        overwrite: bool,
    ) -> None:
        try:
            metadata = os.stat(
                name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return
        if not stat.S_ISREG(metadata.st_mode):
            raise ResearchTaskError(
                f"task artifact target is not a regular file: {relative_path}"
            )
        if not overwrite:
            raise ResearchTaskError(
                f"refusing to overwrite task artifact: {relative_path}"
            )

    @staticmethod
    def _write_all(file_descriptor: int, payload: bytes) -> None:
        view = memoryview(payload)
        while view:
            written = os.write(file_descriptor, view)
            if written <= 0:
                raise OSError("short write while persisting task artifact")
            view = view[written:]

    def _validated_task_name(self, task_path: Path) -> str:
        raw = Path(task_path)
        if ".." in raw.parts:
            raise InvalidTaskIdError("task path escapes the research workspace")
        candidate = Path(os.path.abspath(os.fspath(raw)))
        task_name = candidate.name
        if (
            candidate.parent != self.research_root
            or not TASK_ID_RE.fullmatch(task_name)
            or ".." in task_name
        ):
            raise InvalidTaskIdError("task path escapes the research workspace")
        return task_name

    @staticmethod
    def _artifact_parts(relative_path: str) -> tuple[str, ...]:
        relative = Path(relative_path)
        if (
            relative.is_absolute()
            or not relative.parts
            or ".." in relative.parts
            or any(part in {"", "."} for part in relative.parts)
        ):
            raise InvalidTaskIdError(
                "task artifact path escapes the task directory"
            )
        return tuple(relative.parts)

    @staticmethod
    def _directory_flags() -> int:
        return (
            os.O_RDONLY
            | os.O_NOFOLLOW
            | os.O_DIRECTORY
            | getattr(os, "O_CLOEXEC", 0)
        )

    @staticmethod
    def _require_identity(
        descriptor: int,
        expected: tuple[int, int],
        message: str,
    ) -> None:
        metadata = os.fstat(descriptor)
        if not stat.S_ISDIR(metadata.st_mode):
            raise ResearchTaskError(message)
        if (metadata.st_dev, metadata.st_ino) != expected:
            raise ResearchTaskError(message)

    @staticmethod
    def _require_safe_openat() -> None:
        required = (os.open, os.mkdir, os.stat, os.unlink, os.link, os.rename)
        if (
            not hasattr(os, "O_NOFOLLOW")
            or not hasattr(os, "O_DIRECTORY")
            or any(operation not in os.supports_dir_fd for operation in required)
        ):
            raise ResearchTaskError(
                "this platform cannot safely persist research tasks"
            )


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_json_constant(_value: str) -> Any:
    raise ValueError("non-standard JSON constant")


def _finite_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("non-finite JSON number")
    return parsed
