"""Validated read-only Provider for project-local research bundles."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import stat
from typing import Any, Iterable, Mapping, Sequence

from investkit.errors import InvestKitError
from investkit.filesystem import resolved_root, stable_json_bytes
from investkit.security import contains_sensitive_key, contains_sensitive_value

from .base import Provider, ProviderRecord


BUNDLE_SCHEMA_VERSION = "1.0"
MAX_BUNDLE_BYTES = 2 * 1024 * 1024
OPERATION_NAMES = (
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
_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "bundle_version",
        "created_at",
        "retrieved_at",
        "as_of_date",
        "currency",
        "market",
        "status",
        "warnings",
        "security",
        "sources",
        "operations",
    }
)
_IDENTITY_FIELDS = ("security_id", "ticker", "legal_name", "exchange")
_SOURCE_REQUIRED_FIELDS = (
    "source_id",
    "publisher",
    "title",
    "source_type",
    "locator",
    "retrieved_at",
    "quality",
    "freshness",
    "access_notes",
    "license_notes",
)
class BundleInputError(InvestKitError):
    """Raised when the local input file violates a filesystem boundary."""


class BundleValidationError(InvestKitError):
    """Raised when a decoded research bundle violates the governed contract."""


@dataclass(frozen=True)
class ValidatedBundle:
    """Immutable normalized representation used for persistence and serving."""

    value: Mapping[str, Any]
    canonical_bytes: bytes
    sha256: str
    origin: str


def load_research_bundle(
    project_root: str | Path,
    input_path: str | Path,
) -> ValidatedBundle:
    """Load, normalize, and validate one safe project-local JSON bundle."""

    project = resolved_root(project_root)
    relative = _project_relative_input(project, input_path)
    _checked_regular_path(project, relative)
    payload = _bounded_read(project, relative)
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise BundleInputError("research bundle must be valid UTF-8 JSON") from error
    try:
        decoded = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
            parse_float=_finite_float,
        )
        return validate_research_bundle_mapping(decoded, origin=relative.as_posix())
    except BundleValidationError:
        raise
    except (
        json.JSONDecodeError,
        OverflowError,
        RecursionError,
        TypeError,
        ValueError,
    ) as error:
        raise BundleValidationError("research bundle is not valid JSON") from error


def validate_research_bundle_mapping(
    value: Mapping[str, Any], *, origin: str
) -> ValidatedBundle:
    """Validate an acquired in-memory bundle through the same imported boundary."""

    if not isinstance(value, Mapping) or not isinstance(origin, str) or not origin:
        raise BundleValidationError("research bundle mapping or origin is invalid")
    decoded = deepcopy(dict(value))
    _reject_sensitive_content(decoded)
    _validate_bundle(decoded)
    try:
        canonical = stable_json_bytes(decoded)
    except (TypeError, ValueError, OverflowError) as error:
        raise BundleValidationError("research bundle is not finite JSON") from error
    if len(canonical) > MAX_BUNDLE_BYTES:
        raise BundleValidationError("research bundle exceeds the size limit")
    return ValidatedBundle(
        value=deepcopy(decoded),
        canonical_bytes=canonical,
        sha256=hashlib.sha256(canonical).hexdigest(),
        origin=origin,
    )


class FileProvider(Provider):
    """Serve a fully validated bundle without later filesystem reads."""

    def __init__(self, project_root: str | Path, input_path: str | Path) -> None:
        self._load_validated(load_research_bundle(project_root, input_path))

    @classmethod
    def from_mapping(
        cls, value: Mapping[str, Any], *, origin: str
    ) -> "FileProvider":
        """Create a snapshot Provider from already acquired, untrusted mapping data."""

        instance = cls.__new__(cls)
        instance._load_validated(
            validate_research_bundle_mapping(value, origin=origin)
        )
        return instance

    def _load_validated(self, bundle: ValidatedBundle) -> None:
        self._bundle = deepcopy(dict(bundle.value))
        self.bundle_bytes = bundle.canonical_bytes
        self.bundle_sha256 = bundle.sha256
        self.bundle_origin = bundle.origin
        security = _object(self._bundle.get("security"), "security")
        self._security_id = _text(security.get("security_id"), "security.security_id")
        self._accepted_queries = {
            self._security_id.casefold(),
            _text(security.get("ticker"), "security.ticker").casefold(),
            _text(security.get("legal_name"), "security.legal_name").casefold(),
            *(
                str(alias).strip().casefold()
                for alias in security.get("aliases", [])
                if isinstance(alias, str) and alias.strip()
            ),
        }

    @property
    def bundle(self) -> Mapping[str, Any]:
        """Return a defensive copy suitable for explicit task persistence."""

        return deepcopy(self._bundle)

    def identify_security(self, query: str) -> ProviderRecord:
        normalized = str(query).strip().casefold()
        if not normalized or normalized not in self._accepted_queries:
            raise LookupError("security query does not match the imported bundle identity")
        return self._response("identify_security")

    def get_security_profile(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response("get_security_profile")

    def get_financial_statements(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response("get_financial_statements")

    def get_price_history(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response("get_price_history")

    def get_valuation_inputs(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response("get_valuation_inputs")

    def get_source_metadata(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response("get_source_metadata")

    def get_peer_comparables(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response("get_peer_comparables")

    def get_earnings_history(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response("get_earnings_history")

    def get_catalyst_events(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response("get_catalyst_events")

    def _validate_security_id(self, security_id: str) -> None:
        if str(security_id).strip() != self._security_id:
            raise LookupError("security identifier does not match the imported bundle")

    def _response(self, operation_name: str) -> dict[str, Any]:
        operations = _object(self._bundle.get("operations"), "operations")
        operation = _object(operations.get(operation_name), f"operations.{operation_name}")
        response = deepcopy(dict(_object(operation.get("data"), f"{operation_name}.data")))
        response.update(
            {
                "as_of_date": self._bundle["as_of_date"],
                "bundle_sha256": self.bundle_sha256,
                "bundle_version": self._bundle["bundle_version"],
                "currency": self._bundle["currency"],
                "input_mode": "imported",
                "is_demo": False,
                "market": self._bundle["market"],
                "retrieved_at": self._bundle["retrieved_at"],
                "source": "validated project-local research bundle",
                "source_ids": deepcopy(operation["source_ids"]),
                "warnings": [
                    *deepcopy(self._bundle["warnings"]),
                    *deepcopy(operation["warnings"]),
                ],
            }
        )
        return response


def _project_relative_input(project_root: Path, value: str | Path) -> Path:
    raw = Path(value).expanduser()
    if raw.is_absolute():
        try:
            relative = raw.relative_to(project_root)
        except ValueError as error:
            raise BundleInputError("research bundle must be inside the project root") from error
    else:
        relative = raw
    if not relative.parts or ".." in relative.parts:
        raise BundleInputError("research bundle path escapes the project root")
    return relative


def _checked_regular_path(project_root: Path, relative: Path) -> Path:
    current = project_root
    for part in relative.parts:
        current = current / part
        try:
            metadata = current.lstat()
        except OSError as error:
            raise BundleInputError("research bundle file is missing or inaccessible") from error
        if stat.S_ISLNK(metadata.st_mode):
            raise BundleInputError("research bundle path contains a symlink")
    try:
        resolved = current.resolve(strict=True)
    except OSError as error:
        raise BundleInputError("research bundle file is missing or inaccessible") from error
    if not resolved.is_relative_to(project_root):
        raise BundleInputError("research bundle path escapes the project root")
    try:
        metadata = resolved.stat()
    except OSError as error:
        raise BundleInputError("research bundle file is missing or inaccessible") from error
    if not stat.S_ISREG(metadata.st_mode):
        raise BundleInputError("research bundle must be a regular file")
    if metadata.st_size > MAX_BUNDLE_BYTES:
        raise BundleInputError("research bundle exceeds the maximum allowed size")
    return resolved


def _bounded_read(project_root: Path, relative: Path) -> bytes:
    """Read through directory descriptors so a checked parent cannot be swapped."""

    descriptor = _open_project_file(project_root, relative)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BUNDLE_BYTES:
            raise BundleInputError("research bundle is not a bounded regular file")
        chunks: list[bytes] = []
        size = 0
        while True:
            chunk = os.read(descriptor, min(128 * 1024, MAX_BUNDLE_BYTES + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            if size > MAX_BUNDLE_BYTES:
                raise BundleInputError("research bundle exceeds the maximum allowed size")
        after = os.fstat(descriptor)
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
            raise BundleInputError("research bundle changed while it was being validated")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _open_project_file(project_root: Path, relative: Path) -> int:
    """Open one root-relative file without following any path component."""

    if not relative.parts or relative.is_absolute() or ".." in relative.parts:
        raise BundleInputError("research bundle path escapes the project root")
    if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
        raise BundleInputError("this platform cannot safely open a project-local bundle")
    directory_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_DIRECTORY", 0)
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
    directory_descriptors: list[int] = []
    try:
        root_descriptor = os.open(project_root, directory_flags)
        directory_descriptors.append(root_descriptor)
        if not stat.S_ISDIR(os.fstat(root_descriptor).st_mode):
            raise OSError("project root is not a directory")
        for part in relative.parts[:-1]:
            parent_descriptor = os.open(
                part,
                directory_flags,
                dir_fd=directory_descriptors[-1],
            )
            directory_descriptors.append(parent_descriptor)
            if not stat.S_ISDIR(os.fstat(parent_descriptor).st_mode):
                raise OSError("research bundle parent is not a directory")
        return os.open(
            relative.parts[-1],
            file_flags,
            dir_fd=directory_descriptors[-1],
        )
    except OSError as error:
        raise BundleInputError("research bundle cannot be opened safely") from error
    finally:
        for directory_descriptor in reversed(directory_descriptors):
            os.close(directory_descriptor)


def _unique_object(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BundleValidationError("research bundle contains a duplicate JSON key")
        result[key] = value
    return result


def _reject_json_constant(_value: str) -> Any:
    """Reject NaN and infinities, which RFC 8259 JSON does not permit."""

    raise BundleValidationError("research bundle is not valid JSON")


def _finite_float(value: str) -> float:
    """Reject exponent overflow that Python would otherwise decode as infinity."""

    parsed = float(value)
    if not math.isfinite(parsed):
        raise BundleValidationError("research bundle is not valid JSON: non-finite number")
    return parsed


def _validate_bundle(bundle: Mapping[str, Any]) -> None:
    if set(bundle) != _TOP_LEVEL_FIELDS:
        raise BundleValidationError("research bundle top-level fields are incomplete or unsupported")
    if bundle.get("schema_version") != BUNDLE_SCHEMA_VERSION:
        raise BundleValidationError("research bundle schema version is unsupported")
    for field in ("bundle_version", "currency", "market"):
        _text(bundle.get(field), field)
    if bundle.get("status") != "imported":
        raise BundleValidationError("research bundle status must be imported")
    _nonempty_strings(bundle.get("warnings"), "warnings")
    bundle_as_of = _date_value(bundle.get("as_of_date"), "as_of_date")
    bundle_created = _timestamp_value(bundle.get("created_at"), "created_at")
    bundle_retrieved = _timestamp_value(bundle.get("retrieved_at"), "retrieved_at")
    if bundle_as_of > bundle_created.date() or bundle_created > bundle_retrieved:
        raise BundleValidationError("research bundle date chronology is inconsistent")

    security = _object(bundle.get("security"), "security")
    for field in _IDENTITY_FIELDS:
        _text(security.get(field), f"security.{field}")
    aliases = security.get("aliases", [])
    if not isinstance(aliases, list) or not all(
        isinstance(alias, str) and alias.strip() for alias in aliases
    ):
        raise BundleValidationError("security.aliases must contain only non-empty strings")

    source_values = bundle.get("sources")
    if not isinstance(source_values, list) or not source_values:
        raise BundleValidationError("research bundle requires a non-empty source registry")
    source_ids: set[str] = set()
    for index, raw_source in enumerate(source_values):
        source = _object(raw_source, f"sources[{index}]")
        for field in _SOURCE_REQUIRED_FIELDS:
            _text(source.get(field), f"sources[{index}].{field}")
        source_id = str(source["source_id"])
        if source_id != source_id.strip():
            raise BundleValidationError(
                "research source IDs cannot contain leading or trailing whitespace"
            )
        if source_id in source_ids:
            raise BundleValidationError("research bundle contains duplicate source IDs")
        source_ids.add(source_id)
        publication_date = (
            _date_value(source.get("publication_date"), "source publication_date")
            if source.get("publication_date") is not None
            else None
        )
        source_as_of = (
            _date_value(source.get("as_of_date"), "source as_of_date")
            if source.get("as_of_date") is not None
            else None
        )
        source_retrieved = _timestamp_value(
            source.get("retrieved_at"), "source retrieved_at"
        )
        if (
            (publication_date is not None and publication_date > source_retrieved.date())
            or (source_as_of is not None and source_as_of > source_retrieved.date())
            or source_retrieved > bundle_created
        ):
            raise BundleValidationError("research source date chronology is inconsistent")

    operations = _object(bundle.get("operations"), "operations")
    if set(operations) != set(OPERATION_NAMES):
        raise BundleValidationError("research bundle must define exactly nine Provider operations")
    for name in OPERATION_NAMES:
        operation = _object(operations.get(name), f"operations.{name}")
        if set(operation) != {"data", "source_ids", "warnings"}:
            raise BundleValidationError(f"operation {name} fields are incomplete or unsupported")
        data = _object(operation.get("data"), f"operations.{name}.data")
        _validate_operation_data(name, data)
        references = _string_list(operation.get("source_ids"), f"{name}.source_ids")
        if not references and not _is_source_free_data(data, name):
            raise BundleValidationError(
                f"operation {name} must contain only explicit gaps without a supporting source"
            )
        unresolved = sorted(set(references) - source_ids)
        if unresolved:
            raise BundleValidationError(f"operation {name} references an unresolved source ID")
        _nonempty_strings(operation.get("warnings"), f"{name}.warnings")

    identity = _object(operations["identify_security"].get("data"), "identify_security.data")
    if any(
        identity.get(field) != security.get(field)
        for field in (*_IDENTITY_FIELDS, "aliases")
    ):
        raise BundleValidationError("security identity conflicts with identify_security operation")
    metadata_operation = operations["get_source_metadata"]
    metadata = _object(metadata_operation.get("data"), "source metadata data")
    metadata_sources = metadata.get("sources")
    if not isinstance(metadata_sources, list):
        raise BundleValidationError("source metadata operation must preserve the source registry")
    metadata_references = _string_list(
        metadata_operation.get("source_ids"), "get_source_metadata.source_ids"
    )
    metadata_ids = {
        str(value.get("source_id"))
        for value in metadata_sources
        if isinstance(value, Mapping) and isinstance(value.get("source_id"), str)
    }
    if (
        metadata_ids != source_ids
        or set(metadata_references) != source_ids
        or len(metadata_references) != len(source_ids)
        or len(metadata_sources) != len(source_values)
        or metadata_sources != source_values
    ):
        raise BundleValidationError("source metadata registry differs from the bundle source registry")


def _reject_sensitive_content(value: Any) -> None:
    def visit(candidate: Any) -> Iterable[tuple[str | None, Any]]:
        if isinstance(candidate, Mapping):
            for key, item in candidate.items():
                yield str(key), item
                yield from visit(item)
        elif isinstance(candidate, list):
            for item in candidate:
                yield None, item
                yield from visit(item)

    for key, candidate in visit(value):
        if key is not None and contains_sensitive_key(key):
            raise BundleValidationError("research bundle contains a credential-like field")
        if contains_sensitive_value(candidate):
            raise BundleValidationError("research bundle contains a credential-like value")


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise BundleValidationError(f"{label} must be an object")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BundleValidationError(f"{label} must be a non-empty string")
    return value.strip()


def _nonempty_strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise BundleValidationError(f"{label} must be a non-empty string list")
    return [str(item) for item in value]


def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() and item == item.strip()
        for item in value
    ):
        raise BundleValidationError(
            f"{label} must contain canonical non-empty strings without edge whitespace"
        )
    return [str(item) for item in value]


def _is_source_free_data(value: Mapping[str, Any], operation_name: str) -> bool:
    """Accept only explicit null/empty-array gaps plus optional limitations."""

    if "limitations" in value:
        _nonempty_strings(
            value["limitations"], f"{operation_name}.data.limitations"
        )
    gap_values = [item for key, item in value.items() if key != "limitations"]
    return bool(gap_values) and all(_is_explicit_gap_value(item) for item in gap_values)


def _is_explicit_gap_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, list):
        return not value
    if isinstance(value, Mapping):
        return bool(value) and all(
            _is_explicit_gap_value(item) for item in value.values()
        )
    return False


def _validate_operation_data(name: str, data: Mapping[str, Any]) -> None:
    """Validate the thin shared shapes needed before task creation."""

    if name == "identify_security":
        _optional_string_list(data, "aliases", name)
        return
    if name == "get_security_profile":
        for key in (
            "segments",
            "products",
            "geographies",
            "business_risks",
            "risks",
            "research_drivers",
        ):
            _optional_string_list(data, key, name)
        for key in (
            "management",
            "capital_allocation",
            "competitive_context",
            "revenue_components",
            "order_to_cash",
        ):
            _optional_object(data, key, name)
        for key in (
            "employee_count",
            "employees",
            "customer_concentration_percent",
        ):
            _optional_number(data, key, name)
        return
    if name == "get_financial_statements":
        periods = _optional_object_list(data, "periods", name)
        for period in periods:
            for key, value in period.items():
                if key == "fiscal_year" or value is None:
                    continue
                if isinstance(value, bool) or not isinstance(value, (int, float, str)):
                    raise BundleValidationError(
                        "financial statement period fields must be scalar values or null"
                    )
        return
    if name == "get_price_history":
        _optional_object_list(data, "observations", name)
        _optional_number(data, "latest_price", name)
        return
    if name == "get_valuation_inputs":
        for key in (
            "wacc",
            "terminal_growth",
            "diluted_shares",
            "cash",
            "total_debt",
        ):
            _optional_number(data, key, name)
        for key in (
            "forecast_unlevered_free_cash_flow",
            "sensitivity_wacc_values",
            "sensitivity_terminal_growth_values",
        ):
            _optional_number_list(data, key, name)
        _optional_object(data, "scenario_assumptions", name)
        return
    if name == "get_source_metadata":
        _optional_object_list(data, "sources", name, allow_null=False)
        return
    if name == "get_peer_comparables":
        _optional_object_list(data, "peers", name)
        _optional_text(data, "selection_method", name)
        return
    if name == "get_earnings_history":
        events = _optional_object_list(data, "events", name)
        for event in events:
            for key in ("actual", "expectation", "guidance"):
                _optional_object(event, key, f"{name}.events")
            if "transcript_available" in event and event["transcript_available"] not in {
                True,
                False,
                None,
            }:
                raise BundleValidationError(
                    "earnings transcript availability must be boolean or null"
                )
        if "transcript_available" in data and data["transcript_available"] not in {
            True,
            False,
            None,
        }:
            raise BundleValidationError(
                "earnings transcript availability must be boolean or null"
            )
        return
    if name == "get_catalyst_events":
        _optional_object_list(data, "events", name)


def _optional_object(
    value: Mapping[str, Any], key: str, label: str
) -> Mapping[str, Any] | None:
    if key not in value or value[key] is None:
        return None
    if not isinstance(value[key], Mapping):
        raise BundleValidationError(f"{label}.{key} must be an object or null")
    return value[key]


def _optional_object_list(
    value: Mapping[str, Any],
    key: str,
    label: str,
    *,
    allow_null: bool = True,
) -> list[Mapping[str, Any]]:
    if key not in value:
        return []
    candidate = value[key]
    if candidate is None and allow_null:
        return []
    if not isinstance(candidate, list) or not all(
        isinstance(item, Mapping) for item in candidate
    ):
        raise BundleValidationError(f"{label}.{key} must be an object list or null")
    return list(candidate)


def _optional_string_list(value: Mapping[str, Any], key: str, label: str) -> None:
    if key not in value or value[key] is None:
        return
    candidate = value[key]
    if not isinstance(candidate, list) or not all(
        isinstance(item, str) and item.strip() for item in candidate
    ):
        raise BundleValidationError(f"{label}.{key} must be a string list or null")


def _optional_number_list(value: Mapping[str, Any], key: str, label: str) -> None:
    if key not in value or value[key] is None:
        return
    candidate = value[key]
    if not isinstance(candidate, list) or not all(
        not isinstance(item, bool) and isinstance(item, (int, float))
        for item in candidate
    ):
        raise BundleValidationError(f"{label}.{key} must be a number list or null")


def _optional_number(value: Mapping[str, Any], key: str, label: str) -> None:
    if key not in value or value[key] is None:
        return
    if isinstance(value[key], bool) or not isinstance(value[key], (int, float)):
        raise BundleValidationError(f"{label}.{key} must be a number or null")


def _optional_text(value: Mapping[str, Any], key: str, label: str) -> None:
    if key not in value or value[key] is None:
        return
    if not isinstance(value[key], str) or not value[key].strip():
        raise BundleValidationError(f"{label}.{key} must be text or null")


def _date_value(value: Any, label: str) -> date:
    if not isinstance(value, str):
        raise BundleValidationError(f"{label} must be YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise BundleValidationError(f"{label} must be YYYY-MM-DD") from error
    if parsed.isoformat() != value or parsed > date.today():
        raise BundleValidationError(f"{label} is invalid or future-dated")
    return parsed


def _timestamp_value(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise BundleValidationError(f"{label} must be a UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise BundleValidationError(f"{label} must be a valid UTC timestamp") from error
    if parsed.tzinfo is None or parsed.astimezone(timezone.utc) > datetime.now(timezone.utc):
        raise BundleValidationError(f"{label} is invalid or future-dated")
    return parsed


__all__ = [
    "BUNDLE_SCHEMA_VERSION",
    "BundleInputError",
    "BundleValidationError",
    "FileProvider",
    "MAX_BUNDLE_BYTES",
    "OPERATION_NAMES",
    "ValidatedBundle",
    "load_research_bundle",
]
