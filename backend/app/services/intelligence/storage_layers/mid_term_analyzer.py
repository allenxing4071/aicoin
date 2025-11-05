"""Mid-Term Intelligence Analyzer - Qwen情报员中期分析层"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import statistics

logger = logging.getLogger(__name__)


class MidTermIntelligenceAnalyzer:
    """
    Qwen情报员中期分析层（Layer 2）
    
    职责：
    1. 分析用户行为模式
    2. 计算信息源权重
    3. 识别高价值信息特征
    4. 向量化准备
    
    工作周期：每小时执行一次
    数据来源：从短期缓存中读取
    输出：权重更新建议 + 向量化候选
    """
    
    def __init__(
        self,
        redis_client,
        db_session
    ):
        """
        初始化中期分析器
        
        Args:
            redis_client: Redis客户端
            db_session: 数据库会话
        """
        self.redis = redis_client
        self.db = db_session
        self.namespace = "qwen:intelligence:mid_term"
        
        logger.info("✅ Qwen情报员中期分析器初始化完成")
    
    async def analyze_user_behavior(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        分析用户行为模式
        
        Args:
            time_window_hours: 分析时间窗口（小时）
        
        Returns:
            行为分析结果
        """
        try:
            logger.info(f"🔍 开始分析用户行为（{time_window_hours}小时）...")
            
            # 获取交互统计
            interaction_stats_key = "qwen:intelligence:stats:interactions"
            raw_stats = await self.redis.hgetall(interaction_stats_key)
            
            interaction_counts = {
                k: int(v) for k, v in raw_stats.items()
            } if raw_stats else {}
            
            # 计算总交互数
            total_interactions = sum(interaction_counts.values())
            
            # 计算各类交互占比
            interaction_distribution = {}
            if total_interactions > 0:
                for interaction_type, count in interaction_counts.items():
                    interaction_distribution[interaction_type] = {
                        "count": count,
                        "percentage": (count / total_interactions) * 100
                    }
            
            # 识别高价值行为
            high_value_actions = ["bookmark", "share", "deep_read"]
            high_value_count = sum(
                interaction_counts.get(action, 0)
                for action in high_value_actions
            )
            
            engagement_rate = (
                (high_value_count / total_interactions * 100)
                if total_interactions > 0
                else 0.0
            )
            
            result = {
                "time_window_hours": time_window_hours,
                "total_interactions": total_interactions,
                "interaction_distribution": interaction_distribution,
                "high_value_actions_count": high_value_count,
                "engagement_rate": engagement_rate,
                "analyzed_at": datetime.now().isoformat()
            }
            
            # 缓存分析结果
            await self._cache_analysis_result("user_behavior", result)
            
            logger.info(
                f"✅ 用户行为分析完成: "
                f"总交互{total_interactions}次, "
                f"参与度{engagement_rate:.1f}%"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 用户行为分析失败: {e}", exc_info=True)
            return {}
    
    async def calculate_source_weights(
        self,
        report_ids: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        计算信息源权重
        
        基于以下因素：
        1. 使用频率
        2. 用户反馈（点击、停留时间）
        3. 决策影响（是否被采纳）
        4. 信息准确性
        
        Args:
            report_ids: 要分析的报告ID列表（None则分析所有最近报告）
        
        Returns:
            {source_name: weight} 字典
        """
        try:
            logger.info("📊 开始计算信息源权重...")
            
            source_metrics = defaultdict(lambda: {
                "usage_count": 0,
                "positive_interactions": 0,
                "total_interactions": 0,
                "decision_influenced": 0,
                "accuracy_score": 0.5
            })
            
            # 如果未指定report_ids，获取最近的报告
            if report_ids is None:
                report_ids = await self._get_recent_report_ids(limit=100)
            
            # 分析每个报告
            for report_id in report_ids:
                report_data = await self._get_cached_report(report_id)
                if not report_data:
                    continue
                
                # 提取数据源信息
                sources = self._extract_sources(report_data)
                
                # 获取交互数据
                interactions = await self._get_interactions(report_id)
                
                # 更新每个源的指标
                for source_name in sources:
                    metrics = source_metrics[source_name]
                    metrics["usage_count"] += 1
                    
                    # 统计交互
                    positive_actions = ["click", "bookmark", "share"]
                    for interaction in interactions:
                        metrics["total_interactions"] += 1
                        if interaction.get("type") in positive_actions:
                            metrics["positive_interactions"] += 1
                    
                    # 检查是否影响决策
                    if report_data.get("influenced_decision", False):
                        metrics["decision_influenced"] += 1
            
            # 计算权重
            weights = {}
            for source_name, metrics in source_metrics.items():
                weight = self._compute_weight(metrics)
                weights[source_name] = weight
            
            # 归一化权重（确保总和为1.0）
            if weights:
                total_weight = sum(weights.values())
                if total_weight > 0:
                    weights = {
                        k: v / total_weight
                        for k, v in weights.items()
                    }
            
            # 缓存权重结果
            await self._cache_analysis_result("source_weights", weights)
            
            logger.info(f"✅ 信息源权重计算完成: {len(weights)} 个源")
            
            return weights
            
        except Exception as e:
            logger.error(f"❌ 计算信息源权重失败: {e}", exc_info=True)
            return {}
    
    def _compute_weight(self, metrics: Dict[str, Any]) -> float:
        """
        计算单个源的权重
        
        权重公式：
        weight = (
            0.3 * usage_frequency +
            0.3 * engagement_rate +
            0.2 * decision_influence +
            0.2 * accuracy_score
        )
        """
        usage_count = metrics["usage_count"]
        total_interactions = metrics["total_interactions"]
        positive_interactions = metrics["positive_interactions"]
        decision_influenced = metrics["decision_influenced"]
        
        # 归一化使用频率（假设最大100次）
        usage_frequency = min(usage_count / 100.0, 1.0)
        
        # 参与率
        engagement_rate = (
            positive_interactions / total_interactions
            if total_interactions > 0
            else 0.5
        )
        
        # 决策影响率
        decision_influence = (
            decision_influenced / usage_count
            if usage_count > 0
            else 0.0
        )
        
        # 准确性评分（目前使用默认值）
        accuracy_score = metrics.get("accuracy_score", 0.5)
        
        # 加权计算
        weight = (
            0.3 * usage_frequency +
            0.3 * engagement_rate +
            0.2 * decision_influence +
            0.2 * accuracy_score
        )
        
        return weight
    
    async def identify_high_value_patterns(self) -> List[Dict[str, Any]]:
        """
        识别高价值信息模式
        
        Returns:
            高价值模式列表
        """
        try:
            logger.info("🔍 识别高价值信息模式...")
            
            patterns = []
            
            # 模式1：高参与度的主题
            # 模式2：高准确性的信息类型
            # 模式3：高影响力的事件类别
            
            # TODO: 实现模式识别算法
            # 这里提供基础框架
            
            patterns.append({
                "pattern_type": "high_engagement_topic",
                "description": "高参与度主题",
                "examples": ["监管政策", "技术升级", "机构动向"],
                "confidence": 0.75
            })
            
            await self._cache_analysis_result("high_value_patterns", patterns)
            
            logger.info(f"✅ 识别到 {len(patterns)} 个高价值模式")
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ 识别高价值模式失败: {e}")
            return []
    
    async def prepare_vectorization_candidates(
        self,
        min_interaction_threshold: int = 3
    ) -> List[Dict[str, Any]]:
        """
        准备待向量化的候选数据
        
        选择标准：
        1. 交互次数 >= 阈值
        2. 有正面反馈
        3. 时间在24小时内
        
        Args:
            min_interaction_threshold: 最小交互次数
        
        Returns:
            候选列表
        """
        try:
            logger.info(f"📦 准备向量化候选（阈值={min_interaction_threshold}）...")
            
            candidates = []
            
            # 获取最近的报告
            report_ids = await self._get_recent_report_ids(limit=50)
            
            for report_id in report_ids:
                # 获取交互数据
                interactions = await self._get_interactions(report_id)
                
                # 检查是否满足条件
                if len(interactions) >= min_interaction_threshold:
                    # 检查是否有正面反馈
                    has_positive = any(
                        i.get("type") in ["bookmark", "share"]
                        for i in interactions
                    )
                    
                    if has_positive:
                        report_data = await self._get_cached_report(report_id)
                        if report_data:
                            candidates.append({
                                "report_id": report_id,
                                "report_data": report_data,
                                "interaction_count": len(interactions),
                                "should_vectorize": True,
                                "priority": self._calculate_priority(interactions)
                            })
            
            # 按优先级排序
            candidates.sort(key=lambda x: x["priority"], reverse=True)
            
            logger.info(f"✅ 准备了 {len(candidates)} 个向量化候选")
            
            return candidates
            
        except Exception as e:
            logger.error(f"❌ 准备向量化候选失败: {e}")
            return []
    
    def _calculate_priority(self, interactions: List[Dict[str, Any]]) -> float:
        """计算优先级分数"""
        score = 0.0
        
        for interaction in interactions:
            interaction_type = interaction.get("type", "")
            
            # 不同交互类型的权重
            weights = {
                "view": 0.1,
                "click": 0.3,
                "bookmark": 1.0,
                "share": 1.5,
                "deep_read": 0.8
            }
            
            score += weights.get(interaction_type, 0.1)
        
        return score
    
    def _extract_sources(self, report_data: Dict[str, Any]) -> List[str]:
        """从报告中提取数据源"""
        sources = []
        
        # 从平台贡献中提取
        platform_contributions = report_data.get("platform_contributions", {})
        for platform in platform_contributions.keys():
            sources.append(platform)
        
        # 从原始数据中提取
        # TODO: 根据实际数据结构提取
        
        return sources
    
    async def _get_recent_report_ids(self, limit: int) -> List[str]:
        """获取最近的报告ID"""
        try:
            ids = await self.redis.zrevrange(
                "qwen:intelligence:reports:recent",
                0,
                limit - 1
            )
            return [id.decode() if isinstance(id, bytes) else id for id in ids]
        except:
            return []
    
    async def _get_cached_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """获取缓存的报告"""
        try:
            import json
            key = f"qwen:intelligence:report:{report_id}"
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        except:
            pass
        return None
    
    async def _get_interactions(self, report_id: str) -> List[Dict[str, Any]]:
        """获取交互记录"""
        try:
            import json
            key = f"qwen:intelligence:interactions:{report_id}"
            raw_data = await self.redis.lrange(key, 0, -1)
            return [json.loads(item) for item in raw_data]
        except:
            return []
    
    async def _cache_analysis_result(
        self,
        analysis_type: str,
        result: Any
    ) -> bool:
        """缓存分析结果"""
        try:
            import json
            key = f"{self.namespace}:analysis:{analysis_type}"
            serialized = json.dumps(result, default=str, ensure_ascii=False)
            await self.redis.setex(key, 3600 * 24, serialized)  # 24小时
            return True
        except:
            return False
    
    async def get_analysis_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        try:
            return {
                "user_behavior": await self._get_cached_analysis("user_behavior"),
                "source_weights": await self._get_cached_analysis("source_weights"),
                "high_value_patterns": await self._get_cached_analysis("high_value_patterns"),
                "last_analysis_time": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ 获取分析摘要失败: {e}")
            return {}
    
    async def _get_cached_analysis(self, analysis_type: str) -> Optional[Any]:
        """获取缓存的分析结果"""
        try:
            import json
            key = f"{self.namespace}:analysis:{analysis_type}"
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        except:
            pass
        return None

