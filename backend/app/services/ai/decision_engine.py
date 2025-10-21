"""AI Decision Engine"""

from decimal import Decimal
from typing import Dict, Any
import logging
import time
from app.services.ai.llm_client import llm_client
from app.services.ai.prompts import build_trading_prompt, TRADING_SYSTEM_PROMPT
from app.schemas.decision import AIDecisionOutput

logger = logging.getLogger(__name__)


class AIDecisionEngine:
    """AI决策引擎"""
    
    async def make_decision(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        account_info: Dict[str, Any]
    ) -> tuple[AIDecisionOutput, int]:
        """
        执行AI交易决策
        
        Args:
            symbol: 交易品种
            market_data: 市场数据 (klines, orderbook, ticker)
            account_info: 账户信息 (balance, positions)
            
        Returns:
            (决策结果, 延迟ms)
        """
        try:
            start_time = time.time()
            
            # 构建Prompt
            prompt = build_trading_prompt(
                symbol=symbol,
                current_price=Decimal(str(market_data.get('current_price', 0))),
                kline_data=market_data.get('klines', []),
                orderbook=market_data.get('orderbook', {}),
                account_balance=Decimal(str(account_info.get('balance', 0))),
                position_info=account_info.get('position', {})
            )
            
            logger.info(f"Making AI decision for {symbol}")
            
            # 调用LLM
            response = await llm_client.call_llm_with_fallback(
                prompt=prompt,
                system_prompt=TRADING_SYSTEM_PROMPT
            )
            
            # 解析响应
            decision_data = llm_client.parse_json_response(response)
            
            # 验证并创建决策对象
            decision = AIDecisionOutput(
                action=decision_data.get('action', 'HOLD').upper(),
                size=Decimal(str(decision_data.get('size', 0))),
                confidence=Decimal(str(decision_data.get('confidence', 0))),
                reasoning=decision_data.get('reasoning', 'No reasoning provided')[:500]
            )
            
            # 计算延迟
            latency_ms = int((time.time() - start_time) * 1000)
            
            logger.info(
                f"AI Decision: {decision.action} {decision.size} @ "
                f"confidence {decision.confidence}, latency {latency_ms}ms"
            )
            
            return decision, latency_ms
            
        except Exception as e:
            logger.error(f"Error making AI decision: {e}")
            
            # 返回保守的HOLD决策
            fallback_decision = AIDecisionOutput(
                action="HOLD",
                size=Decimal(0),
                confidence=Decimal(0),
                reasoning=f"Error occurred: {str(e)[:200]}"
            )
            
            return fallback_decision, 0


# Global decision engine instance
decision_engine = AIDecisionEngine()

