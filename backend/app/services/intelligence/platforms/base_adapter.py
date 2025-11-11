"""Base Platform Adapter - 平台适配器基类"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PlatformRole:
    """平台角色定义"""
    FREE_MONITOR = "基础监控员"
    REALTIME_SCOUT = "实时情报员"
    DEEP_ANALYST = "深度分析师"


class BasePlatformAdapter(ABC):
    """
    平台适配器基类
    
    所有AI平台适配器必须继承此类并实现抽象方法
    """
    
    def __init__(
        self,
        platform_name: str,
        role: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        enabled: bool = True,
        provider: Optional[str] = None  # 新增：数据库provider标识
    ):
        """
        初始化平台适配器
        
        Args:
            platform_name: 平台名称
            role: 平台角色（基础监控员/实时情报员/深度分析师）
            api_key: API密钥（如需要）
            base_url: API基础URL（如需要）
            enabled: 是否启用
            provider: 数据库provider标识（qwen/baidu/tencent/volcano等）
        """
        self.platform_name = platform_name
        self.role = role
        self.api_key = api_key
        self.base_url = base_url
        self.enabled = enabled
        self.provider = provider or self._infer_provider(platform_name)
        
        # 统计信息
        self.call_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_cost = 0.0
        self.last_call_time: Optional[datetime] = None
        
        logger.info(f"✅ 平台适配器初始化: {platform_name} ({role}) [provider={self.provider}]")
    
    def _infer_provider(self, platform_name: str) -> str:
        """从平台名称推断provider"""
        name_lower = platform_name.lower()
        if 'qwen' in name_lower or '阿里' in name_lower or 'aliyun' in name_lower:
            return 'qwen'
        elif 'baidu' in name_lower or '百度' in name_lower:
            return 'baidu'
        elif 'tencent' in name_lower or '腾讯' in name_lower:
            return 'tencent'
        elif 'volcano' in name_lower or '火山' in name_lower:
            return 'volcano'
        elif 'aws' in name_lower:
            return 'aws'
        else:
            return 'unknown'
    
    @abstractmethod
    async def analyze(
        self,
        data_sources: Dict[str, Any],
        query_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分析数据源并生成情报
        
        Args:
            data_sources: 原始数据源数据（新闻、巨鲸活动、链上数据等）
            query_context: 查询上下文（可选）
        
        Returns:
            分析结果字典，包含：
            {
                "platform": str,
                "role": str,
                "analysis": str,
                "confidence": float,
                "key_findings": List[str],
                "timestamp": datetime,
                "cost": float
            }
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取平台统计信息
        
        Returns:
            统计信息字典
        """
        success_rate = (
            self.success_count / self.call_count 
            if self.call_count > 0 
            else 0.0
        )
        
        return {
            "platform_name": self.platform_name,
            "role": self.role,
            "enabled": self.enabled,
            "call_count": self.call_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": success_rate,
            "total_cost": self.total_cost,
            "last_call_time": self.last_call_time.isoformat() if self.last_call_time else None
        }
    
    async def _record_call(self, success: bool, cost: float = 0.0, response_time: float = 0.0):
        """
        记录调用统计（实时同步到数据库）
        
        Args:
            success: 是否成功
            cost: 调用成本
            response_time: 响应时间（毫秒）
        """
        # 1. 更新内存统计
        self.call_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.total_cost += cost
        self.last_call_time = datetime.now()
        
        # 2. 实时同步到数据库
        if self.provider and self.provider != 'unknown':
            try:
                from app.services.intelligence.platform_manager import platform_manager
                # 异步更新数据库（不阻塞当前调用）
                await platform_manager.update_platform_stats(
                    provider=self.provider,
                    success=success,
                    response_time=response_time,
                    cost=cost
                )
                logger.debug(f"✅ 平台统计已同步: {self.platform_name} (provider={self.provider})")
            except Exception as e:
                logger.warning(f"⚠️  数据库统计同步失败 ({self.platform_name}): {e}")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.platform_name}, role={self.role}, enabled={self.enabled})>"

