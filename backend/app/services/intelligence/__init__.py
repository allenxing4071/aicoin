"""Intelligence Services Package"""

from .models import (
    IntelligenceReport,
    NewsItem,
    WhaleActivity,
    OnChainMetrics,
    SentimentType
)
from .cloud_platform_coordinator import CloudPlatformCoordinator
from .multi_platform_coordinator import MultiPlatformCoordinator

# 创建全局云平台协调器实例（用于API管理）
cloud_platform_coordinator = CloudPlatformCoordinator()

__all__ = [
    "IntelligenceReport",
    "NewsItem",
    "WhaleActivity",
    "OnChainMetrics",
    "SentimentType",
    "CloudPlatformCoordinator",
    "MultiPlatformCoordinator",
    "cloud_platform_coordinator"
]

