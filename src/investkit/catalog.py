"""Strict, offline Runtime catalog for Investment Research Harness assets."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import stat
from typing import Any, Mapping

from .assets import CATALOG_PATH, source_file
from .errors import AssetValidationError


ASSET_TYPES = frozenset(
    {
        "agent_skill",
        "mcp_or_tool",
        "data_provider",
        "quant_module",
        "agent",
        "workflow",
        "template",
        "reference",
        "reject",
    }
)
DECISIONS = frozenset(
    {"adopt", "adapt", "extract", "reference", "duplicate", "unsafe", "reject", "unknown"}
)
RUNTIME_STATES = frozenset(
    {
        "ready",
        "credential_required",
        "permission_required",
        "review_required",
        "unavailable",
        "blocked",
        "reference_only",
        "duplicate",
        "error",
    }
)
ORIGINS = frozenset({"first_party", "candidate"})
APPROVAL_STATUSES = frozenset({"approved", "not_requested"})
NETWORK_MODES = frozenset({"offline", "explicit_permission"})
ADAPTER_KINDS = frozenset(
    {"skill", "tool", "mcp", "data_provider", "quant", "agent", "workflow", "template", "reference", "none"}
)
_MAX_CATALOG_BYTES = 2 * 1024 * 1024
_ROOT_FIELDS = frozenset({"schema_version", "catalog_version", "profiles", "assets"})
_ASSET_FIELDS = frozenset(
    {
        "id",
        "name",
        "origin",
        "type",
        "capabilities",
        "decision",
        "approval_status",
        "review_status",
        "license_status",
        "state",
        "adapter_kind",
        "adapter_id",
        "dependencies",
        "credentials",
        "network_mode",
        "allowed_hosts",
        "platforms",
        "source",
        "reason",
        "evidence",
    }
)
_ENTRY_FIELDS = _ASSET_FIELDS | {"profile"}
_REQUIRED_FIELDS = _ASSET_FIELDS


class CatalogValidationError(AssetValidationError):
    """Raised when the governed asset catalog is malformed or inconsistent."""


@dataclass(frozen=True)
class AssetRecord:
    id: str
    name: str
    origin: str
    type: str
    capabilities: tuple[str, ...]
    decision: str
    approval_status: str
    review_status: str
    license_status: str
    state: str
    adapter_kind: str
    adapter_id: str | None
    dependencies: tuple[str, ...]
    credentials: tuple[str, ...]
    network_mode: str
    allowed_hosts: tuple[str, ...]
    platforms: tuple[str, ...]
    source: str
    reason: str
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-compatible view without credential values."""

        value = asdict(self)
        for field in (
            "capabilities",
            "dependencies",
            "credentials",
            "allowed_hosts",
            "platforms",
            "evidence",
        ):
            value[field] = list(value[field])
        return value


@dataclass(frozen=True)
class AssetCatalog:
    schema_version: str
    catalog_version: str
    assets: tuple[AssetRecord, ...]

    def get(self, asset_id: str) -> AssetRecord:
        for asset in self.assets:
            if asset.id == asset_id:
                return asset
        raise KeyError(asset_id)

    def filter(
        self,
        *,
        type: str | None = None,
        capability: str | None = None,
        decision: str | None = None,
        state: str | None = None,
    ) -> tuple[AssetRecord, ...]:
        """Return deterministic catalog matches for exact normalized filters."""

        result = (
            asset
            for asset in self.assets
            if (type is None or asset.type == type)
            and (capability is None or capability in asset.capabilities)
            and (decision is None or asset.decision == decision)
            and (state is None or asset.state == state)
        )
        return tuple(sorted(result, key=lambda asset: asset.id))


def load_asset_catalog(source_root: str | Path) -> AssetCatalog:
    """Load the governed catalog from a checkout or wheel-delivered source root."""

    root = Path(source_root).expanduser().resolve()
    return load_asset_catalog_file(source_file(root, CATALOG_PATH))


