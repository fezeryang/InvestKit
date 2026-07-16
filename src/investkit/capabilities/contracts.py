"""Schema construction and validation for persisted capability results."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "1.0"
VALID_STATUSES = frozenset({"completed", "skipped", "failed"})
BASE_FIELDS = frozenset(
    {
        "schema_version",
        "capability",
        "status",
        "skill",
        "method",
        "facts",
        "assumptions",
        "estimates",
        "unknowns",
        "findings",
        "risks",
        "warnings",
        "source_ids",
    }
)


def build_capability_result(
    capability: str,
    *,
    status: str,
    skill: Mapping[str, str],
    method: Mapping[str, Any],
    facts: Sequence[Mapping[str, Any]] = (),
    assumptions: Sequence[Mapping[str, Any]] = (),
    estimates: Sequence[Mapping[str, Any]] = (),
    unknowns: Sequence[Mapping[str, Any] | str] = (),
    findings: Sequence[Mapping[str, Any] | str] = (),
    risks: Sequence[Mapping[str, Any] | str] = (),
    warnings: Sequence[str] = (),
    skip_reason: str | None = None,
    missing_inputs: Sequence[str] = (),
) -> dict[str, Any]:
    """Build and validate one JSON-safe capability result envelope."""

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "capability": capability,
        "status": status,
        "skill": deepcopy(dict(skill)),
        "method": deepcopy(dict(method)),
        "facts": _copy_mappings(facts, "facts"),
        "assumptions": _copy_mappings(assumptions, "assumptions"),
        "estimates": _copy_mappings(estimates, "estimates"),
        "unknowns": _copy_records(unknowns, "unknown"),
        "findings": _copy_records(findings, "finding"),
        "risks": _copy_records(risks, "risk"),
        "warnings": _clean_strings(warnings, "warnings"),
        "source_ids": [],
    }
    result["source_ids"] = _referenced_sources(result)
    if status == "skipped" or skip_reason is not None or missing_inputs:
        result["skip_reason"] = str(skip_reason or "").strip()
        result["missing_inputs"] = _clean_strings(missing_inputs, "missing_inputs")
    validate_capability_result(result, expected=capability)
    return result


def validate_capability_result(
    value: Mapping[str, Any],
    *,
    expected: str,
) -> None:
    """Reject malformed, ambiguous, or internally inconsistent results."""

    if not isinstance(value, Mapping):
        raise TypeError("capability result must be a mapping")
    required = set(BASE_FIELDS)
    missing = required - set(value)
    if missing:
        raise ValueError(f"capability result is missing fields: {sorted(missing)}")
    status = value.get("status")
    if status not in VALID_STATUSES:
        raise ValueError("capability status must be completed, skipped, or failed")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported capability result schema version")
    if value.get("capability") != expected:
        raise ValueError("capability result does not match the expected capability")

    _validate_version_record(value.get("skill"), "skill")
    _validate_version_record(value.get("method"), "method")
    facts = _record_list(value.get("facts"), "facts")
    assumptions = _record_list(value.get("assumptions"), "assumptions")
    estimates = _record_list(value.get("estimates"), "estimates")
    unknowns = _record_list(value.get("unknowns"), "unknowns")
    _record_list(value.get("findings"), "findings")
    _record_list(value.get("risks"), "risks")
    warnings = value.get("warnings")
    if not isinstance(warnings, list) or not all(_nonempty_string(item) for item in warnings):
        raise TypeError("warnings must be a list of non-empty strings")

    for fact in facts:
        _require_nonempty(fact, ("id", "statement"), "fact")
        sources = fact.get("source_ids")
        if (
            not isinstance(sources, list)
            or not sources
            or not all(_nonempty_string(item) for item in sources)
        ):
            raise ValueError("each fact must reference one or more source_ids")
    for assumption in assumptions:
        _require_nonempty(
            assumption,
            ("id", "statement", "rationale", "materiality"),
            "assumption",
        )
    for estimate in estimates:
        _require_nonempty(estimate, ("id", "label", "method"), "estimate")
        if "value" not in estimate:
            raise ValueError("each estimate requires a value field")
        input_ids = estimate.get("input_ids")
        explicit_inputs = estimate.get("inputs")
        if not _nonempty_string_list(input_ids) and not (
            isinstance(explicit_inputs, Mapping) and bool(explicit_inputs)
        ):
            raise ValueError("each estimate requires material input_ids or explicit inputs")
    for unknown in unknowns:
        _require_nonempty(unknown, ("id", "impact"), "unknown")
        if not _nonempty_string(unknown.get("gap")) and not _nonempty_string(
            unknown.get("question")
        ):
            raise ValueError("each unknown requires a gap or question")

    source_ids = value.get("source_ids")
    if not isinstance(source_ids, list) or not all(
        _nonempty_string(item) for item in source_ids
    ):
        raise TypeError("source_ids must be a list of non-empty strings")
    expected_sources = _referenced_sources(value)
    if source_ids != expected_sources:
        raise ValueError("source_ids must be the deduplicated referenced-source union")

    if status == "skipped":
        if not _nonempty_string(value.get("skip_reason")):
            raise ValueError("a skipped result requires skip_reason")
        if not _nonempty_string_list(value.get("missing_inputs")):
            raise ValueError("a skipped result requires missing_inputs")
        if facts or assumptions or estimates or value.get("findings"):
            raise ValueError("a skipped result cannot masquerade as completed analysis")


def _copy_mappings(
    values: Sequence[Mapping[str, Any]],
    field: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for value in values:
        if not isinstance(value, Mapping):
            raise TypeError(f"{field} entries must be mappings")
        records.append(deepcopy(dict(value)))
    return records


def _copy_records(
    values: Sequence[Mapping[str, Any] | str],
    prefix: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, value in enumerate(values, start=1):
        if isinstance(value, Mapping):
            records.append(deepcopy(dict(value)))
        elif _nonempty_string(value):
            statement = str(value).strip()
            record = {"id": f"{prefix}-{index}", "statement": statement}
            if prefix == "unknown":
                record = {
                    "id": f"unknown-{index}",
                    "gap": statement,
                    "impact": "The affected conclusion remains unresolved.",
                }
            records.append(record)
        else:
            raise TypeError(f"{prefix} entries must be mappings or non-empty strings")
    return records


def _referenced_sources(value: Mapping[str, Any]) -> list[str]:
    source_ids: list[str] = []
    for field in ("facts", "findings", "risks"):
        records = value.get(field, [])
        if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
            continue
        for record in records:
            if not isinstance(record, Mapping):
                continue
            for source_id in record.get("source_ids", []):
                if _nonempty_string(source_id) and source_id not in source_ids:
                    source_ids.append(str(source_id).strip())
    return source_ids


def _validate_version_record(value: Any, field: str) -> None:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field} must be a mapping")
    _require_nonempty(value, ("name", "version"), field)


def _record_list(value: Any, field: str) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        raise TypeError(f"{field} must be a list")
    if not all(isinstance(record, Mapping) for record in value):
        raise TypeError(f"{field} entries must be mappings")
    return value


def _require_nonempty(
    value: Mapping[str, Any],
    fields: Sequence[str],
    label: str,
) -> None:
    for field in fields:
        if not _nonempty_string(value.get(field)):
            raise ValueError(f"each {label} requires {field}")


def _clean_strings(values: Sequence[str], field: str) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{field} must be a sequence of strings")
    result = [str(value).strip() for value in values if str(value).strip()]
    if len(result) != len(values):
        raise ValueError(f"{field} cannot contain empty values")
    return list(dict.fromkeys(result))


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(_nonempty_string(item) for item in value)
    )
