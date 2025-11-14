"""
Debate Rate Limiter - 辩论限流保护
防止 API 成本失控
"""

from datetime import datetime
from typing import Optional
import logging

from app.core.redis_client import RedisClient

logger = logging.getLogger(__name__)


class DebateRateLimiter:
    """辩论限流器"""
    
    def __init__(self, redis_client: RedisClient, daily_limit: int = 100, hourly_limit: int = 10):
        """
        初始化限流器
        
        Args:
            redis_client: Redis 客户端
            daily_limit: 每日最大辩论次数
            hourly_limit: 每小时最大辩论次数
        """
        self.redis = redis_client
        self.daily_limit = daily_limit
        self.hourly_limit = hourly_limit
    
    async def check_rate_limit(self) -> tuple[bool, Optional[str]]:
        """
        检查是否超过限流
        
        Returns:
            (是否允许, 拒绝原因)
        """
        today = datetime.now().strftime("%Y%m%d")
        hour = datetime.now().strftime("%Y%m%d%H")
        
        daily_key = f"debate:daily:{today}"
        hourly_key = f"debate:hourly:{hour}"
        
        try:
            # 检查每日限制
            daily_count_str = await self.redis.get(daily_key)
            daily_count = int(daily_count_str) if daily_count_str else 0
            
            if daily_count >= self.daily_limit:
                logger.warning(f"⚠️  达到每日辩论限制: {daily_count}/{self.daily_limit}")
                return False, f"达到每日限制({self.daily_limit}次)"
            
            # 检查每小时限制
            hourly_count_str = await self.redis.get(hourly_key)
            hourly_count = int(hourly_count_str) if hourly_count_str else 0
            
            if hourly_count >= self.hourly_limit:
                logger.warning(f"⚠️  达到每小时辩论限制: {hourly_count}/{self.hourly_limit}")
                return False, f"达到每小时限制({self.hourly_limit}次)"
            
            return True, None
            
        except Exception as e:
            logger.error(f"检查限流失败: {e}")
            # 出错时允许通过（避免限流器故障导致系统不可用）
            return True, None
    
    async def increment_count(self):
        """增加辩论计数"""
        today = datetime.now().strftime("%Y%m%d")
        hour = datetime.now().strftime("%Y%m%d%H")
        
        daily_key = f"debate:daily:{today}"
        hourly_key = f"debate:hourly:{hour}"
        
        try:
            # 增加每日计数
            await self.redis.incr(daily_key)
            await self.redis.expire(daily_key, 86400)  # 24小时过期
            
            # 增加每小时计数
            await self.redis.incr(hourly_key)
            await self.redis.expire(hourly_key, 3600)  # 1小时过期
            
            logger.debug("📊 辩论计数已更新")
            
        except Exception as e:
            logger.error(f"更新辩论计数失败: {e}")
    
    async def get_current_counts(self) -> dict:
        """获取当前计数"""
        today = datetime.now().strftime("%Y%m%d")
        hour = datetime.now().strftime("%Y%m%d%H")
        
        daily_key = f"debate:daily:{today}"
        hourly_key = f"debate:hourly:{hour}"
        
        try:
            daily_count_str = await self.redis.get(daily_key)
            hourly_count_str = await self.redis.get(hourly_key)
            
            daily_count = int(daily_count_str) if daily_count_str else 0
            hourly_count = int(hourly_count_str) if hourly_count_str else 0
            
            return {
                "daily_count": daily_count,
                "daily_limit": self.daily_limit,
                "daily_remaining": max(0, self.daily_limit - daily_count),
                "hourly_count": hourly_count,
                "hourly_limit": self.hourly_limit,
                "hourly_remaining": max(0, self.hourly_limit - hourly_count)
            }
            
        except Exception as e:
            logger.error(f"获取计数失败: {e}")
            return {
                "daily_count": 0,
                "daily_limit": self.daily_limit,
                "daily_remaining": self.daily_limit,
                "hourly_count": 0,
                "hourly_limit": self.hourly_limit,
                "hourly_remaining": self.hourly_limit
            }
    
    async def reset_counts(self):
        """重置计数（管理员操作）"""
        today = datetime.now().strftime("%Y%m%d")
        hour = datetime.now().strftime("%Y%m%d%H")
        
        daily_key = f"debate:daily:{today}"
        hourly_key = f"debate:hourly:{hour}"
        
        try:
            await self.redis.delete(daily_key)
            await self.redis.delete(hourly_key)
            logger.warning("🔄 辩论计数已重置")
        except Exception as e:
            logger.error(f"重置计数失败: {e}")

