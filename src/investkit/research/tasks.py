"""Safe filesystem persistence for InvestKit research tasks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping
from uuid import uuid4

from investkit.errors import FilesystemBoundaryError, safe_error_message
from investkit.filesystem import resolve_within


TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,95}$")


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


def new_task_id() -> str:
    """Create a sortable task ID with collision-resistant entropy."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"demo-{timestamp}-{uuid4().hex[:10]}"


class TaskStore:
    """Read and atomically update task state below one project root."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).expanduser().resolve()
        if not self.project_root.is_dir():
            raise ResearchTaskError(
                f"project root does not exist: {self.project_root}"
            )
        self.research_root = resolve_within(
            self.project_root, "workspace/research"
        )
        self.research_root.mkdir(parents=True, exist_ok=True)

    def create(self, task_id: str) -> Path:
        """Create and return a new exclusive task directory."""

        task_path = self.task_path(task_id)
        try:
            task_path.mkdir(mode=0o700)
            (task_path / "data").mkdir(mode=0o700)
            (task_path / "capabilities").mkdir(mode=0o700)
        except FileExistsError as error:
            raise ResearchTaskError(f"research task already exists: {task_id}") from error
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

        path = self._artifact_path(task_path, relative_path)
        try:
            with path.open("r", encoding="utf-8") as stream:
                return json.load(stream)
        except FileNotFoundError as error:
            raise CorruptTaskError(
                f"task is incomplete: missing {relative_path}"
            ) from error
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise CorruptTaskError(
                f"corrupt or invalid task artifact: {relative_path}"
            ) from error

    def read_text(self, task_path: Path, relative_path: str) -> str:
        """Read a UTF-8 task text artifact."""

        path = self._artifact_path(task_path, relative_path)
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
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

        text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
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
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not overwrite:
            raise ResearchTaskError(f"refusing to overwrite task artifact: {relative_path}")
        file_descriptor, temporary_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            text=True,
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, path)
        except BaseException:
            temporary_path.unlink(missing_ok=True)
            raise
        return path

    def append_event(self, task_path: Path, event: Mapping[str, Any]) -> None:
        """Append one structured event to the durable run log."""

        path = self._artifact_path(task_path, "run-log.json")
        if path.exists():
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

        return self._artifact_path(task_path, relative_path).is_file()

    def _artifact_path(self, task_path: Path, relative_path: str) -> Path:
        if task_path.is_symlink():
            raise InvalidTaskIdError("task path is an unsafe symlink")
        resolved_task = task_path.resolve()
        if not resolved_task.is_relative_to(self.research_root):
            raise InvalidTaskIdError("task path escapes the research workspace")
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise InvalidTaskIdError("task artifact path escapes the task directory")
        try:
            return resolve_within(resolved_task, relative)
        except FilesystemBoundaryError as error:
            raise InvalidTaskIdError(
                "task artifact path escapes or aliases the task directory"
            ) from error
