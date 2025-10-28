"""DeepSeek AI决策引擎 - 完全自主决策模式"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal
from loguru import logger
import openai

from app.core.config import settings
from app.core.redis_client import RedisClient


class DeepSeekDecisionEngine:
    """DeepSeek AI决策引擎 - 完全自主决策，无人工限制"""
    
    def __init__(self, redis_client: RedisClient, initial_capital: float = 10000.0):
        self.redis_client = redis_client
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model_name = "deepseek-chat"
        self.base_url = "https://api.deepseek.com/v1"
        
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # ✅ AI自主管理的资金
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # ❌ 移除所有人工限制参数
        # self.confidence_threshold = 0.7  # 删除
        # self.max_position_size = Decimal("1000")  # 删除
        # self.risk_tolerance = 0.02  # 删除
        
        # 决策历史
        self.decision_history = []
        self.total_decisions = 0
        self.successful_decisions = 0
        
    async def analyze_market_data(self, market_data: Dict[str, Any], account_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析市场数据并做出自主交易决策"""
        try:
            # 如果没有提供账户状态，使用默认值
            if account_state is None:
                account_state = {
                    'balance': self.current_capital,
                    'positions': [],
                    'total_pnl': 0
                }
            
            # 构建AI自主决策提示
            prompt = self._build_analysis_prompt(market_data, account_state)
            
            # 调用DeepSeek API
            response = await self._call_deepseek_api(prompt)
            
            # 解析响应 (AI的完全自主决策)
            analysis_result = self._parse_analysis_response(response)
            
            # 记录决策
            await self._record_decision(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze market data: {e}")
            return self._get_fallback_decision()
    
    def _build_analysis_prompt(self, market_data: Dict[str, Any], account_state: Dict[str, Any]) -> str:
        """构建AI自主决策提示 - nof1.ai风格"""
        
        # 获取当前持仓信息
        positions = account_state.get('positions', [])
        balance = account_state.get('balance', self.current_capital)
        total_pnl = account_state.get('total_pnl', 0)
        
        prompt = f"""You are an autonomous crypto trading AI participating in Alpha Arena, competing against other AI models.

═══════════════════════════════════════════════════════════
ACCOUNT STATUS
═══════════════════════════════════════════════════════════
Initial Capital: ${self.initial_capital:,.2f}
Current Balance: ${balance:,.2f}
Total PnL: ${total_pnl:,.2f} ({(total_pnl/self.initial_capital*100):.2f}%)
Current Positions: {len(positions)} open position(s)

Position Details:
{self._format_positions(positions)}

═══════════════════════════════════════════════════════════
MARKET DATA (Real-time from Hyperliquid)
═══════════════════════════════════════════════════════════
BTC: ${market_data.get('BTC', {}).get('price', 0):,.2f}
ETH: ${market_data.get('ETH', {}).get('price', 0):,.2f}
SOL: ${market_data.get('SOL', {}).get('price', 0):,.2f}
BNB: ${market_data.get('BNB', {}).get('price', 0):,.2f}
DOGE: ${market_data.get('DOGE', {}).get('price', 0):,.4f}
XRP: ${market_data.get('XRP', {}).get('price', 0):,.4f}

Market Trend: {market_data.get('trend', 'neutral')}
Volatility: {market_data.get('volatility', 'medium')}

═══════════════════════════════════════════════════════════
YOUR CAPABILITIES
═══════════════════════════════════════════════════════════
✅ Open LONG positions (buy)
✅ Open SHORT positions (sell)
✅ Close existing positions
✅ Hold (do nothing)
✅ Trade perpetual contracts on Hyperliquid
✅ YOU decide position sizes (any amount up to your balance)
✅ YOU decide stop-loss and take-profit levels
✅ YOU manage your own risk

═══════════════════════════════════════════════════════════
YOUR OBJECTIVE
═══════════════════════════════════════════════════════════
Maximize risk-adjusted returns. You are competing against:
- Qwen 3 Max
- Other AI models

Your goal is to generate the highest Sharpe ratio and total returns.

═══════════════════════════════════════════════════════════
YOUR TASK
═══════════════════════════════════════════════════════════
Analyze the current market conditions and your account status.
Make YOUR OWN trading decision based on YOUR OWN analysis.

YOU are fully autonomous. All decisions are YOURS:
- Position sizing is YOUR decision
- Risk management is YOUR responsibility  
- Entry/exit timing is YOUR choice
- Stop-loss levels are YOUR decision
- Take-profit targets are YOUR decision

Think like a professional hedge fund manager. Consider:
1. Market trend and momentum
2. Your current positions and exposure
3. Risk-reward ratio
4. Portfolio diversification
5. Market volatility
6. Your competitive position vs other AIs

═══════════════════════════════════════════════════════════
RESPOND IN JSON FORMAT
═══════════════════════════════════════════════════════════
{{
  "analysis": "Your detailed market analysis and reasoning (2-3 sentences)",
  "action": "open_long" | "open_short" | "close_position" | "hold",
  "symbol": "BTC" | "ETH" | "SOL" | "BNB" | "DOGE" | "XRP",
  "size_usd": 1000.0,  // YOUR decision on position size in USD
  "leverage": 1,  // Leverage to use (1-5x)
  "stop_loss_pct": 0.02,  // YOUR stop-loss percentage (e.g., 0.02 = 2%)
  "take_profit_pct": 0.05,  // YOUR take-profit percentage (e.g., 0.05 = 5%)
  "reasoning": "Why you made this specific decision",
  "risk_assessment": "Your assessment of the risk in this trade",
  "confidence": 0.75,  // Your confidence level (0-1)
  "expected_return": 0.03,  // Your expected return percentage
  "time_horizon": "short" | "medium" | "long"  // Expected holding period
}}

IMPORTANT: 
- Be decisive. Don't be overly conservative.
- You're competing to WIN, not just to preserve capital.
- Smart risk-taking is rewarded.
- But also don't be reckless - you can lose everything.
- Return ONLY valid JSON, no extra text.
"""
        return prompt
    
    def _format_positions(self, positions: List[Dict]) -> str:
        """格式化持仓信息"""
        if not positions:
            return "No open positions"
        
        formatted = []
        for i, pos in enumerate(positions, 1):
            formatted.append(
                f"  {i}. {pos.get('symbol', 'N/A')} - "
                f"{pos.get('side', 'N/A')} "
                f"${pos.get('size_usd', 0):,.2f} "
                f"(PnL: ${pos.get('pnl', 0):,.2f})"
            )
        return "\n".join(formatted)
    
    async def _call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的加密货币交易AI，擅长技术分析和风险管理。请提供准确、客观的交易建议。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}")
            raise
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """解析AI自主决策响应"""
        try:
            # 尝试解析JSON
            if response.strip().startswith('{'):
                result = json.loads(response)
            else:
                # 如果不是JSON格式，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in response")
            
            # 验证必要字段 (新的自主决策格式)
            required_fields = [
                'analysis', 'action', 'symbol', 'size_usd', 
                'leverage', 'stop_loss_pct', 'take_profit_pct',
                'reasoning', 'risk_assessment', 'confidence', 
                'expected_return', 'time_horizon'
            ]
            for field in required_fields:
                if field not in result:
                    result[field] = self._get_default_value(field)
            
            # 添加元数据
            result['timestamp'] = datetime.now().isoformat()
            result['model'] = 'deepseek-chat'
            
            logger.info(f"DeepSeek AI Decision: {result.get('action')} {result.get('symbol')} ${result.get('size_usd')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse AI decision response: {e}")
            logger.error(f"Response content: {response[:500]}...")  # 记录前500字符用于调试
            return self._get_fallback_decision()
    
    def _get_default_value(self, field: str) -> Any:
        """获取默认值"""
        defaults = {
            'analysis': 'Market analysis unavailable',
            'action': 'hold',
            'symbol': 'BTC',
            'size_usd': 0,
            'leverage': 1,
            'stop_loss_pct': 0.02,
            'take_profit_pct': 0.05,
            'reasoning': 'Conservative approach due to missing data',
            'risk_assessment': 'Unknown risk level',
            'confidence': 0.5,
            'expected_return': 0,
            'time_horizon': 'medium'
        }
        return defaults.get(field, None)
    
    def _get_fallback_decision(self) -> Dict[str, Any]:
        """获取备用决策 - 当API调用失败时"""
        return {
            'analysis': 'AI service temporarily unavailable. Holding position.',
            'action': 'hold',
            'symbol': 'BTC',
            'size_usd': 0,
            'leverage': 1,
            'stop_loss_pct': 0.02,
            'take_profit_pct': 0.05,
            'reasoning': 'System error - maintaining current positions',
            'risk_assessment': 'Cannot assess risk due to service outage',
            'confidence': 0.3,
            'expected_return': 0,
            'time_horizon': 'short',
            'timestamp': datetime.now().isoformat(),
            'model': 'deepseek-chat',
            'fallback': True
        }
    
    async def _record_decision(self, decision: Dict[str, Any]):
        """记录决策"""
        try:
            decision_id = f"deepseek_decision_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            decision_record = {
                'decision_id': decision_id,
                'model': 'deepseek-chat',
                'decision': decision,
                'timestamp': datetime.now().isoformat()
            }
            
            # 存储到Redis
            await self.redis_client.set(f"decision:{decision_id}", decision_record, expire=86400)
            
            # 更新统计
            self.decision_history.append(decision_record)
            self.total_decisions += 1
            
            # AI完全自主决策，所有决策都计入统计
            # 不根据置信度判断成功与否，由实际交易结果决定
            
            logger.info(f"DeepSeek autonomous decision recorded: {decision_id}")
            logger.info(f"Action: {decision.get('action')}, Symbol: {decision.get('symbol')}, Size: ${decision.get('size_usd')}")
            
        except Exception as e:
            logger.error(f"Failed to record decision: {e}")
    
    async def get_decision_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取决策历史"""
        try:
            # 从Redis获取最近的决策
            keys = await self.redis_client.redis.keys("decision:deepseek_decision_*")
            keys.sort(reverse=True)  # 按时间倒序
            
            decisions = []
            for key in keys[:limit]:
                decision = await self.redis_client.get(key)
                if decision:
                    decisions.append(decision)
            
            return decisions
            
        except Exception as e:
            logger.error(f"Failed to get decision history: {e}")
            return self.decision_history[-limit:] if self.decision_history else []
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        try:
            success_rate = (self.successful_decisions / self.total_decisions * 100) if self.total_decisions > 0 else 0
            
            return {
                'total_decisions': self.total_decisions,
                'successful_decisions': self.successful_decisions,
                'success_rate': round(success_rate, 2),
                'initial_capital': self.initial_capital,
                'current_capital': self.current_capital,
                'model_name': self.model_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {
                'total_decisions': 0,
                'successful_decisions': 0,
                'success_rate': 0,
                'initial_capital': self.initial_capital,
                'current_capital': self.current_capital,
                'model_name': self.model_name,
                'timestamp': datetime.now().isoformat()
            }
    
    async def validate_decision(self, decision: Dict[str, Any], current_balance: float) -> bool:
        """基础安全验证 - 只检查账户安全，不限制AI决策"""
        try:
            # ✅ 只检查账户不能透支
            size_usd = decision.get('size_usd', 0)
            if size_usd > current_balance:
                logger.warning(f"Insufficient balance: ${size_usd} > ${current_balance}")
                return False
            
            # ✅ 检查杠杆合理性
            leverage = decision.get('leverage', 1)
            if leverage < 1 or leverage > 10:
                logger.warning(f"Invalid leverage: {leverage}")
                return False
            
            # ❌ 删除所有其他人工限制
            # 不检查置信度
            # 不检查仓位大小上限
            # 不检查风险等级
            
            return True
            
        except Exception as e:
            logger.error(f"Decision validation failed: {e}")
            return False
