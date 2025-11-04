"""Intelligence Report Storage Service"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from app.core.redis_client import redis_client
from .models import IntelligenceReport as IntelligenceReportModel

# TODO: 添加PostgreSQL存储需要异步实现
# from sqlalchemy.orm import Session
# from app.core.database import AsyncSessionLocal
# from app.models.intelligence import IntelligenceReport as IntelligenceReportDB

logger = logging.getLogger(__name__)


class IntelligenceStorage:
    """Store and retrieve intelligence reports in Redis and PostgreSQL"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.key_prefix = "intelligence:report:"
        self.latest_key = "intelligence:latest"
        self.history_key = "intelligence:history"
        self.max_history = 100  # Keep last 100 reports
    
    async def store_report(self, report: IntelligenceReportModel) -> bool:
        """
        Store intelligence report in Redis
        
        TODO: PostgreSQL持久化存储需要异步实现
        
        Args:
            report: Intelligence report to store
            
        Returns:
            bool: True if storage successful
        """
        try:
            # 1. Store to Redis (fast, 7-day cache)
            redis_success = await self._store_to_redis(report)
            
            # TODO: 2. Store to PostgreSQL (persistent, long-term) - 需要异步实现
            # postgres_success = await self._store_to_postgres_async(report)
            
            if redis_success:
                logger.info(f"✅ 存储情报报告成功: {report.timestamp} (Redis: ✅)")
            
            return redis_success
            
        except Exception as e:
            logger.error(f"❌ 存储情报报告失败: {e}")
            return False
    
    async def _store_to_redis(self, report: IntelligenceReportModel) -> bool:
        """Store intelligence report to Redis"""
        try:
            report_key = f"{self.key_prefix}{report.timestamp.isoformat()}"
            report_data = report.to_dict()
            
            # Store the report (redis_client.set() uses 'expire' parameter, not 'ex')
            await self.redis.set(report_key, report_data, expire=86400 * 7)  # Keep for 7 days
            
            # Update latest pointer
            await self.redis.set(self.latest_key, report_key, expire=86400 * 30)  # Keep pointer for 30 days
            
            # Add to history list
            await self.redis.lpush(self.history_key, report_key)
            await self.redis.ltrim(self.history_key, 0, self.max_history - 1)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis存储失败: {e}")
            return False
    
    # TODO: 实现异步PostgreSQL存储
    # async def _store_to_postgres_async(self, report: IntelligenceReportModel) -> bool:
    #     """Store intelligence report to PostgreSQL (async)"""
    #     async with AsyncSessionLocal() as db:
    #         try:
    #             # Implementation here...
    #             pass
    #         except Exception as e:
    #             logger.error(f"❌ PostgreSQL存储失败: {e}")
    #             await db.rollback()
    #             return False
    
    async def get_latest_report(self) -> Optional[IntelligenceReportModel]:
        """Get the most recent intelligence report"""
        try:
            latest_key = await self.redis.get(self.latest_key)
            if not latest_key:
                logger.warning("⚠️  没有找到最新情报报告")
                return None
            
            # redis_client.get() already handles JSON deserialization
            report_data = await self.redis.get(latest_key)
            if not report_data:
                return None
            
            # report_data is already a dict (auto-deserialized by redis_client)
            report = IntelligenceReportModel.from_dict(report_data)
            
            logger.info(f"✅ 获取最新情报报告: {report.timestamp}")
            return report
            
        except Exception as e:
            logger.error(f"❌ 获取最新情报报告失败: {e}")
            return None
    
    async def get_report_history(self, limit: int = 10) -> List[IntelligenceReportModel]:
        """Get recent intelligence reports"""
        try:
            report_keys = await self.redis.lrange(self.history_key, 0, limit - 1)
            reports = []
            
            for key in report_keys:
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                
                # redis_client.get() already handles JSON deserialization
                report_data = await self.redis.get(key)
                if report_data:
                    reports.append(IntelligenceReportModel.from_dict(report_data))
            
            logger.info(f"✅ 获取历史情报报告: {len(reports)} 条")
            return reports
            
        except Exception as e:
            logger.error(f"❌ 获取历史情报报告失败: {e}")
            return []
    
    async def get_report_by_timestamp(self, timestamp: datetime) -> Optional[IntelligenceReportModel]:
        """Get specific report by timestamp"""
        try:
            report_key = f"{self.key_prefix}{timestamp.isoformat()}"
            # redis_client.get() already handles JSON deserialization
            report_data = await self.redis.get(report_key)
            
            if not report_data:
                return None
            
            return IntelligenceReportModel.from_dict(report_data)
            
        except Exception as e:
            logger.error(f"❌ 获取指定时间情报报告失败: {e}")
            return None
    
    async def is_report_fresh(self, max_age_minutes: int = 30) -> bool:
        """Check if the latest report is still fresh"""
        try:
            latest_report = await self.get_latest_report()
            if not latest_report:
                return False
            
            age = datetime.now() - latest_report.timestamp
            is_fresh = age.total_seconds() < (max_age_minutes * 60)
            
            if not is_fresh:
                logger.info(f"⏰ 情报报告已过期: {age.total_seconds() / 60:.1f} 分钟前")
            
            return is_fresh
            
        except Exception as e:
            logger.error(f"❌ 检查情报新鲜度失败: {e}")
            return False


# Singleton instance
intelligence_storage = IntelligenceStorage(redis_client)

