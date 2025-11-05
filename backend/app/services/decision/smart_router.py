"""DeepSeek Smart Router - 智能混合路由器

根据实际效果动态调整模型使用策略
支持五种路由策略：adaptive/single_best/ab_testing/ensemble_voting/scenario_based
"""

from typing import Dict, Any, Optional, Literal
from datetime import datetime, timedelta, date
from enum import Enum
import logging
import asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.models.model_performance import ModelPerformanceMetric, RoutingDecision
from .model_clients import Trained70BClient, DefaultAPIClient

logger = logging.getLogger(__name__)


class RoutingStrategy(str, Enum):
    """路由策略枚举"""
    SINGLE_BEST = "single_best"          # 单模型：选最优
    AB_TESTING = "ab_testing"            # AB测试：轮流使用
    ENSEMBLE_VOTING = "ensemble_voting"  # 双模型投票
    SCENARIO_BASED = "scenario_based"    # 场景分配
    ADAPTIVE = "adaptive"                # 自适应


class DeepSeekSmartRouter:
    """
    DeepSeek智能混合路由器
    
    核心功能：
    1. 实时追踪两个模型的效果
    2. 根据实际表现动态调整策略
    3. 支持多种混合使用模式
    4. 自动优化决策质量
    """
    
    def __init__(
        self,
        trained_client: Optional[Trained70BClient] = None,
        default_client: Optional[DefaultAPIClient] = None,
        strategy: Optional[RoutingStrategy] = None
    ):
        self.trained_client = trained_client or Trained70BClient()
        self.default_client = default_client or DefaultAPIClient()
        
        self.current_strategy = strategy or RoutingStrategy(settings.DEEPSEEK_ROUTING_STRATEGY)
        self.auto_fallback = settings.DEEPSEEK_AUTO_FALLBACK
        
        # AB测试计数器
        self.ab_test_counter = 0
        
        logger.info(f"✅ DeepSeek智能路由器初始化: {self.current_strategy}")
    
    async def make_decision(
        self,
        market_data: Dict[str, Any],
        intelligence_report: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        智能路由决策
        
        Returns:
            {
                "decision": "BUY/SELL/HOLD",
                "confidence": 0.85,
                "reasoning": "...",
                "routing_info": {...}
            }
        """
        try:
            # 如果是自适应策略，先选择最优策略
            if self.current_strategy == RoutingStrategy.ADAPTIVE:
                actual_strategy = await self._select_best_strategy()
            else:
                actual_strategy = self.current_strategy
            
            logger.info(f"🎯 使用策略: {actual_strategy}")
            
            # 根据策略执行决策
            if actual_strategy == RoutingStrategy.SINGLE_BEST:
                result = await self._single_best_strategy(market_data, intelligence_report, context)
            elif actual_strategy == RoutingStrategy.AB_TESTING:
                result = await self._ab_testing_strategy(market_data, intelligence_report, context)
            elif actual_strategy == RoutingStrategy.ENSEMBLE_VOTING:
                result = await self._ensemble_voting_strategy(market_data, intelligence_report, context)
            elif actual_strategy == RoutingStrategy.SCENARIO_BASED:
                result = await self._scenario_based_strategy(market_data, intelligence_report, context)
            else:
                result = await self._single_best_strategy(market_data, intelligence_report, context)
            
            # 记录决策
            await self._record_decision(result)
            
            return result
            
        except Exception as e:
            logger.error(f"路由决策失败: {e}", exc_info=True)
            return {
                "decision": "HOLD",
                "confidence": 0.0,
                "reasoning": f"决策失败: {e}",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def _single_best_strategy(
        self,
        market_data: Dict[str, Any],
        intelligence_report: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """策略1：单模型决策（选最优）"""
        # 获取模型性能
        trained_score = await self._calculate_model_score("trained_70b")
        api_score = await self._calculate_model_score("default_api")
        
        # 检查训练模型是否可用
        trained_available = self.trained_client.is_available() and settings.DEEPSEEK_70B_AVAILABLE
        
        # 选择得分更高的模型
        if trained_available and trained_score >= api_score:
            model_name = "trained_70b"
            try:
                result = await self.trained_client.make_decision(market_data, intelligence_report, context)
                reason = f"70B模型综合得分更高({trained_score:.2f} vs {api_score:.2f})"
            except Exception as e:
                if self.auto_fallback:
                    logger.warning(f"70B模型失败，降级到默认API: {e}")
                    result = await self.default_client.make_decision(market_data, intelligence_report, context)
                    result["fallback_triggered"] = True
                    model_name = "default_api"
                    reason = "70B失败，自动降级"
                else:
                    raise
        else:
            model_name = "default_api"
            result = await self.default_client.make_decision(market_data, intelligence_report, context)
            if not trained_available:
                reason = "70B模型不可用，使用默认API"
            else:
                reason = f"默认API综合得分更高({api_score:.2f} vs {trained_score:.2f})"
        
        result["routing_info"] = {
            "strategy_used": "single_best",
            "models_called": [model_name],
            "why_this_strategy": reason,
            "trained_score": trained_score,
            "api_score": api_score
        }
        
        return result
    
    async def _ab_testing_strategy(
        self,
        market_data: Dict[str, Any],
        intelligence_report: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """策略2：AB测试（轮流使用）"""
        self.ab_test_counter += 1
        
        # 检查训练模型是否可用
        trained_available = self.trained_client.is_available() and settings.DEEPSEEK_70B_AVAILABLE
        
        if trained_available and (self.ab_test_counter % 2 == 0):
            model_name = "trained_70b"
            try:
                result = await self.trained_client.make_decision(market_data, intelligence_report, context)
            except Exception as e:
                if self.auto_fallback:
                    logger.warning(f"70B失败，使用默认API: {e}")
                    result = await self.default_client.make_decision(market_data, intelligence_report, context)
                    result["fallback_triggered"] = True
                    model_name = "default_api"
                else:
                    raise
        else:
            model_name = "default_api"
            result = await self.default_client.make_decision(market_data, intelligence_report, context)
        
        result["routing_info"] = {
            "strategy_used": "ab_testing",
            "models_called": [model_name],
            "why_this_strategy": "AB测试中，轮流使用以积累对比数据",
            "ab_test_round": self.ab_test_counter
        }
        
        return result
    
    async def _ensemble_voting_strategy(
        self,
        market_data: Dict[str, Any],
        intelligence_report: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """策略3：双模型投票（都用）"""
        logger.info("🗳️  启动双模型投票...")
        
        results = []
        models_used = []
        
        # 尝试调用训练模型
        if self.trained_client.is_available() and settings.DEEPSEEK_70B_AVAILABLE:
            try:
                trained_result = await self.trained_client.make_decision(market_data, intelligence_report, context)
                results.append(("trained_70b", trained_result))
                models_used.append("trained_70b")
            except Exception as e:
                logger.warning(f"训练模型调用失败: {e}")
        
        # 调用默认API
        try:
            api_result = await self.default_client.make_decision(market_data, intelligence_report, context)
            results.append(("default_api", api_result))
            models_used.append("default_api")
        except Exception as e:
            logger.error(f"默认API也失败: {e}")
            if not results:
                raise
        
        # 投票
        if len(results) == 2:
            # 两个模型都成功
            trained_decision = results[0][1]["decision"]
            api_decision = results[1][1]["decision"]
            
            if trained_decision == api_decision:
                final_decision = trained_decision
                final_confidence = (results[0][1]["confidence"] + results[1][1]["confidence"]) / 2
                consensus = "一致"
            else:
                # 选择置信度更高的
                if results[0][1]["confidence"] >= results[1][1]["confidence"]:
                    final_decision = trained_decision
                    final_confidence = results[0][1]["confidence"]
                    consensus = "分歧，采纳70B"
                else:
                    final_decision = api_decision
                    final_confidence = results[1][1]["confidence"]
                    consensus = "分歧，采纳API"
        else:
            # 只有一个成功
            final_decision = results[0][1]["decision"]
            final_confidence = results[0][1]["confidence"]
            consensus = "单模型"
        
        return {
            "decision": final_decision,
            "confidence": final_confidence,
            "reasoning": f"双模型投票结果: {consensus}",
            "routing_info": {
                "strategy_used": "ensemble_voting",
                "models_called": models_used,
                "why_this_strategy": "重要决策，使用双模型投票",
                "consensus": consensus
            },
            "timestamp": datetime.now()
        }
    
    async def _scenario_based_strategy(
        self,
        market_data: Dict[str, Any],
        intelligence_report: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """策略4：场景分配（根据风险）"""
        risk_level = self._assess_risk(market_data, intelligence_report)
        
        trained_available = self.trained_client.is_available() and settings.DEEPSEEK_70B_AVAILABLE
        
        if risk_level == "high" and trained_available:
            # 高风险用准确率更高的模型
            model_name = "trained_70b"
            try:
                result = await self.trained_client.make_decision(market_data, intelligence_report, context)
                reason = "高风险场景，使用70B模型"
            except Exception as e:
                if self.auto_fallback:
                    result = await self.default_client.make_decision(market_data, intelligence_report, context)
                    model_name = "default_api"
                    reason = "70B失败，降级处理"
                else:
                    raise
        else:
            # 低风险用默认API（更快更便宜）
            model_name = "default_api"
            result = await self.default_client.make_decision(market_data, intelligence_report, context)
            reason = f"{risk_level}风险场景，使用默认API"
        
        result["routing_info"] = {
            "strategy_used": "scenario_based",
            "models_called": [model_name],
            "why_this_strategy": reason,
            "risk_level": risk_level
        }
        
        return result
    
    def _assess_risk(self, market_data: Dict[str, Any], intelligence_report: Dict[str, Any]) -> Literal["high", "medium", "low"]:
        """评估风险等级"""
        risk_score = 0
        
        # 检查波动性
        if market_data.get("volatility", 0) > 0.05:
            risk_score += 2
        
        # 检查情报风险因素
        risk_factors = intelligence_report.get("risk_factors", [])
        risk_score += len(risk_factors)
        
        if risk_score >= 4:
            return "high"
        elif risk_score <= 1:
            return "low"
        else:
            return "medium"
    
    async def _select_best_strategy(self) -> RoutingStrategy:
        """自适应：选择最优策略"""
        async with get_db_session() as db:
            # 获取最近的性能数据
            trained_perf = await self._get_recent_performance(db, "trained_70b")
            api_perf = await self._get_recent_performance(db, "default_api")
            
            # 情况1：样本不足
            min_samples = settings.MIN_SAMPLES_FOR_EVALUATION
            if (not trained_perf or trained_perf.total_decisions < min_samples or
                not api_perf or api_perf.total_decisions < min_samples):
                logger.info("📊 样本不足，选择AB测试策略")
                return RoutingStrategy.AB_TESTING
            
            # 情况2：效果接近
            accuracy_diff = abs(trained_perf.accuracy - api_perf.accuracy)
            if accuracy_diff < 0.05:
                logger.info("🗳️  效果接近，选择双模型投票")
                return RoutingStrategy.ENSEMBLE_VOTING
            
            # 情况3：明显优劣
            if accuracy_diff > 0.15:
                logger.info("⭐ 性能差异明显，选择单模型")
                return RoutingStrategy.SINGLE_BEST
            
            # 默认：场景分配
            logger.info("🎯 选择场景分配策略")
            return RoutingStrategy.SCENARIO_BASED
    
    async def _get_recent_performance(self, db: AsyncSession, model_name: str) -> Optional[ModelPerformanceMetric]:
        """获取最近的性能指标"""
        window_days = settings.PERFORMANCE_WINDOW_DAYS
        cutoff_date = (datetime.now() - timedelta(days=window_days)).date()
        
        result = await db.execute(
            select(ModelPerformanceMetric)
            .where(ModelPerformanceMetric.model_name == model_name)
            .where(ModelPerformanceMetric.metric_date >= cutoff_date)
            .order_by(ModelPerformanceMetric.metric_date.desc())
            .limit(1)
        )
        
        return result.scalar_one_or_none()
    
    async def _calculate_model_score(self, model_name: str) -> float:
        """计算模型综合得分"""
        async with get_db_session() as db:
            perf = await self._get_recent_performance(db, model_name)
            
            if not perf or perf.total_decisions == 0:
                return 0.5  # 默认中等分数
            
            # 综合得分：准确率40% + 盈利率30% + 响应15% + 成本15%
            accuracy_score = perf.accuracy if perf.accuracy else 0.0
            profit_score = max(0, min(1, perf.profit_rate)) if perf.profit_rate else 0.0
            
            # 响应时间得分（1秒=1分，5秒=0分）
            speed_score = max(0, min(1, (5 - (perf.avg_response_time or 2)) / 4))
            
            # 成本得分（$0.001=1分，$0.1=0分）
            cost_score = max(0, min(1, (0.1 - (perf.avg_cost or 0.01)) / 0.099))
            
            total_score = (
                accuracy_score * 0.40 +
                profit_score * 0.30 +
                speed_score * 0.15 +
                cost_score * 0.15
            )
            
            return total_score
    
    async def _record_decision(self, result: Dict[str, Any]):
        """记录决策"""
        try:
            async with get_db_session() as db:
                routing_info = result.get("routing_info", {})
                
                decision_record = RoutingDecision(
                    decision_id=f"dec_{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(result)}",
                    routing_strategy=routing_info.get("strategy_used", "unknown"),
                    model_used=result.get("model_used", "unknown"),
                    models_called=routing_info.get("models_called", []),
                    decision=result.get("decision"),
                    confidence=result.get("confidence"),
                    reasoning=result.get("reasoning"),
                    why_this_strategy=routing_info.get("why_this_strategy"),
                    fallback_triggered=result.get("fallback_triggered", False),
                    routing_metadata=routing_info,
                    response_time=result.get("response_time"),
                    cost=result.get("cost")
                )
                
                db.add(decision_record)
                await db.commit()
                
        except Exception as e:
            logger.error(f"记录决策失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取路由统计"""
        return {
            "current_strategy": self.current_strategy,
            "ab_test_counter": self.ab_test_counter,
            "trained_available": self.trained_client.is_available(),
            "default_available": self.default_client.is_available()
        }

