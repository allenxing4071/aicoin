"""Long-Term Intelligence Store - Qwen情报员长期存储层（PostgreSQL）"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class LongTermIntelligenceStore:
    """
    Qwen情报员长期存储层（Layer 3）
    
    职责：
    1. 存储结构化情报知识
    2. 维护信息源权重历史
    3. 记录情报效果评估
    4. 提供历史查询接口
    
    存储介质：PostgreSQL
    保留策略：永久保存，定期归档
    """
    
    def __init__(self, db_session):
        """
        初始化长期存储
        
        Args:
            db_session: 数据库会话
        """
        self.db = db_session
        
        logger.info("✅ Qwen情报员长期存储初始化完成")
    
    async def store_source_weight(
        self,
        source_name: str,
        source_type: str,
        weight: float,
        metrics: Dict[str, Any]
    ) -> bool:
        """
        存储信息源权重
        
        Args:
            source_name: 源名称
            source_type: 源类型（news/whale/onchain/search）
            weight: 权重值
            metrics: 指标数据
        
        Returns:
            是否存储成功
        """
        try:
            from app.models.intelligence_source_weight import IntelligenceSourceWeight
            
            # 查找或创建
            stmt = f"SELECT * FROM intelligence_source_weights WHERE source_name = '{source_name}'"
            result = await self.db.execute(stmt)
            existing = result.first()
            
            if existing:
                # 更新
                update_stmt = f"""
                UPDATE intelligence_source_weights
                SET dynamic_weight = {weight},
                    usage_count = {metrics.get('usage_count', 0)},
                    positive_feedback_count = {metrics.get('positive_feedback', 0)},
                    effectiveness_score = {metrics.get('effectiveness', 0.5)},
                    updated_at = NOW()
                WHERE source_name = '{source_name}'
                """
                await self.db.execute(update_stmt)
            else:
                # 创建
                insert_stmt = f"""
                INSERT INTO intelligence_source_weights
                (source_name, source_type, base_weight, dynamic_weight, 
                 usage_count, positive_feedback_count, effectiveness_score)
                VALUES ('{source_name}', '{source_type}', 0.5, {weight},
                        {metrics.get('usage_count', 0)}, {metrics.get('positive_feedback', 0)},
                        {metrics.get('effectiveness', 0.5)})
                """
                await self.db.execute(insert_stmt)
            
            await self.db.commit()
            
            logger.debug(f"✅ 信息源权重已存储: {source_name} = {weight:.3f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 存储信息源权重失败: {e}", exc_info=True)
            await self.db.rollback()
            return False
    
    async def get_source_weight(self, source_name: str) -> Optional[float]:
        """
        获取信息源权重
        
        Args:
            source_name: 源名称
        
        Returns:
            权重值
        """
        try:
            stmt = f"""
            SELECT dynamic_weight FROM intelligence_source_weights
            WHERE source_name = '{source_name}'
            """
            result = await self.db.execute(stmt)
            row = result.first()
            
            if row:
                return float(row[0])
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取信息源权重失败: {e}")
            return None
    
    async def get_all_source_weights(self) -> Dict[str, float]:
        """
        获取所有信息源权重
        
        Returns:
            {source_name: weight} 字典
        """
        try:
            stmt = """
            SELECT source_name, dynamic_weight
            FROM intelligence_source_weights
            ORDER BY dynamic_weight DESC
            """
            result = await self.db.execute(stmt)
            rows = result.fetchall()
            
            return {
                row[0]: float(row[1])
                for row in rows
            }
            
        except Exception as e:
            logger.error(f"❌ 获取所有权重失败: {e}")
            return {}
    
    async def record_feedback(
        self,
        report_id: str,
        source_name: str,
        feedback_type: str,
        effectiveness_rating: Optional[float] = None,
        decision_influenced: bool = False,
        decision_outcome: Optional[str] = None
    ) -> bool:
        """
        记录情报反馈
        
        Args:
            report_id: 报告ID
            source_name: 源名称
            feedback_type: 反馈类型
            effectiveness_rating: 效果评分
            decision_influenced: 是否影响决策
            decision_outcome: 决策结果
        
        Returns:
            是否记录成功
        """
        try:
            insert_stmt = f"""
            INSERT INTO intelligence_feedback
            (report_id, source_name, feedback_type, effectiveness_rating,
             decision_influenced, decision_outcome)
            VALUES ('{report_id}', '{source_name}', '{feedback_type}',
                    {effectiveness_rating if effectiveness_rating else 'NULL'},
                    {decision_influenced}, 
                    {f"'{decision_outcome}'" if decision_outcome else 'NULL'})
            """
            await self.db.execute(insert_stmt)
            await self.db.commit()
            
            logger.debug(f"✅ 反馈已记录: {source_name} - {feedback_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 记录反馈失败: {e}")
            await self.db.rollback()
            return False
    
    async def get_source_statistics(
        self,
        source_name: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取信息源统计数据
        
        Args:
            source_name: 源名称
            days: 统计天数
        
        Returns:
            统计数据
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            stmt = f"""
            SELECT 
                COUNT(*) as total_feedbacks,
                AVG(effectiveness_rating) as avg_effectiveness,
                SUM(CASE WHEN decision_influenced THEN 1 ELSE 0 END) as influenced_count,
                SUM(CASE WHEN decision_outcome = 'success' THEN 1 ELSE 0 END) as success_count
            FROM intelligence_feedback
            WHERE source_name = '{source_name}'
              AND created_at >= '{cutoff_date.isoformat()}'
            """
            
            result = await self.db.execute(stmt)
            row = result.first()
            
            if row:
                return {
                    "source_name": source_name,
                    "days": days,
                    "total_feedbacks": row[0] or 0,
                    "avg_effectiveness": float(row[1]) if row[1] else 0.0,
                    "influenced_count": row[2] or 0,
                    "success_count": row[3] or 0,
                    "success_rate": (
                        (row[3] / row[2] * 100)
                        if row[2] and row[2] > 0
                        else 0.0
                    )
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ 获取源统计失败: {e}")
            return {}
    
    async def get_top_sources(
        self,
        limit: int = 10,
        metric: str = "effectiveness"
    ) -> List[Dict[str, Any]]:
        """
        获取Top N信息源
        
        Args:
            limit: 返回数量
            metric: 排序指标（effectiveness/weight/usage）
        
        Returns:
            Top源列表
        """
        try:
            order_by = {
                "effectiveness": "effectiveness_score DESC",
                "weight": "dynamic_weight DESC",
                "usage": "usage_count DESC"
            }.get(metric, "effectiveness_score DESC")
            
            stmt = f"""
            SELECT source_name, source_type, dynamic_weight,
                   usage_count, effectiveness_score, last_used_at
            FROM intelligence_source_weights
            ORDER BY {order_by}
            LIMIT {limit}
            """
            
            result = await self.db.execute(stmt)
            rows = result.fetchall()
            
            return [
                {
                    "source_name": row[0],
                    "source_type": row[1],
                    "weight": float(row[2]),
                    "usage_count": row[3],
                    "effectiveness": float(row[4]),
                    "last_used_at": row[5].isoformat() if row[5] else None
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"❌ 获取Top源失败: {e}")
            return []
    
    async def cleanup_old_feedback(self, days: int = 90) -> int:
        """
        清理旧反馈数据
        
        Args:
            days: 保留天数
        
        Returns:
            删除的记录数
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            stmt = f"""
            DELETE FROM intelligence_feedback
            WHERE created_at < '{cutoff_date.isoformat()}'
            """
            
            result = await self.db.execute(stmt)
            await self.db.commit()
            
            deleted = result.rowcount
            logger.info(f"✅ 清理旧反馈: {deleted} 条")
            
            return deleted
            
        except Exception as e:
            logger.error(f"❌ 清理旧反馈失败: {e}")
            await self.db.rollback()
            return 0

