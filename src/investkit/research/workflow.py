"""Deterministic offline Investment Core workflow and safe resume behavior."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, MutableMapping, Sequence

from investkit.assets import (
    FIXTURE_PATH,
    REQUIRED_SPECS,
    SPEC_VERSION_RE,
    WORKFLOW_PATH,
    resolve_source_root,
    source_file as validated_source_file,
)
from investkit.capabilities.analysis import run_capability
from investkit.capabilities.catalog import RUNTIME_SKILLS, discover_skill_files
from investkit.capabilities.contracts import validate_capability_result
from investkit.filesystem import resolve_within, resolved_root
from investkit.providers.base import Provider
from investkit.providers.demo import DemoProvider
from investkit.providers.file import (
    BundleInputError,
    BundleValidationError,
    FileProvider,
)

from .report import render_report
from .tasks import (
    CorruptTaskError,
    ResearchResult,
    ResearchTaskError,
    TaskStore,
    new_task_id,
    safe_error_message,
    utc_now,
)


EXPECTED_STEPS = tuple(RUNTIME_SKILLS)
WORKFLOW_ID = "company-deep-dive"
MANDATORY_COMPLETED_CAPABILITIES = frozenset(
    {"bear-case-analysis", "source-verification", "investment-report"}
)
REQUIRED_PROVIDER_METADATA = frozenset(
    {"as_of_date", "currency", "market", "source", "is_demo", "warnings"}
)
REQUIRED_COMPLETED_ARTIFACTS = (
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
IMPORTED_BUNDLE_PATH = "input/research-bundle.json"
DATA_PATHS = {
    "identity": "data/security-identity.json",
    "source_metadata": "data/source-metadata.json",
    "profile": "data/security-profile.json",
    "statements": "data/financial-statements.json",
    "price_history": "data/price-history.json",
    "valuation_inputs": "data/valuation-inputs.json",
    "peers": "data/peer-comparables.json",
    "earnings": "data/earnings-history.json",
    "catalysts": "data/catalyst-events.json",
}
STEP_DATA_REQUIREMENTS = {
    "security-identification": (
        DATA_PATHS["identity"],
        DATA_PATHS["source_metadata"],
        "sources.json",
    ),
    "company-deep-research": (DATA_PATHS["profile"],),
    "business-model-analysis": (DATA_PATHS["profile"],),
    "financial-statement-analysis": (DATA_PATHS["statements"],),
    "earnings-quality-analysis": (DATA_PATHS["statements"],),
    "valuation-analysis": (
        DATA_PATHS["valuation_inputs"],
        DATA_PATHS["price_history"],
    ),
    "comps-analysis": (DATA_PATHS["peers"],),
    "earnings-analysis": (DATA_PATHS["earnings"],),
    "investment-thesis": (),
    "bear-case-analysis": (),
    "catalyst-analysis": (DATA_PATHS["catalysts"],),
    "source-verification": ("sources.json",),
    "investment-report": ("report.md",),
}
SKILL_VERSION_RE = re.compile(r"(?im)^version\s*:\s*[\"']?([^\s\"']+)")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def run_demo_research(
    project_root: str | Path,
    source_root: str | Path,
    *,
    provider: Provider | None = None,
) -> ResearchResult:
    """Create and execute one unique fictional company-deep-dive task."""

    store = _initialized_task_store(project_root)
    source = _source_root(source_root)
    workflow = _load_workflow(source)
    loaded_specs = _load_specs(source)
    installed_skills = _load_installed_skills(store.project_root, source)
    task_id = new_task_id("demo")
    task_path = store.create(task_id)
    question = (
        "What do the bundled fictional company records show when analyzed by "
        "the complete Investment Core workflow and its explicit limitations?"
    )
    task, plan = _initialize_task(
        store,
        task_path,
        task_id=task_id,
        question=question,
        workflow=workflow,
        loaded_specs=loaded_specs,
        installed_skills=installed_skills,
        input_mode="demo",
        security_query="demo",
        input_record=None,
    )
    active_provider = provider if provider is not None else DemoProvider(source)
    context: dict[str, Any] = {
        "capability_results": {},
        "installed_skills": installed_skills,
        "loaded_specs": loaded_specs,
        "plan": plan,
        "question": question,
        "input_mode": "demo",
        "security_query": "demo",
        "source_root": source,
        "sources": {"schema_version": "1.0", "sources": []},
        "task": task,
        "workflow": workflow,
    }
    return _execute(store, task_path, active_provider, context, resumed=False)


def run_research(
    project_root: str | Path,
    source_root: str | Path,
    *,
    input_path: str | Path,
    question: str,
) -> ResearchResult:
    """Run the full workflow over one validated project-local research bundle."""

    provider = FileProvider(Path(project_root), input_path)
    return run_research_bundle(
        project_root,
        source_root,
        provider=provider,
        question=question,
    )


def run_research_bundle(
    project_root: str | Path,
    source_root: str | Path,
    *,
    provider: FileProvider,
    question: str,
    acquisition_mode: str = "user_imported",
) -> ResearchResult:
    """Run imported research from one already validated immutable Provider snapshot."""

    normalized_question = str(question).strip()
    if not normalized_question:
        raise ResearchTaskError("research question must be non-empty")
    if acquisition_mode not in {"user_imported", "official_live"}:
        raise ResearchTaskError("research acquisition mode is unsupported")
    store = _initialized_task_store(project_root)
    source = _source_root(source_root)
    workflow = _load_workflow(source)
    loaded_specs = _load_specs(source)
    installed_skills = _load_installed_skills(store.project_root, source)
    security = _mapping(provider.bundle.get("security"), "bundle security")
    security_query = _required_text(
        security.get("ticker", security.get("security_id")), "security query"
    )
    task_id = new_task_id("research")
    task_path = store.create(task_id)
    input_record = {
        "bundle_version": _required_text(
            provider.bundle.get("bundle_version"), "bundle version"
        ),
        "acquisition_mode": acquisition_mode,
        "origin": provider.bundle_origin,
        "sha256": provider.bundle_sha256,
        "snapshot": IMPORTED_BUNDLE_PATH,
    }
    task, plan = _initialize_task(
        store,
        task_path,
        task_id=task_id,
        question=normalized_question,
        workflow=workflow,
        loaded_specs=loaded_specs,
        installed_skills=installed_skills,
        input_mode="imported",
        security_query=security_query,
        input_record=input_record,
    )
    # Persist the validated canonical snapshot before analytical execution.
    store.write_text(
        task_path,
        IMPORTED_BUNDLE_PATH,
        provider.bundle_bytes.decode("utf-8"),
        overwrite=False,
    )
    context: dict[str, Any] = {
        "capability_results": {},
        "input_mode": "imported",
        "input_record": input_record,
        "installed_skills": installed_skills,
        "loaded_specs": loaded_specs,
        "plan": plan,
        "question": normalized_question,
        "security_query": security_query,
        "source_root": source,
        "sources": {"input_mode": "imported", "schema_version": "1.0", "sources": []},
        "task": task,
        "workflow": workflow,
    }
    return _execute(store, task_path, provider, context, resumed=False)


def resume_demo_research(
    project_root: str | Path,
    task_id: str,
    source_root: str | Path,
    *,
    provider: Provider | None = None,
) -> ResearchResult:
    """Resume an incomplete task or validate an immutable completed task."""

    return _resume_research(
        project_root,
        task_id,
        source_root,
        provider=provider,
        expected_mode="demo",
    )


def resume_research(
    project_root: str | Path,
    task_id: str,
    source_root: str | Path,
) -> ResearchResult:
    """Resume an imported task from its persisted validated bundle snapshot."""

    return _resume_research(
        project_root,
        task_id,
        source_root,
        provider=None,
        expected_mode="imported",
    )


def _resume_research(
    project_root: str | Path,
    task_id: str,
    source_root: str | Path,
    *,
    provider: Provider | None,
    expected_mode: str,
) -> ResearchResult:
    """Shared resume implementation with explicit mode compatibility."""

    store = _initialized_task_store(project_root)
    task_path = store.task_path(task_id, require_exists=True)
    task = _validated_task(store.read_json(task_path, "task.json"), task_id)
    plan = _validated_plan(store.read_json(task_path, "plan.json"))
    loaded_specs = _record_list(store.read_json(task_path, "loaded-specs.json"), "specs")
    installed_skills = _record_list(
        store.read_json(task_path, "installed-skills.json"), "skills"
    )
    _validate_snapshot_records(loaded_specs, installed_skills)
    question = _read_question(
        store,
        task_path,
        allow_legacy=plan.get("version") == "0.2.0",
    )
    _validate_task_snapshots(task, question, plan)
    input_mode = _task_input_mode(task)
    if input_mode != expected_mode:
        raise CorruptTaskError(
            f"research task input mode is {input_mode}; use the matching resume command"
        )
    input_record = _validate_imported_snapshot(store, task_path, task)

    if task["status"] == "completed":
        _validate_completed_task(store, task_path, plan, task)
        store.append_event(
            task_path,
            {
                "event": "resume",
                "input_mode": input_mode,
                "message": "Completed task inspected; immutable artifacts preserved.",
                "status": "completed",
                "timestamp": utc_now(),
            },
        )
        return ResearchResult(
            task_id=task_id,
            status="completed",
            task_path=task_path,
            report_path=task_path / "report.md",
        )

    source = _source_root(source_root)
    workflow = _load_workflow(source)
    if workflow["version"] != plan["version"]:
        raise CorruptTaskError(
            "task workflow version differs from the available first-party source"
        )
    current_specs = _load_specs(source)
    current_skills = _load_installed_skills(store.project_root, source)
    if _snapshot_signature(current_specs) != _snapshot_signature(loaded_specs):
        raise CorruptTaskError(
            "task spec snapshot differs from the available first-party source"
        )
    if _snapshot_signature(current_skills) != _snapshot_signature(installed_skills):
        raise CorruptTaskError(
            "task Skill snapshot differs from the current Codex installation"
        )

    context = _hydrate_context(
        store,
        task_path,
        installed_skills=installed_skills,
        loaded_specs=loaded_specs,
        plan=plan,
        question=question,
        input_mode=input_mode,
        input_record=input_record,
        security_query=str(task.get("security_query", "demo")),
        source_root=source,
        task=task,
        workflow=workflow,
    )
    if provider is not None:
        active_provider = provider
    elif input_mode == "imported":
        active_provider = FileProvider(store.project_root, task_path / IMPORTED_BUNDLE_PATH)
        if active_provider.bundle_sha256 != input_record.get("sha256"):
            raise CorruptTaskError("persisted research bundle snapshot hash mismatch")
    else:
        active_provider = DemoProvider(source)
    if input_mode == "imported":
        if not isinstance(active_provider, FileProvider):
            raise CorruptTaskError("imported resume requires its persisted bundle provider")
        _validate_imported_provider_state(
            store,
            task_path,
            task,
            active_provider,
        )
        _validate_imported_completed_capabilities(
            store,
            task_path,
            context,
            plan,
        )
    store.append_event(
        task_path,
        {
            "event": "resume",
            "input_mode": input_mode,
            "message": "Resuming only incomplete workflow stages.",
            "status": "running",
            "timestamp": utc_now(),
        },
    )
    return _execute(store, task_path, active_provider, context, resumed=True)


def _initialize_task(
    store: TaskStore,
    task_path: Path,
    *,
    task_id: str,
    question: str,
    workflow: Mapping[str, Any],
    loaded_specs: list[dict[str, Any]],
    installed_skills: list[dict[str, Any]],
    input_mode: str,
    security_query: str,
    input_record: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    created_at = utc_now()
    plan = {
        "schema_version": "1.0",
        "input_mode": input_mode,
        "steps": [
            {
                "id": step["id"],
                "output": step["output"],
                "status": "pending",
            }
            for step in workflow["steps"]
        ],
        "version": workflow["version"],
        "workflow": workflow["id"],
    }
    task = {
        "artifact_hashes": {},
        "completed_steps": [],
        "created_at": created_at,
        "current_step": None,
        "data": [],
        "id": task_id,
        "input": dict(input_record) if input_record is not None else None,
        "input_mode": input_mode,
        "outcome": None,
        "question": question,
        "security_query": security_query,
        "schema_version": "1.0",
        "skills": [record["name"] for record in installed_skills],
        "specs": [record["name"] for record in loaded_specs],
        "status": "created",
        "updated_at": created_at,
        "warnings": [],
        "workflow": {"id": workflow["id"], "version": workflow["version"]},
    }
    store.write_text(task_path, "question.md", _question_markdown(question))
    store.write_json(task_path, "plan.json", plan)
    store.write_json(task_path, "loaded-specs.json", {"specs": loaded_specs})
    store.write_json(task_path, "installed-skills.json", {"skills": installed_skills})
    store.write_json(
        task_path,
        "sources.json",
        {"input_mode": input_mode, "schema_version": "1.0", "sources": []},
    )
    store.write_json(
        task_path,
        "assumptions.json",
        {"assumptions": [], "input_mode": input_mode, "schema_version": "1.0"},
    )
    store.write_json(
        task_path,
        "findings.json",
        {
            "capabilities": {},
            "findings": [],
            "input_mode": input_mode,
            "schema_version": "1.0",
        },
    )
    store.write_json(
        task_path,
        "risks.json",
        {
            "input_mode": input_mode,
            "risks": [],
            "schema_version": "1.0",
            "unknowns": [],
            "warnings": [],
        },
    )
    store.write_json(task_path, "task.json", task)
    store.append_event(
        task_path,
        {
            "event": "task",
            "input_mode": input_mode,
            "status": "created",
            "timestamp": created_at,
        },
    )
    return task, plan


def _execute(
    store: TaskStore,
    task_path: Path,
    provider: Provider,
    context: MutableMapping[str, Any],
    *,
    resumed: bool,
) -> ResearchResult:
    task = _mutable_mapping(context["task"], "task")
    plan = _mutable_mapping(context["plan"], "plan")
    task.update(
        {"current_step": None, "outcome": None, "status": "running", "updated_at": utc_now()}
    )
    store.write_json(task_path, "task.json", task)
    store.append_event(
        task_path,
        {
            "event": "task",
            "input_mode": _context_input_mode(context),
            "resumed": resumed,
            "status": "running",
            "timestamp": task["updated_at"],
        },
    )

    for step in plan["steps"]:
        step_id = str(step["id"])
        if step.get("status") == "completed":
            result = _validate_completed_step(store, task_path, step_id)
            _capability_results(context)[step_id] = result
            store.append_event(
                task_path,
                {
                    "event": "step",
                    "status": "resume-skipped",
                    "step": step_id,
                    "timestamp": utc_now(),
                },
            )
            continue

        started_at = utc_now()
        step.update({"error": None, "started_at": started_at, "status": "running"})
        task.update({"current_step": step_id, "status": "running", "updated_at": started_at})
        store.write_json(task_path, "plan.json", plan)
        store.write_json(task_path, "task.json", task)
        store.append_event(
            task_path,
            {"event": "step", "status": "running", "step": step_id, "timestamp": started_at},
        )
        try:
            result = _execute_step(step_id, store, task_path, provider, context)
            if result["status"] == "failed":
                raise ResearchTaskError(f"capability failed: {step_id}")
        except Exception as error:
            message = safe_error_message(error)
            failed_at = utc_now()
            step.update({"error": message, "failed_at": failed_at, "status": "failed"})
            task.update(
                {
                    "current_step": step_id,
                    "outcome": {"error": message, "status": "failed"},
                    "status": "failed",
                    "updated_at": failed_at,
                }
            )
            store.write_json(task_path, "plan.json", plan)
            store.write_json(task_path, "task.json", task)
            store.append_event(
                task_path,
                {
                    "error": message,
                    "event": "step",
                    "status": "failed",
                    "step": step_id,
                    "timestamp": failed_at,
                },
            )
            return ResearchResult(
                task_id=task_path.name,
                status="failed",
                task_path=task_path,
                error=message,
            )

        completed_at = utc_now()
        step.update({"completed_at": completed_at, "status": "completed"})
        completed_steps = list(task.get("completed_steps", []))
        if step_id not in completed_steps:
            completed_steps.append(step_id)
        task.update(
            {
                "completed_steps": completed_steps,
                "current_step": step_id,
                "updated_at": completed_at,
            }
        )
        store.write_json(task_path, "plan.json", plan)
        store.write_json(task_path, "task.json", task)
        store.append_event(
            task_path,
            {
                "capability_status": result["status"],
                "event": "step",
                "status": "completed",
                "step": step_id,
                "timestamp": completed_at,
            },
        )

    try:
        _complete_task(store, task_path, plan, task, context)
    except Exception as error:
        message = safe_error_message(error)
        failed_at = utc_now()
        task.update(
            {
                "current_step": None,
                "outcome": {"error": message, "status": "failed"},
                "status": "failed",
                "updated_at": failed_at,
            }
        )
        store.write_json(task_path, "task.json", task)
        store.append_event(
            task_path,
            {
                "error": message,
                "event": "task",
                "status": "failed",
                "timestamp": failed_at,
            },
        )
        return ResearchResult(
            task_id=task_path.name,
            status="failed",
            task_path=task_path,
            error=message,
        )
    return ResearchResult(
        task_id=task_path.name,
        status="completed",
        task_path=task_path,
        report_path=task_path / "report.md",
    )


def _execute_step(
    step_id: str,
    store: TaskStore,
    task_path: Path,
    provider: Provider,
    context: MutableMapping[str, Any],
) -> dict[str, Any]:
    if step_id == "security-identification":
        input_mode = _context_input_mode(context)
        query = _required_text(context.get("security_query"), "security query")
        identity = _provider_record(
            provider.identify_security(query), step_id, input_mode=input_mode
        )
        security_id = _required_text(identity.get("security_id"), "security ID")
        source_metadata = _provider_record(
            provider.get_source_metadata(security_id),
            step_id,
            input_mode=input_mode,
        )
        sources = _build_sources(
            source_metadata,
            _path_value(context["source_root"]),
            input_mode=input_mode,
        )
        context.update(
            {"identity": identity, "source_metadata": source_metadata, "sources": sources}
        )
        store.write_json(task_path, DATA_PATHS["identity"], identity)
        store.write_json(task_path, DATA_PATHS["source_metadata"], source_metadata)
        store.write_json(task_path, "sources.json", sources)
    else:
        security_id = _security_id(context)
        if step_id == "company-deep-research":
            _fetch_and_store(
                context,
                store,
                task_path,
                "profile",
                provider.get_security_profile(security_id),
                step_id,
            )
        elif step_id == "financial-statement-analysis":
            _fetch_and_store(
                context,
                store,
                task_path,
                "statements",
                provider.get_financial_statements(security_id),
                step_id,
            )
        elif step_id == "valuation-analysis":
            _fetch_and_store(
                context,
                store,
                task_path,
                "valuation_inputs",
                provider.get_valuation_inputs(security_id),
                step_id,
            )
            _fetch_and_store(
                context,
                store,
                task_path,
                "price_history",
                provider.get_price_history(security_id),
                step_id,
            )
        elif step_id == "comps-analysis":
            _fetch_and_store(
                context,
                store,
                task_path,
                "peers",
                provider.get_peer_comparables(security_id),
                step_id,
            )
        elif step_id == "earnings-analysis":
            _fetch_and_store(
                context,
                store,
                task_path,
                "earnings",
                provider.get_earnings_history(security_id),
                step_id,
            )
        elif step_id == "catalyst-analysis":
            _fetch_and_store(
                context,
                store,
                task_path,
                "catalysts",
                provider.get_catalyst_events(security_id),
                step_id,
            )

    result = run_capability(step_id, _analysis_inputs(context, step_id))
    method = _mutable_mapping(result.get("method"), "capability method")
    method["input_mode"] = _context_input_mode(context)
    validate_capability_result(result, expected=step_id)
    _validate_result_sources(result, _known_source_ids(context))
    if (
        _capability_must_complete(
            step_id,
            input_mode=_context_input_mode(context),
            prior=_capability_results(context),
        )
        and result["status"] != "completed"
    ):
        raise ResearchTaskError(f"mandatory capability did not complete: {step_id}")

    prospective = {**_capability_results(context), step_id: result}
    if step_id == "investment-report":
        report = render_report(
            task_id=task_path.name,
            question=str(context["question"]),
            identity=_mapping(context.get("identity"), "identity"),
            capability_results=prospective,
            sources=_mapping(context.get("sources"), "sources"),
            installed_skills=_record_sequence(context["installed_skills"], "installed Skills"),
            loaded_specs=_record_sequence(context["loaded_specs"], "loaded specs"),
            generation_time=utc_now(),
            input_mode=_context_input_mode(context),
            input_provenance=_mapping(
                context.get("input_record"), "input provenance"
            )
            if _context_input_mode(context) == "imported"
            else {},
        )
        store.write_text(task_path, "report.md", report)

    capability_path = f"capabilities/{step_id}.json"
    store.write_json(task_path, capability_path, result, overwrite=False)
    _capability_results(context)[step_id] = result
    _refresh_aggregate_artifacts(
        store,
        task_path,
        _capability_results(context),
        input_mode=_context_input_mode(context),
    )
    return result


def _fetch_and_store(
    context: MutableMapping[str, Any],
    store: TaskStore,
    task_path: Path,
    key: str,
    value: Mapping[str, Any],
    operation: str,
) -> None:
    record = _provider_record(
        value,
        operation,
        input_mode=_context_input_mode(context),
    )
    context[key] = record
    store.write_json(task_path, DATA_PATHS[key], record)


def _complete_task(
    store: TaskStore,
    task_path: Path,
    plan: Mapping[str, Any],
    task: MutableMapping[str, Any],
    context: Mapping[str, Any],
) -> None:
    data_directory = store.artifact_path(task_path, "data")
    data_files = sorted(
        path.relative_to(task_path).as_posix()
        for path in data_directory.glob("*.json")
        if path.is_file() and not path.is_symlink()
    )
    task.update(
        {
            "current_step": None,
            "data": data_files,
            "warnings": _all_warnings(context),
            "updated_at": utc_now(),
        }
    )
    store.write_json(task_path, "task.json", task)
    _validate_final_artifacts(store, task_path, plan)
    task["artifact_hashes"] = _artifact_hashes(store, task_path)
    completed_at = utc_now()
    task.update(
        {
            "outcome": {"report": "report.md", "status": "completed"},
            "status": "completed",
            "updated_at": completed_at,
        }
    )
    store.write_json(task_path, "task.json", task)
    store.append_event(
        task_path,
        {"event": "task", "status": "completed", "timestamp": completed_at},
    )


def _load_workflow(source_root: Path) -> dict[str, Any]:
    path = _source_file(source_root, WORKFLOW_PATH)
    try:
        workflow = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ResearchTaskError("company-deep-dive workflow definition is invalid") from error
    if not isinstance(workflow, dict) or workflow.get("id") != WORKFLOW_ID:
        raise ResearchTaskError("company-deep-dive workflow identity is invalid")
    steps = workflow.get("steps")
    if not isinstance(steps, list):
        raise ResearchTaskError("company-deep-dive workflow steps are invalid")
    identifiers = tuple(
        str(step.get("id", "")) if isinstance(step, Mapping) else "" for step in steps
    )
    if identifiers != EXPECTED_STEPS:
        raise ResearchTaskError("company-deep-dive workflow step order is invalid")
    for step in steps:
        identifier = str(step["id"])
        if step.get("output") != f"capabilities/{identifier}.json":
            raise ResearchTaskError("company-deep-dive workflow output mapping is invalid")
    if tuple(workflow.get("skills", [])) != EXPECTED_STEPS:
        raise ResearchTaskError("company-deep-dive Skill order is invalid")
    if set(workflow.get("specs", [])) != set(REQUIRED_SPECS):
        raise ResearchTaskError("company-deep-dive spec set is invalid")
    if not isinstance(workflow.get("version"), str) or not workflow["version"]:
        raise ResearchTaskError("company-deep-dive workflow version is missing")
    return workflow


def _load_specs(source_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for name in REQUIRED_SPECS:
        relative_path = Path("specs") / name
        path = _source_file(source_root, relative_path)
        match = SPEC_VERSION_RE.search(path.read_text(encoding="utf-8"))
        if not match:
            raise ResearchTaskError(f"research spec has no version: {name}")
        records.append(
            {
                "name": name,
                "path": relative_path.as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "version": match.group(1),
            }
        )
    return records


def _load_installed_skills(
    project_root: Path,
    source_root: Path,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    target_root = project_root / ".agents" / "skills"
    for name in EXPECTED_STEPS:
        canonical_root = source_root / "skills" / name
        files: list[dict[str, str]] = []
        for source in discover_skill_files(source_root, name):
            relative = source.relative_to(canonical_root)
            target_relative = Path(name) / relative
            target = target_root / target_relative
            if target.is_symlink() or not target.is_file():
                raise ResearchTaskError(
                    f"required installed Skill file is missing or unsafe: {target_relative.as_posix()}"
                )
            if not target.resolve().is_relative_to(target_root.resolve()):
                raise ResearchTaskError("installed Skill file escapes the Codex target")
            source_bytes = source.read_bytes()
            target_bytes = target.read_bytes()
            if target_bytes != source_bytes:
                raise ResearchTaskError(
                    f"installed Skill differs from first-party source: {target_relative.as_posix()}"
                )
            files.append(
                {
                    "path": target.relative_to(project_root).as_posix(),
                    "sha256": hashlib.sha256(target_bytes).hexdigest(),
                    "source_path": source.relative_to(source_root).as_posix(),
                }
            )
        skill_path = canonical_root / "SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        version_match = SKILL_VERSION_RE.search(text)
        records.append(
            {
                "files": files,
                "name": name,
                "path": f".agents/skills/{name}/SKILL.md",
                "sha256": hashlib.sha256(skill_path.read_bytes()).hexdigest(),
                "source_path": f"skills/{name}/SKILL.md",
                "version": version_match.group(1) if version_match else "unknown",
            }
        )
    return records


def _hydrate_context(
    store: TaskStore,
    task_path: Path,
    **base: Any,
) -> dict[str, Any]:
    context = dict(base)
    context["capability_results"] = {}
    for key, relative_path in DATA_PATHS.items():
        if store.artifact_is_file(task_path, relative_path):
            context[key] = store.read_json(task_path, relative_path)
    context["sources"] = store.read_json(task_path, "sources.json")
    plan = _mapping(context["plan"], "plan")
    for step in plan["steps"]:
        if step.get("status") == "completed":
            result = _validate_completed_step(store, task_path, str(step["id"]))
            _capability_results(context)[str(step["id"])] = result
    return context


def _validate_completed_step(
    store: TaskStore,
    task_path: Path,
    step_id: str,
) -> dict[str, Any]:
    if step_id not in EXPECTED_STEPS:
        raise CorruptTaskError("completed task contains an unknown capability stage")
    relative_path = f"capabilities/{step_id}.json"
    result = store.read_json(task_path, relative_path)
    if not isinstance(result, Mapping):
        raise CorruptTaskError(f"corrupt capability artifact: {step_id}")
    try:
        validate_capability_result(result, expected=step_id)
    except (TypeError, ValueError) as error:
        raise CorruptTaskError(f"corrupt capability artifact: {step_id}") from error
    if result.get("status") not in {"completed", "skipped"}:
        raise CorruptTaskError(f"completed stage has invalid capability status: {step_id}")
    if _persisted_capability_must_complete(store, task_path, step_id) and result.get(
        "status"
    ) != "completed":
        raise CorruptTaskError(f"mandatory capability is incomplete: {step_id}")
    sources = store.read_json(task_path, "sources.json")
    _validate_result_sources(result, _source_ids(sources))
    for required in STEP_DATA_REQUIREMENTS[step_id]:
        if not store.artifact_is_file(task_path, required):
            raise CorruptTaskError(
                f"completed stage {step_id} is missing {required}"
            )
        if Path(required).suffix == ".json":
            value = store.read_json(task_path, required)
            if not isinstance(value, Mapping):
                raise CorruptTaskError(f"corrupt task artifact: {required}")
        elif not store.read_text(task_path, required).strip():
            raise CorruptTaskError(f"empty task artifact: {required}")
    return dict(result)


def _capability_must_complete(
    capability: str,
    *,
    input_mode: str,
    prior: Mapping[str, Any],
) -> bool:
    """Apply mandatory completion only where the evidence makes it meaningful."""

    if capability not in MANDATORY_COMPLETED_CAPABILITIES:
        return False
    if capability != "bear-case-analysis":
        return True
    if input_mode == "demo":
        return True
    thesis = prior.get("investment-thesis")
    return isinstance(thesis, Mapping) and thesis.get("status") == "completed"


def _persisted_capability_must_complete(
    store: TaskStore,
    task_path: Path,
    capability: str,
) -> bool:
    """Evaluate the conditional bear-case gate from durable artifacts."""

    if capability not in MANDATORY_COMPLETED_CAPABILITIES:
        return False
    if capability != "bear-case-analysis":
        return True
    thesis = store.read_json(task_path, "capabilities/investment-thesis.json")
    if not isinstance(thesis, Mapping):
        raise CorruptTaskError("corrupt capability artifact: investment-thesis")
    return thesis.get("status") == "completed"


def _validate_final_artifacts(
    store: TaskStore,
    task_path: Path,
    plan: Mapping[str, Any],
) -> None:
    if any(step.get("status") != "completed" for step in plan["steps"]):
        raise ResearchTaskError("completed workflow has incomplete stages")
    for relative_path in REQUIRED_COMPLETED_ARTIFACTS:
        if not store.artifact_is_file(task_path, relative_path):
            raise ResearchTaskError(f"required task artifact is missing: {relative_path}")
        if Path(relative_path).suffix == ".json":
            store.read_json(task_path, relative_path)
        elif not store.read_text(task_path, relative_path).strip():
            raise ResearchTaskError(f"required task artifact is empty: {relative_path}")
    task = _mapping(store.read_json(task_path, "task.json"), "task")
    if _task_input_mode(task) == "imported":
        _validate_imported_snapshot(store, task_path, task)
    for step_id in EXPECTED_STEPS:
        _validate_completed_step(store, task_path, step_id)
    actual = {
        path.stem
        for path in store.artifact_path(task_path, "capabilities").glob("*.json")
        if path.is_file() and not path.is_symlink()
    }
    if actual != set(EXPECTED_STEPS):
        raise ResearchTaskError("capability artifact set is incomplete or unexpected")
    _validate_report_materials(store, task_path)


def _validate_completed_task(
    store: TaskStore,
    task_path: Path,
    plan: Mapping[str, Any],
    task: Mapping[str, Any],
) -> None:
    try:
        _validate_final_artifacts(store, task_path, plan)
    except ResearchTaskError as error:
        raise CorruptTaskError(str(error)) from error
    data_references = task.get("data")
    if not isinstance(data_references, list) or not data_references:
        raise CorruptTaskError("completed task has no persisted data references")
    expected_data = set(DATA_PATHS.values())
    if set(data_references) != expected_data or len(data_references) != len(expected_data):
        raise CorruptTaskError("completed task has an incomplete data manifest")
    for relative_path in data_references:
        if (
            not isinstance(relative_path, str)
            or not relative_path.startswith("data/")
            or not store.artifact_is_file(task_path, relative_path)
        ):
            raise CorruptTaskError("completed task has an invalid data reference")
    data_directory = store.artifact_path(task_path, "data")
    actual_data: set[str] = set()
    for path in data_directory.iterdir():
        if path.is_symlink():
            raise CorruptTaskError("completed task data contains an unsafe symlink")
        if path.is_file():
            actual_data.add(path.relative_to(task_path).as_posix())
    if actual_data != expected_data:
        raise CorruptTaskError("completed task data set is incomplete or unexpected")
    if tuple(task.get("completed_steps", [])) != EXPECTED_STEPS:
        raise CorruptTaskError("completed task has an inconsistent step manifest")
    if task.get("current_step") is not None:
        raise CorruptTaskError("completed task still names a current step")
    outcome = task.get("outcome")
    if not isinstance(outcome, Mapping) or outcome.get("report") != "report.md":
        raise CorruptTaskError("completed task has an invalid report reference")
    expected_hashes = task.get("artifact_hashes")
    if not isinstance(expected_hashes, Mapping) or not expected_hashes:
        raise CorruptTaskError("completed task has no immutable artifact hashes")
    actual_hashes = _artifact_hashes(store, task_path)
    if dict(expected_hashes) != actual_hashes:
        raise CorruptTaskError("completed task immutable artifact hash mismatch")


def _task_input_mode(task: Mapping[str, Any]) -> str:
    """Interpret pre-v0.3 tasks as demo without rewriting durable state."""

    mode = task.get("input_mode", "demo")
    if mode not in {"demo", "imported"}:
        raise CorruptTaskError("corrupt task record: unsupported input mode")
    return str(mode)


def _validate_imported_snapshot(
    store: TaskStore,
    task_path: Path,
    task: Mapping[str, Any],
) -> dict[str, Any]:
    if _task_input_mode(task) == "demo":
        return {}
    record = task.get("input")
    if not isinstance(record, Mapping):
        raise CorruptTaskError("imported task has no persisted input record")
    if record.get("snapshot") != IMPORTED_BUNDLE_PATH:
        raise CorruptTaskError("imported task has an invalid bundle snapshot path")
    expected_hash = str(record.get("sha256", ""))
    if not SHA256_RE.fullmatch(expected_hash):
        raise CorruptTaskError("imported task has an invalid bundle snapshot hash")
    path = store.artifact_path(task_path, IMPORTED_BUNDLE_PATH)
    if not path.is_file() or path.is_symlink():
        raise CorruptTaskError("imported task bundle snapshot is missing or unsafe")
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        raise CorruptTaskError("persisted research bundle snapshot hash mismatch")
    if not isinstance(record.get("bundle_version"), str) or not record["bundle_version"]:
        raise CorruptTaskError("imported task has no bundle version")
    try:
        provider = FileProvider(store.project_root, path)
    except (BundleInputError, BundleValidationError) as error:
        raise CorruptTaskError("persisted research bundle snapshot is invalid") from error
    if provider.bundle_sha256 != expected_hash:
        raise CorruptTaskError("persisted research bundle canonical hash mismatch")
    if provider.bundle.get("bundle_version") != record["bundle_version"]:
        raise CorruptTaskError("persisted research bundle version mismatch")
    return dict(record)


def _validate_imported_provider_state(
    store: TaskStore,
    task_path: Path,
    task: Mapping[str, Any],
    provider: FileProvider,
) -> None:
    """Prove every persisted imported Provider record still equals the snapshot."""

    query = _required_text(task.get("security_query"), "security query")
    identity = _provider_record(
        provider.identify_security(query),
        "identify_security",
        input_mode="imported",
    )
    security_id = _required_text(identity.get("security_id"), "security ID")
    source_metadata = _provider_record(
        provider.get_source_metadata(security_id),
        "get_source_metadata",
        input_mode="imported",
    )
    expected: dict[str, dict[str, Any]] = {
        DATA_PATHS["identity"]: identity,
        DATA_PATHS["source_metadata"]: source_metadata,
        DATA_PATHS["profile"]: _provider_record(
            provider.get_security_profile(security_id),
            "get_security_profile",
            input_mode="imported",
        ),
        DATA_PATHS["statements"]: _provider_record(
            provider.get_financial_statements(security_id),
            "get_financial_statements",
            input_mode="imported",
        ),
        DATA_PATHS["price_history"]: _provider_record(
            provider.get_price_history(security_id),
            "get_price_history",
            input_mode="imported",
        ),
        DATA_PATHS["valuation_inputs"]: _provider_record(
            provider.get_valuation_inputs(security_id),
            "get_valuation_inputs",
            input_mode="imported",
        ),
        DATA_PATHS["peers"]: _provider_record(
            provider.get_peer_comparables(security_id),
            "get_peer_comparables",
            input_mode="imported",
        ),
        DATA_PATHS["earnings"]: _provider_record(
            provider.get_earnings_history(security_id),
            "get_earnings_history",
            input_mode="imported",
        ),
        DATA_PATHS["catalysts"]: _provider_record(
            provider.get_catalyst_events(security_id),
            "get_catalyst_events",
            input_mode="imported",
        ),
    }
    data_root = store.artifact_path(task_path, "data")
    if not data_root.is_dir() or data_root.is_symlink():
        raise CorruptTaskError("imported task Provider data directory is unsafe")
    allowed_names = {Path(relative).name for relative in expected}
    for path in data_root.iterdir():
        if path.is_symlink() or not path.is_file() or path.name not in allowed_names:
            raise CorruptTaskError("imported task contains unexpected Provider data")
    for relative_path, expected_record in expected.items():
        if not store.artifact_is_file(task_path, relative_path):
            continue
        if store.read_json(task_path, relative_path) != expected_record:
            raise CorruptTaskError(
                f"imported Provider data differs from the persisted snapshot: {relative_path}"
            )
    expected_sources = {
        "input_mode": "imported",
        "schema_version": "1.0",
        "sources": source_metadata.get("sources"),
    }
    if store.artifact_is_file(task_path, "sources.json") and (
        store.read_json(task_path, "sources.json") != expected_sources
    ):
        raise CorruptTaskError(
            "imported source registry differs from the persisted snapshot"
        )


def _validate_imported_completed_capabilities(
    store: TaskStore,
    task_path: Path,
    context: MutableMapping[str, Any],
    plan: Mapping[str, Any],
) -> None:
    """Reproduce every completed imported result before trusting failed state."""

    verification_context = dict(context)
    verification_context["capability_results"] = {}
    verified_results: dict[str, Any] = {}
    steps = plan.get("steps")
    if not isinstance(steps, list):
        raise CorruptTaskError("corrupt imported task plan")
    for step in steps:
        if not isinstance(step, Mapping) or step.get("status") != "completed":
            continue
        step_id = str(step.get("id", ""))
        persisted = _validate_completed_step(store, task_path, step_id)
        try:
            expected = run_capability(
                step_id,
                _analysis_inputs(verification_context, step_id),
            )
            method = _mutable_mapping(
                expected.get("method"), "reproduced capability method"
            )
            method["input_mode"] = "imported"
            validate_capability_result(expected, expected=step_id)
            _validate_result_sources(
                expected,
                _known_source_ids(verification_context),
            )
        except Exception as error:
            raise CorruptTaskError(
                f"completed imported capability cannot be reproduced: {step_id}"
            ) from error
        if expected != persisted:
            raise CorruptTaskError(
                f"completed imported capability differs from derived evidence: {step_id}"
            )
        verified_results[step_id] = expected
        _capability_results(verification_context)[step_id] = expected
    _capability_results(context).update(verified_results)


def _validate_report_materials(store: TaskStore, task_path: Path) -> None:
    results = {
        step_id: store.read_json(task_path, f"capabilities/{step_id}.json")
        for step_id in EXPECTED_STEPS
    }
    prior_ids: set[str] = set()
    prior_sources: set[str] = set()
    for step_id in EXPECTED_STEPS[:-1]:
        result = _mapping(results[step_id], step_id)
        prior_sources.update(str(value) for value in result.get("source_ids", []))
        for field in ("facts", "assumptions", "estimates", "unknowns", "findings", "risks"):
            for record in result.get(field, []):
                if isinstance(record, Mapping) and record.get("id"):
                    prior_ids.add(str(record["id"]))
    report_result = _mapping(results["investment-report"], "investment report")
    method = _mapping(report_result.get("method"), "investment report method")
    emitted_ids = set(str(value) for value in method.get("emitted_claim_ids", []))
    emitted_sources = set(str(value) for value in method.get("emitted_source_ids", []))
    if not emitted_ids.issubset(prior_ids) or not emitted_sources.issubset(prior_sources):
        raise ResearchTaskError("investment report introduces unstructured material")
    report = store.read_text(task_path, "report.md")
    if not report.strip():
        raise ResearchTaskError("investment report is empty")


def _refresh_aggregate_artifacts(
    store: TaskStore,
    task_path: Path,
    results: Mapping[str, Mapping[str, Any]],
    *,
    input_mode: str,
) -> None:
    findings: list[dict[str, Any]] = []
    assumptions: list[dict[str, Any]] = []
    risks: list[dict[str, Any]] = []
    unknowns: list[dict[str, Any]] = []
    warnings: list[str] = []
    capability_index: dict[str, dict[str, Any]] = {}
    for capability in EXPECTED_STEPS:
        result = results.get(capability)
        if not isinstance(result, Mapping):
            continue
        capability_index[capability] = {
            "artifact": f"capabilities/{capability}.json",
            "status": result.get("status"),
        }
        findings.extend(_tagged_records(result.get("findings"), capability))
        assumptions.extend(_tagged_records(result.get("assumptions"), capability))
        risks.extend(_tagged_records(result.get("risks"), capability))
        unknowns.extend(_tagged_records(result.get("unknowns"), capability))
        for warning in result.get("warnings", []):
            text = str(warning).strip()
            if text and text not in warnings:
                warnings.append(text)
    store.write_json(
        task_path,
        "findings.json",
        {
            "capabilities": capability_index,
            "findings": findings,
            "input_mode": input_mode,
            "schema_version": "1.0",
        },
    )
    store.write_json(
        task_path,
        "assumptions.json",
        {
            "assumptions": assumptions,
            "input_mode": input_mode,
            "schema_version": "1.0",
        },
    )
    store.write_json(
        task_path,
        "risks.json",
        {
            "risks": risks,
            "input_mode": input_mode,
            "schema_version": "1.0",
            "unknowns": unknowns,
            "warnings": warnings,
        },
    )


def _tagged_records(value: Any, capability: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ResearchTaskError(f"invalid {capability} aggregate records")
    records: list[dict[str, Any]] = []
    for record in value:
        if not isinstance(record, Mapping):
            raise ResearchTaskError(f"invalid {capability} aggregate record")
        records.append({"capability": capability, **dict(record)})
    return records


def _artifact_hashes(store: TaskStore, task_path: Path) -> dict[str, str]:
    relative_paths = [
        "question.md",
        "plan.json",
        "loaded-specs.json",
        "installed-skills.json",
        "sources.json",
        "assumptions.json",
        "findings.json",
        "risks.json",
        "report.md",
        *[DATA_PATHS[key] for key in DATA_PATHS],
        *[f"capabilities/{step_id}.json" for step_id in EXPECTED_STEPS],
    ]
    if store.artifact_is_file(task_path, IMPORTED_BUNDLE_PATH):
        relative_paths.append(IMPORTED_BUNDLE_PATH)
    hashes: dict[str, str] = {}
    for relative_path in sorted(relative_paths):
        path = store.artifact_path(task_path, relative_path)
        if not path.is_file():
            raise ResearchTaskError(f"cannot hash missing task artifact: {relative_path}")
        hashes[relative_path] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def _build_sources(
    source_metadata: Mapping[str, Any],
    source_root: Path,
    *,
    input_mode: str,
) -> dict[str, Any]:
    if input_mode == "imported":
        raw_sources = source_metadata.get("sources")
        if not isinstance(raw_sources, list) or not raw_sources:
            raise ResearchTaskError("imported source registry is missing or empty")
        records: list[dict[str, Any]] = []
        seen: set[str] = set()
        for value in raw_sources:
            if not isinstance(value, Mapping):
                raise ResearchTaskError("imported source registry contains an invalid record")
            source_id = _required_text(value.get("source_id"), "source ID")
            if source_id in seen:
                raise ResearchTaskError("imported source registry contains duplicate IDs")
            seen.add(source_id)
            records.append(dict(value))
        return {
            "input_mode": "imported",
            "schema_version": "1.0",
            "sources": records,
        }
    if input_mode != "demo":
        raise ResearchTaskError("unsupported workflow input mode")
    fixture = _source_file(source_root, FIXTURE_PATH)
    source_id = _required_text(source_metadata.get("source_id"), "source ID")
    record = {
        **dict(source_metadata),
        "artifacts": list(DATA_PATHS.values()),
        "canonical_path": FIXTURE_PATH.as_posix(),
        "sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
        "source_id": source_id,
    }
    return {"input_mode": "demo", "schema_version": "1.0", "sources": [record]}


def _analysis_inputs(context: Mapping[str, Any], capability: str) -> dict[str, Any]:
    inputs = {
        key: context[key]
        for key in (
            "identity",
            "profile",
            "statements",
            "price_history",
            "valuation_inputs",
            "peers",
            "earnings",
            "catalysts",
            "source_metadata",
            "sources",
            "capability_results",
        )
        if key in context
    }
    inputs["input_mode"] = _context_input_mode(context)
    input_record = context.get("input_record")
    inputs["evidence_origin"] = (
        input_record.get("acquisition_mode", "user_imported")
        if isinstance(input_record, Mapping)
        else "user_imported"
    )
    source_keys = {
        "security-identification": ("identity",),
        "company-deep-research": ("profile",),
        "business-model-analysis": ("profile",),
        "financial-statement-analysis": ("statements",),
        "earnings-quality-analysis": ("statements",),
        "valuation-analysis": ("price_history", "valuation_inputs"),
        "comps-analysis": ("peers",),
        "earnings-analysis": ("earnings",),
        "catalyst-analysis": ("catalysts",),
    }.get(capability)
    if source_keys is not None:
        active_source_ids: set[str] = set()
        for source_key in source_keys:
            record = context.get(source_key)
            if not isinstance(record, Mapping):
                continue
            source_ids = record.get("source_ids", [])
            if not isinstance(source_ids, list) or not all(
                isinstance(source_id, str) and source_id.strip()
                for source_id in source_ids
            ):
                raise ResearchTaskError(
                    f"provider record for {source_key} has invalid source IDs"
                )
            active_source_ids.update(source_id.strip() for source_id in source_ids)
        inputs["active_source_ids"] = sorted(active_source_ids)
    return inputs


def _provider_record(
    value: Any,
    operation: str,
    *,
    input_mode: str,
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ResearchTaskError(f"provider returned an invalid record for {operation}")
    missing = REQUIRED_PROVIDER_METADATA - set(value)
    if missing:
        raise ResearchTaskError(
            f"provider record for {operation} is missing: {', '.join(sorted(missing))}"
        )
    expected_demo = input_mode == "demo"
    if value.get("is_demo") is not expected_demo:
        raise ResearchTaskError("provider record input mode does not match the workflow")
    if not expected_demo:
        if value.get("input_mode") != "imported":
            raise ResearchTaskError("imported provider record has no imported mode marker")
        if not SHA256_RE.fullmatch(str(value.get("bundle_sha256", ""))):
            raise ResearchTaskError("imported provider record has no valid bundle hash")
        source_ids = value.get("source_ids")
        if not isinstance(source_ids, list) or not all(
            isinstance(source_id, str) and source_id for source_id in source_ids
        ):
            raise ResearchTaskError("imported provider record has invalid source IDs")
    for field in ("as_of_date", "currency", "market", "source"):
        _required_text(value.get(field), f"provider {field}")
    if not value.get("fixture_version") and not value.get("retrieved_at"):
        raise ResearchTaskError(f"provider record for {operation} has no version or retrieval time")
    warnings = value.get("warnings")
    if not isinstance(warnings, list) or not warnings:
        raise ResearchTaskError(f"provider record for {operation} has no warnings")
    return dict(value)


def _validate_result_sources(result: Mapping[str, Any], known_ids: set[str]) -> None:
    if not known_ids:
        raise ResearchTaskError("capability result has no persisted source registry")
    for field in ("facts", "findings", "risks"):
        records = result.get(field, [])
        if not isinstance(records, list):
            raise ResearchTaskError(f"capability result has invalid {field}")
        for record in records:
            if not isinstance(record, Mapping):
                raise ResearchTaskError(f"capability result has invalid {field} record")
            references = {str(value) for value in record.get("source_ids", [])}
            if not references.issubset(known_ids):
                raise ResearchTaskError("capability result references an unknown source ID")
    result_sources = {str(value) for value in result.get("source_ids", [])}
    if not result_sources.issubset(known_ids):
        raise ResearchTaskError("capability result source union is unresolved")


def _known_source_ids(context: Mapping[str, Any]) -> set[str]:
    return _source_ids(context.get("sources"))


def _source_ids(value: Any) -> set[str]:
    if not isinstance(value, Mapping) or not isinstance(value.get("sources"), list):
        raise ResearchTaskError("persisted source registry is invalid")
    return {
        str(record["source_id"])
        for record in value["sources"]
        if isinstance(record, Mapping) and record.get("source_id")
    }


def _validated_task(value: Any, task_id: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CorruptTaskError("corrupt task record: task.json must be an object")
    if value.get("id") != task_id:
        raise CorruptTaskError("corrupt task record: task ID does not match directory")
    if value.get("status") not in {"created", "running", "failed", "completed"}:
        raise CorruptTaskError("corrupt task record: invalid status")
    return value


def _validated_plan(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or not isinstance(value.get("steps"), list):
        raise CorruptTaskError("corrupt task plan")
    if value.get("workflow") != WORKFLOW_ID or not isinstance(value.get("version"), str):
        raise CorruptTaskError("corrupt task plan: workflow identity is invalid")
    identifiers = tuple(
        str(step.get("id", "")) if isinstance(step, Mapping) else ""
        for step in value["steps"]
    )
    if identifiers != EXPECTED_STEPS:
        raise CorruptTaskError("corrupt task plan: workflow step order is invalid")
    for step in value["steps"]:
        if step.get("status") not in {"pending", "running", "failed", "completed"}:
            raise CorruptTaskError("corrupt task plan: invalid step status")
        identifier = str(step["id"])
        if step.get("output") != f"capabilities/{identifier}.json":
            raise CorruptTaskError("corrupt task plan: invalid capability output")
    return value


def _validate_task_snapshots(
    task: Mapping[str, Any],
    question: str,
    plan: Mapping[str, Any],
) -> None:
    if task.get("question") != question:
        raise CorruptTaskError("corrupt task record: research question does not match")
    mode = _task_input_mode(task)
    if plan.get("input_mode", "demo") != mode:
        raise CorruptTaskError("corrupt task record: plan input mode is inconsistent")
    query = task.get("security_query", "demo")
    if not isinstance(query, str) or not query.strip():
        raise CorruptTaskError("corrupt task record: security query is missing")
    if tuple(task.get("skills", [])) != EXPECTED_STEPS:
        raise CorruptTaskError("corrupt task record: installed Skill snapshot is invalid")
    if set(task.get("specs", [])) != set(REQUIRED_SPECS):
        raise CorruptTaskError("corrupt task record: loaded spec snapshot is invalid")
    plan_steps = plan.get("steps")
    if not isinstance(plan_steps, list):
        raise CorruptTaskError("corrupt task record: plan steps are invalid")
    completed_steps: list[str] = []
    encountered_incomplete = False
    for step in plan_steps:
        status = step.get("status")
        if status == "completed":
            if encountered_incomplete:
                raise CorruptTaskError(
                    "corrupt task record: completed steps are not an ordered prefix"
                )
            completed_steps.append(str(step["id"]))
        else:
            encountered_incomplete = True
    task_completed = task.get("completed_steps")
    if not isinstance(task_completed, list) or task_completed != completed_steps:
        raise CorruptTaskError(
            "corrupt task record: completed step manifest does not match the plan"
        )
    workflow = task.get("workflow")
    if (
        not isinstance(workflow, Mapping)
        or workflow.get("id") != plan.get("workflow")
        or workflow.get("version") != plan.get("version")
    ):
        raise CorruptTaskError("corrupt task record: workflow snapshot is inconsistent")


def _validate_snapshot_records(
    loaded_specs: Sequence[Mapping[str, Any]],
    installed_skills: Sequence[Mapping[str, Any]],
) -> None:
    spec_names = [str(record.get("name", "")) for record in loaded_specs]
    skill_names = [str(record.get("name", "")) for record in installed_skills]
    if len(spec_names) != len(set(spec_names)) or set(spec_names) != set(REQUIRED_SPECS):
        raise CorruptTaskError("corrupt task artifact: loaded spec set is invalid")
    if tuple(skill_names) != EXPECTED_STEPS:
        raise CorruptTaskError("corrupt task artifact: installed Skill set is invalid")
    for record in loaded_specs:
        name = str(record["name"])
        if (
            record.get("path") != f"specs/{name}"
            or not isinstance(record.get("version"), str)
            or not record.get("version")
            or not SHA256_RE.fullmatch(str(record.get("sha256", "")))
        ):
            raise CorruptTaskError(f"corrupt task artifact: invalid spec record {name}")
    for record in installed_skills:
        name = str(record["name"])
        files = record.get("files")
        if (
            record.get("path") != f".agents/skills/{name}/SKILL.md"
            or record.get("source_path") != f"skills/{name}/SKILL.md"
            or not isinstance(record.get("version"), str)
            or not record.get("version")
            or not SHA256_RE.fullmatch(str(record.get("sha256", "")))
            or not isinstance(files, list)
            or not files
        ):
            raise CorruptTaskError(f"corrupt task artifact: invalid Skill record {name}")
        for file_record in files:
            if (
                not isinstance(file_record, Mapping)
                or not str(file_record.get("path", "")).startswith(f".agents/skills/{name}/")
                or not str(file_record.get("source_path", "")).startswith(f"skills/{name}/")
                or not SHA256_RE.fullmatch(str(file_record.get("sha256", "")))
            ):
                raise CorruptTaskError(f"corrupt task artifact: invalid Skill file {name}")


def _snapshot_signature(records: Sequence[Mapping[str, Any]]) -> str:
    return json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _question_markdown(question: str) -> str:
    """Render a reversible Markdown code view without active markup or URLs."""

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


def _read_question(
    store: TaskStore,
    task_path: Path,
    *,
    allow_legacy: bool,
) -> str:
    raw = store.read_text(task_path, "question.md")
    prefix = "# Research Question\n\n    "
    if raw.startswith(prefix) and raw.endswith("\n"):
        encoded = raw[len(prefix) : -1]
        if "\n" in encoded:
            raise CorruptTaskError("corrupt task artifact: question.md")
        try:
            value = json.loads(encoded)
        except json.JSONDecodeError as error:
            raise CorruptTaskError("corrupt task artifact: question.md") from error
        if (
            not isinstance(value, str)
            or not value.strip()
            or _question_markdown(value) != raw
        ):
            raise CorruptTaskError("corrupt task artifact: question.md")
        return value
    if allow_legacy:
        text = raw.strip()
        if text.startswith("# Research Question"):
            text = text[len("# Research Question") :].strip()
        if text:
            return text
    raise CorruptTaskError("corrupt task artifact: question.md")


def _record_list(value: Any, key: str) -> list[dict[str, Any]]:
    if not isinstance(value, Mapping) or not isinstance(value.get(key), list):
        raise CorruptTaskError(f"corrupt task artifact: expected {key} records")
    records = value[key]
    if not all(isinstance(record, dict) for record in records):
        raise CorruptTaskError(f"corrupt task artifact: invalid {key} records")
    return records


def _capability_results(context: MutableMapping[str, Any]) -> dict[str, Any]:
    value = context.get("capability_results")
    if not isinstance(value, dict):
        raise ResearchTaskError("capability result context is invalid")
    return value


def _security_id(context: Mapping[str, Any]) -> str:
    identity = _mapping(context.get("identity"), "security identity")
    return _required_text(identity.get("security_id"), "security ID")


def _all_warnings(context: Mapping[str, Any]) -> list[str]:
    warnings: list[str] = []
    for key in DATA_PATHS:
        record = context.get(key)
        if not isinstance(record, Mapping):
            continue
        for warning in record.get("warnings", []):
            text = str(warning).strip()
            if text and text not in warnings:
                warnings.append(text)
    return warnings


def _context_input_mode(context: Mapping[str, Any]) -> str:
    mode = context.get("input_mode", "demo")
    if mode not in {"demo", "imported"}:
        raise ResearchTaskError("workflow input mode is invalid")
    return str(mode)


def _initialized_task_store(project_root: str | Path) -> TaskStore:
    """Open task storage only after immutable initialization markers exist."""

    try:
        project = resolved_root(project_root)
        required_files = (
            ".investkit/config.json",
            ".investkit/install-manifest.json",
            ".agents/investkit.json",
        )
        if any(not resolve_within(project, relative).is_file() for relative in required_files):
            raise ResearchTaskError("project is not initialized")
        research_root = resolve_within(project, "workspace/research")
        if not research_root.is_dir():
            raise ResearchTaskError("project is not initialized")
    except ResearchTaskError:
        raise
    except Exception as error:
        raise ResearchTaskError(
            "project is not initialized; run investkit init first"
        ) from error
    return TaskStore(project)


def _mapping(value: Any, description: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ResearchTaskError(f"missing or invalid {description}")
    return value


def _mutable_mapping(value: Any, description: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ResearchTaskError(f"missing or invalid {description}")
    return value


def _record_sequence(value: Any, description: str) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ResearchTaskError(f"missing or invalid {description}")
    if not all(isinstance(record, Mapping) for record in value):
        raise ResearchTaskError(f"invalid {description}")
    return list(value)


def _required_text(value: Any, description: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ResearchTaskError(f"missing or invalid {description}")
    return value.strip()


def _source_root(value: str | Path) -> Path:
    try:
        return resolve_source_root(value)
    except Exception as error:
        raise ResearchTaskError("first-party source root is missing or inaccessible") from error


def _source_file(source_root: Path, relative_path: Path) -> Path:
    try:
        return validated_source_file(source_root, relative_path)
    except Exception as error:
        raise ResearchTaskError(
            f"required first-party asset is missing: {relative_path.as_posix()}"
        ) from error


def _path_value(value: Any) -> Path:
    if not isinstance(value, Path):
        raise ResearchTaskError("source root context is invalid")
    return value
