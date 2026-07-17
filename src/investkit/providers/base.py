"""Provider contract for normalized InvestKit research data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


ProviderRecord = Mapping[str, Any]


class Provider(ABC):
    """Read-only research-data interface implemented by InvestKit providers."""

    @abstractmethod
    def identify_security(self, query: str) -> ProviderRecord:
        """Resolve a query to a stable security identity."""

    @abstractmethod
    def get_security_profile(self, security_id: str) -> ProviderRecord:
        """Return normalized company profile data."""

    @abstractmethod
    def get_financial_statements(self, security_id: str) -> ProviderRecord:
        """Return normalized financial statement periods."""

    @abstractmethod
    def get_price_history(self, security_id: str) -> ProviderRecord:
        """Return dated price observations used by research calculations."""

    @abstractmethod
    def get_valuation_inputs(self, security_id: str) -> ProviderRecord:
        """Return normalized inputs for bounded valuation methods."""

    @abstractmethod
    def get_source_metadata(self, security_id: str) -> ProviderRecord:
        """Return provenance and limitations for provider records."""

    @abstractmethod
    def get_peer_comparables(self, security_id: str) -> ProviderRecord:
        """Return a bounded peer set with explicit inclusion decisions."""

    @abstractmethod
    def get_earnings_history(self, security_id: str) -> ProviderRecord:
        """Return point-in-time actual, expectation, and guidance records."""

    @abstractmethod
    def get_catalyst_events(self, security_id: str) -> ProviderRecord:
        """Return dated events with evidence and explicit uncertainty."""
