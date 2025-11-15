"""Tencent Qwen Search Adapter - 腾讯云Qwen联网搜索适配器"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from app.utils.timezone import get_beijing_time
import logging
import httpx
from ..base_adapter import BasePlatformAdapter, PlatformRole

logger = logging.getLogger(__name__)


class TencentQwenAdapter(BasePlatformAdapter):
    """
    腾讯云 - Qwen联网搜索适配器
    
    职责：
    1. 使用腾讯云提供的Qwen模型联网搜索能力
    2. 获取最新的市场新闻动态
    3. 查找官方公告和监管信息
    
    特点：
    - 腾讯云AI平台
    - 支持联网搜索
    - 稳定可靠
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://hunyuan.tencentcloudapi.com",
        model: str = "qwen-plus",
        enabled: bool = True
    ):
        super().__init__(
            platform_name="腾讯云 (Qwen搜索)",
            role=PlatformRole.REALTIME_SCOUT,
            api_key=api_key,
            base_url=base_url,
            enabled=enabled
        )
        
        self.client = httpx.AsyncClient(timeout=30.0)
        self.model = model
    
    async def analyze(
        self,
        data_sources: Dict[str, Any],
        query_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        实时搜索分析
        
        Args:
            data_sources: 原始数据源
            query_context: 查询上下文
        
        Returns:
            实时搜索结果
        """
        try:
            logger.info("🔍 腾讯云 - Qwen联网搜索开始...")
            
            # 构建搜索查询
            search_query = self._build_search_query(data_sources, query_context)
            
            # 调用腾讯云API
            # 注意：实际API格式需根据腾讯云文档调整
            response = await self.client.post(
                f"{self.base_url}/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是专业的加密货币实时情报员，使用联网搜索获取最新信息。"
                        },
                        {
                            "role": "user",
                            "content": search_query
                        }
                    ],
                    "search": True,  # 启用搜索
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            response.raise_for_status()
            result_data = response.json()
            
            analysis_text = result_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 提取关键发现
            key_findings = self._extract_key_findings(analysis_text)
            
            # 记录成功调用
            response_time = (get_beijing_time() - start_time).total_seconds() * 1000
            await self._record_call(success=True, cost=0.0, response_time=response_time)
            
            result = {
                "platform": self.platform_name,
                "role": self.role,
                "analysis": analysis_text,
                "confidence": 0.85,
                "key_findings": key_findings,
                "search_query": search_query,
                "timestamp": get_beijing_time(),
                "cost": 0.0
            }
            
            logger.info(f"✅ 腾讯云搜索完成: {len(key_findings)} 个关键发现")
            return result
            
        except Exception as e:
            logger.error(f"❌ 腾讯云搜索失败: {e}", exc_info=True)
            response_time = (get_beijing_time() - start_time).total_seconds() * 1000 if "start_time" in locals() else 0.0
            await self._record_call(success=False, cost=0.0, response_time=response_time)
            
            return {
                "platform": self.platform_name,
                "role": self.role,
                "analysis": "腾讯云实时搜索暂时不可用",
                "confidence": 0.0,
                "key_findings": [],
                "timestamp": get_beijing_time(),
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
        
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (
                line[0].isdigit() or 
                line.startswith('•') or 
                line.startswith('-') or
                line.startswith('*')
            ):
                cleaned = line.lstrip('0123456789.•-* \t')
                if len(cleaned) > 10:
                    key_findings.append(cleaned)
        
        return key_findings[:10]
    
    async def health_check(self) -> bool:
        """健康检查"""
        if not self.enabled:
            return False
        
        try:
            start_time = get_beijing_time()
            response = await self.client.post(
                f"{self.base_url}/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 10
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"腾讯云健康检查失败: {e}")
            return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

