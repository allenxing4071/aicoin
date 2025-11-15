"""
DecisionEngineV2集成示例
展示如何集成Prompt系统和三层记忆
"""

import logging
from typing import Dict, Any, Optional
import uuid
import asyncio

from app.services.decision.prompt_manager_db import PromptManagerDB
from app.services.memory.prompt_memory_extension import PromptMemoryExtension
from app.services.memory.prompt_performance_memory import PromptPerformanceMemory

logger = logging.getLogger(__name__)


class DecisionEngineV2Integration:
    """
    DecisionEngineV2集成示例
    
    展示如何：
    1. 从数据库加载Prompt（根据权限等级）
    2. 智能推荐最佳Prompt（从Qdrant）
    3. 记录决策到三层记忆
    """
    
    def __init__(
        self,
        prompt_manager: PromptManagerDB,
        prompt_memory_ext: PromptMemoryExtension,
        prompt_perf_memory: PromptPerformanceMemory
    ):
        self.prompt_manager = prompt_manager
        self.prompt_memory_ext = prompt_memory_ext
        self.prompt_perf_memory = prompt_perf_memory
    
    async def make_decision(
        self,
        user_permission_level: str,
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        做出交易决策（集成三层记忆）
        
        Args:
            user_permission_level: 用户权限等级（L0-L5）
            market_data: 市场数据
        
        Returns:
            决策结果
        """
        logger.info(f"🤖 开始决策（权限等级: {user_permission_level}）")
        
        # ===== 1. 智能推荐Prompt（从Qdrant） =====
        recommended_prompt = await self.prompt_perf_memory.recommend_best_prompt(
            current_market_data=market_data,
            permission_level=user_permission_level
        )
        
        if recommended_prompt and recommended_prompt["confidence_score"] > 0.7:
            logger.info(f"🎯 使用推荐Prompt: {recommended_prompt['prompt_template_id']} (置信度: {recommended_prompt['confidence_score']:.2f})")
            template_id = recommended_prompt["prompt_template_id"]
        else:
            # 降级到默认Prompt
            logger.info(f"⚠️  无高置信度推荐，使用默认Prompt")
            template_id = None
        
        # ===== 2. 获取Prompt模板（从数据库） =====
        template = self.prompt_manager.get_template(
            category="decision",
            name="default",
            permission_level=user_permission_level
        )
        
        if not template:
            logger.error("❌ 无法加载Prompt模板")
            return {"error": "Prompt模板加载失败"}
        
        logger.info(f"📝 使用Prompt: {template.category}/{template.name} (v{template.version}, {template.permission_level or '通用'})")
        
        # ===== 3. 构建完整Prompt =====
        prompt_content = template.content
        
        # 动态插入市场数据
        prompt_with_data = f"""
{prompt_content}

## 当前市场数据
- 交易对: {market_data.get('symbol')}
- 价格: ${market_data.get('price')}
- 24h涨跌: {market_data.get('change_24h')}%
- 成交量: {market_data.get('volume')}
- 波动率: {market_data.get('volatility')}%

请基于以上信息做出决策。
"""
        
        # ===== 4. 调用DeepSeek决策（模拟） =====
        # TODO: 实际调用DeepSeek API
        decision = {
            "action": "LONG",
            "confidence": 0.85,
            "position_size_usd": 1000,
            "stop_loss": market_data.get('price') * 0.98,
            "take_profit": market_data.get('price') * 1.03,
            "reasoning": "技术指标看涨，市场情绪积极"
        }
        
        logger.info(f"✅ 决策完成: {decision['action']} (置信度: {decision['confidence']})")
        
        # ===== 5. 记录到短期记忆（Redis） =====
        decision_id = str(uuid.uuid4())
        
        await self.prompt_memory_ext.record_prompt_usage(
            decision_id=decision_id,
            prompt_template_id=template.id,
            prompt_version=template.version,
            permission_level=user_permission_level,
            timestamp=datetime.now(),
            market_data=market_data,
            decision_result=decision
        )
        
        logger.info(f"💾 已记录到短期记忆（Redis）: {decision_id}")
        
        # ===== 6. 异步存储到长期记忆（Qdrant） =====
        asyncio.create_task(
            self.prompt_perf_memory.store_prompt_decision(
                decision_id=decision_id,
                prompt_template_id=template.id,
                prompt_version=template.version,
                prompt_content=template.content,
                permission_level=user_permission_level,
                market_data=market_data,
                decision=decision
            )
        )
        
        logger.info(f"🚀 已提交到长期记忆（Qdrant）异步存储")
        
        # ===== 7. 返回决策结果 =====
        return {
            "decision_id": decision_id,
            "prompt_template_id": template.id,
            "prompt_version": template.version,
            **decision
        }


# ===== 使用示例 =====

async def example_usage():
    """使用示例"""
    from app.core.database import get_db
    from app.core.redis_client import redis_client
    from qdrant_client import QdrantClient
    
    # 初始化组件
    db = await anext(get_db())
    prompt_manager = PromptManagerDB(db)
    await prompt_manager.load_from_db()
    
    prompt_memory_ext = PromptMemoryExtension(redis_client)
    
    qdrant_client = QdrantClient(host="localhost", port=6333)
    prompt_perf_memory = PromptPerformanceMemory(qdrant_client)
    
    # 创建决策引擎
    engine = DecisionEngineV2Integration(
        prompt_manager=prompt_manager,
        prompt_memory_ext=prompt_memory_ext,
        prompt_perf_memory=prompt_perf_memory
    )
    
    # 模拟市场数据
    market_data = {
        "symbol": "BTCUSDT",
        "price": 45000.0,
        "change_24h": 2.5,
        "volume": 1500000000,
        "volatility": 3.2
    }
    
    # 做出决策
    decision = await engine.make_decision(
        user_permission_level="L2",
        market_data=market_data
    )
    
    print(f"决策结果: {decision}")


if __name__ == "__main__":
    import asyncio
    from datetime import datetime
    asyncio.run(example_usage())

