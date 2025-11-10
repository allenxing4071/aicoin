"""
AI成本管理服务
管理AI模型的定价、使用统计和预算控制
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_model_pricing import AIModelPricing, AIModelUsageLog, AIBudgetAlert

logger = logging.getLogger(__name__)


class AICostManager:
    """AI成本管理器"""
    
    # 模型定价配置（人民币/百万tokens）
    MODEL_PRICING = {
        # DeepSeek系列
        "deepseek-chat": {
            "provider": "deepseek",
            "display_name": "DeepSeek Chat",
            "type": "decision",
            "input_price": 1.0,   # ¥1.0/百万tokens
            "output_price": 2.0,  # ¥2.0/百万tokens
            "description": "DeepSeek标准对话模型，用于AI交易决策"
        },
        "deepseek-reasoner": {
            "provider": "deepseek",
            "display_name": "DeepSeek Reasoner",
            "type": "decision",
            "input_price": 4.0,
            "output_price": 16.0,
            "description": "DeepSeek推理模型，深度思考能力"
        },
        
        # Qwen系列
        "qwen-plus": {
            "provider": "qwen",
            "display_name": "Qwen-Plus",
            "type": "intelligence",
            "input_price": 4.0,   # ¥4.0/百万tokens
            "output_price": 12.0, # ¥12.0/百万tokens
            "description": "通义千问Plus，用于情报分析"
        },
        "qwen-turbo": {
            "provider": "qwen",
            "display_name": "Qwen-Turbo",
            "type": "intelligence",
            "input_price": 2.0,
            "output_price": 6.0,
            "description": "通义千问Turbo，快速响应"
        },
        "qwen-max": {
            "provider": "qwen",
            "display_name": "Qwen-Max",
            "type": "intelligence",
            "input_price": 40.0,
            "output_price": 120.0,
            "description": "通义千问Max，最强性能"
        },
        
        # OpenAI系列
        "gpt-4o": {
            "provider": "openai",
            "display_name": "GPT-4o",
            "type": "analysis",
            "input_price": 15.0,
            "output_price": 60.0,
            "description": "OpenAI GPT-4o，多模态能力"
        },
        "gpt-4o-mini": {
            "provider": "openai",
            "display_name": "GPT-4o Mini",
            "type": "analysis",
            "input_price": 1.05,
            "output_price": 4.2,
            "description": "OpenAI GPT-4o Mini，性价比高"
        },
        
        # Claude系列
        "claude-3.5-sonnet": {
            "provider": "anthropic",
            "display_name": "Claude 3.5 Sonnet",
            "type": "analysis",
            "input_price": 21.0,
            "output_price": 105.0,
            "description": "Anthropic Claude 3.5 Sonnet，强大推理"
        },
        
        # Groq (免费)
        "groq-llama": {
            "provider": "groq",
            "display_name": "Groq Llama",
            "type": "intelligence",
            "input_price": 0.0,
            "output_price": 0.0,
            "is_free": True,
            "description": "Groq免费模型，快速监控"
        },
    }
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def initialize_pricing(self):
        """初始化模型定价配置"""
        try:
            for model_name, config in self.MODEL_PRICING.items():
                # 检查是否已存在
                result = await self.db.execute(
                    select(AIModelPricing).where(AIModelPricing.model_name == model_name)
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    # 创建新记录
                    pricing = AIModelPricing(
                        model_name=model_name,
                        provider=config["provider"],
                        display_name=config["display_name"],
                        model_type=config["type"],
                        input_price_per_million=config["input_price"],
                        output_price_per_million=config["output_price"],
                        is_free=config.get("is_free", False),
                        description=config.get("description", ""),
                        enabled=True
                    )
                    self.db.add(pricing)
            
            await self.db.commit()
            logger.info(f"✅ 初始化了 {len(self.MODEL_PRICING)} 个AI模型定价配置")
            
        except Exception as e:
            logger.error(f"❌ 初始化模型定价失败: {e}")
            await self.db.rollback()
            raise
    
    async def record_usage(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        response_time: float = 0,
        success: bool = True,
        error_message: str = None,
        purpose: str = None,
        symbol: str = None,
        request_id: str = None
    ) -> float:
        """
        记录模型使用并返回成本
        
        Returns:
            float: 本次调用成本（元）
        """
        try:
            # 获取定价配置
            result = await self.db.execute(
                select(AIModelPricing).where(AIModelPricing.model_name == model_name)
            )
            pricing = result.scalar_one_or_none()
            
            if not pricing:
                logger.warning(f"⚠️  模型 {model_name} 未配置定价，使用默认值")
                cost = 0.0
            else:
                # 计算成本
                cost = pricing.calculate_cost(input_tokens, output_tokens)
                
                # 更新统计
                pricing.total_calls += 1
                pricing.total_input_tokens += input_tokens
                pricing.total_output_tokens += output_tokens
                pricing.total_cost += cost
                pricing.current_month_cost += cost
                pricing.last_used_at = datetime.now()
                
                # 检查预算告警
                if pricing.should_alert() and not pricing.is_budget_exceeded():
                    await self._create_alert(
                        model_name=model_name,
                        alert_type="threshold",
                        alert_level="warning",
                        current_cost=pricing.current_month_cost,
                        budget_limit=pricing.monthly_budget,
                        message=f"模型 {pricing.display_name} 已使用 {pricing.current_month_cost/pricing.monthly_budget*100:.1f}% 的月度预算"
                    )
                elif pricing.is_budget_exceeded():
                    await self._create_alert(
                        model_name=model_name,
                        alert_type="exceeded",
                        alert_level="critical",
                        current_cost=pricing.current_month_cost,
                        budget_limit=pricing.monthly_budget,
                        message=f"模型 {pricing.display_name} 已超出月度预算！"
                    )
            
            # 记录使用日志
            usage_log = AIModelUsageLog(
                model_name=model_name,
                request_id=request_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                response_time=response_time,
                success=success,
                error_message=error_message,
                purpose=purpose,
                symbol=symbol
            )
            self.db.add(usage_log)
            
            await self.db.commit()
            
            logger.info(f"💰 {model_name}: {input_tokens}in + {output_tokens}out = ¥{cost:.4f}")
            
            return cost
            
        except Exception as e:
            logger.error(f"❌ 记录使用失败: {e}")
            await self.db.rollback()
            return 0.0
    
    async def get_model_stats(self, model_name: str = None) -> List[Dict[str, Any]]:
        """获取模型统计信息"""
        try:
            query = select(AIModelPricing)
            if model_name:
                query = query.where(AIModelPricing.model_name == model_name)
            
            result = await self.db.execute(query.order_by(AIModelPricing.total_cost.desc()))
            pricings = result.scalars().all()
            
            stats = []
            for p in pricings:
                stats.append({
                    "model_name": p.model_name,
                    "display_name": p.display_name,
                    "provider": p.provider,
                    "type": p.model_type,
                    "is_free": p.is_free,
                    "enabled": p.enabled,
                    "total_calls": p.total_calls,
                    "total_cost": round(p.total_cost, 2),
                    "current_month_cost": round(p.current_month_cost, 2),
                    "monthly_budget": p.monthly_budget,
                    "remaining_budget": round(p.remaining_budget(), 2) if p.monthly_budget > 0 else None,
                    "usage_percentage": round(p.current_month_cost / p.monthly_budget * 100, 1) if p.monthly_budget > 0 else 0,
                    "input_price": p.input_price_per_million,
                    "output_price": p.output_price_per_million,
                    "last_used_at": p.last_used_at.isoformat() if p.last_used_at else None,
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 获取模型统计失败: {e}")
            return []
    
    async def get_total_cost_summary(self) -> Dict[str, Any]:
        """获取总成本摘要"""
        try:
            result = await self.db.execute(
                select(
                    func.sum(AIModelPricing.total_cost).label('total_cost'),
                    func.sum(AIModelPricing.current_month_cost).label('month_cost'),
                    func.sum(AIModelPricing.total_calls).label('total_calls'),
                    func.count(AIModelPricing.id).label('model_count')
                )
            )
            row = result.first()
            
            # 获取今日成本
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            result = await self.db.execute(
                select(func.sum(AIModelUsageLog.cost))
                .where(AIModelUsageLog.created_at >= today_start)
            )
            today_cost = result.scalar() or 0.0
            
            return {
                "total_cost": round(row.total_cost or 0, 2),
                "month_cost": round(row.month_cost or 0, 2),
                "today_cost": round(today_cost, 2),
                "total_calls": row.total_calls or 0,
                "model_count": row.model_count or 0,
            }
            
        except Exception as e:
            logger.error(f"❌ 获取成本摘要失败: {e}")
            return {}
    
    async def get_usage_history(
        self,
        model_name: str = None,
        days: int = 7,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取使用历史"""
        try:
            query = select(AIModelUsageLog)
            
            if model_name:
                query = query.where(AIModelUsageLog.model_name == model_name)
            
            # 最近N天
            start_date = datetime.now() - timedelta(days=days)
            query = query.where(AIModelUsageLog.created_at >= start_date)
            
            query = query.order_by(AIModelUsageLog.created_at.desc()).limit(limit)
            
            result = await self.db.execute(query)
            logs = result.scalars().all()
            
            return [
                {
                    "id": log.id,
                    "model_name": log.model_name,
                    "input_tokens": log.input_tokens,
                    "output_tokens": log.output_tokens,
                    "cost": round(log.cost, 4),
                    "response_time": log.response_time,
                    "success": log.success,
                    "purpose": log.purpose,
                    "symbol": log.symbol,
                    "created_at": log.created_at.isoformat(),
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"❌ 获取使用历史失败: {e}")
            return []
    
    async def update_monthly_budget(self, model_name: str, budget: float):
        """更新月度预算"""
        try:
            result = await self.db.execute(
                select(AIModelPricing).where(AIModelPricing.model_name == model_name)
            )
            pricing = result.scalar_one_or_none()
            
            if pricing:
                pricing.monthly_budget = budget
                await self.db.commit()
                logger.info(f"✅ 更新 {model_name} 月度预算为 ¥{budget}")
            else:
                logger.warning(f"⚠️  模型 {model_name} 不存在")
                
        except Exception as e:
            logger.error(f"❌ 更新预算失败: {e}")
            await self.db.rollback()
    
    async def reset_monthly_costs(self):
        """重置月度成本（每月1号执行）"""
        try:
            result = await self.db.execute(select(AIModelPricing))
            pricings = result.scalars().all()
            
            for pricing in pricings:
                pricing.current_month_cost = 0.0
            
            await self.db.commit()
            logger.info("✅ 已重置所有模型的月度成本")
            
        except Exception as e:
            logger.error(f"❌ 重置月度成本失败: {e}")
            await self.db.rollback()
    
    async def _create_alert(
        self,
        model_name: str,
        alert_type: str,
        alert_level: str,
        current_cost: float,
        budget_limit: float,
        message: str
    ):
        """创建预算告警"""
        try:
            # 检查是否已有未解决的相同告警
            result = await self.db.execute(
                select(AIBudgetAlert).where(
                    and_(
                        AIBudgetAlert.model_name == model_name,
                        AIBudgetAlert.alert_type == alert_type,
                        AIBudgetAlert.is_resolved == False
                    )
                )
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                alert = AIBudgetAlert(
                    model_name=model_name,
                    alert_type=alert_type,
                    alert_level=alert_level,
                    current_cost=current_cost,
                    budget_limit=budget_limit,
                    usage_percentage=current_cost / budget_limit * 100 if budget_limit > 0 else 0,
                    message=message
                )
                self.db.add(alert)
                logger.warning(f"⚠️  {message}")
                
        except Exception as e:
            logger.error(f"❌ 创建告警失败: {e}")
    
    async def get_cost_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """获取成本优化建议"""
        suggestions = []
        
        try:
            # 获取所有模型统计
            stats = await self.get_model_stats()
            
            for stat in stats:
                if stat["is_free"]:
                    continue
                
                # 建议1: 高成本模型
                if stat["current_month_cost"] > 1000:
                    suggestions.append({
                        "type": "high_cost",
                        "model": stat["display_name"],
                        "current_cost": stat["current_month_cost"],
                        "suggestion": f"考虑使用更便宜的替代模型，或减少调用频率",
                        "priority": "high"
                    })
                
                # 建议2: 接近预算
                if stat["monthly_budget"] > 0 and stat["usage_percentage"] > 80:
                    suggestions.append({
                        "type": "budget_warning",
                        "model": stat["display_name"],
                        "usage_percentage": stat["usage_percentage"],
                        "suggestion": f"已使用 {stat['usage_percentage']:.1f}% 预算，建议调整使用策略",
                        "priority": "medium"
                    })
            
            # 建议3: 总成本优化
            summary = await self.get_total_cost_summary()
            if summary["month_cost"] > 5000:
                suggestions.append({
                    "type": "overall_optimization",
                    "current_cost": summary["month_cost"],
                    "suggestion": "月度总成本较高，建议：\n1. 增加决策间隔（当前10分钟可改为15分钟）\n2. 使用更便宜的模型\n3. 实施智能触发策略",
                    "priority": "high"
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ 获取优化建议失败: {e}")
            return []


# 全局实例（需要在使用时传入db_session）
def get_cost_manager(db_session: AsyncSession) -> AICostManager:
    """获取成本管理器实例"""
    return AICostManager(db_session)

