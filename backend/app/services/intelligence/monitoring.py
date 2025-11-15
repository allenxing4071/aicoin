"""
Intelligence System Monitoring - 情报系统监控

提供情报系统的健康检查、性能监控和指标统计
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.redis_client import RedisClient
from app.utils.timezone import get_beijing_time

logger = logging.getLogger(__name__)


class IntelligenceMonitor:
    """
    情报系统监控器
    
    功能：
    1. 系统健康检查
    2. 性能指标统计
    3. 存储层状态监控
    4. 多平台协调监控
    """
    
    def __init__(self, redis_client: RedisClient, db_session):
        """
        初始化监控器
        
        Args:
            redis_client: Redis客户端
            db_session: 数据库会话
        """
        self.redis = redis_client
        self.db_session = db_session
        
        # 性能指标缓存键
        self.metrics_key_prefix = "intelligence:metrics"
        
        logger.info("✅ IntelligenceMonitor初始化完成")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        获取系统健康状态
        
        Returns:
            Dict: 健康状态字典
        """
        try:
            health = {
                "timestamp": get_beijing_time().isoformat(),
                "overall_status": "healthy",
                "components": {}
            }
            
            # 检查L1缓存健康
            l1_health = await self._check_l1_health()
            health["components"]["l1_cache"] = l1_health
            
            # 检查L2分析器健康
            l2_health = await self._check_l2_health()
            health["components"]["l2_analyzer"] = l2_health
            
            # 检查L3存储健康
            l3_health = await self._check_l3_health()
            health["components"]["l3_store"] = l3_health
            
            # 检查L4向量库健康
            l4_health = await self._check_l4_health()
            health["components"]["l4_vector"] = l4_health
            
            # 检查多平台协调器健康
            platform_health = await self._check_platform_health()
            health["components"]["multi_platform"] = platform_health
            
            # 计算总体状态
            component_statuses = [comp["status"] for comp in health["components"].values()]
            if all(status == "healthy" for status in component_statuses):
                health["overall_status"] = "healthy"
            elif any(status == "unhealthy" for status in component_statuses):
                health["overall_status"] = "degraded"
            else:
                health["overall_status"] = "unknown"
            
            return health
            
        except Exception as e:
            logger.error(f"❌ 获取系统健康状态失败: {e}", exc_info=True)
            return {
                "timestamp": get_beijing_time().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
    
    async def _check_l1_health(self) -> Dict[str, Any]:
        """检查L1缓存健康"""
        try:
            from .storage_layers import ShortTermIntelligenceCache
            
            l1_cache = ShortTermIntelligenceCache(self.redis)
            
            # 检查是否能获取最新报告
            start = time.time()
            latest = await l1_cache.get_latest_report()
            latency = time.time() - start
            
            return {
                "status": "healthy",
                "has_data": latest is not None,
                "latency_ms": round(latency * 1000, 2),
                "last_updated": latest.get("timestamp") if latest else None
            }
        except Exception as e:
            logger.error(f"L1健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_l2_health(self) -> Dict[str, Any]:
        """检查L2分析器健康"""
        try:
            from .storage_layers import MidTermIntelligenceAnalyzer
            
            l2_analyzer = MidTermIntelligenceAnalyzer(self.redis, self.db_session)
            
            # 检查是否能计算权重
            start = time.time()
            weights = await l2_analyzer.calculate_source_weights()
            latency = time.time() - start
            
            return {
                "status": "healthy",
                "source_count": len(weights),
                "latency_ms": round(latency * 1000, 2)
            }
        except Exception as e:
            logger.error(f"L2健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_l3_health(self) -> Dict[str, Any]:
        """检查L3存储健康"""
        try:
            from .storage_layers import LongTermIntelligenceStore
            
            l3_store = LongTermIntelligenceStore(self.db_session)
            
            # 简单检查：尝试查询权重历史
            # 这里只做基本检查，不实际查询数据库
            
            return {
                "status": "healthy",
                "note": "Basic health check passed"
            }
        except Exception as e:
            logger.error(f"L3健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_l4_health(self) -> Dict[str, Any]:
        """检查L4向量库健康"""
        try:
            from qdrant_client import QdrantClient
            from app.core.config import settings
            
            # 直接使用QdrantClient检查，避免重复创建collection
            client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT
            )
            
            # 检查collection是否存在
            collection_name = "intelligence_knowledge"
            collections = client.get_collections().collections
            collection_exists = any(c.name == collection_name for c in collections)
            
            if not collection_exists:
                return {
                    "status": "unhealthy",
                    "error": f"Collection '{collection_name}' does not exist"
                }
            
            # 获取collection信息
            collection_info = client.get_collection(collection_name)
            
            return {
                "status": "healthy",
                "collection": collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count
            }
        except Exception as e:
            logger.error(f"L4健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_platform_health(self) -> Dict[str, Any]:
        """检查多平台协调器健康"""
        try:
            from .multi_platform_coordinator import MultiPlatformCoordinator
            
            # 简单检查：确认协调器可以初始化
            coordinator = MultiPlatformCoordinator()
            
            return {
                "status": "healthy",
                "note": "Multi-platform coordinator initialized"
            }
        except Exception as e:
            logger.error(f"多平台健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标
        
        Returns:
            Dict: 性能指标字典
        """
        try:
            metrics = {
                "timestamp": get_beijing_time().isoformat(),
                "collection_metrics": await self._get_collection_metrics(),
                "cache_metrics": await self._get_cache_metrics(),
                "platform_metrics": await self._get_platform_metrics(),
                "storage_metrics": await self._get_storage_metrics()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ 获取性能指标失败: {e}", exc_info=True)
            return {
                "timestamp": get_beijing_time().isoformat(),
                "error": str(e)
            }
    
    async def _get_collection_metrics(self) -> Dict[str, Any]:
        """获取情报收集指标"""
        try:
            # 从Redis获取收集指标
            key = f"{self.metrics_key_prefix}:collection"
            
            total_count = await self.redis.get(f"{key}:total_count") or 0
            success_count = await self.redis.get(f"{key}:success_count") or 0
            avg_time = await self.redis.get(f"{key}:avg_time") or 0
            
            return {
                "total_collections": int(total_count),
                "successful_collections": int(success_count),
                "success_rate": float(success_count) / float(total_count) if int(total_count) > 0 else 0,
                "avg_collection_time_seconds": float(avg_time)
            }
        except Exception as e:
            logger.error(f"获取收集指标失败: {e}")
            return {}
    
    async def _get_cache_metrics(self) -> Dict[str, Any]:
        """获取缓存指标"""
        try:
            key = f"{self.metrics_key_prefix}:cache"
            
            hit_count = await self.redis.get(f"{key}:hit_count") or 0
            miss_count = await self.redis.get(f"{key}:miss_count") or 0
            
            total = int(hit_count) + int(miss_count)
            hit_rate = float(hit_count) / total if total > 0 else 0
            
            return {
                "cache_hits": int(hit_count),
                "cache_misses": int(miss_count),
                "cache_hit_rate": hit_rate
            }
        except Exception as e:
            logger.error(f"获取缓存指标失败: {e}")
            return {}
    
    async def _get_platform_metrics(self) -> Dict[str, Any]:
        """获取平台指标"""
        try:
            key = f"{self.metrics_key_prefix}:platform"
            
            total_calls = await self.redis.get(f"{key}:total_calls") or 0
            success_calls = await self.redis.get(f"{key}:success_calls") or 0
            
            return {
                "total_platform_calls": int(total_calls),
                "successful_calls": int(success_calls),
                "platform_success_rate": float(success_calls) / float(total_calls) if int(total_calls) > 0 else 0
            }
        except Exception as e:
            logger.error(f"获取平台指标失败: {e}")
            return {}
    
    async def _get_storage_metrics(self) -> Dict[str, Any]:
        """获取存储指标"""
        try:
            key = f"{self.metrics_key_prefix}:storage"
            
            l1_writes = await self.redis.get(f"{key}:l1_writes") or 0
            l2_analyses = await self.redis.get(f"{key}:l2_analyses") or 0
            l3_writes = await self.redis.get(f"{key}:l3_writes") or 0
            l4_vectorizations = await self.redis.get(f"{key}:l4_vectorizations") or 0
            
            return {
                "l1_cache_writes": int(l1_writes),
                "l2_analyses_completed": int(l2_analyses),
                "l3_store_writes": int(l3_writes),
                "l4_vectorizations": int(l4_vectorizations)
            }
        except Exception as e:
            logger.error(f"获取存储指标失败: {e}")
            return {}
    
    async def record_collection_metric(self, success: bool, duration_seconds: float):
        """
        记录情报收集指标
        
        Args:
            success: 是否成功
            duration_seconds: 耗时（秒）
        """
        try:
            key = f"{self.metrics_key_prefix}:collection"
            
            # 增加计数
            await self.redis.incr(f"{key}:total_count")
            if success:
                await self.redis.incr(f"{key}:success_count")
            
            # 更新平均时间（简化版：使用移动平均）
            current_avg = float(await self.redis.get(f"{key}:avg_time") or 0)
            total_count = int(await self.redis.get(f"{key}:total_count") or 1)
            new_avg = (current_avg * (total_count - 1) + duration_seconds) / total_count
            await self.redis.set(f"{key}:avg_time", str(new_avg))
            
        except Exception as e:
            logger.error(f"记录收集指标失败: {e}")
    
    async def record_cache_metric(self, hit: bool):
        """
        记录缓存指标
        
        Args:
            hit: 是否命中
        """
        try:
            key = f"{self.metrics_key_prefix}:cache"
            
            if hit:
                await self.redis.incr(f"{key}:hit_count")
            else:
                await self.redis.incr(f"{key}:miss_count")
                
        except Exception as e:
            logger.error(f"记录缓存指标失败: {e}")
    
    async def record_platform_metric(self, success: bool):
        """
        记录平台调用指标
        
        Args:
            success: 是否成功
        """
        try:
            key = f"{self.metrics_key_prefix}:platform"
            
            await self.redis.incr(f"{key}:total_calls")
            if success:
                await self.redis.incr(f"{key}:success_calls")
                
        except Exception as e:
            logger.error(f"记录平台指标失败: {e}")
    
    async def record_storage_metric(self, layer: str):
        """
        记录存储层指标
        
        Args:
            layer: 存储层（l1/l2/l3/l4）
        """
        try:
            key = f"{self.metrics_key_prefix}:storage"
            
            if layer == "l1":
                await self.redis.incr(f"{key}:l1_writes")
            elif layer == "l2":
                await self.redis.incr(f"{key}:l2_analyses")
            elif layer == "l3":
                await self.redis.incr(f"{key}:l3_writes")
            elif layer == "l4":
                await self.redis.incr(f"{key}:l4_vectorizations")
                
        except Exception as e:
            logger.error(f"记录存储指标失败: {e}")
    
    async def get_system_summary(self) -> Dict[str, Any]:
        """
        获取系统摘要（健康+性能）
        
        Returns:
            Dict: 系统摘要
        """
        try:
            health = await self.get_system_health()
            metrics = await self.get_performance_metrics()
            
            return {
                "timestamp": get_beijing_time().isoformat(),
                "health": health,
                "metrics": metrics,
                "summary": {
                    "overall_status": health.get("overall_status"),
                    "total_collections": metrics.get("collection_metrics", {}).get("total_collections", 0),
                    "cache_hit_rate": metrics.get("cache_metrics", {}).get("cache_hit_rate", 0),
                    "platform_success_rate": metrics.get("platform_metrics", {}).get("platform_success_rate", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 获取系统摘要失败: {e}", exc_info=True)
            return {
                "timestamp": get_beijing_time().isoformat(),
                "error": str(e)
            }

