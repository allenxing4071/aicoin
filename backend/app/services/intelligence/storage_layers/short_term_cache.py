"""Short-Term Intelligence Cache - Qwen情报员短期存储层（Redis）"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class ShortTermIntelligenceCache:
    """
    Qwen情报员短期缓存层（Layer 1）
    
    职责：
    1. 存储原始情报数据
    2. 缓存最近的情报报告
    3. 记录用户交互行为
    4. 提供快速访问接口
    
    存储介质：Redis
    TTL策略：24小时自动过期
    """
    
    def __init__(self, redis_client):
        """
        初始化短期缓存
        
        Args:
            redis_client: Redis客户端实例
        """
        self.redis = redis_client
        self.namespace = "qwen:intelligence"
        self.ttl_hours = 24  # 24小时过期
        
        logger.info("✅ Qwen情报员短期缓存初始化完成")
    
    async def store_report(
        self,
        report_id: str,
        report_data: Dict[str, Any]
    ) -> bool:
        """
        存储情报报告
        
        Args:
            report_id: 报告唯一ID
            report_data: 报告数据
        
        Returns:
            是否存储成功
        """
        try:
            key = f"{self.namespace}:report:{report_id}"
            
            # 序列化报告数据
            serialized = json.dumps(report_data, default=str, ensure_ascii=False)
            
            # 存储到Redis
            await self.redis.setex(
                key,
                self.ttl_hours * 3600,  # 转换为秒
                serialized
            )
            
            # 添加到最近报告列表
            await self.redis.zadd(
                f"{self.namespace}:reports:recent",
                {report_id: datetime.now().timestamp()}
            )
            
            # 维护列表大小（最多100个）
            await self.redis.zremrangebyrank(
                f"{self.namespace}:reports:recent",
                0,
                -101
            )
            
            logger.debug(f"✅ 情报报告已缓存: {report_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 存储情报报告失败: {e}", exc_info=True)
            return False
    
    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        获取情报报告
        
        Args:
            report_id: 报告ID
        
        Returns:
            报告数据，不存在则返回None
        """
        try:
            key = f"{self.namespace}:report:{report_id}"
            data = await self.redis.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取情报报告失败: {e}")
            return None
    
    async def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """
        获取最新的情报报告
        
        Returns:
            最新报告数据
        """
        try:
            # 获取最新的report_id
            recent_ids = await self.redis.zrevrange(
                f"{self.namespace}:reports:recent",
                0,
                0
            )
            
            if not recent_ids:
                return None
            
            latest_id = recent_ids[0]
            return await self.get_report(latest_id)
            
        except Exception as e:
            logger.error(f"❌ 获取最新报告失败: {e}")
            return None
    
    async def get_recent_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的N个报告
        
        Args:
            limit: 返回数量
        
        Returns:
            报告列表
        """
        try:
            # 获取最近的report_ids
            recent_ids = await self.redis.zrevrange(
                f"{self.namespace}:reports:recent",
                0,
                limit - 1
            )
            
            reports = []
            for report_id in recent_ids:
                report = await self.get_report(report_id)
                if report:
                    reports.append(report)
            
            return reports
            
        except Exception as e:
            logger.error(f"❌ 获取最近报告失败: {e}")
            return []
    
    async def record_interaction(
        self,
        report_id: str,
        interaction_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        记录用户交互行为
        
        Args:
            report_id: 报告ID
            interaction_type: 交互类型（view/click/bookmark/share等）
            metadata: 额外元数据
        
        Returns:
            是否记录成功
        """
        try:
            interaction_key = f"{self.namespace}:interactions:{report_id}"
            
            interaction_data = {
                "type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # 添加到交互列表
            await self.redis.rpush(
                interaction_key,
                json.dumps(interaction_data, ensure_ascii=False)
            )
            
            # 设置过期时间
            await self.redis.expire(interaction_key, self.ttl_hours * 3600)
            
            # 更新统计
            stats_key = f"{self.namespace}:stats:interactions"
            await self.redis.hincrby(stats_key, interaction_type, 1)
            
            logger.debug(f"✅ 记录交互: {report_id} - {interaction_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 记录交互失败: {e}")
            return False
    
    async def get_interactions(
        self,
        report_id: str
    ) -> List[Dict[str, Any]]:
        """
        获取报告的交互记录
        
        Args:
            report_id: 报告ID
        
        Returns:
            交互记录列表
        """
        try:
            interaction_key = f"{self.namespace}:interactions:{report_id}"
            raw_data = await self.redis.lrange(interaction_key, 0, -1)
            
            interactions = []
            for item in raw_data:
                interactions.append(json.loads(item))
            
            return interactions
            
        except Exception as e:
            logger.error(f"❌ 获取交互记录失败: {e}")
            return []
    
    async def cache_source_data(
        self,
        source_name: str,
        data: Any,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        缓存数据源的原始数据
        
        Args:
            source_name: 数据源名称
            data: 数据内容
            ttl_seconds: 过期时间（秒）
        
        Returns:
            是否缓存成功
        """
        try:
            key = f"{self.namespace}:source:{source_name}"
            
            serialized = json.dumps(data, default=str, ensure_ascii=False)
            
            ttl = ttl_seconds or (self.ttl_hours * 3600)
            await self.redis.setex(key, ttl, serialized)
            
            logger.debug(f"✅ 数据源已缓存: {source_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 缓存数据源失败: {e}")
            return False
    
    async def get_source_data(self, source_name: str) -> Optional[Any]:
        """
        获取缓存的数据源数据
        
        Args:
            source_name: 数据源名称
        
        Returns:
            数据内容
        """
        try:
            key = f"{self.namespace}:source:{source_name}"
            data = await self.redis.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取数据源缓存失败: {e}")
            return None
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计数据
        """
        try:
            # 报告数量
            report_count = await self.redis.zcard(
                f"{self.namespace}:reports:recent"
            )
            
            # 交互统计
            interaction_stats = await self.redis.hgetall(
                f"{self.namespace}:stats:interactions"
            )
            
            return {
                "total_reports_cached": report_count,
                "interaction_stats": {
                    k: int(v) for k, v in interaction_stats.items()
                } if interaction_stats else {},
                "ttl_hours": self.ttl_hours,
                "namespace": self.namespace
            }
            
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return {}
    
    async def clear_expired(self) -> int:
        """
        清理过期数据（Redis会自动处理，这里仅用于手动触发）
        
        Returns:
            清理的数量
        """
        try:
            # Redis会自动清理过期键，这里主要是清理僵尸引用
            cutoff_time = (datetime.now() - timedelta(hours=self.ttl_hours)).timestamp()
            
            removed = await self.redis.zremrangebyscore(
                f"{self.namespace}:reports:recent",
                0,
                cutoff_time
            )
            
            logger.info(f"✅ 清理过期引用: {removed} 个")
            return removed
            
        except Exception as e:
            logger.error(f"❌ 清理过期数据失败: {e}")
            return 0

