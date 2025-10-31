"""DecisionEngineV2 - 集成权限、约束、记忆的AI决策引擎"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal
import logging

import openai

from app.core.config import settings
from app.core.redis_client import RedisClient
from app.services.constraints.permission_manager import PermissionManager, PerformanceData
from app.services.constraints.constraint_validator import ConstraintValidator
from app.services.memory.short_term_memory import ShortTermMemory
from app.services.memory.long_term_memory import LongTermMemory
from app.services.memory.knowledge_base import KnowledgeBase
from app.services.decision.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class DecisionEngineV2:
    """
    DecisionEngineV2 - v2.0决策引擎
    
    核心改进：
    1. 集成L0-L5动态权限系统
    2. 集成硬约束+软约束验证
    3. 集成三层记忆系统
    4. 平衡的Prompt设计
    5. 完整的决策流程
    """
    
    def __init__(
        self,
        redis_client: RedisClient,
        db_session: Any,
        api_key: Optional[str] = None,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com/v1"
    ):
        self.redis_client = redis_client
        self.db_session = db_session
        
        # OpenAI客户端（DeepSeek兼容）
        self.client = openai.OpenAI(
            api_key=api_key or settings.DEEPSEEK_API_KEY,
            base_url=base_url
        )
        self.model = model
        
        # 初始化子系统
        self.permission_mgr = PermissionManager(db_session)
        self.constraint_validator = ConstraintValidator(redis_client)
        self.short_memory = ShortTermMemory(redis_client)
        self.long_memory = LongTermMemory(
            qdrant_host=settings.QDRANT_HOST,
            qdrant_port=settings.QDRANT_PORT,
            api_key=settings.OPENAI_API_KEY
        )
        self.knowledge_base = KnowledgeBase(db_session)
        
        # 当前权限等级
        self.current_permission_level = settings.INITIAL_PERMISSION_LEVEL
        
        logger.info(f"✅ DecisionEngineV2 initialized at level {self.current_permission_level}")
    
    async def make_decision(
        self,
        market_data: Dict[str, Any],
        account_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        做出交易决策
        
        完整流程：
        1. 获取当前权限配置
        2. 加载记忆数据
        3. 构建Prompt
        4. 调用LLM
        5. 解析响应
        6. 验证约束
        7. 记录决策
        
        Args:
            market_data: 市场数据
            account_state: 账户状态
        
        Returns:
            决策结果
        """
        
        decision_id = f"dec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # === 第1步：权限检查 ===
            logger.info(f"🔑 当前权限等级: {self.current_permission_level}")
            
            permission = self.permission_mgr.get_permission(self.current_permission_level)
            permission_config = self.permission_mgr.get_permission_summary(self.current_permission_level)
            
            # 检查是否在保护模式
            if self.current_permission_level == "L0":
                logger.warning("🚨 处于保护模式（L0），禁止开新仓")
                return {
                    "decision_id": decision_id,
                    "action": "hold",
                    "symbol": "",
                    "size_usd": 0,
                    "confidence": 0.0,
                    "reasoning": "System in protection mode (L0), awaiting manual review",
                    "status": "REJECTED",
                    "notes": "L0保护模式"
                }
            
            # === 第2步：加载记忆 ===
            logger.info("🧠 加载记忆数据...")
            
            # 2.1 短期记忆
            recent_decisions = await self.short_memory.get_recent_decisions(count=10, hours=24)
            daily_trade_count = await self.short_memory.get_today_trade_count()
            
            # 2.2 长期记忆（相似场景）
            current_decision_context = {
                "symbol": "BTC",  # 临时，后续可改进
                "action": "analyze",
                "confidence": 0.5
            }
            similar_situations = await self.long_memory.find_similar_situations(
                market_data,
                current_decision_context,
                limit=5
            )
            
            # 2.3 知识库（经验教训）
            lessons_learned = await self.knowledge_base.get_relevant_lessons(
                symbol="BTC",
                action="all",
                limit=5
            )
            
            # === 第3步：构建Prompt ===
            logger.info("📝 构建决策Prompt...")
            
            constraints = self.constraint_validator.get_constraint_summary()
            
            prompt = PromptTemplates.build_decision_prompt_v2(
                account_state=account_state,
                market_data=market_data,
                permission_level=self.current_permission_level,
                permission_config=permission_config,
                constraints=constraints,
                recent_decisions=recent_decisions,
                similar_situations=similar_situations,
                lessons_learned=lessons_learned
            )
            
            # === 第4步：调用LLM ===
            logger.info("🤖 调用AI模型进行决策...")
            
            response = await self._call_llm(prompt)
            
            # === 第5步：解析响应 ===
            logger.info("📊 解析AI响应...")
            
            ai_decision = self._parse_response(response)
            ai_decision["decision_id"] = decision_id
            
            # === 第6步：软约束验证 ===
            logger.info("🔍 应用软约束...")
            
            ai_decision = await self.constraint_validator.validate_soft_constraints(
                ai_decision,
                self.current_permission_level,
                daily_trade_count
            )
            
            # 如果已被软约束拒绝，直接返回
            if ai_decision.get("status") == "REJECTED":
                logger.warning(f"❌ 软约束拒绝: {ai_decision.get('notes')}")
                await self._record_decision(ai_decision, market_data, "REJECTED")
                return ai_decision
            
            # === 第7步：硬约束验证 ===
            if ai_decision.get("action") in ["open_long", "open_short"]:
                logger.info("🛡️  验证硬约束...")
                
                # 构建交易请求
                proposed_trade = {
                    "symbol": ai_decision.get("symbol"),
                    "action": ai_decision.get("action"),
                    "size_usd": ai_decision.get("size_usd"),
                    "leverage": permission.max_leverage,  # 使用当前权限的最大杠杆
                    "position_value": ai_decision.get("size_usd", 0) * permission.max_leverage,
                    "required_margin": ai_decision.get("size_usd", 0),
                }
                
                is_valid, reason = await self.constraint_validator.validate_hard_constraints(
                    account_state,
                    proposed_trade
                )
                
                if not is_valid:
                    logger.error(f"🚫 硬约束拒绝: {reason}")
                    ai_decision["status"] = "REJECTED"
                    ai_decision["notes"] = f"硬约束拒绝: {reason}"
                    await self._record_decision(ai_decision, market_data, "REJECTED")
                    return ai_decision
            
            # === 第8步：权限验证 ===
            if ai_decision.get("action") in ["open_long", "open_short"]:
                logger.info("🔐 验证权限限制...")
                
                is_valid, reason = self.permission_mgr.validate_trade_request(
                    level=self.current_permission_level,
                    position_size=Decimal(str(ai_decision.get("size_usd", 0))),
                    account_balance=Decimal(str(account_state.get("balance", 0))),
                    leverage=permission.max_leverage,
                    confidence=ai_decision.get("confidence", 0.0),
                    daily_trade_count=daily_trade_count
                )
                
                if not is_valid:
                    logger.error(f"🔒 权限限制拒绝: {reason}")
                    ai_decision["status"] = "REJECTED"
                    ai_decision["notes"] = f"权限限制: {reason}"
                    await self._record_decision(ai_decision, market_data, "REJECTED")
                    return ai_decision
            
            # === 第9步：检查强制平仓 ===
            should_liquidate, liquidate_reason = await self.constraint_validator.check_forced_liquidation(
                account_state
            )
            
            if should_liquidate:
                logger.critical(f"🚨 触发强制平仓: {liquidate_reason}")
                ai_decision = {
                    "decision_id": decision_id,
                    "action": "close_all",
                    "symbol": "ALL",
                    "size_usd": 0,
                    "confidence": 1.0,
                    "reasoning": f"强制平仓: {liquidate_reason}",
                    "status": "APPROVED",
                    "notes": "触发风控保护"
                }
                
                # 降级到L0
                self.current_permission_level = "L0"
                logger.critical("⬇️  权限降级到L0（保护模式）")
            
            # === 第10步：记录决策 ===
            if ai_decision.get("status") != "REJECTED":
                ai_decision["status"] = "APPROVED"
            
            await self._record_decision(ai_decision, market_data, ai_decision.get("status"))
            
            # 如果是交易动作，递增计数
            if ai_decision.get("action") in ["open_long", "open_short"]:
                await self.short_memory.increment_today_trade_count()
            
            logger.info(f"✅ 决策完成: {ai_decision.get('action')} {ai_decision.get('symbol')}")
            
            return ai_decision
        
        except Exception as e:
            logger.error(f"❌ 决策失败: {e}", exc_info=True)
            return {
                "decision_id": decision_id,
                "action": "hold",
                "symbol": "",
                "size_usd": 0,
                "confidence": 0.0,
                "reasoning": f"系统错误: {str(e)}",
                "status": "ERROR",
                "notes": str(e)
            }
    
    async def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional cryptocurrency trading AI assistant with strict risk management."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                timeout=30
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            # 尝试提取JSON
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                json_str = response
            
            decision = json.loads(json_str)
            
            # 验证必要字段
            required_fields = ["action", "symbol", "confidence", "reasoning"]
            for field in required_fields:
                if field not in decision:
                    decision[field] = self._get_default_value(field)
            
            return decision
        
        except Exception as e:
            logger.error(f"解析响应失败: {e}")
            return {
                "action": "hold",
                "symbol": "",
                "size_usd": 0,
                "confidence": 0.0,
                "reasoning": f"解析失败: {str(e)}",
                "status": "ERROR"
            }
    
    def _get_default_value(self, field: str) -> Any:
        """获取字段默认值"""
        defaults = {
            "action": "hold",
            "symbol": "",
            "size_usd": 0,
            "confidence": 0.0,
            "reasoning": "No reasoning provided",
            "stop_loss_pct": 0.03,
            "take_profit_pct": 0.05
        }
        return defaults.get(field, "")
    
    async def _record_decision(
        self,
        decision: Dict[str, Any],
        market_data: Dict[str, Any],
        status: str
    ):
        """记录决策到记忆系统"""
        try:
            decision_id = decision.get("decision_id")
            timestamp = datetime.now()
            
            # 1. 记录到短期记忆
            await self.short_memory.record_decision(
                decision_id=decision_id,
                timestamp=timestamp,
                symbol=decision.get("symbol", ""),
                action=decision.get("action", "hold"),
                size_usd=decision.get("size_usd", 0),
                confidence=decision.get("confidence", 0.0),
                reasoning=decision.get("reasoning", ""),
                market_data=market_data
            )
            
            await self.short_memory.update_decision_result(
                decision_id=decision_id,
                status=status,
                result=decision.get("notes", "")
            )
            
            # 2. 如果状态是APPROVED，记录到长期记忆
            if status == "APPROVED":
                await self.long_memory.store_decision(
                    decision_id=decision_id,
                    timestamp=timestamp,
                    market_data=market_data,
                    decision=decision
                )
            
            logger.debug(f"📝 决策已记录: {decision_id}")
        
        except Exception as e:
            logger.error(f"记录决策失败: {e}")
    
    async def evaluate_and_adjust_permission(
        self,
        performance_data: PerformanceData
    ) -> tuple[str, str]:
        """
        评估表现并调整权限等级
        
        Returns:
            (new_level, reason)
        """
        try:
            new_level, reason = await self.permission_mgr.evaluate_permission_level(
                self.current_permission_level,
                performance_data
            )
            
            if new_level != self.current_permission_level:
                old_level = self.current_permission_level
                self.current_permission_level = new_level
                
                logger.warning(f"🔄 权限变更: {old_level} → {new_level}, 原因: {reason}")
                
                # TODO: 记录到数据库 permission_history
            
            return new_level, reason
        
        except Exception as e:
            logger.error(f"权限评估失败: {e}")
            return self.current_permission_level, "评估失败"

