"""DeepSeek AI决策引擎"""

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
    """DeepSeek AI决策引擎"""
    
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model_name = "deepseek-chat"
        self.base_url = "https://api.deepseek.com/v1"
        
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 决策配置
        self.confidence_threshold = 0.7  # 置信度阈值
        self.max_position_size = Decimal("1000")  # 最大持仓金额
        self.risk_tolerance = 0.02  # 风险容忍度 2%
        
        # 决策历史
        self.decision_history = []
        self.total_decisions = 0
        self.successful_decisions = 0
        
    async def analyze_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析市场数据"""
        try:
            # 构建分析提示
            prompt = self._build_analysis_prompt(market_data)
            
            # 调用DeepSeek API
            response = await self._call_deepseek_api(prompt)
            
            # 解析响应
            analysis_result = self._parse_analysis_response(response)
            
            # 记录决策
            await self._record_decision(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze market data: {e}")
            return await self._get_fallback_decision()
    
    def _build_analysis_prompt(self, market_data: Dict[str, Any]) -> str:
        """构建分析提示"""
        prompt = f"""
你是一个专业的加密货币交易AI，需要分析当前市场数据并做出交易决策。

当前市场数据：
- BTC价格: ${market_data.get('BTC', {}).get('price', 0):,.2f}
- ETH价格: ${market_data.get('ETH', {}).get('price', 0):,.2f}
- SOL价格: ${market_data.get('SOL', {}).get('price', 0):,.2f}
- 市场趋势: {market_data.get('trend', 'neutral')}
- 波动率: {market_data.get('volatility', 'medium')}

请分析以下内容：
1. 市场趋势分析
2. 技术指标评估
3. 风险因素识别
4. 交易建议

请以JSON格式返回分析结果，包含以下字段：
- analysis: 市场分析总结
- trend: 趋势判断 (bullish/bearish/neutral)
- confidence: 置信度 (0-1)
- recommendation: 交易建议 (buy/sell/hold)
- target_symbol: 目标交易对
- position_size: 建议仓位大小 (0-1000)
- stop_loss: 止损价格
- take_profit: 止盈价格
- reasoning: 决策理由
- risk_level: 风险等级 (low/medium/high)

请确保返回有效的JSON格式。
"""
        return prompt
    
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
        """解析分析响应"""
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
            
            # 验证必要字段
            required_fields = ['analysis', 'trend', 'confidence', 'recommendation', 'target_symbol']
            for field in required_fields:
                if field not in result:
                    result[field] = self._get_default_value(field)
            
            # 添加时间戳
            result['timestamp'] = datetime.now().isoformat()
            result['model'] = 'deepseek-chat'
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return self._get_fallback_decision()
    
    def _get_default_value(self, field: str) -> Any:
        """获取默认值"""
        defaults = {
            'analysis': '市场分析暂时不可用',
            'trend': 'neutral',
            'confidence': 0.5,
            'recommendation': 'hold',
            'target_symbol': 'BTC',
            'position_size': 100,
            'stop_loss': 0,
            'take_profit': 0,
            'reasoning': '基于当前市场数据的保守建议',
            'risk_level': 'medium'
        }
        return defaults.get(field, None)
    
    async def _get_fallback_decision(self) -> Dict[str, Any]:
        """获取备用决策"""
        return {
            'analysis': '市场数据分析暂时不可用，采用保守策略',
            'trend': 'neutral',
            'confidence': 0.3,
            'recommendation': 'hold',
            'target_symbol': 'BTC',
            'position_size': 50,
            'stop_loss': 0,
            'take_profit': 0,
            'reasoning': '系统异常，采用保守策略',
            'risk_level': 'low',
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
            
            if decision.get('confidence', 0) >= self.confidence_threshold:
                self.successful_decisions += 1
            
            logger.info(f"DeepSeek decision recorded: {decision_id}")
            
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
                'confidence_threshold': self.confidence_threshold,
                'model_name': self.model_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {
                'total_decisions': 0,
                'successful_decisions': 0,
                'success_rate': 0,
                'confidence_threshold': self.confidence_threshold,
                'model_name': self.model_name,
                'timestamp': datetime.now().isoformat()
            }
    
    async def validate_decision(self, decision: Dict[str, Any]) -> bool:
        """验证决策"""
        try:
            # 检查置信度
            confidence = decision.get('confidence', 0)
            if confidence < 0.3:
                logger.warning(f"Low confidence decision: {confidence}")
                return False
            
            # 检查仓位大小
            position_size = decision.get('position_size', 0)
            if position_size > self.max_position_size:
                logger.warning(f"Position size too large: {position_size}")
                return False
            
            # 检查风险等级
            risk_level = decision.get('risk_level', 'medium')
            if risk_level == 'high' and confidence < 0.8:
                logger.warning("High risk decision with low confidence")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Decision validation failed: {e}")
            return False
    
    async def optimize_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """优化决策"""
        try:
            # 根据风险等级调整仓位大小
            risk_level = decision.get('risk_level', 'medium')
            base_position = decision.get('position_size', 100)
            
            if risk_level == 'low':
                optimized_position = min(base_position * 1.2, self.max_position_size)
            elif risk_level == 'high':
                optimized_position = max(base_position * 0.5, 50)
            else:
                optimized_position = base_position
            
            decision['position_size'] = optimized_position
            
            # 调整置信度
            if decision.get('confidence', 0) < 0.5:
                decision['recommendation'] = 'hold'
                decision['position_size'] = 0
            
            return decision
            
        except Exception as e:
            logger.error(f"Decision optimization failed: {e}")
            return decision
