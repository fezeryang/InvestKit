"""Research data providers shipped with InvestKit."""

from .base import Provider, ProviderRecord
from .ciccwm import CiccwmClient
from .demo import DemoProvider
from .eastmoney import EastmoneyMxClient
from .file import FileProvider
from .fusion import (
    ProviderFusionError,
    fuse_ciccwm_research_bundle,
    fuse_equity_research_bundle,
    fuse_guangfa_target_bundle,
)
from .guangfa import GuangfaClient, normalize_a_share_symbol
from .sse import SseAnnouncementClient

__all__ = [
    "DemoProvider",
    "CiccwmClient",
    "EastmoneyMxClient",
    "FileProvider",
    "ProviderFusionError",
    "GuangfaClient",
    "Provider",
    "ProviderRecord",
    "SseAnnouncementClient",
    "fuse_equity_research_bundle",
    "fuse_ciccwm_research_bundle",
    "fuse_guangfa_target_bundle",
    "normalize_a_share_symbol",
]
