"""Source Weight Optimizer - 信息源权重优化器"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class SourceWeightOptimizer:
    """
    信息源权重优化器
    
    职责：
    1. 收集反馈数据
    2. 计算动态权重
    3. 优化信息源优先级
    4. 生成优化建议
    
    优化策略：
    - 基于使用频率
    - 基于用户反馈
    - 基于决策影响
    - 基于准确性评估
    """
    
    def __init__(
        self,
        redis_client,
        db_session
    ):
        """
        初始化权重优化器
        
        Args:
            redis_client: Redis客户端
            db_session: 数据库会话
        """
        self.redis = redis_client
        self.db = db_session
        
        # 权重计算参数
        self.weights_formula = {
            "usage_frequency": 0.25,
            "user_engagement": 0.30,
            "decision_influence": 0.25,
            "accuracy_score": 0.20
        }
        
        logger.info("✅ 信息源权重优化器初始化完成")
    
    async def optimize_weights(
        self,
        time_window_days: int = 30
    ) -> Dict[str, float]:
        """
        优化所有信息源权重
        
        Args:
            time_window_days: 分析时间窗口（天）
        
        Returns:
            {source_name: optimized_weight} 字典
        """
        try:
            logger.info(f"🔧 开始优化信息源权重（{time_window_days}天窗口）...")
            
            # 1. 收集反馈数据
            feedback_data = await self._collect_feedback_data(time_window_days)
            
            # 2. 计算每个源的指标
            source_metrics = await self._calculate_source_metrics(feedback_data)
            
            # 3. 计算优化后的权重
            optimized_weights = {}
            for source_name, metrics in source_metrics.items():
                weight = self._compute_optimized_weight(metrics)
                optimized_weights[source_name] = weight
            
            # 4. 归一化权重
            optimized_weights = self._normalize_weights(optimized_weights)
            
            # 5. 更新到数据库
            await self._update_weights_to_db(optimized_weights, source_metrics)
            
            # 6. 缓存到Redis
            await self._cache_weights(optimized_weights)
            
            logger.info(f"✅ 权重优化完成: {len(optimized_weights)} 个源")
            
            return optimized_weights
            
        except Exception as e:
            logger.error(f"❌ 权重优化失败: {e}", exc_info=True)
            return {}
    
    async def _collect_feedback_data(
        self,
        days: int
    ) -> List[Dict[str, Any]]:
        """收集反馈数据"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            stmt = f"""
            SELECT 
                source_name,
                user_interaction,
                effectiveness_rating,
                decision_influenced,
                decision_outcome,
                feedback_type,
                created_at
            FROM intelligence_feedback
            WHERE created_at >= '{cutoff_date.isoformat()}'
            ORDER BY created_at DESC
            """
            
            result = await self.db.execute(stmt)
            rows = result.fetchall()
            
            feedback_data = []
            for row in rows:
                feedback_data.append({
                    "source_name": row[0],
                    "user_interaction": row[1],
                    "effectiveness_rating": float(row[2]) if row[2] else None,
                    "decision_influenced": bool(row[3]),
                    "decision_outcome": row[4],
                    "feedback_type": row[5],
                    "created_at": row[6]
                })
            
            logger.debug(f"收集到 {len(feedback_data)} 条反馈数据")
            return feedback_data
            
        except Exception as e:
            logger.error(f"收集反馈数据失败: {e}")
            return []
    
    async def _calculate_source_metrics(
        self,
        feedback_data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """计算源指标"""
        source_metrics = defaultdict(lambda: {
            "total_usage": 0,
            "positive_interactions": 0,
            "total_interactions": 0,
            "decision_influenced": 0,
            "successful_decisions": 0,
            "failed_decisions": 0,
            "effectiveness_ratings": []
        })
        
        for feedback in feedback_data:
            source_name = feedback["source_name"]
            metrics = source_metrics[source_name]
            
            # 使用次数
            metrics["total_usage"] += 1
            
            # 交互统计
            if feedback["user_interaction"]:
                metrics["total_interactions"] += 1
                if feedback["user_interaction"] in ["click", "bookmark", "share"]:
                    metrics["positive_interactions"] += 1
            
            # 决策影响
            if feedback["decision_influenced"]:
                metrics["decision_influenced"] += 1
                
                if feedback["decision_outcome"] == "success":
                    metrics["successful_decisions"] += 1
                elif feedback["decision_outcome"] == "failure":
                    metrics["failed_decisions"] += 1
            
            # 效果评分
            if feedback["effectiveness_rating"] is not None:
                metrics["effectiveness_ratings"].append(feedback["effectiveness_rating"])
        
        return dict(source_metrics)
    
    def _compute_optimized_weight(
        self,
        metrics: Dict[str, Any]
    ) -> float:
        """
        计算优化后的权重
        
        公式：
        weight = Σ(factor_weight * normalized_factor_value)
        """
        # 1. 使用频率 (0-1)
        usage_frequency = min(metrics["total_usage"] / 100.0, 1.0)
        
        # 2. 用户参与度 (0-1)
        user_engagement = (
            metrics["positive_interactions"] / metrics["total_interactions"]
            if metrics["total_interactions"] > 0
            else 0.5
        )
        
        # 3. 决策影响力 (0-1)
        decision_influence = (
            metrics["decision_influenced"] / metrics["total_usage"]
            if metrics["total_usage"] > 0
            else 0.0
        )
        
        # 4. 准确性评分 (0-1)
        if metrics["effectiveness_ratings"]:
            import statistics
            accuracy_score = statistics.mean(metrics["effectiveness_ratings"])
        else:
            # 基于成功率的默认评分
            total_decisions = metrics["successful_decisions"] + metrics["failed_decisions"]
            if total_decisions > 0:
                accuracy_score = metrics["successful_decisions"] / total_decisions
            else:
                accuracy_score = 0.5  # 默认中等
        
        # 加权计算
        weight = (
            self.weights_formula["usage_frequency"] * usage_frequency +
            self.weights_formula["user_engagement"] * user_engagement +
            self.weights_formula["decision_influence"] * decision_influence +
            self.weights_formula["accuracy_score"] * accuracy_score
        )
        
        return weight
    
    def _normalize_weights(
        self,
        weights: Dict[str, float]
    ) -> Dict[str, float]:
        """归一化权重，使总和为1"""
        if not weights:
            return {}
        
        total = sum(weights.values())
        if total == 0:
            return {k: 1.0 / len(weights) for k in weights.keys()}
        
        return {
            source: weight / total
            for source, weight in weights.items()
        }
    
    async def _update_weights_to_db(
        self,
        weights: Dict[str, float],
        metrics: Dict[str, Dict[str, Any]]
    ) -> bool:
        """更新权重到数据库"""
        try:
            for source_name, weight in weights.items():
                source_metrics = metrics.get(source_name, {})
                
                # 检查是否存在
                check_stmt = f"""
                SELECT id FROM intelligence_source_weights
                WHERE source_name = '{source_name}'
                """
                result = await self.db.execute(check_stmt)
                existing = result.first()
                
                if existing:
                    # 更新
                    update_stmt = f"""
                    UPDATE intelligence_source_weights
                    SET dynamic_weight = {weight},
                        usage_count = {source_metrics.get('total_usage', 0)},
                        positive_feedback_count = {source_metrics.get('positive_interactions', 0)},
                        effectiveness_score = {self._get_effectiveness(source_metrics)},
                        last_used_at = NOW(),
                        updated_at = NOW()
                    WHERE source_name = '{source_name}'
                    """
                    await self.db.execute(update_stmt)
                else:
                    # 插入新记录
                    insert_stmt = f"""
                    INSERT INTO intelligence_source_weights
                    (source_name, source_type, base_weight, dynamic_weight, 
                     usage_count, positive_feedback_count, effectiveness_score)
                    VALUES ('{source_name}', 'auto_detected', 0.5, {weight},
                            {source_metrics.get('total_usage', 0)},
                            {source_metrics.get('positive_interactions', 0)},
                            {self._get_effectiveness(source_metrics)})
                    """
                    await self.db.execute(insert_stmt)
            
            await self.db.commit()
            logger.debug("✅ 权重已更新到数据库")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新权重到数据库失败: {e}")
            await self.db.rollback()
            return False
    
    def _get_effectiveness(self, metrics: Dict[str, Any]) -> float:
        """计算效果评分"""
        if metrics.get("effectiveness_ratings"):
            import statistics
            return statistics.mean(metrics["effectiveness_ratings"])
        return 0.5
    
    async def _cache_weights(
        self,
        weights: Dict[str, float]
    ) -> bool:
        """缓存权重到Redis"""
        try:
            import json
            key = "qwen:intelligence:optimized_weights"
            serialized = json.dumps(weights, ensure_ascii=False)
            await self.redis.setex(key, 3600 * 24, serialized)  # 24小时
            return True
        except Exception as e:
            logger.error(f"缓存权重失败: {e}")
            return False
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """
        生成优化报告
        
        Returns:
            优化报告
        """
        try:
            # 获取当前权重
            stmt = """
            SELECT source_name, dynamic_weight, usage_count, 
                   effectiveness_score, updated_at
            FROM intelligence_source_weights
            ORDER BY dynamic_weight DESC
            LIMIT 20
            """
            result = await self.db.execute(stmt)
            rows = result.fetchall()
            
            top_sources = [
                {
                    "source_name": row[0],
                    "weight": float(row[1]),
                    "usage_count": row[2],
                    "effectiveness": float(row[3]),
                    "last_updated": row[4].isoformat() if row[4] else None
                }
                for row in rows
            ]
            
            # 统计信息
            total_sources = len(top_sources)
            avg_weight = sum(s["weight"] for s in top_sources) / total_sources if total_sources > 0 else 0
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "total_sources": total_sources,
                "average_weight": avg_weight,
                "top_sources": top_sources[:10],
                "optimization_formula": self.weights_formula
            }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ 生成优化报告失败: {e}")
            return {}
    
    async def suggest_improvements(self) -> List[Dict[str, Any]]:
        """
        提供优化建议
        
        Returns:
            改进建议列表
        """
        suggestions = []
        
        try:
            # 获取低权重但高使用的源
            stmt = """
            SELECT source_name, dynamic_weight, usage_count
            FROM intelligence_source_weights
            WHERE usage_count > 10 AND dynamic_weight < 0.3
            ORDER BY usage_count DESC
            LIMIT 5
            """
            result = await self.db.execute(stmt)
            rows = result.fetchall()
            
            for row in rows:
                suggestions.append({
                    "type": "undervalued_source",
                    "source_name": row[0],
                    "current_weight": float(row[1]),
                    "usage_count": row[2],
                    "suggestion": "该源使用频繁但权重较低，建议检查质量或提高权重"
                })
            
            # 获取高权重但低使用的源
            stmt = """
            SELECT source_name, dynamic_weight, usage_count
            FROM intelligence_source_weights
            WHERE dynamic_weight > 0.7 AND usage_count < 5
            ORDER BY dynamic_weight DESC
            LIMIT 5
            """
            result = await self.db.execute(stmt)
            rows = result.fetchall()
            
            for row in rows:
                suggestions.append({
                    "type": "overvalued_source",
                    "source_name": row[0],
                    "current_weight": float(row[1]),
                    "usage_count": row[2],
                    "suggestion": "该源权重高但使用少，可能被高估或未充分利用"
                })
            
            logger.info(f"✅ 生成了 {len(suggestions)} 条优化建议")
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ 生成优化建议失败: {e}")
            return []

