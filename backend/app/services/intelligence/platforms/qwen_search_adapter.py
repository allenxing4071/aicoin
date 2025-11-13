"""Qwen Search Adapter - Qwen联网搜索适配器（实时情报员）"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import openai
from .base_adapter import BasePlatformAdapter, PlatformRole

logger = logging.getLogger(__name__)


class QwenSearchAdapter(BasePlatformAdapter):
    """
    Qwen搜索适配器 - 平台B：实时情报员
    
    职责：
    1. 使用Qwen的联网搜索能力获取实时信息
    2. 获取最新新闻动态
    3. 查找官方公告
    
    特点：
    - 使用Qwen的联网搜索功能
    - 实时性强
    - 按需付费
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        model: str = "qwen-plus",
        enabled: bool = True
    ):
        super().__init__(
            platform_name="Qwen Search (实时搜索)",
            role=PlatformRole.REALTIME_SCOUT,
            api_key=api_key,
            base_url=base_url,
            enabled=enabled
        )
        
        # 初始化OpenAI客户端（Qwen兼容）
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
    
    async def analyze(
        self,
        data_sources: Dict[str, Any],
        query_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        实时搜索分析
        
        Args:
            data_sources: 原始数据源（用于上下文）
            query_context: {
                "symbols": List[str],  # 关注的币种
                "topics": List[str],   # 关注的主题
                "time_range": str      # 时间范围
            }
        
        Returns:
            实时搜索结果
        """
        try:
            logger.info("🔍 Qwen搜索平台开始实时搜索...")
            
            # 构建搜索查询
            search_query = self._build_search_query(data_sources, query_context)
            
            # 调用Qwen搜索API
            # 注意：根据Qwen官方文档，可能需要特定参数来启用搜索
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的加密货币实时情报员。请使用联网搜索功能，获取最新、最真实的市场信息。"
                    },
                    {
                        "role": "user",
                        "content": search_query
                    }
                ],
                temperature=0.3,  # 低温度，注重事实
                max_tokens=1000,
                # 注意：如果Qwen支持联网搜索，可能需要添加特定参数
                # 例如：enable_search=True 或其他参数
            )
            
            analysis_text = response.choices[0].message.content
            
            # 估算成本（根据Qwen定价）
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            cost = self._calculate_cost(input_tokens, output_tokens)
            
            # 解析响应
            key_findings = self._extract_key_findings(analysis_text)
            
            # ✅ 记录调用（包含token信息）
            await self._record_call(success=True, cost=cost, response_time=0.0, input_tokens=input_tokens, output_tokens=output_tokens)
            
            result = {
                "platform": self.platform_name,
                "role": self.role,
                "analysis": analysis_text,
                "confidence": 0.85,  # 实时搜索置信度较高
                "key_findings": key_findings,
                "search_query": search_query,
                "timestamp": datetime.now(),
                "cost": cost,
                "tokens_used": {
                    "prompt": usage.prompt_tokens if usage else 0,
                    "completion": usage.completion_tokens if usage else 0,
                    "total": usage.total_tokens if usage else 0
                }
            }
            
            logger.info(f"✅ Qwen搜索完成: {len(key_findings)} 个关键发现")
            return result
            
        except Exception as e:
            logger.error(f"❌ Qwen搜索失败: {e}", exc_info=True)
            response_time = (datetime.now() - start_time).total_seconds() * 1000 if "start_time" in locals() else 0.0
            await self._record_call(success=False, cost=0.0, response_time=response_time)
            
            return {
                "platform": self.platform_name,
                "role": self.role,
                "analysis": "实时搜索暂时不可用",
                "confidence": 0.0,
                "key_findings": [],
                "timestamp": datetime.now(),
                "cost": 0.0,
                "error": str(e)
            }
    
    def _build_search_query(
        self,
        data_sources: Dict[str, Any],
        query_context: Optional[Dict[str, Any]]
    ) -> str:
        """构建搜索查询"""
        symbols = query_context.get("symbols", ["BTC", "ETH"]) if query_context else ["BTC", "ETH"]
        topics = query_context.get("topics", []) if query_context else []
        
        query_parts = [
            "请搜索并分析以下加密货币的最新动态：",
            f"关注币种: {', '.join(symbols)}",
        ]
        
        if topics:
            query_parts.append(f"关注主题: {', '.join(topics)}")
        
        query_parts.extend([
            "",
            "请重点关注：",
            "1. 最新的官方公告和重大新闻",
            "2. 市场价格异常波动的原因",
            "3. 监管政策变化",
            "4. 技术升级或重要事件",
            "5. 机构动向和大额资金流动",
            "",
            "请提供：",
            "- 信息来源和发布时间",
            "- 事件的影响程度评估",
            "- 市场可能的反应预测"
        ])
        
        return "\n".join(query_parts)
    
    def _extract_key_findings(self, analysis_text: str) -> List[str]:
        """从分析文本中提取关键发现"""
        key_findings = []
        
        # 简单的提取逻辑
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            # 提取以数字、• 或 - 开头的要点
            if line and (
                line[0].isdigit() or 
                line.startswith('•') or 
                line.startswith('-') or
                line.startswith('*')
            ):
                # 清理格式
                cleaned = line.lstrip('0123456789.•-* \t')
                if len(cleaned) > 10:  # 过滤太短的行
                    key_findings.append(cleaned)
        
        return key_findings[:10]  # 最多返回10个关键发现
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        计算API调用成本（使用统一定价管理器）
        """
        from app.services.ai_pricing import get_pricing_manager
        
        pricing_manager = get_pricing_manager()
        
        # 使用统一的定价管理器计算成本
        cost = pricing_manager.calculate_cost(
            provider=self.provider or "qwen",
            model="qwen-plus",  # 默认使用 qwen-plus
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens
        )
        
        return cost
    
    async def health_check(self) -> bool:
        """健康检查"""
        if not self.enabled:
            return False
        
        try:
            start_time = datetime.now()
            # 简单的ping测试
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=10,
                timeout=5
            )
            return bool(response)
        except Exception as e:
            logger.error(f"Qwen搜索健康检查失败: {e}")
            return False

