"""Free Platform Adapter - 免费平台适配器（基础监控员）"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from .base_adapter import BasePlatformAdapter, PlatformRole

logger = logging.getLogger(__name__)


class FreePlatformAdapter(BasePlatformAdapter):
    """
    免费平台适配器 - 平台A：基础监控员
    
    职责：
    1. 高频信息筛选
    2. 初步情报过滤
    3. 基础模式识别
    
    特点：
    - 使用免费API额度
    - 低成本运营
    - 适合高频、基础性任务
    """
    
    def __init__(self, enabled: bool = True):
        super().__init__(
            platform_name="Free Platform (基础监控)",
            role=PlatformRole.FREE_MONITOR,
            enabled=enabled
        )
        self.filter_rules = self._load_filter_rules()
    
    def _load_filter_rules(self) -> Dict[str, Any]:
        """加载过滤规则"""
        return {
            "high_impact_keywords": [
                "监管", "禁令", "批准", "上市", "退市",
                "黑客", "漏洞", "攻击", "盗币",
                "减半", "升级", "分叉", "合并",
                "机构", "基金", "ETF", "SEC", "CFTC"
            ],
            "whale_threshold_usd": 1_000_000,  # $1M
            "sentiment_keywords": {
                "bullish": ["看涨", "上涨", "突破", "创新高", "利好", "买入"],
                "bearish": ["看跌", "下跌", "跌破", "创新低", "利空", "卖出"]
            }
        }
    
    async def analyze(
        self,
        data_sources: Dict[str, Any],
        query_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        基础分析：快速筛选高价值信息
        
        Args:
            data_sources: {
                "news_items": List[NewsItem],
                "whale_signals": List[WhaleActivity],
                "on_chain_metrics": OnChainMetrics
            }
            query_context: 查询上下文
        
        Returns:
            分析结果
        """
        try:
            logger.info("🔍 免费平台开始基础筛选...")
            
            news_items = data_sources.get("news_items", [])
            whale_signals = data_sources.get("whale_signals", [])
            
            # 1. 筛选高影响力新闻
            high_impact_news = self._filter_high_impact_news(news_items)
            
            # 2. 筛选大额巨鲸活动
            significant_whales = self._filter_significant_whales(whale_signals)
            
            # 3. 识别市场情绪
            market_sentiment = self._detect_sentiment(news_items)
            
            # 4. 生成关键发现
            key_findings = []
            
            if high_impact_news:
                key_findings.append(f"发现 {len(high_impact_news)} 条高影响力新闻")
            
            if significant_whales:
                total_value = sum(w.amount_usd for w in significant_whales)
                key_findings.append(f"检测到 {len(significant_whales)} 个大额巨鲸活动，总价值 ${total_value:,.0f}")
            
            if market_sentiment != "neutral":
                key_findings.append(f"市场情绪偏向: {market_sentiment}")
            
            # 记录成功调用
            await self._record_call(success=True, cost=0.0)
            
            result = {
                "platform": self.platform_name,
                "role": self.role,
                "analysis": self._generate_summary(high_impact_news, significant_whales, market_sentiment),
                "confidence": 0.7,  # 基础分析置信度
                "key_findings": key_findings,
                "filtered_data": {
                    "high_impact_news": [self._serialize_news(n) for n in high_impact_news],
                    "significant_whales": [self._serialize_whale(w) for w in significant_whales],
                    "market_sentiment": market_sentiment
                },
                "timestamp": datetime.now(),
                "cost": 0.0
            }
            
            logger.info(f"✅ 免费平台分析完成: {len(key_findings)} 个关键发现")
            return result
            
        except Exception as e:
            logger.error(f"❌ 免费平台分析失败: {e}", exc_info=True)
            await self._record_call(success=False, cost=0.0)
            
            return {
                "platform": self.platform_name,
                "role": self.role,
                "analysis": "基础筛选暂时不可用",
                "confidence": 0.0,
                "key_findings": [],
                "timestamp": datetime.now(),
                "cost": 0.0,
                "error": str(e)
            }
    
    def _filter_high_impact_news(self, news_items: List) -> List:
        """筛选高影响力新闻"""
        high_impact = []
        
        for news in news_items:
            # 检查是否包含高影响关键词
            title = news.title.lower() if hasattr(news, 'title') else ""
            content = news.content.lower() if hasattr(news, 'content') else ""
            
            for keyword in self.filter_rules["high_impact_keywords"]:
                if keyword in title or keyword in content:
                    high_impact.append(news)
                    break
            
            # 或者标记为高影响
            if hasattr(news, 'impact') and news.impact == "high":
                if news not in high_impact:
                    high_impact.append(news)
        
        return high_impact
    
    def _filter_significant_whales(self, whale_signals: List) -> List:
        """筛选大额巨鲸活动"""
        threshold = self.filter_rules["whale_threshold_usd"]
        return [
            w for w in whale_signals 
            if hasattr(w, 'amount_usd') and w.amount_usd >= threshold
        ]
    
    def _detect_sentiment(self, news_items: List) -> str:
        """检测市场情绪"""
        bullish_count = 0
        bearish_count = 0
        
        sentiment_keywords = self.filter_rules["sentiment_keywords"]
        
        for news in news_items:
            text = (
                (news.title if hasattr(news, 'title') else "") + " " +
                (news.content if hasattr(news, 'content') else "")
            ).lower()
            
            # 检查看涨关键词
            for keyword in sentiment_keywords["bullish"]:
                if keyword in text:
                    bullish_count += 1
                    break
            
            # 检查看跌关键词
            for keyword in sentiment_keywords["bearish"]:
                if keyword in text:
                    bearish_count += 1
                    break
        
        if bullish_count > bearish_count * 1.5:
            return "bullish"
        elif bearish_count > bullish_count * 1.5:
            return "bearish"
        else:
            return "neutral"
    
    def _generate_summary(self, high_impact_news: List, significant_whales: List, sentiment: str) -> str:
        """生成摘要"""
        summary_parts = []
        
        if high_impact_news:
            summary_parts.append(f"筛选出 {len(high_impact_news)} 条高影响力新闻")
        
        if significant_whales:
            summary_parts.append(f"发现 {len(significant_whales)} 个大额巨鲸活动")
        
        summary_parts.append(f"市场情绪: {sentiment}")
        
        return "；".join(summary_parts) + "。建议关注这些高优先级信息。"
    
    def _serialize_news(self, news) -> Dict[str, Any]:
        """序列化新闻对象"""
        return {
            "title": news.title if hasattr(news, 'title') else "",
            "source": news.source if hasattr(news, 'source') else "",
            "impact": news.impact if hasattr(news, 'impact') else "unknown",
            "sentiment": news.sentiment if hasattr(news, 'sentiment') else "neutral",
            "published_at": news.published_at.isoformat() if hasattr(news, 'published_at') else None
        }
    
    def _serialize_whale(self, whale) -> Dict[str, Any]:
        """序列化巨鲸对象"""
        return {
            "symbol": whale.symbol if hasattr(whale, 'symbol') else "",
            "action": whale.action if hasattr(whale, 'action') else "",
            "amount_usd": whale.amount_usd if hasattr(whale, 'amount_usd') else 0,
            "timestamp": whale.timestamp.isoformat() if hasattr(whale, 'timestamp') else None
        }
    
    async def health_check(self) -> bool:
        """健康检查"""
        # 免费平台总是可用（基于规则，不依赖外部API）
        return self.enabled

