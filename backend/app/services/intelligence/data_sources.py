"""External Data Sources for Intelligence Gathering"""

import logging
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
import aiohttp
from .models import NewsItem, WhaleActivity, OnChainMetrics
from app.core.config import settings

logger = logging.getLogger(__name__)


class CryptoNewsAPI:
    """Fetch crypto news from multiple sources (RSS Feeds)"""
    
    def __init__(self):
        # RSS源配置（可以从数据库或Redis动态加载）
        self.rss_sources = [
            {
                "name": "CoinDesk",
                "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                "enabled": True
            },
            {
                "name": "CoinTelegraph",
                "url": "https://cointelegraph.com/rss",
                "enabled": True
            }
        ]
        # 从配置文件读取是否使用Mock数据
        self.use_mock = getattr(settings, 'RSS_USE_MOCK', False)  # 默认使用真实数据
    
    async def fetch_latest_news(self, limit: int = 10) -> List[NewsItem]:
        """Fetch latest crypto news from RSS feeds or mock data"""
        try:
            # 检查是否使用真实RSS源
            if not self.use_mock and any(source["enabled"] for source in self.rss_sources):
                return await self._fetch_from_rss(limit)
            else:
                return await self._fetch_mock_data(limit)
            
        except Exception as e:
            logger.error(f"❌ 获取新闻失败: {e}")
            return []
    
    async def _fetch_from_rss(self, limit: int) -> List[NewsItem]:
        """从真实RSS源获取新闻"""
        try:
            import feedparser
            
            all_news = []
            
            for source in self.rss_sources:
                if not source["enabled"]:
                    continue
                
                try:
                    logger.info(f"📰 正在获取 {source['name']} RSS...")
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(source["url"], timeout=aiohttp.ClientTimeout(total=10)) as response:
                            if response.status == 200:
                                rss_content = await response.text()
                                feed = feedparser.parse(rss_content)
                                
                                for entry in feed.entries[:5]:  # 每个源取5条
                                    # 解析发布时间
                                    published_at = datetime.now()
                                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                        published_at = datetime(*entry.published_parsed[:6])
                                    
                                    # 提取内容摘要
                                    content = entry.get('summary', '') or entry.get('description', '')
                                    if content:
                                        # 清理HTML标签
                                        import re
                                        content = re.sub(r'<[^>]+>', '', content)[:200]
                                    
                                    news_item = NewsItem(
                                        title=entry.get('title', 'No Title'),
                                        source=source['name'],
                                        url=entry.get('link', ''),
                                        published_at=published_at,
                                        content=content,
                                        impact="medium",  # 默认中等影响，后续由Qwen分析
                                        sentiment="neutral"  # 默认中性，后续由Qwen分析
                                    )
                                    all_news.append(news_item)
                                
                                logger.info(f"✓ {source['name']}: 获取到 {len(feed.entries[:5])} 条新闻")
                            else:
                                logger.warning(f"⚠️  {source['name']} HTTP {response.status}")
                                
                except Exception as e:
                    logger.error(f"❌ 获取 {source['name']} 失败: {e}")
                    continue
            
            # 按时间排序，返回最新的
            all_news.sort(key=lambda x: x.published_at, reverse=True)
            result = all_news[:limit]
            
            logger.info(f"✅ RSS源共获取到 {len(result)} 条新闻")
            return result if result else await self._fetch_mock_data(limit)
            
        except ImportError:
            logger.warning("⚠️  feedparser未安装，回退到Mock数据。请运行: pip install feedparser")
            return await self._fetch_mock_data(limit)
        except Exception as e:
            logger.error(f"❌ RSS解析失败: {e}，回退到Mock数据")
            return await self._fetch_mock_data(limit)
    
    async def _fetch_mock_data(self, limit: int) -> List[NewsItem]:
        """获取Mock数据（用于测试或RSS源不可用时）"""
        logger.info("📝 使用Mock数据（测试模式）")
        
            mock_news = [
                {
                    "title": "Bitcoin突破10万美元大关，机构买盘强劲",
                    "source": "CoinDesk",
                    "url": "https://coindesk.com/btc-100k",
                    "published_at": datetime.now() - timedelta(hours=2),
                    "content": "比特币价格突破历史新高，主要由机构投资者推动...",
                    "impact": "high",
                    "sentiment": "bullish"
                },
                {
                    "title": "以太坊Layer2活跃度创新高",
                    "source": "Decrypt",
                    "url": "https://decrypt.co/eth-l2",
                    "published_at": datetime.now() - timedelta(hours=5),
                    "content": "Arbitrum和Optimism交易量激增...",
                    "impact": "medium",
                    "sentiment": "bullish"
                },
                {
                    "title": "美联储会议纪要：加息周期可能接近尾声",
                    "source": "Reuters",
                    "url": "https://reuters.com/fed",
                    "published_at": datetime.now() - timedelta(hours=8),
                    "content": "联储官员暗示可能暂停加息...",
                    "impact": "high",
                    "sentiment": "neutral"
                }
            ]
            
        news_items = []
            for item in mock_news[:limit]:
                news_items.append(NewsItem(
                    title=item["title"],
                    source=item["source"],
                    url=item["url"],
                    published_at=item["published_at"],
                    content=item["content"],
                    impact=item["impact"],
                    sentiment=item["sentiment"]
                ))
            
        logger.info(f"✅ Mock数据: {len(news_items)} 条新闻")
            return news_items


