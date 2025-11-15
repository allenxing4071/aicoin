"""DecisionEngineV2 - 集成权限、约束、记忆的AI决策引擎"""

import asyncio
import json
import os
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
from app.services.decision.prompt_manager_db import PromptManagerDB
from app.services.intelligence.storage import intelligence_storage
from app.services.decision.debate_system import DebateCoordinator
from app.services.decision.debate_memory import DebateMemoryManager
from app.services.decision.debate_config import DebateConfigManager
from app.services.decision.debate_rate_limiter import DebateRateLimiter
from qdrant_client import QdrantClient

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
            embedding_provider="auto"  # 自动选择: Qwen > DeepSeek > OpenAI
        )
        self.knowledge_base = KnowledgeBase(db_session)
        
        # 初始化Prompt管理器（新版：数据库版本）
        self.prompt_manager = PromptManagerDB(db_session)
        self._prompt_manager_initialized = False  # 标记是否已加载
        logger.info("✅ Prompt管理器（数据库版）初始化成功")
        
        # 初始化辩论系统（新增）
        try:
            # 创建 Qdrant 客户端（复用现有配置）
            qdrant_client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT
            )
            
            # 初始化辩论组件（传入prompt_manager）
            self.debate_coordinator = DebateCoordinator(
                llm_client=self.client,
                max_debate_rounds=1,  # 默认1轮，后续从配置读取
                timeout_seconds=60,
                prompt_manager=self.prompt_manager  # 新增：传入PromptManager
            )
            
            self.debate_memory = DebateMemoryManager(
                qdrant_client=qdrant_client,
                embedding_client=self.client,
                embedding_model="text-embedding-3-small"
            )
            
            self.debate_config = DebateConfigManager(db_session)
            self.debate_limiter = DebateRateLimiter(redis_client, daily_limit=100, hourly_limit=10)
            
            logger.info("✅ 辩论系统初始化成功")
        except Exception as e:
            logger.error(f"⚠️  辩论系统初始化失败: {e}，将禁用辩论功能")
            self.debate_coordinator = None
            self.debate_memory = None
            self.debate_config = None
            self.debate_limiter = None
        
        # 当前权限等级 - 使用配置文件默认值（避免在__init__中进行异步数据库查询）
        self.current_permission_level = settings.INITIAL_PERMISSION_LEVEL
        self._permission_loaded_from_db = False
        
        logger.info(f"✅ DecisionEngineV2 initialized at level {self.current_permission_level}")
    
    async def _get_latest_intelligence(self):
        """
        从L1缓存获取最新情报（优化性能）
        
        优先从L1缓存获取（<10ms），如果缓存未命中则从旧存储获取
        
        Returns:
            Optional[IntelligenceReport]: 最新情报报告
        """
        try:
            # 优先从L1缓存获取（<10ms）
            from app.services.intelligence.storage_layers import ShortTermIntelligenceCache
            from app.services.intelligence.models import IntelligenceReport, SentimentType
            from datetime import datetime
            
            l1_cache = ShortTermIntelligenceCache(self.redis_client)
            
            cached_report = await l1_cache.get_latest_report()
            if cached_report:
                logger.debug("✅ 从L1缓存获取情报（快速路径）")
                # 转换为IntelligenceReport对象
                return self._dict_to_intelligence_report(cached_report)
            
            # Fallback: 从旧存储获取
            logger.debug("⚠️  L1缓存未命中，从旧存储获取")
            return await intelligence_storage.get_latest_report()
            
        except Exception as e:
            logger.warning(f"⚠️  获取情报失败: {e}，使用fallback")
            return await intelligence_storage.get_latest_report()
    
    def _dict_to_intelligence_report(self, data: Dict[str, Any]):
        """
        将字典转换为IntelligenceReport对象
        
        Args:
            data: 情报数据字典
            
        Returns:
            IntelligenceReport: 情报报告对象
        """
        from app.services.intelligence.models import IntelligenceReport, SentimentType, NewsItem, WhaleActivity, OnChainMetrics
        from datetime import datetime
        from app.utils.timezone import get_beijing_time
        
        # 解析时间戳
        timestamp_str = data.get("timestamp")
        if isinstance(timestamp_str, str):
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except:
                timestamp = get_beijing_time()
        else:
            timestamp = get_beijing_time()
        
        # 解析市场情绪
        sentiment_str = data.get("market_sentiment", "NEUTRAL")
        try:
            sentiment = SentimentType[sentiment_str]
        except KeyError:
            sentiment = SentimentType.NEUTRAL
        
        # 创建报告（简化版，只包含关键字段）
        report = IntelligenceReport(
            timestamp=timestamp,
            market_sentiment=sentiment,
            sentiment_score=data.get("sentiment_score", 0.0),
            key_news=[],  # 简化处理
            whale_signals=[],  # 简化处理
            on_chain_metrics=OnChainMetrics(
                exchange_net_flow=0,
                active_addresses=0,
                gas_price=0,
                transaction_volume=0,
                timestamp=timestamp
            ),
            risk_factors=data.get("risk_factors", []),
            opportunities=data.get("opportunities", []),
            qwen_analysis=data.get("qwen_analysis", ""),
            confidence=data.get("confidence", 0.7)
        )
        
        # 添加扩展属性（多平台验证信息）
        if 'platform_contributions' in data:
            report.platform_contributions = data['platform_contributions']
        if 'platform_consensus' in data:
            report.platform_consensus = data['platform_consensus']
        if 'verification_metadata' in data:
            report.verification_metadata = data['verification_metadata']
        if 'summary' in data:
            report.summary = data['summary']
        
        return report
    
    async def _ensure_prompt_manager_loaded(self):
        """确保Prompt管理器已从数据库加载"""
        if not self._prompt_manager_initialized:
            try:
                await self.prompt_manager.load_from_db()
                self._prompt_manager_initialized = True
                logger.info("✅ Prompt模板已从数据库加载")
            except Exception as e:
                logger.error(f"❌ Prompt模板加载失败: {e}")
    
    async def _load_default_permission_level(self) -> str:
        """从数据库加载默认权限等级（异步）"""
        try:
            from app.models.permission_config import PermissionLevelConfig
            from sqlalchemy import select
            
            # 查询is_default=True的权限等级
            stmt = select(PermissionLevelConfig).where(
                PermissionLevelConfig.is_default == True,
                PermissionLevelConfig.is_active == True
            ).limit(1)
            
            result = await self.db_session.execute(stmt)
            default_config = result.scalars().first()
            
            if default_config:
                logger.info(f"📌 从数据库加载默认权限等级: {default_config.level} ({default_config.name})")
                return default_config.level
            else:
                logger.warning(f"⚠️ 数据库中没有找到默认权限等级，使用配置文件默认值: {settings.INITIAL_PERMISSION_LEVEL}")
                return settings.INITIAL_PERMISSION_LEVEL
                
        except Exception as e:
            logger.error(f"❌ 从数据库加载默认权限等级失败: {e}，使用配置文件默认值: {settings.INITIAL_PERMISSION_LEVEL}")
            return settings.INITIAL_PERMISSION_LEVEL
    
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
            # 首次调用时从数据库加载默认权限
            if not self._permission_loaded_from_db:
                self.current_permission_level = await self._load_default_permission_level()
                self._permission_loaded_from_db = True
            
            # === 第1步：权限检查 ===
            logger.info(f"🔑 当前权限等级: {self.current_permission_level}")
            
            permission = await self.permission_mgr.get_permission(self.current_permission_level)
            permission_config = await self.permission_mgr.get_permission_summary(self.current_permission_level)
            
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
            
            # 2.4 Qwen情报报告（优先从L1缓存获取）
            intelligence_report = await self._get_latest_intelligence()
            if intelligence_report:
                logger.info(f"🕵️‍♀️ 获取Qwen情报: 情绪={intelligence_report.market_sentiment.value}, 置信度={intelligence_report.confidence:.2f}")
                # 显示多平台验证信息（如果有）
                if hasattr(intelligence_report, 'platform_contributions') and intelligence_report.platform_contributions:
                    logger.info(f"   📊 多平台验证: {len(intelligence_report.platform_contributions)}个平台")
                    if hasattr(intelligence_report, 'platform_consensus'):
                        logger.info(f"   🎯 平台共识度: {intelligence_report.platform_consensus:.1%}")
            else:
                logger.warning("⚠️  未找到Qwen情报报告")
            
            # === 第2.5步：多空辩论（强制启用 - 调试模式）===
            debate_result = None
            if self.debate_coordinator and self.debate_config and self.debate_limiter:
                try:
                    # 🔥 临时：强制启用辩论以提升决策质量
                    should_debate = True  # await self._should_enable_debate(account_state)
                    logger.info("🔥 辩论系统已强制启用（调试模式）")
                    
                    if should_debate:
                        # 检查限流
                        can_debate, limit_reason = await self.debate_limiter.check_rate_limit()
                        
                        if can_debate:
                            logger.info("⚔️  启动多空辩论机制...")
                            
                            # 构建市场情况描述（用于记忆检索）
                            situation_desc = self._build_situation_description(market_data, intelligence_report)
                            
                            # 获取历史记忆
                            past_memories = []
                            if await self.debate_config.should_use_memory():
                                past_memories = self.debate_memory.get_manager_memories(situation_desc, n_matches=2)
                            
                            # 准备增强的情报报告字典（包含多平台验证信息）
                            intelligence_dict = {}
                            if intelligence_report:
                                intelligence_dict = {
                                    "market_sentiment": intelligence_report.market_sentiment.value,
                                    "confidence": intelligence_report.confidence,
                                    "summary": intelligence_report.summary[:500] if hasattr(intelligence_report, 'summary') and intelligence_report.summary else "",
                                    # 新增：多平台验证信息
                                    "platform_contributions": getattr(intelligence_report, 'platform_contributions', {}),
                                    "platform_consensus": getattr(intelligence_report, 'platform_consensus', 0.0),
                                    "verification_metadata": getattr(intelligence_report, 'verification_metadata', {})
                                }
                            
                            # 执行辩论
                            debate_result = await self.debate_coordinator.conduct_debate(
                                market_data=market_data,
                                intelligence_report=intelligence_dict,
                                past_memories=past_memories
                            )
                            
                            # 更新限流计数
                            await self.debate_limiter.increment_count()
                            
                            logger.info(f"✅ 辩论完成 - 推荐: {debate_result['final_decision'].get('recommendation')}, "
                                      f"共识度: {debate_result['consensus_level']:.2f}, "
                                      f"耗时: {debate_result['duration_seconds']}秒")
                        else:
                            logger.warning(f"⏸️  辩论被限流跳过: {limit_reason}")
                    else:
                        logger.debug("⏸️  不满足辩论触发条件，跳过")
                        
                except Exception as e:
                    logger.error(f"❌ 辩论执行失败: {e}", exc_info=True)
                    debate_result = None
            
            # === 第3步：构建Prompt ===
            logger.info("📝 构建决策Prompt...")
            
            constraints = self.constraint_validator.get_constraint_summary()
            
            # 使用新版PromptManagerDB构建Prompt
            await self._ensure_prompt_manager_loaded()
            
            # 获取对应权限等级的Prompt模板
            template = self.prompt_manager.get_template(
                category="decision",
                name="default",
                permission_level=self.current_permission_level
            )
            
            if template:
                # 使用模板渲染（模板中已包含基础结构）
                prompt = template.content
                
                # 追加动态数据
                prompt += f"""

## 当前市场数据
{json.dumps(market_data, indent=2, ensure_ascii=False)}

## 账户状态
- 余额: ${account_state.get('balance', 0):.2f}
- 持仓: {account_state.get('position', 'NONE')}
- 可用资金: ${account_state.get('available', 0):.2f}

## 约束条件
{json.dumps(constraints, indent=2, ensure_ascii=False)}

## 最近决策
{json.dumps(recent_decisions[:3], indent=2, ensure_ascii=False) if recent_decisions else "无"}

## 相似场景
{json.dumps(similar_situations[:2], indent=2, ensure_ascii=False) if similar_situations else "无"}
"""
                
                # 如果有情报报告，追加
                if intelligence_report:
                    prompt += f"""

## Qwen情报分析
- 市场情绪: {intelligence_report.market_sentiment.value}
- 置信度: {intelligence_report.confidence:.2f}
- 摘要: {getattr(intelligence_report, 'summary', '')[:300]}
"""
                
                # 如果有辩论结果，追加
                if debate_result and debate_result.get('final_decision'):
                    prompt += f"""

## 多角度辩论结论
{json.dumps(debate_result, indent=2, ensure_ascii=False)}
"""
                
                logger.info(f"✅ 使用Prompt模板: {template.category}/{template.name} v{template.version} ({template.permission_level or '通用'})")
            else:
                # Fallback：使用简化版本
                logger.warning(f"⚠️  未找到Prompt模板，使用fallback")
                prompt = f"""你是专业的加密货币交易AI（权限等级：{self.current_permission_level}）。

## 当前市场数据
{json.dumps(market_data, indent=2, ensure_ascii=False)}

## 账户状态
{json.dumps(account_state, indent=2, ensure_ascii=False)}

请基于以上信息做出交易决策，返回JSON格式。"""
            
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
            
            # === 详细决策日志输出 ===
            logger.info("="*60)
            logger.info("🎯 决策详情：")
            logger.info(f"  - 决策ID: {ai_decision.get('decision_id')}")
            logger.info(f"  - 动作: {ai_decision.get('action')}")
            logger.info(f"  - 币种: {ai_decision.get('symbol')}")
            logger.info(f"  - 金额: {ai_decision.get('size_usd')} USD")
            logger.info(f"  - 置信度: {ai_decision.get('confidence'):.2f} (阈值: {permission.confidence_threshold})")
            logger.info(f"  - 状态: {ai_decision.get('status')}")
            logger.info(f"  - 推理: {ai_decision.get('reasoning')[:200] if ai_decision.get('reasoning') else 'N/A'}")
            if ai_decision.get('notes'):
                logger.info(f"  - 备注: {ai_decision.get('notes')}")
            
            # 如果被拒绝，详细说明原因
            if ai_decision.get("status") == "REJECTED":
                logger.warning("❌ 决策被拒绝！")
                logger.warning(f"   拒绝原因: {ai_decision.get('notes')}")
                logger.warning(f"   当前权限: {self.current_permission_level}")
                logger.warning(f"   置信度阈值: {permission.confidence_threshold}")
                logger.warning(f"   实际置信度: {ai_decision.get('confidence')}")
            else:
                logger.info(f"✅ 决策通过: {ai_decision.get('action')} {ai_decision.get('symbol')}")
            
            logger.info("="*60)
            
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
        import time
        from app.services.ai_usage_logger import log_ai_call
        
        start_time = time.time()
        success = False
        error_message = None
        input_tokens = 0
        output_tokens = 0
        cost = 0.0
        
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
            
            # 提取token使用信息
            if hasattr(response, 'usage') and response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                
                # 计算成本（DeepSeek定价：输入¥1/M, 输出¥2/M）
                cost = (input_tokens / 1_000_000 * 1.0) + (output_tokens / 1_000_000 * 2.0)
            
            success = True
            response_time = time.time() - start_time
            
            # 异步记录使用日志
            try:
                await log_ai_call(
                    db=self.db_session,
                    model_name=self.model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost,
                    platform_id=1,  # DeepSeek平台ID（假设为1）
                    success=True,
                    response_time=response_time,
                    purpose="decision",
                    request_id=f"dec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
            except Exception as log_error:
                logger.warning(f"记录AI使用日志失败（不影响主流程）: {log_error}")
            
            return response.choices[0].message.content
        
        except Exception as e:
            error_message = str(e)
            response_time = time.time() - start_time
            
            # 记录失败日志
            try:
                await log_ai_call(
                    db=self.db_session,
                    model_name=self.model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost,
                    platform_id=1,  # DeepSeek平台ID
                    success=False,
                    error_message=error_message,
                    response_time=response_time,
                    purpose="decision",
                    request_id=f"dec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
            except Exception as log_error:
                logger.warning(f"记录AI使用日志失败: {log_error}")
            
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
        """记录决策到记忆系统和数据库"""
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
            
            # 3. 保存到数据库
            await self._save_to_database(
                decision=decision,
                market_data=market_data,
                status=status,
                timestamp=timestamp
            )
            
            logger.debug(f"📝 决策已记录: {decision_id}")
        
        except Exception as e:
            logger.error(f"记录决策失败: {e}")
    
    async def _save_to_database(
        self,
        decision: Dict[str, Any],
        market_data: Dict[str, Any],
        status: str,
        timestamp: datetime
    ):
        """保存决策到Postgres数据库"""
        try:
            from app.models.ai_decision import AIDecision
            
            db_decision = AIDecision(
                timestamp=timestamp,
                symbol=decision.get("symbol", ""),
                market_data=market_data,
                decision=decision,
                executed=(status == "APPROVED"),
                reject_reason=decision.get("notes") if status != "APPROVED" else None,
                model_name=decision.get("model_name", "deepseek-chat-v3.1")
            )
            
            self.db_session.add(db_decision)
            await self.db_session.commit()
            logger.debug(f"💾 决策已保存到数据库: {decision.get('decision_id')}")
            
        except Exception as e:
            logger.error(f"保存决策到数据库失败: {e}")
            await self.db_session.rollback()
    
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
    
    async def _should_enable_debate(self, account_state: Dict[str, Any]) -> bool:
        """
        判断是否应该启用辩论
        
        Args:
            account_state: 账户状态
        
        Returns:
            是否启用辩论
        """
        if not self.debate_config:
            return False
        
        return await self.debate_config.should_trigger_debate(account_state)
    
    def _build_situation_description(self, market_data: Dict, intelligence_report: Any) -> str:
        """
        构建市场情况描述（用于记忆检索）
        
        Args:
            market_data: 市场数据
            intelligence_report: 情报报告
        
        Returns:
            情况描述字符串
        """
        desc_parts = []
        
        # 添加价格信息
        if "price" in market_data:
            desc_parts.append(f"Current price: ${market_data['price']}")
        
        # 添加趋势信息
        if "trend" in market_data:
            desc_parts.append(f"Trend: {market_data['trend']}")
        
        # 添加情报信息
        if intelligence_report:
            desc_parts.append(f"Market sentiment: {intelligence_report.market_sentiment.value}")
            if intelligence_report.summary:
                desc_parts.append(f"Summary: {intelligence_report.summary[:200]}")
        
        return " | ".join(desc_parts)

