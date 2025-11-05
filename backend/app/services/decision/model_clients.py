"""DeepSeek Model Clients - 模型客户端封装

封装训练好的70B模型和默认API客户端
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import openai
from app.core.config import settings

logger = logging.getLogger(__name__)


class Trained70BClient:
    """
    训练好的70B模型客户端（百度部署）
    
    用于调用在百度智能云部署的训练好的DeepSeek 70B模型
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "deepseek-70b-trained"
    ):
        self.api_key = api_key or settings.DEEPSEEK_70B_API_KEY
        self.base_url = base_url or settings.DEEPSEEK_70B_BASE_URL
        self.model = model
        
        if not self.api_key or not self.base_url:
            logger.warning("训练70B模型API密钥或URL未配置")
            self.available = False
        else:
            self.client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.available = True
    
    async def make_decision(
        self,
        market_data: Dict[str, Any],
        intelligence_report: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        使用训练好的70B模型做决策
        
        Args:
            market_data: 市场数据
            intelligence_report: 情报报告
            context: 额外上下文
        
        Returns:
            决策结果
        """
        if not self.available:
            raise RuntimeError("训练70B模型不可用：API未配置")
        
        try:
            prompt = self._build_decision_prompt(market_data, intelligence_report, context)
            
            start_time = datetime.now()
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是专业的加密货币交易决策AI，基于市场数据和情报做出交易决策。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            decision_text = response.choices[0].message.content
            
            # 解析决策
            parsed = self._parse_decision(decision_text)
            parsed["model_used"] = "trained_70b"
            parsed["response_time"] = response_time
            parsed["cost"] = self._estimate_cost(response.usage)
            
            return parsed
            
        except Exception as e:
            logger.error(f"训练70B模型决策失败: {e}", exc_info=True)
            raise
    
    def _build_decision_prompt(
        self,
        market_data: Dict[str, Any],
        intelligence_report: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """构建决策Prompt"""
        return f"""
请基于以下信息做出交易决策：

【市场数据】
{market_data}

【情报报告】
{intelligence_report}

请输出：
1. 决策：BUY/SELL/HOLD
2. 置信度：0.0-1.0
3. 推理过程
"""
    
    def _parse_decision(self, decision_text: str) -> Dict[str, Any]:
        """解析决策文本"""
        decision = "HOLD"
        if "BUY" in decision_text.upper():
            decision = "BUY"
        elif "SELL" in decision_text.upper():
            decision = "SELL"
        
        # TODO: 从文本中提取置信度
        confidence = 0.8
        
        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": decision_text,
            "timestamp": datetime.now()
        }
    
    def _estimate_cost(self, usage) -> float:
        """估算成本"""
        if not usage:
            return 0.0
        # 假设价格（需要根据实际调整）
        input_cost = (usage.prompt_tokens / 1_000_000) * 0.50
        output_cost = (usage.completion_tokens / 1_000_000) * 1.50
        return input_cost + output_cost
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return self.available


class DefaultAPIClient:
    """
    默认DeepSeek API客户端
    
    用于调用用户提供的默认DeepSeek API（保底方案）
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "deepseek-chat"
    ):
        self.api_key = api_key or settings.DEEPSEEK_DEFAULT_API_KEY or settings.DEEPSEEK_API_KEY
        self.base_url = base_url or settings.DEEPSEEK_DEFAULT_BASE_URL or "https://api.deepseek.com"
        self.model = model
        
        if not self.api_key:
            logger.error("默认DeepSeek API密钥未配置")
            self.available = False
        else:
            self.client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.available = True
    
    async def make_decision(
        self,
        market_data: Dict[str, Any],
        intelligence_report: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        使用默认API做决策
        
        Args:
            market_data: 市场数据
            intelligence_report: 情报报告
            context: 额外上下文
        
        Returns:
            决策结果
        """
        if not self.available:
            raise RuntimeError("默认DeepSeek API不可用：API密钥未配置")
        
        try:
            prompt = self._build_decision_prompt(market_data, intelligence_report, context)
            
            start_time = datetime.now()
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是专业的加密货币交易决策AI，基于市场数据和情报做出交易决策。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            decision_text = response.choices[0].message.content
            
            # 解析决策
            parsed = self._parse_decision(decision_text)
            parsed["model_used"] = "default_api"
            parsed["response_time"] = response_time
            parsed["cost"] = self._estimate_cost(response.usage)
            
            return parsed
            
        except Exception as e:
            logger.error(f"默认API决策失败: {e}", exc_info=True)
            raise
    
    def _build_decision_prompt(
        self,
        market_data: Dict[str, Any],
        intelligence_report: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """构建决策Prompt"""
        return f"""
请基于以下信息做出交易决策：

【市场数据】
{market_data}

【情报报告】
{intelligence_report}

请输出：
1. 决策：BUY/SELL/HOLD
2. 置信度：0.0-1.0
3. 推理过程
"""
    
    def _parse_decision(self, decision_text: str) -> Dict[str, Any]:
        """解析决策文本"""
        decision = "HOLD"
        if "BUY" in decision_text.upper():
            decision = "BUY"
        elif "SELL" in decision_text.upper():
            decision = "SELL"
        
        # TODO: 从文本中提取置信度
        confidence = 0.75
        
        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": decision_text,
            "timestamp": datetime.now()
        }
    
    def _estimate_cost(self, usage) -> float:
        """估算成本"""
        if not usage:
            return 0.0
        # DeepSeek定价
        input_cost = (usage.prompt_tokens / 1_000_000) * 0.14
        output_cost = (usage.completion_tokens / 1_000_000) * 0.28
        return input_cost + output_cost
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return self.available