def load_asset_catalog_file(path: str | Path) -> AssetCatalog:
    """Load one bounded regular JSON file with strict schema validation."""

    candidate = Path(path)
    try:
        metadata = os.lstat(candidate)
    except OSError as error:
        raise CatalogValidationError("asset catalog is missing or inaccessible") from error
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > _MAX_CATALOG_BYTES:
        raise CatalogValidationError("asset catalog must be a bounded regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        descriptor = os.open(candidate, flags)
    except OSError as error:
        raise CatalogValidationError("asset catalog is unsafe or inaccessible") from error
    try:
        file_metadata = os.fstat(descriptor)
        if not stat.S_ISREG(file_metadata.st_mode) or file_metadata.st_size > _MAX_CATALOG_BYTES:
            raise CatalogValidationError("asset catalog must be a bounded regular file")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(128 * 1024, _MAX_CATALOG_BYTES + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            if total > _MAX_CATALOG_BYTES:
                raise CatalogValidationError("asset catalog exceeds the size limit")
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    try:
        text = b"".join(chunks).decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise CatalogValidationError("asset catalog is not strict UTF-8 JSON") from error
    return _validate_catalog(value)


def _validate_catalog(value: Any) -> AssetCatalog:
    root = _object(value, "catalog")
    _exact_fields(root, _ROOT_FIELDS, "catalog")
    schema_version = _text(root.get("schema_version"), "schema_version")
    if schema_version != "1.0":
        raise CatalogValidationError("unsupported asset catalog schema version")
    catalog_version = _text(root.get("catalog_version"), "catalog_version")
    profiles_raw = _object(root.get("profiles", {}), "profiles")
    profiles: dict[str, Mapping[str, Any]] = {}
    for name, profile_value in profiles_raw.items():
        profile_name = _text(name, "profile name")
        profile = _object(profile_value, f"profile {profile_name}")
        unknown = set(profile) - _ASSET_FIELDS
        if unknown:
            raise CatalogValidationError(f"profile {profile_name} has unknown fields")
        if "id" in profile or "name" in profile:
            raise CatalogValidationError("profiles cannot define asset identity")
        profiles[profile_name] = profile

    raw_assets = root.get("assets")
    if not isinstance(raw_assets, list) or not raw_assets:
        raise CatalogValidationError("catalog assets must be a non-empty array")
    assets: list[AssetRecord] = []
    seen_ids: set[str] = set()
    for index, raw_asset in enumerate(raw_assets):
        entry = _object(raw_asset, f"asset {index}")
        unknown = set(entry) - _ENTRY_FIELDS
        if unknown:
            raise CatalogValidationError(f"asset {index} has unknown fields")
        profile_name = entry.get("profile")
        merged: dict[str, Any] = {}
        if profile_name is not None:
            normalized_profile = _text(profile_name, "profile")
            if normalized_profile not in profiles:
                raise CatalogValidationError(f"asset {index} uses an unknown profile")
            merged.update(profiles[normalized_profile])
        merged.update({key: child for key, child in entry.items() if key != "profile"})
        _exact_fields(merged, _REQUIRED_FIELDS, f"asset {index}")
        asset = _asset_record(merged, index)
        if asset.id in seen_ids:
            raise CatalogValidationError("asset catalog contains duplicate IDs")
        seen_ids.add(asset.id)
        assets.append(asset)

    for asset in assets:
        missing = set(asset.dependencies) - seen_ids
        if missing:
            raise CatalogValidationError(f"asset {asset.id} has unknown dependencies")
        if asset.id in asset.dependencies:
            raise CatalogValidationError(f"asset {asset.id} depends on itself")
    _reject_dependency_cycles(assets)
    return AssetCatalog(schema_version, catalog_version, tuple(sorted(assets, key=lambda item: item.id)))


def _asset_record(value: Mapping[str, Any], index: int) -> AssetRecord:
    label = f"asset {index}"
    identifier = _text(value["id"], f"{label} id")
    record = AssetRecord(
        id=identifier,
        name=_text(value["name"], f"{label} name"),
        origin=_choice(value["origin"], ORIGINS, f"{label} origin"),
        type=_choice(value["type"], ASSET_TYPES, f"{label} type"),
        capabilities=_strings(value["capabilities"], f"{label} capabilities", nonempty=True),
        decision=_choice(value["decision"], DECISIONS, f"{label} decision"),
        approval_status=_choice(value["approval_status"], APPROVAL_STATUSES, f"{label} approval"),
        review_status=_text(value["review_status"], f"{label} review status"),
        license_status=_text(value["license_status"], f"{label} license status"),
        state=_choice(value["state"], RUNTIME_STATES, f"{label} state"),
        adapter_kind=_choice(value["adapter_kind"], ADAPTER_KINDS, f"{label} adapter kind"),
        adapter_id=None if value["adapter_id"] is None else _text(value["adapter_id"], f"{label} adapter id"),
        dependencies=_strings(value["dependencies"], f"{label} dependencies"),
        credentials=_strings(value["credentials"], f"{label} credentials"),
        network_mode=_choice(value["network_mode"], NETWORK_MODES, f"{label} network mode"),
        allowed_hosts=_strings(value["allowed_hosts"], f"{label} allowed hosts"),
        platforms=_strings(value["platforms"], f"{label} platforms"),
        source=_text(value["source"], f"{label} source"),
        reason=_text(value["reason"], f"{label} reason", limit=1000),
        evidence=_strings(value["evidence"], f"{label} evidence", nonempty=True),
    )
    if record.state == "ready" and (
        record.approval_status != "approved" or not record.adapter_id
    ):
        raise CatalogValidationError(f"ready asset {identifier} lacks approval or adapter")
    if record.adapter_kind == "none" and record.adapter_id is not None:
        raise CatalogValidationError(f"asset {identifier} has an adapter ID without an adapter")
    if record.adapter_id and any(fragment in record.adapter_id.replace("\\", "/") for fragment in ("third_party/raw", "adapted/skills")):
        raise CatalogValidationError(f"asset {identifier} references a forbidden adapter path")
    if record.credentials and record.network_mode != "explicit_permission":
        raise CatalogValidationError(f"asset {identifier} has credentials without explicit network permission")
    if record.network_mode == "offline" and record.allowed_hosts:
        raise CatalogValidationError(f"offline asset {identifier} cannot allow network hosts")
    return record


def _reject_dependency_cycles(assets: list[AssetRecord]) -> None:
    dependencies = {asset.id: asset.dependencies for asset in assets}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in visiting:
            raise CatalogValidationError("asset catalog dependency graph contains a cycle")
        if identifier in visited:
            return
        visiting.add(identifier)
        for dependency in dependencies[identifier]:
            visit(dependency)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in sorted(dependencies):
        visit(identifier)


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CatalogValidationError(f"{label} must be an object")
    return value


def _exact_fields(value: Mapping[str, Any], expected: frozenset[str], label: str) -> None:
    if set(value) != expected:
        raise CatalogValidationError(f"{label} fields do not match the catalog contract")


def _text(value: Any, label: str, *, limit: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip() or len(value) > limit:
        raise CatalogValidationError(f"{label} must be bounded non-empty text")
    return value


def _choice(value: Any, allowed: frozenset[str], label: str) -> str:
    text = _text(value, label)
    if text not in allowed:
        raise CatalogValidationError(f"{label} is unsupported")
    return text


def _strings(value: Any, label: str, *, nonempty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or (nonempty and not value):
        raise CatalogValidationError(f"{label} must be an array of text")
    result = tuple(_text(item, label, limit=1000) for item in value)
    if len(result) != len(set(result)):
        raise CatalogValidationError(f"{label} contains duplicates")
    return result


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate JSON object key")
        value[key] = child
    return value


def _reject_constant(value: str) -> Any:
    del value
    raise ValueError("non-finite JSON number")
