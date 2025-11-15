"""Intelligence Coordinator - 统一情报协调器

整合所有情报功能：
1. 协调多平台情报收集（MultiPlatformCoordinator）
2. 管理四层存储流转（L1-L4）
3. 提供统一的情报接口
4. 支持配置化开关
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.utils.timezone import get_beijing_time
from .models import IntelligenceReport, SentimentType, NewsItem, WhaleActivity, OnChainMetrics
from .qwen_engine import QwenIntelligenceEngine
from .multi_platform_coordinator import MultiPlatformCoordinator
from .storage_layers import (
    ShortTermIntelligenceCache,
    MidTermIntelligenceAnalyzer,
    LongTermIntelligenceStore,
    IntelligenceVectorKB
)
from .platforms import (
    FreePlatformAdapter,
    QwenSearchAdapter,
    QwenDeepAdapter
)
from .data_sources import crypto_news_api, on_chain_data_api

logger = logging.getLogger(__name__)


class IntelligenceCoordinator:
    """
    统一情报协调器 - 整合所有情报功能
    
    职责：
    1. 协调多平台情报收集（MultiPlatformCoordinator）
    2. 管理四层存储流转（L1-L4）
    3. 提供统一的情报接口
    4. 支持配置化开关
    """
    
    def __init__(self, redis_client, db_session):
        """
        初始化统一情报协调器
        
        Args:
            redis_client: Redis客户端
            db_session: 数据库会话
        """
        self.redis_client = redis_client
        self.db_session = db_session
        
        # 配置开关
        self.use_multi_platform = getattr(settings, 'INTELLIGENCE_USE_MULTI_PLATFORM', True)
        self.use_storage_layers = getattr(settings, 'INTELLIGENCE_USE_STORAGE_LAYERS', True)
        
        # 异步任务追踪
        self._storage_tasks: list = []
        self._task_lock = asyncio.Lock()
        
        # 初始化四层存储
        try:
            self.l1_cache = ShortTermIntelligenceCache(redis_client)
            self.l2_analyzer = MidTermIntelligenceAnalyzer(redis_client, db_session)
            self.l3_store = LongTermIntelligenceStore(db_session)
            self.l4_vector = IntelligenceVectorKB(
                qdrant_host=getattr(settings, 'QDRANT_HOST', 'localhost'),
                qdrant_port=getattr(settings, 'QDRANT_PORT', 6333),
                collection_name="intelligence_knowledge",
                embedding_provider="qwen"
            )
            logger.info("✅ 四层存储架构初始化成功")
        except Exception as e:
            logger.error(f"⚠️ 四层存储初始化失败: {e}，将禁用存储层功能")
            self.use_storage_layers = False
            self.l1_cache = None
            self.l2_analyzer = None
            self.l3_store = None
            self.l4_vector = None
        
        # 初始化多平台协调器
        try:
            self.multi_platform = MultiPlatformCoordinator(
                free_platform=FreePlatformAdapter(),
                search_platform=QwenSearchAdapter(),
                deep_platform=QwenDeepAdapter()
            )
            logger.info("✅ 多平台协调器初始化成功")
        except Exception as e:
            logger.error(f"⚠️ 多平台协调器初始化失败: {e}，将使用fallback引擎")
            self.use_multi_platform = False
            self.multi_platform = None
        
        # 保留旧版引擎作为fallback
        self.fallback_engine = QwenIntelligenceEngine()
        
        logger.info(f"✅ IntelligenceCoordinator初始化完成 (多平台={self.use_multi_platform}, 存储层={self.use_storage_layers})")
    
    async def collect_intelligence(self) -> IntelligenceReport:
        """
        统一的情报收集入口
        
        Returns:
            IntelligenceReport: 情报报告
        """
        start_time = time.time()
        
        try:
            logger.info("🕵️‍♀️ 开始情报收集...")
            
            # 选择情报收集策略
            if self.use_multi_platform and self.multi_platform:
                logger.info("📊 使用多平台协调策略")
                report = await self._collect_with_multi_platform()
            else:
                logger.info("📊 使用fallback引擎")
                report = await self.fallback_engine.collect_intelligence()
            
            # 记录性能指标
            duration = time.time() - start_time
            logger.info(f"✅ 情报收集完成，耗时: {duration:.2f}秒")
            
            # 存储到四层架构（异步，带追踪和错误处理）
            if self.use_storage_layers and report:
                task = asyncio.create_task(self._store_to_layers_with_tracking(report))
                async with self._task_lock:
                    self._storage_tasks.append(task)
                    # 清理已完成的任务
                    self._storage_tasks = [t for t in self._storage_tasks if not t.done()]
            
            return report
            
        except Exception as e:
            logger.error(f"❌ 情报收集失败: {e}，使用fallback引擎", exc_info=True)
            try:
                return await self.fallback_engine.collect_intelligence()
            except Exception as fallback_error:
                logger.error(f"❌ Fallback引擎也失败: {fallback_error}")
                return self._create_emergency_report()
    
    async def _collect_with_multi_platform(self) -> IntelligenceReport:
        """
        使用多平台协调器收集情报
        
        Returns:
            IntelligenceReport: 增强的情报报告
        """
        try:
            # 准备数据源
            logger.info("📡 收集原始数据源...")
            news_items = await crypto_news_api.fetch_latest_news(limit=10)
            whale_signals = await on_chain_data_api.detect_whale_activity()
            on_chain_metrics = await on_chain_data_api.fetch_on_chain_metrics()
            
            data_sources = {
                "news": news_items,
                "whale": whale_signals,
                "onchain": on_chain_metrics
            }
            
            logger.info(f"✅ 数据源收集完成: {len(news_items)}条新闻, {len(whale_signals)}个巨鲸信号")
            
            # 多平台协调分析
            logger.info("🔄 启动多平台协调分析...")
            result = await self.multi_platform.coordinate_analysis(
                data_sources=data_sources,
                query_context={"require_realtime": True}
            )
            
            # 转换为IntelligenceReport格式
            report = self._convert_to_report(result, news_items, whale_signals, on_chain_metrics)
            
            logger.info(f"✅ 多平台协调完成: 情绪={report.market_sentiment.value}, 置信度={report.confidence:.2f}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ 多平台协调失败: {e}", exc_info=True)
            raise
    
    def _convert_to_report(
        self,
        multi_platform_result: Dict[str, Any],
        news_items: list,
        whale_signals: list,
        on_chain_metrics: Any
    ) -> IntelligenceReport:
        """
        将多平台协调结果转换为IntelligenceReport格式
        
        Args:
            multi_platform_result: 多平台协调结果
            news_items: 新闻列表
            whale_signals: 巨鲸信号列表
            on_chain_metrics: 链上指标
        
        Returns:
            IntelligenceReport: 增强的情报报告
        """
        # 解析市场情绪
        sentiment_str = multi_platform_result.get("market_sentiment", "neutral").upper()
        try:
            sentiment = SentimentType[sentiment_str]
        except KeyError:
            sentiment = SentimentType.NEUTRAL
        
        # 创建报告
        report = IntelligenceReport(
            timestamp=get_beijing_time(),
            market_sentiment=sentiment,
            sentiment_score=multi_platform_result.get("sentiment_score", 0.0),
            key_news=news_items[:5],
            whale_signals=whale_signals,
            on_chain_metrics=on_chain_metrics,
            risk_factors=multi_platform_result.get("risk_factors", []),
            opportunities=multi_platform_result.get("opportunities", []),
            qwen_analysis=multi_platform_result.get("analysis", ""),
            confidence=multi_platform_result.get("confidence", 0.7)
        )
        
        # 添加多平台验证信息（扩展属性）
        report.platform_contributions = multi_platform_result.get("platform_contributions", {})
        report.platform_consensus = multi_platform_result.get("coordination_metadata", {}).get("platform_consensus", 0.0)
        report.verification_metadata = multi_platform_result.get("coordination_metadata", {})
        report.summary = multi_platform_result.get("analysis", "")[:500]
        
        return report
    
    async def _store_to_layers(self, report: IntelligenceReport):
        """
        存储到四层架构（异步执行）
        
        Args:
            report: 情报报告
        """
        try:
            report_id = f"intel_{report.timestamp.strftime('%Y%m%d_%H%M%S')}"
            report_data = self._report_to_dict(report)
            
            # L1: 短期缓存（立即执行）
            if self.l1_cache:
                await self.l1_cache.store_report(report_id, report_data)
                logger.info(f"✅ L1缓存完成: {report_id}")
            
            # L2: 触发中期分析（异步，不阻塞）
            if self.l2_analyzer:
                asyncio.create_task(self._trigger_l2_analysis())
            
            # L3: 长期存储（异步）
            if self.l3_store:
                asyncio.create_task(self._store_to_l3(report))
            
            # L4: 向量化（异步）
            if self.l4_vector:
                asyncio.create_task(self._vectorize_to_l4(report, report_id))
            
        except Exception as e:
            logger.error(f"❌ 存储到四层架构失败: {e}", exc_info=True)
    
    async def _store_to_layers_with_tracking(self, report: IntelligenceReport):
        """
        存储到四层架构（带错误追踪和重试）
        
        Args:
            report: 情报报告
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                await self._store_to_layers(report)
                logger.info(f"✅ 四层存储成功")
                return
            except Exception as e:
                retry_count += 1
                logger.error(f"❌ 四层存储失败 (尝试 {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    await asyncio.sleep(2 ** retry_count)  # 指数退避
                else:
                    logger.error(f"❌ 四层存储最终失败，已重试{max_retries}次")
    
    async def wait_for_storage_tasks(self, timeout: float = 30.0):
        """
        等待所有存储任务完成
        
        Args:
            timeout: 超时时间（秒）
        """
        if not self._storage_tasks:
            return
        
        try:
            async with self._task_lock:
                tasks = [t for t in self._storage_tasks if not t.done()]
            
            if tasks:
                logger.info(f"⏳ 等待 {len(tasks)} 个存储任务完成...")
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=timeout
                )
                logger.info(f"✅ 所有存储任务已完成")
        except asyncio.TimeoutError:
            logger.warning(f"⚠️ 存储任务等待超时 ({timeout}秒)")
        except Exception as e:
            logger.error(f"❌ 等待存储任务失败: {e}")

    async def _trigger_l2_analysis(self):
        """触发L2中期分析"""
        try:
            logger.info("🔍 开始L2中期分析...")
            
            # 分析用户行为
            behavior = await self.l2_analyzer.analyze_user_behavior(time_window_hours=24)
            
            # 计算信息源权重
            weights = await self.l2_analyzer.calculate_source_weights()
            
            # 识别高价值模式
            patterns = await self.l2_analyzer.identify_high_value_patterns()
            
            # 准备向量化候选
            candidates = await self.l2_analyzer.prepare_vectorization_candidates(
                min_interaction_threshold=3
            )
            
            logger.info(f"✅ L2分析完成: {len(weights)}个源, {len(patterns)}个模式, {len(candidates)}个候选")
            
        except Exception as e:
            logger.error(f"❌ L2分析失败: {e}", exc_info=True)
    
    async def _store_to_l3(self, report: IntelligenceReport):
        """存储到L3长期存储"""
        try:
            # 存储信息源权重（如果有）
            if hasattr(report, 'platform_contributions'):
                for platform, contribution in report.platform_contributions.items():
                    await self.l3_store.store_source_weight(
                        source_name=platform,
                        source_type="platform",
                        weight=contribution.get('confidence', 0.5),
                        metrics={
                            'usage_count': 1,
                            'positive_feedback': 0,
                            'effectiveness': contribution.get('confidence', 0.5)
                        }
                    )
            
            logger.info("✅ L3存储完成")
            
        except Exception as e:
            logger.error(f"❌ L3存储失败: {e}", exc_info=True)
    
    async def _vectorize_to_l4(self, report: IntelligenceReport, report_id: str):
        """向量化到L4知识库"""
        try:
            # 构建向量化内容
            content = f"{report.qwen_analysis}\n\n"
            content += f"市场情绪: {report.market_sentiment.value}\n"
            content += f"风险因素: {', '.join(report.risk_factors[:3])}\n"
            content += f"机会点: {', '.join(report.opportunities[:2])}"
            
            # 构建元数据
            metadata = {
                "source": "multi_platform",
                "category": "market_intelligence",
                "sentiment": report.market_sentiment.value,
                "importance": report.confidence,
                "timestamp": report.timestamp
            }
            
            # 向量化
            await self.l4_vector.vectorize_intelligence(
                intelligence_id=report_id,
                content=content,
                metadata=metadata
            )
            
            logger.info("✅ L4向量化完成")
            
        except Exception as e:
            logger.error(f"❌ L4向量化失败: {e}", exc_info=True)
    
    def _report_to_dict(self, report: IntelligenceReport) -> Dict[str, Any]:
        """将IntelligenceReport转换为字典"""
        data = {
            "timestamp": report.timestamp.isoformat(),
            "market_sentiment": report.market_sentiment.value,
            "sentiment_score": report.sentiment_score,
            "confidence": report.confidence,
            "qwen_analysis": report.qwen_analysis,
            "risk_factors": report.risk_factors,
            "opportunities": report.opportunities,
            "key_news": [
                {
                    "title": news.title,
                    "source": news.source,
                    "url": news.url,
                    "published_at": news.published_at.isoformat() if hasattr(news.published_at, 'isoformat') else str(news.published_at),
                    "impact": news.impact,
                    "sentiment": news.sentiment
                }
                for news in report.key_news
            ] if report.key_news else [],
            "whale_signals": [
                {
                    "symbol": whale.symbol,
                    "action": whale.action,
                    "amount_usd": whale.amount_usd,
                    "timestamp": whale.timestamp.isoformat() if hasattr(whale.timestamp, 'isoformat') else str(whale.timestamp)
                }
                for whale in report.whale_signals
            ] if report.whale_signals else []
        }
        
        # 添加扩展属性
        if hasattr(report, 'platform_contributions'):
            data['platform_contributions'] = report.platform_contributions
        if hasattr(report, 'platform_consensus'):
            data['platform_consensus'] = report.platform_consensus
        if hasattr(report, 'verification_metadata'):
            data['verification_metadata'] = report.verification_metadata
        if hasattr(report, 'summary'):
            data['summary'] = report.summary
        
        return data
    
    def _create_emergency_report(self) -> IntelligenceReport:
        """创建紧急fallback报告（当所有方法都失败时）"""
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
    
    async def get_latest_intelligence(self) -> Optional[IntelligenceReport]:
        """
        从L1缓存获取最新情报（快速访问）
        
        Returns:
            Optional[IntelligenceReport]: 最新情报报告
        """
        try:
            if self.use_storage_layers and self.l1_cache:
                cached_data = await self.l1_cache.get_latest_report()
                if cached_data:
                    return self._dict_to_report(cached_data)
            
            # Fallback: 从旧存储获取
            from .storage import intelligence_storage
            return await intelligence_storage.get_latest_report()
            
        except Exception as e:
            logger.warning(f"⚠️ 获取最新情报失败: {e}")
            return None
    
    def _dict_to_report(self, data: Dict[str, Any]) -> IntelligenceReport:
        """将字典转换为IntelligenceReport"""
        # 解析时间戳
        timestamp_str = data.get("timestamp")
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = get_beijing_time()
        
        # 解析市场情绪
        sentiment_str = data.get("market_sentiment", "NEUTRAL")
        try:
            sentiment = SentimentType[sentiment_str]
        except KeyError:
            sentiment = SentimentType.NEUTRAL
        
        # 创建报告
        report = IntelligenceReport(
            timestamp=timestamp,
            market_sentiment=sentiment,
            sentiment_score=data.get("sentiment_score", 0.0),
            key_news=[],  # 简化处理
            whale_signals=[],  # 简化处理
            on_chain_metrics=OnChainMetrics(
                exchange_net_flow=0,
                active_addresses=0,
                gas_price=0,
                transaction_volume=0,
                timestamp=timestamp
            ),
            risk_factors=data.get("risk_factors", []),
            opportunities=data.get("opportunities", []),
            qwen_analysis=data.get("qwen_analysis", ""),
            confidence=data.get("confidence", 0.7)
        )
        
        # 添加扩展属性
        if 'platform_contributions' in data:
            report.platform_contributions = data['platform_contributions']
        if 'platform_consensus' in data:
            report.platform_consensus = data['platform_consensus']
        if 'verification_metadata' in data:
            report.verification_metadata = data['verification_metadata']
        if 'summary' in data:
            report.summary = data['summary']
        
        return report

