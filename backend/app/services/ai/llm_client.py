"""LLM Client for AI decisions"""

from openai import AsyncOpenAI
from typing import Optional, Dict, Any
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM客户端 (支持DeepSeek/Claude/GPT-4)"""
    
    def __init__(self):
        self.deepseek_client = None
        self.claude_client = None
        self.openai_client = None
        
        # 初始化DeepSeek客户端
        if settings.DEEPSEEK_API_KEY:
            self.deepseek_client = AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com"
            )
            logger.info("DeepSeek client initialized")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def call_deepseek(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        调用DeepSeek API
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            LLM响应内容
        """
        if not self.deepseek_client:
            raise ValueError("DeepSeek client not initialized. Please set DEEPSEEK_API_KEY")
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            logger.info(f"Calling DeepSeek API, prompt length: {len(prompt)}")
            
            response = await self.deepseek_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=settings.LLM_TIMEOUT
            )
            
            content = response.choices[0].message.content
            logger.info(f"DeepSeek response received, length: {len(content)}")
            
            return content
            
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}")
            raise
    
    async def call_llm_with_fallback(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        调用LLM (带备用方案)
        
        优先级: DeepSeek -> Claude -> GPT-4
        """
        try:
            # 优先使用DeepSeek
            if self.deepseek_client:
                return await self.call_deepseek(prompt, system_prompt)
            
            # TODO: 添加Claude和GPT-4备用方案
            raise ValueError("No LLM client available")
            
        except Exception as e:
            logger.error(f"All LLM clients failed: {e}")
            raise
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM的JSON响应
        
        Args:
            response: LLM原始响应
            
        Returns:
            解析后的JSON对象
        """
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取JSON部分
            try:
                # 查找第一个{和最后一个}
                start = response.find('{')
                end = response.rfind('}') + 1
                
                if start != -1 and end > start:
                    json_str = response[start:end]
                    return json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                    
            except Exception as e:
                logger.error(f"Failed to parse JSON from response: {response[:200]}")
                raise ValueError(f"Invalid JSON response: {e}")


# Global LLM client instance
llm_client = LLMClient()