class OnChainDataAPI:
    """Fetch on-chain data and whale activity"""
    
    def __init__(self):
        self.whale_threshold_usd = 1_000_000  # $1M+ transactions
    
    async def detect_whale_activity(self, symbols: List[str] = None) -> List[WhaleActivity]:
        """Detect recent whale transactions"""
        try:
            if symbols is None:
                symbols = ["BTC", "ETH", "SOL"]
            
            whale_activities = []
            
            # Mock data (replace with real API like Whale Alert, Etherscan, etc.)
            mock_whales = [
                {
                    "symbol": "BTC",
                    "action": "buy",
                    "amount_usd": 15_000_000,
                    "address": "bc1q...xyz",
                    "timestamp": datetime.now() - timedelta(hours=1),
                    "exchange": "Binance"
                },
                {
                    "symbol": "ETH",
                    "action": "transfer",
                    "amount_usd": 8_000_000,
                    "address": "0x...abc",
                    "timestamp": datetime.now() - timedelta(hours=3),
                    "exchange": None
                },
                {
                    "symbol": "SOL",
                    "action": "sell",
                    "amount_usd": 2_500_000,
                    "address": "Sol...def",
                    "timestamp": datetime.now() - timedelta(hours=6),
                    "exchange": "Coinbase"
                }
            ]
            
            for whale in mock_whales:
                if whale["symbol"] in symbols:
                    whale_activities.append(WhaleActivity(
                        symbol=whale["symbol"],
                        action=whale["action"],
                        amount_usd=whale["amount_usd"],
                        address=whale["address"],
                        timestamp=whale["timestamp"],
                        exchange=whale["exchange"]
                    ))
            
            logger.info(f"🐋 检测到 {len(whale_activities)} 个巨鲸活动")
            return whale_activities
            
        except Exception as e:
            logger.error(f"❌ 检测巨鲸活动失败: {e}")
            return []
    
    async def fetch_on_chain_metrics(self) -> OnChainMetrics:
        """Fetch current on-chain metrics"""
        try:
            # Mock data (replace with real API like Glassnode, CryptoQuant)
            metrics = OnChainMetrics(
                exchange_net_flow=-50_000_000,  # Negative = outflow (bullish)
                active_addresses=1_250_000,
                gas_price=25.5,  # Gwei
                transaction_volume=5_000_000_000,  # $5B
                timestamp=datetime.now()
            )
            
            logger.info(f"📊 获取链上指标成功")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ 获取链上指标失败: {e}")
            # Return default metrics
            return OnChainMetrics(
                exchange_net_flow=0,
                active_addresses=0,
                gas_price=0,
                transaction_volume=0,
                timestamp=datetime.now()
            )


# Singleton instances
crypto_news_api = CryptoNewsAPI()
on_chain_data_api = OnChainDataAPI()

