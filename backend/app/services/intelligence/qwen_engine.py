"""Qwen Intelligence Engine - Market Intelligence Officer"""

import logging
from datetime import datetime
from typing import List, Optional
import openai
from app.core.config import settings
from app.utils.timezone import get_beijing_time
from .models import IntelligenceReport, SentimentType
from .data_sources import crypto_news_api, on_chain_data_api
from .storage import intelligence_storage

logger = logging.getLogger(__name__)


class QwenIntelligenceEngine:
    """
    Qwen作为情报官(Intelligence Officer)
    负责收集和分析市场情报，不直接参与交易决策
    """
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL
        )
        self.model = settings.QWEN_MODEL
        self.is_running = False
        self.last_report_time: Optional[datetime] = None
    
    async def collect_intelligence(self) -> IntelligenceReport:
        """
        收集完整的市场情报
        这是主入口方法，协调所有情报收集工作
        """
        try:
            logger.info("🕵️‍♀️ Qwen情报官开始收集情报...")
            
            # 并发收集所有数据
            news_items = await crypto_news_api.fetch_latest_news(limit=10)
            whale_signals = await on_chain_data_api.detect_whale_activity()
            on_chain_metrics = await on_chain_data_api.fetch_on_chain_metrics()
            
            # 使用Qwen分析所有情报
            report = await self.generate_intelligence_report(
                news_items=news_items,
                whale_signals=whale_signals,
                on_chain_metrics=on_chain_metrics
            )
            
            # 存储报告
            await intelligence_storage.store_report(report)
            self.last_report_time = report.timestamp
            
            logger.info(f"✅ Qwen情报报告生成完成: 情绪={report.market_sentiment.value}, 置信度={report.confidence:.2f}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Qwen情报收集失败: {e}", exc_info=True)
            # Return a minimal report
            return self._create_fallback_report()
    
    async def generate_intelligence_report(
        self,
        news_items: List,
        whale_signals: List,
        on_chain_metrics
    ) -> IntelligenceReport:
        """使用Qwen分析所有情报并生成综合报告"""
        import time
        
        try:
            # 构建分析prompt
            prompt = self._build_analysis_prompt(news_items, whale_signals, on_chain_metrics)
            
            # 调用Qwen进行分析
            start_time = time.time()
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的加密货币市场情报分析师。你的任务是分析市场数据、新闻和链上信息，为交易AI提供客观、全面的情报报告。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more factual analysis
                max_tokens=1500
            )
            response_time = time.time() - start_time
            
            # 提取token和成本信息
            input_tokens = 0
            output_tokens = 0
            cost = 0.0
            
            if hasattr(response, 'usage') and response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                # Qwen定价：输入¥4/M, 输出¥12/M
                cost = (input_tokens / 1_000_000 * 4.0) + (output_tokens / 1_000_000 * 12.0)
            
            # 异步记录使用日志（不阻塞主流程）
            try:
                from app.core.database import AsyncSessionLocal
                from app.services.ai_usage_logger import log_ai_call
                
                async with AsyncSessionLocal() as db:
                    await log_ai_call(
                        db=db,
                        model_name=self.model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cost=cost,
                        platform_id=2,  # Qwen平台ID（假设为2）
                        success=True,
                        response_time=response_time,
                        purpose="intelligence",
                        request_id=f"intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )
            except Exception as log_error:
                logger.warning(f"记录Qwen使用日志失败（不影响主流程）: {log_error}")
            
            analysis_text = response.choices[0].message.content
            
            # 解析Qwen的分析结果
            sentiment, sentiment_score, risk_factors, opportunities, confidence = self._parse_qwen_analysis(
                analysis_text
            )
            
            # 构建完整报告
            report = IntelligenceReport(
                timestamp=get_beijing_time(),
                market_sentiment=sentiment,
                sentiment_score=sentiment_score,
                key_news=news_items[:5],  # Top 5 news
                whale_signals=whale_signals,
                on_chain_metrics=on_chain_metrics,
                risk_factors=risk_factors,
                opportunities=opportunities,
                qwen_analysis=analysis_text,
                confidence=confidence
            )
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Qwen分析失败: {e}", exc_info=True)
            return self._create_fallback_report()
    
    def _build_analysis_prompt(self, news_items, whale_signals, on_chain_metrics) -> str:
        """构建发给Qwen的分析prompt"""
        prompt = """请分析以下加密货币市场情报，并提供你的专业判断：

═══════════════════════════════════════════════════════════
📰 最新新闻 (Latest News)
═══════════════════════════════════════════════════════════
"""
        
        for i, news in enumerate(news_items[:5], 1):
            prompt += f"\n{i}. 【{news.source}】{news.title}\n"
            if news.content:
                prompt += f"   内容: {news.content[:100]}...\n"
            prompt += f"   影响: {news.impact} | 情绪: {news.sentiment}\n"
        
        prompt += f"""
═══════════════════════════════════════════════════════════
🐋 巨鲸活动 (Whale Activity)
═══════════════════════════════════════════════════════════
"""
        
        for whale in whale_signals:
            action_cn = {"buy": "买入", "sell": "卖出", "transfer": "转账"}.get(whale.action, whale.action)
            prompt += f"\n• {whale.symbol}: {action_cn} ${whale.amount_usd:,.0f}"
            if whale.exchange:
                prompt += f" ({whale.exchange})"
            prompt += "\n"
        
        prompt += f"""
═══════════════════════════════════════════════════════════
📊 链上指标 (On-Chain Metrics)
═══════════════════════════════════════════════════════════
• 交易所净流量: ${on_chain_metrics.exchange_net_flow:,.0f} (负数=流出=看涨)
• 活跃地址数: {on_chain_metrics.active_addresses:,}
• Gas价格: {on_chain_metrics.gas_price:.2f} Gwei
• 交易量: ${on_chain_metrics.transaction_volume:,.0f}

═══════════════════════════════════════════════════════════
🎯 请提供你的分析 (Your Analysis)
═══════════════════════════════════════════════════════════

请按以下格式输出你的分析：

1. **市场情绪** (BULLISH/BEARISH/NEUTRAL): 
2. **情绪强度** (-1.0到1.0的数值):
3. **风险因素** (列出3-5个):
4. **机会点** (列出2-3个):
5. **综合分析** (200字以内的专业分析):
6. **置信度** (0.0-1.0):

请保持客观，基于数据和事实进行分析。
"""
        return prompt
    
    def _parse_qwen_analysis(self, analysis_text: str) -> tuple:
        """解析Qwen的分析结果"""
        try:
            # 简单解析（实际项目中应该用更robust的方法）
            sentiment = SentimentType.NEUTRAL
            sentiment_score = 0.0
            risk_factors = []
            opportunities = []
            confidence = 0.7
            
            lines = analysis_text.split('\n')
            for line in lines:
                line_lower = line.lower()
                
                if 'bullish' in line_lower or '看涨' in line_lower or '乐观' in line_lower:
                    sentiment = SentimentType.BULLISH
                    sentiment_score = 0.6
                elif 'bearish' in line_lower or '看跌' in line_lower or '悲观' in line_lower:
                    sentiment = SentimentType.BEARISH
                    sentiment_score = -0.6
                
                if '风险' in line and '：' in line:
                    risk = line.split('：')[1].strip()
                    if risk:
                        risk_factors.append(risk)
                
                if '机会' in line and '：' in line:
                    opp = line.split('：')[1].strip()
                    if opp:
                        opportunities.append(opp)
                
                if '置信度' in line:
                    try:
                        # Extract number from line
                        import re
                        match = re.search(r'(\d+\.?\d*)', line)
                        if match:
                            conf_val = float(match.group(1))
                            confidence = conf_val if conf_val <= 1.0 else conf_val / 100
                    except:
                        pass
            
            # Default values if parsing failed
            if not risk_factors:
                risk_factors = ["市场波动性", "监管不确定性", "宏观经济环境"]
            if not opportunities:
                opportunities = ["技术面突破", "机构资金流入"]
            
            return sentiment, sentiment_score, risk_factors, opportunities, confidence
            
        except Exception as e:
            logger.error(f"❌ 解析Qwen分析失败: {e}")
            return SentimentType.NEUTRAL, 0.0, ["数据不足"], ["观望"], 0.5
    
    def _create_fallback_report(self) -> IntelligenceReport:
        """创建fallback报告（当Qwen失败时）"""
        from .models import OnChainMetrics
        return IntelligenceReport(
            timestamp=get_beijing_time(),
            market_sentiment=SentimentType.NEUTRAL,
            sentiment_score=0.0,
            key_news=[],
            whale_signals=[],
            on_chain_metrics=OnChainMetrics(
                exchange_net_flow=0,
                active_addresses=0,
                gas_price=0,
                transaction_volume=0,
                timestamp=get_beijing_time()
            ),
            risk_factors=["情报系统暂时不可用"],
            opportunities=[],
            qwen_analysis="情报收集系统暂时不可用，使用默认配置。",
            confidence=0.3
        )
    
    async def start(self):
        """启动情报引擎"""
        self.is_running = True
        logger.info("🕵️‍♀️ Qwen情报引擎已启动")
    
    async def stop(self):
        """停止情报引擎"""
        self.is_running = False
        logger.info("🛑 Qwen情报引擎已停止")


# Singleton instance
qwen_intelligence_engine = QwenIntelligenceEngine()

