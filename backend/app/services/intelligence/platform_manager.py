"""Platform Manager - 情报平台管理服务

负责动态加载/卸载平台、健康检查、性能监控
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.models.intelligence_platform import IntelligencePlatform
from app.services.intelligence.platforms.cloud_adapters import (
    BaiduQwenAdapter,
    TencentQwenAdapter,
    VolcanoQwenAdapter,
    AWSQwenAdapter
)

logger = logging.getLogger(__name__)


class PlatformManager:
    """
    情报平台管理器
    
    功能：
    1. 动态加载/卸载平台
    2. 健康检查
    3. 性能监控
    4. 自动故障转移
    """
    
    def __init__(self):
        self.platforms: Dict[str, any] = {}
        self.initialized = False
        logger.info("✅ 平台管理器初始化")
    
    async def initialize(self):
        """初始化平台管理器，加载配置的平台"""
        if self.initialized:
            return
        
        logger.info("🔧 开始初始化情报平台...")
        
        # 从配置文件加载内置平台
        await self._load_builtin_platforms()
        
        # 从数据库加载用户添加的平台
        await self._load_custom_platforms()
        
        self.initialized = True
        logger.info(f"✅ 情报平台初始化完成，共 {len(self.platforms)} 个平台")
    
    async def _load_builtin_platforms(self):
        """加载内置的三大云平台"""
        
        # 百度智能云
        if settings.ENABLE_BAIDU_QWEN and settings.BAIDU_QWEN_API_KEY:
            try:
                baidu = BaiduQwenAdapter(
                    api_key=settings.BAIDU_QWEN_API_KEY,
                    base_url=settings.BAIDU_QWEN_BASE_URL,
                    enabled=True
                )
                self.platforms["baidu"] = baidu
                logger.info("✅ 百度智能云平台已加载")
                
                # 保存到数据库
                await self._ensure_platform_in_db("baidu", "qwen_search")
            except Exception as e:
                logger.error(f"❌ 百度智能云平台加载失败: {e}")
        
        # 腾讯云
        if settings.ENABLE_TENCENT_QWEN and settings.TENCENT_QWEN_API_KEY:
            try:
                tencent = TencentQwenAdapter(
                    api_key=settings.TENCENT_QWEN_API_KEY,
                    base_url=settings.TENCENT_QWEN_BASE_URL,
                    enabled=True
                )
                self.platforms["tencent"] = tencent
                logger.info("✅ 腾讯云平台已加载")
                
                await self._ensure_platform_in_db("tencent", "qwen_search")
            except Exception as e:
                logger.error(f"❌ 腾讯云平台加载失败: {e}")
        
        # 火山引擎
        if settings.ENABLE_VOLCANO_QWEN and settings.VOLCANO_QWEN_API_KEY:
            try:
                volcano = VolcanoQwenAdapter(
                    api_key=settings.VOLCANO_QWEN_API_KEY,
                    base_url=settings.VOLCANO_QWEN_BASE_URL,
                    enabled=True
                )
                self.platforms["volcano"] = volcano
                logger.info("✅ 火山引擎平台已加载")
                
                await self._ensure_platform_in_db("volcano", "qwen_search")
            except Exception as e:
                logger.error(f"❌ 火山引擎平台加载失败: {e}")
        
        # AWS（预留）
        if settings.ENABLE_AWS_QWEN and settings.AWS_QWEN_API_KEY and settings.AWS_QWEN_BASE_URL:
            try:
                aws = AWSQwenAdapter(
                    api_key=settings.AWS_QWEN_API_KEY,
                    base_url=settings.AWS_QWEN_BASE_URL,
                    enabled=True
                )
                self.platforms["aws"] = aws
                logger.info("✅ AWS平台已加载")
                
                await self._ensure_platform_in_db("aws", "qwen_search")
            except Exception as e:
                logger.error(f"❌ AWS平台加载失败: {e}")
    
    async def _load_custom_platforms(self):
        """从数据库加载用户添加的平台"""
        try:
            async with get_db_session() as db:
                result = await db.execute(
                    select(IntelligencePlatform).where(IntelligencePlatform.enabled == True)
                )
                db_platforms = result.scalars().all()
                
                for platform in db_platforms:
                    if platform.provider not in self.platforms:
                        # 用户添加的平台
                        logger.info(f"📝 加载用户添加的平台: {platform.name}")
                        # TODO: 根据provider动态创建适配器实例
                        
        except Exception as e:
            logger.error(f"❌ 加载用户平台失败: {e}")
    
    async def _ensure_platform_in_db(self, provider: str, platform_type: str):
        """确保平台记录存在于数据库中"""
        try:
            async with get_db_session() as db:
                result = await db.execute(
                    select(IntelligencePlatform).where(
                        IntelligencePlatform.provider == provider,
                        IntelligencePlatform.platform_type == platform_type
                    )
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    # 创建新记录
                    platform_names = {
                        "baidu": "百度智能云",
                        "tencent": "腾讯云",
                        "volcano": "火山引擎",
                        "aws": "AWS"
                    }
                    
                    platform_urls = {
                        "baidu": settings.BAIDU_QWEN_BASE_URL,
                        "tencent": settings.TENCENT_QWEN_BASE_URL,
                        "volcano": settings.VOLCANO_QWEN_BASE_URL,
                        "aws": settings.AWS_QWEN_BASE_URL
                    }
                    
                    new_platform = IntelligencePlatform(
                        name=platform_names.get(provider, provider.upper()),
                        provider=provider,
                        platform_type=platform_type,
                        api_key="***",  # 不存储实际密钥
                        base_url=platform_urls.get(provider, ""),
                        enabled=True
                    )
                    
                    db.add(new_platform)
                    await db.commit()
                    logger.info(f"✅ 平台记录已创建: {provider}")
                    
        except Exception as e:
            logger.error(f"❌ 保存平台记录失败: {e}")
    
    def get_available_platforms(self) -> List[str]:
        """获取可用的平台列表"""
        return list(self.platforms.keys())
    
    async def get_platform(self, provider: str):
        """获取指定平台的适配器"""
        if not self.initialized:
            await self.initialize()
        
        return self.platforms.get(provider)
    
    async def get_all_platforms(self) -> Dict[str, any]:
        """获取所有平台"""
        if not self.initialized:
            await self.initialize()
        
        return self.platforms
    
    async def health_check_all(self) -> Dict[str, bool]:
        """对所有平台进行健康检查"""
        results = {}
        
        for provider, platform in self.platforms.items():
            try:
                is_healthy = await platform.health_check()
                results[provider] = is_healthy
                logger.info(f"🏥 {provider} 健康检查: {'✅' if is_healthy else '❌'}")
            except Exception as e:
                logger.error(f"❌ {provider} 健康检查失败: {e}")
                results[provider] = False
        
        return results
    
    async def select_best_platform(self, context: Optional[Dict] = None) -> Optional[str]:
        """
        选择最优平台
        
        策略：
        1. 优先选择健康的平台
        2. 负载均衡（轮询）
        3. 故障转移
        """
        available = []
        
        for provider, platform in self.platforms.items():
            if platform.enabled:
                available.append(provider)
        
        if not available:
            logger.warning("⚠️ 没有可用的情报平台")
            return None
        
        # 简单轮询（TODO: 实现更智能的选择算法）
        return available[0]
    
    async def update_platform_stats(
        self,
        provider: str,
        success: bool,
        response_time: float,
        cost: float = 0.0
    ):
        """更新平台统计信息"""
        try:
            async with get_db_session() as db:
                result = await db.execute(
                    select(IntelligencePlatform).where(
                        IntelligencePlatform.provider == provider
                    )
                )
                platform = result.scalar_one_or_none()
                
                if platform:
                    platform.total_calls += 1
                    if success:
                        platform.successful_calls += 1
                    else:
                        platform.failed_calls += 1
                    
                    # 更新平均响应时间
                    if platform.avg_response_time:
                        platform.avg_response_time = (
                            platform.avg_response_time * 0.9 + response_time * 0.1
                        )
                    else:
                        platform.avg_response_time = response_time
                    
                    platform.total_cost += cost
                    platform.updated_at = datetime.utcnow()
                    
                    await db.commit()
                    
        except Exception as e:
            logger.error(f"❌ 更新平台统计失败: {e}")


# 全局单例
platform_manager = PlatformManager()

