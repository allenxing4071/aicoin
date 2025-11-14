"""Qwen Deep Analyzer Adapter - Qwen深度推理适配器（深度分析师）"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import openai
from .base_adapter import BasePlatformAdapter, PlatformRole

logger = logging.getLogger(__name__)


class QwenDeepAdapter(BasePlatformAdapter):
    """
    Qwen深度分析适配器 - 平台C：深度分析师
    
    职责：
    1. 复杂推理和关联分析
    2. 综合研判多源信息
    3. 生成深度洞察报告
    
    特点：
    - 使用Qwen的强大推理能力
    - 深度分析，高质量输出
    - 成本较高，用于关键决策
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        model: str = "qwen-plus",
        enabled: bool = True
    ):
        super().__init__(
            platform_name="Qwen Deep Analysis (深度分析)",
            role=PlatformRole.DEEP_ANALYST,
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
        深度综合分析
        
        Args:
            data_sources: {
                "raw_data": {...},           # 原始数据源
                "free_platform_result": {...},  # 免费平台筛选结果
                "search_result": {...}         # 实时搜索结果
            }
            query_context: 查询上下文
        
        Returns:
            深度分析结果
        """
        try:
            logger.info("🧠 Qwen深度分析平台开始综合研判...")
            
            # 构建深度分析Prompt
            analysis_prompt = self._build_analysis_prompt(data_sources, query_context)
            
            # 调用Qwen API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一位顶级的加密货币市场深度分析师。你的任务是：
1. 综合分析多源信息（新闻、链上数据、实时搜索结果）
2. 识别深层关联和因果关系
3. 评估潜在风险和机会
4. 提供高质量的投资洞察

你的分析应该：
- 基于事实和数据
- 逻辑严谨、推理清晰
- 考虑多个维度和可能性
- 提供可操作的建议"""
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.5,  # 平衡创造性和准确性
                max_tokens=2000,  # 允许更长的深度分析
            )
            
            analysis_text = response.choices[0].message.content
            
            # 估算成本
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            cost = self._calculate_cost(input_tokens, output_tokens)
            
            # 解析分析结果
            parsed_analysis = self._parse_analysis(analysis_text)
            
            # ✅ 记录调用（包含token信息）
            await self._record_call(success=True, cost=cost, response_time=0.0, input_tokens=input_tokens, output_tokens=output_tokens)
            
            result = {
                "platform": self.platform_name,
                "role": self.role,
                "analysis": analysis_text,
                "confidence": parsed_analysis.get("confidence", 0.9),
                "key_findings": parsed_analysis.get("key_findings", []),
                "risk_factors": parsed_analysis.get("risk_factors", []),
                "opportunities": parsed_analysis.get("opportunities", []),
                "market_sentiment": parsed_analysis.get("sentiment", "neutral"),
                "sentiment_score": parsed_analysis.get("sentiment_score", 0.0),
                "timestamp": datetime.now(),
                "cost": cost,
                "tokens_used": {
                    "prompt": usage.prompt_tokens if usage else 0,
                    "completion": usage.completion_tokens if usage else 0,
                    "total": usage.total_tokens if usage else 0
                }
            }
            
            logger.info(f"✅ Qwen深度分析完成: 置信度 {result['confidence']:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Qwen深度分析失败: {e}", exc_info=True)
            response_time = (datetime.now() - start_time).total_seconds() * 1000 if "start_time" in locals() else 0.0
            await self._record_call(success=False, cost=0.0, response_time=response_time)
            
            return {
                "platform": self.platform_name,
                "role": self.role,
                "analysis": "深度分析暂时不可用",
                "confidence": 0.0,
                "key_findings": [],
                "risk_factors": [],
                "opportunities": [],
                "timestamp": datetime.now(),
                "cost": 0.0,
                "error": str(e)
            }
    
    def _build_analysis_prompt(
        self,
        data_sources: Dict[str, Any],
        query_context: Optional[Dict[str, Any]]
    ) -> str:
        """构建深度分析Prompt"""
        prompt_parts = [
            "请对以下加密货币市场情报进行深度综合分析：",
            "",
            "═══════════════════════════════════════════════════════════",
            "📊 基础筛选结果（免费平台）",
            "═══════════════════════════════════════════════════════════",
        ]
        
        # 添加免费平台结果
        free_result = data_sources.get("free_platform_result", {})
        if free_result:
            prompt_parts.append(free_result.get("analysis", "暂无基础筛选结果"))
            findings = free_result.get("key_findings", [])
            if findings:
                prompt_parts.append("\n关键发现：")
                for i, finding in enumerate(findings, 1):
                    prompt_parts.append(f"{i}. {finding}")
        
        prompt_parts.extend([
            "",
            "═══════════════════════════════════════════════════════════",
            "🔍 实时搜索结果（DeepSeek搜索）",
            "═══════════════════════════════════════════════════════════",
        ])
        
        # 添加实时搜索结果
        search_result = data_sources.get("search_result", {})
        if search_result:
            prompt_parts.append(search_result.get("analysis", "暂无实时搜索结果"))
        
        prompt_parts.extend([
            "",
            "═══════════════════════════════════════════════════════════",
            "🎯 深度分析任务",
            "═══════════════════════════════════════════════════════════",
            "",
            "请基于以上信息，进行深度综合分析，并按以下结构输出：",
            "",
            "1. **综合分析** (200-300字)：",
            "   - 整合多源信息，识别关键趋势",
            "   - 分析事件之间的关联性",
            "   - 评估市场整体状况",
            "",
            "2. **市场情绪** (看涨/看跌/中性)：",
            "   - 给出明确的情绪判断",
            "   - 提供情绪强度分数 (-1.0 到 1.0)",
            "",
            "3. **风险因素** (列出3-5个)：",
            "   - 识别潜在的下行风险",
            "   - 评估风险的严重程度",
            "",
            "4. **机会点** (列出2-3个)：",
            "   - 识别潜在的上行机会",
            "   - 评估机会的可行性",
            "",
            "5. **置信度** (0.0-1.0)：",
            "   - 对本次分析的整体置信度",
            "",
            "请保持客观、专业，基于事实和逻辑进行推理。"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """解析分析结果"""
        result = {
            "key_findings": [],
            "risk_factors": [],
            "opportunities": [],
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "confidence": 0.8
        }
        
        try:
            start_time = datetime.now()
            lines = analysis_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # 识别章节
                if "风险因素" in line or "Risk" in line:
                    current_section = "risks"
                elif "机会" in line or "Opportunity" in line or "Opportunities" in line:
                    current_section = "opportunities"
                elif "市场情绪" in line or "Sentiment" in line:
                    current_section = "sentiment"
                elif "置信度" in line or "Confidence" in line:
                    current_section = "confidence"
                
                # 提取内容
                if current_section == "risks" and line and (line[0].isdigit() or line.startswith('-')):
                    cleaned = line.lstrip('0123456789.•-* \t')
                    if len(cleaned) > 5:
                        result["risk_factors"].append(cleaned)
                
                elif current_section == "opportunities" and line and (line[0].isdigit() or line.startswith('-')):
                    cleaned = line.lstrip('0123456789.•-* \t')
                    if len(cleaned) > 5:
                        result["opportunities"].append(cleaned)
                
                elif current_section == "sentiment":
                    if "BULLISH" in line.upper() or "看涨" in line:
                        result["sentiment"] = "bullish"
                        result["sentiment_score"] = 0.6
                    elif "BEARISH" in line.upper() or "看跌" in line:
                        result["sentiment"] = "bearish"
                        result["sentiment_score"] = -0.6
                    
                    # 尝试提取分数
                    import re
                    score_match = re.search(r'[-+]?\d*\.?\d+', line)
                    if score_match:
                        try:
                            score = float(score_match.group())
                            if -1.0 <= score <= 1.0:
                                result["sentiment_score"] = score
                        except:
                            pass
                
                elif current_section == "confidence":
                    import re
                    conf_match = re.search(r'\d*\.?\d+', line)
                    if conf_match:
                        try:
                            conf = float(conf_match.group())
                            if conf <= 1.0:
                                result["confidence"] = conf
                            elif conf <= 100:
                                result["confidence"] = conf / 100
                        except:
                            pass
            
            # 默认值
            if not result["risk_factors"]:
                result["risk_factors"] = ["市场波动性", "监管不确定性"]
            if not result["opportunities"]:
                result["opportunities"] = ["技术面突破"]
            
            # 提取关键发现（从开头部分）
            for line in lines[:20]:
                line = line.strip()
                if line and len(line) > 20 and (
                    line[0].isdigit() or 
                    line.startswith('•') or 
                    line.startswith('-')
                ):
                    cleaned = line.lstrip('0123456789.•-* \t')
                    if cleaned not in result["key_findings"]:
                        result["key_findings"].append(cleaned)
                        if len(result["key_findings"]) >= 5:
                            break
            
        except Exception as e:
            logger.error(f"解析分析结果失败: {e}")
        
        return result
    
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
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=10,
                timeout=5
            )
            return bool(response)
        except Exception as e:
            logger.error(f"Qwen深度分析健康检查失败: {e}")
            return False

