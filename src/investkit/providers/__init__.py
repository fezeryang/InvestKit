"""Research data providers shipped with InvestKit."""

from .base import Provider, ProviderRecord
from .demo import DemoProvider

__all__ = ["DemoProvider", "Provider", "ProviderRecord"]
