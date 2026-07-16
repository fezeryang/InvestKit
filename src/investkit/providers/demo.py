"""Offline provider backed by an InvestKit-owned fictional fixture."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
import json
from pathlib import Path
from typing import Any, Mapping

from .base import Provider, ProviderRecord


DEFAULT_FIXTURE = Path("fixtures/demo/aurora-lantern-works.json")
REQUIRED_METADATA = (
    "as_of_date",
    "currency",
    "market",
    "source",
    "fixture_version",
    "is_demo",
    "warnings",
)


class DemoProvider(Provider):
    """Serve deterministic demo records without network or credential access."""

    def __init__(self, asset_root: str | Path) -> None:
        self.asset_root = Path(asset_root).expanduser().resolve()
        fixture_path = (self.asset_root / DEFAULT_FIXTURE).resolve()
        if not fixture_path.is_relative_to(self.asset_root):
            raise ValueError("demo fixture path escapes the first-party asset root")
        self.fixture_path = fixture_path
        self._fixture = self._load_fixture()

    def identify_security(self, query: str) -> ProviderRecord:
        identity = self._fixture["identity"]
        accepted = {
            str(identity["security_id"]).casefold(),
            str(identity["ticker"]).casefold(),
            str(identity["legal_name"]).casefold(),
            *(str(alias).casefold() for alias in identity.get("aliases", [])),
        }
        normalized_query = str(query).strip().casefold()
        if not normalized_query or normalized_query not in accepted:
            raise LookupError(
                "demo security is unknown; use 'demo' or the fixture security ID"
            )
        return self._response(
            identity,
            "Identity is fictional and must not be mapped to a real listed security.",
        )

    def get_security_profile(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response(
            self._fixture["profile"],
            "Employee count is unavailable and remains an explicit unknown.",
        )

    def get_financial_statements(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response(
            self._fixture["financial_statements"],
            "Statements use a fictional accounting basis and are not regulatory filings.",
        )

    def get_price_history(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response(
            self._fixture["price_history"],
            "The latest observation has missing volume and is not a live price.",
        )

    def get_valuation_inputs(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response(
            self._fixture["valuation_inputs"],
            "Historical valuation observations are unavailable; the bounded DCF remains scenario-based.",
        )

    def get_source_metadata(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response(
            self._fixture["source_metadata"],
            "This first-party source describes fictional demo data only.",
        )

    def get_peer_comparables(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response(
            self._fixture["peer_comparables"],
            "The peer set is fictional, deliberately small, and not current market evidence.",
        )

    def get_earnings_history(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response(
            self._fixture["earnings_history"],
            "No earnings transcript is available; management commentary remains unknown.",
        )

    def get_catalyst_events(self, security_id: str) -> ProviderRecord:
        self._validate_security_id(security_id)
        return self._response(
            self._fixture["catalyst_events"],
            "Catalyst outcomes are uncertain fictional scenarios, not price predictions.",
        )

    def _load_fixture(self) -> dict[str, Any]:
        try:
            with self.fixture_path.open("r", encoding="utf-8") as stream:
                fixture = json.load(stream)
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"invalid demo fixture: {self.fixture_path.name}") from error
        if not isinstance(fixture, dict):
            raise ValueError("invalid demo fixture: expected a JSON object")
        missing_metadata = [key for key in REQUIRED_METADATA if key not in fixture]
        if missing_metadata:
            raise ValueError(
                "invalid demo fixture: missing metadata " + ", ".join(missing_metadata)
            )
        if fixture.get("is_demo") is not True:
            raise ValueError("invalid demo fixture: is_demo must be true")
        for field in ("as_of_date", "currency", "market", "source", "fixture_version"):
            value = fixture.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"invalid demo fixture: {field} must be non-empty")
        try:
            parsed_date = date.fromisoformat(fixture["as_of_date"])
        except ValueError as error:
            raise ValueError("invalid demo fixture: as_of_date must be YYYY-MM-DD") from error
        if parsed_date.isoformat() != fixture["as_of_date"]:
            raise ValueError("invalid demo fixture: as_of_date must be YYYY-MM-DD")
        warnings = fixture.get("warnings")
        if (
            not isinstance(warnings, list)
            or not warnings
            or not all(isinstance(value, str) and value.strip() for value in warnings)
        ):
            raise ValueError("invalid demo fixture: warnings must be a non-empty list")
        for section in (
            "identity",
            "profile",
            "financial_statements",
            "price_history",
            "valuation_inputs",
            "source_metadata",
            "peer_comparables",
            "earnings_history",
            "catalyst_events",
        ):
            if not isinstance(fixture.get(section), Mapping):
                raise ValueError(f"invalid demo fixture: missing section {section}")
        identity = fixture["identity"]
        for field in ("security_id", "ticker", "legal_name"):
            value = identity.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"invalid demo fixture: identity.{field} is required")
        peers = fixture["peer_comparables"].get("peers")
        if not isinstance(peers, list) or len(peers) < 3:
            raise ValueError("invalid demo fixture: at least three peers are required")
        if not all(isinstance(peer, Mapping) for peer in peers):
            raise ValueError("invalid demo fixture: peer records must be objects")
        if not any(peer.get("status") == "included" for peer in peers) or not any(
            peer.get("status") == "excluded" and peer.get("reason") for peer in peers
        ):
            raise ValueError(
                "invalid demo fixture: peers require included and explained excluded records"
            )
        earnings_events = fixture["earnings_history"].get("events")
        if not isinstance(earnings_events, list) or not earnings_events:
            raise ValueError("invalid demo fixture: earnings events are required")
        if not all(isinstance(event, Mapping) for event in earnings_events):
            raise ValueError("invalid demo fixture: earnings events must be objects")
        catalyst_events = fixture["catalyst_events"].get("events")
        if not isinstance(catalyst_events, list) or not catalyst_events:
            raise ValueError("invalid demo fixture: catalyst events are required")
        if not all(isinstance(event, Mapping) for event in catalyst_events):
            raise ValueError("invalid demo fixture: catalyst events must be objects")
        return fixture

    def _validate_security_id(self, security_id: str) -> None:
        expected = str(self._fixture["identity"]["security_id"])
        if str(security_id).strip() != expected:
            raise LookupError("unknown demo security identifier")

    def _response(
        self,
        payload: Mapping[str, Any],
        operation_warning: str,
    ) -> dict[str, Any]:
        response = deepcopy(dict(payload))
        response.update(
            {
                "as_of_date": self._fixture["as_of_date"],
                "currency": self._fixture["currency"],
                "fixture_version": self._fixture["fixture_version"],
                "is_demo": True,
                "market": self._fixture["market"],
                "source": self._fixture["source"],
                "warnings": [
                    *deepcopy(self._fixture["warnings"]),
                    operation_warning,
                ],
            }
        )
        return response
