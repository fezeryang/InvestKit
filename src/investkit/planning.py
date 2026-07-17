"""Pure dependency and permission planning for dynamic research tasks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from .catalog import ASSET_TYPES, AssetCatalog, AssetRecord


@dataclass(frozen=True)
class PlanItem:
    asset_id: str
    disposition: str
    effective_state: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ResearchPlan:
    catalog_version: str
    requested_capabilities: tuple[str, ...]
    required_types: tuple[str, ...]
    selected: tuple[PlanItem, ...]
    considered: tuple[PlanItem, ...]
    blocked_capabilities: tuple[str, ...]

    @property
    def runnable(self) -> bool:
        return not self.blocked_capabilities

    def to_dict(self) -> dict[str, object]:
        return {
            "catalog_version": self.catalog_version,
            "requested_capabilities": list(self.requested_capabilities),
            "required_types": list(self.required_types),
            "selected": [item.to_dict() for item in self.selected],
            "considered": [item.to_dict() for item in self.considered],
            "blocked_capabilities": list(self.blocked_capabilities),
            "runnable": self.runnable,
        }


def evaluate_asset_state(
    asset: AssetRecord,
    *,
    credential_names: set[str] | frozenset[str] = frozenset(),
    allow_network: bool = False,
) -> str:
    """Evaluate runtime gates without reading or accepting credential values."""

    if asset.state in {
        "review_required",
        "unavailable",
        "blocked",
        "reference_only",
        "duplicate",
        "error",
    }:
        return asset.state
    if asset.approval_status != "approved":
        return "review_required"
    if any(name not in credential_names for name in asset.credentials):
        return "credential_required"
    if asset.network_mode == "explicit_permission" and not allow_network:
        return "permission_required"
    return "ready"


def build_research_plan(
    catalog: AssetCatalog,
    *,
    capabilities: Iterable[str],
    required_types: Iterable[str] = (),
    credential_names: set[str] | frozenset[str] = frozenset(),
    allow_network: bool = False,
) -> ResearchPlan:
    """Select ready matching assets and their dependencies deterministically."""

    requested = _normalized_unique(capabilities, "capability")
    types = _normalized_unique(required_types, "asset type", allow_empty=True)
    unknown_types = set(types) - ASSET_TYPES
    if unknown_types:
        raise ValueError("research plan contains an unsupported asset type")
    by_id = {asset.id: asset for asset in catalog.assets}
    effective = {
        asset.id: evaluate_asset_state(
            asset,
            credential_names=credential_names,
            allow_network=allow_network,
        )
        for asset in catalog.assets
    }
    roots: set[str] = set()
    blocked: list[str] = []
    matching_ids: set[str] = set()
    for capability in requested:
        matches = [
            asset
            for asset in catalog.assets
            if capability in asset.capabilities
            and (not types or asset.type in types)
        ]
        matching_ids.update(asset.id for asset in matches)
        ready = [asset for asset in matches if effective[asset.id] == "ready"]
        if not ready:
            blocked.append(capability)
            continue
        roots.update(asset.id for asset in ready)

    selected_ids: list[str] = []
    selected_set: set[str] = set()
    invalid_roots: set[str] = set()

    def dependencies_ready(identifier: str, checked: set[str] | None = None) -> bool:
        checked = set() if checked is None else checked
        if identifier in checked:
            return True
        checked.add(identifier)
        asset = by_id[identifier]
        return all(
            effective[dependency] == "ready"
            and dependencies_ready(dependency, checked)
            for dependency in asset.dependencies
        )

    for identifier in sorted(roots):
        if not dependencies_ready(identifier):
            invalid_roots.add(identifier)

    if invalid_roots:
        for capability in requested:
            if any(
                identifier in invalid_roots
                and capability in by_id[identifier].capabilities
                for identifier in roots
            ) and capability not in blocked:
                blocked.append(capability)
        roots -= invalid_roots

    def select(identifier: str) -> None:
        if identifier in selected_set:
            return
        for dependency in sorted(by_id[identifier].dependencies):
            select(dependency)
        selected_set.add(identifier)
        selected_ids.append(identifier)

    for identifier in sorted(roots):
        select(identifier)

    selected = tuple(
        PlanItem(
            asset_id=identifier,
            disposition="selected",
            effective_state="ready",
            reason=(
                "selected for a requested capability"
                if identifier in roots
                else "selected as a required dependency"
            ),
        )
        for identifier in selected_ids
    )
    considered_ids = sorted(matching_ids - selected_set)
    considered = tuple(
        PlanItem(
            asset_id=identifier,
            disposition="not_selected",
            effective_state=effective[identifier],
            reason=by_id[identifier].reason,
        )
        for identifier in considered_ids
    )
    return ResearchPlan(
        catalog_version=catalog.catalog_version,
        requested_capabilities=requested,
        required_types=types,
        selected=selected,
        considered=considered,
        blocked_capabilities=tuple(sorted(set(blocked))),
    )


def _normalized_unique(
    values: Iterable[str], label: str, *, allow_empty: bool = False
) -> tuple[str, ...]:
    normalized: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise ValueError(f"{label} must be non-empty normalized text")
        normalized.add(value)
    if not normalized and not allow_empty:
        raise ValueError(f"at least one {label} is required")
    return tuple(sorted(normalized))
