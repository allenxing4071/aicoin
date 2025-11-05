"""交易所工厂类 - 动态创建和切换交易所适配器"""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.exchange.base_adapter import BaseExchangeAdapter
from app.services.exchange.binance_adapter import BinanceAdapter
from app.services.exchange.hyperliquid_adapter import HyperliquidAdapter
from app.models.exchange_config import ExchangeConfig
from app.core.config import settings
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class ExchangeFactory:
    """
    交易所工厂类
    
    负责:
    1. 根据配置创建交易所适配器实例
    2. 管理当前激活的交易所
    3. 支持动态切换交易所
    """
    
    _instance = None
    _current_adapter: Optional[BaseExchangeAdapter] = None
    _active_exchange_name: Optional[str] = None
    _active_market_type: Optional[str] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def get_active_exchange(cls) -> BaseExchangeAdapter:
        """
        获取当前激活的交易所适配器
        
        Returns:
            BaseExchangeAdapter: 交易所适配器实例
        """
        # 如果已经有缓存的适配器,直接返回
        if cls._current_adapter and cls._current_adapter.is_initialized:
            return cls._current_adapter
        
        # 从数据库读取配置
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ExchangeConfig).filter_by(is_active=True)
            )
            config = result.scalar_one_or_none()
            
            try:
                if not config:
                    # 没有激活的配置,使用默认(Hyperliquid)
                    logger.warning("未找到激活的交易所配置,使用默认Hyperliquid")
                    adapter = await cls._create_hyperliquid_adapter()
                elif config.name == "binance":
                    adapter = await cls._create_binance_adapter(config)
                elif config.name == "hyperliquid":
                    adapter = await cls._create_hyperliquid_adapter(config)
                else:
                    raise ValueError(f"不支持的交易所: {config.name}")
                
                # 缓存适配器
                cls._current_adapter = adapter
                cls._active_exchange_name = config.name if config else "hyperliquid"
                cls._active_market_type = config.market_type if config else "perpetual"
                
                return adapter
                
            except Exception as e:
                logger.error(f"获取交易所适配器失败: {e}", exc_info=True)
                # 降级到默认Hyperliquid
                return await cls._create_hyperliquid_adapter()
    
    @classmethod
    async def _create_binance_adapter(cls, config: Optional[ExchangeConfig] = None) -> BinanceAdapter:
        """创建币安适配器"""
        try:
            logger.info("创建币安适配器...")
            
            # 从配置或环境变量获取API密钥
            if config and config.api_key_encrypted and config.api_secret_encrypted:
                api_key = ExchangeConfig.decrypt_api_key(config.api_key_encrypted)
                api_secret = ExchangeConfig.decrypt_api_key(config.api_secret_encrypted)
                testnet = config.testnet
            else:
                api_key = settings.BINANCE_API_KEY
                api_secret = settings.BINANCE_API_SECRET
                testnet = settings.BINANCE_TESTNET
            
            if not api_key or not api_secret:
                raise ValueError("币安API密钥未配置")
            
            adapter = BinanceAdapter(
                api_key=api_key,
                api_secret=api_secret,
                testnet=testnet
            )
            
            # 初始化
            success = await adapter.initialize()
            if not success:
                raise Exception("币安适配器初始化失败")
            
            logger.info("✅ 币安适配器创建成功")
            return adapter
            
        except Exception as e:
            logger.error(f"创建币安适配器失败: {e}", exc_info=True)
            raise
    
    @classmethod
    async def _create_hyperliquid_adapter(cls, config: Optional[ExchangeConfig] = None) -> HyperliquidAdapter:
        """创建Hyperliquid适配器"""
        try:
            logger.info("创建Hyperliquid适配器...")
            
            # 从配置或环境变量获取钱包信息
            wallet_address = settings.HYPERLIQUID_WALLET_ADDRESS
            private_key = settings.HYPERLIQUID_PRIVATE_KEY
            vault_address = settings.HYPERLIQUID_VAULT_ADDRESS
            testnet = settings.HYPERLIQUID_TESTNET if hasattr(settings, 'HYPERLIQUID_TESTNET') else False
            
            if not wallet_address or not private_key:
                raise ValueError("Hyperliquid钱包凭证未配置")
            
            adapter = HyperliquidAdapter(
                wallet_address=wallet_address,
                private_key=private_key,
                vault_address=vault_address,
                testnet=testnet
            )
            
            # 初始化
            success = await adapter.initialize()
            if not success:
                raise Exception("Hyperliquid适配器初始化失败")
            
            logger.info("✅ Hyperliquid适配器创建成功")
            return adapter
            
        except Exception as e:
            logger.error(f"创建Hyperliquid适配器失败: {e}", exc_info=True)
            raise
    
    @classmethod
    async def switch_exchange(
        cls,
        exchange_name: str,
        market_type: str = 'spot',
        db: Optional[AsyncSession] = None
    ) -> bool:
        """
        切换交易所
        
        Args:
            exchange_name: 交易所名称 ('binance', 'hyperliquid')
            market_type: 市场类型 ('spot', 'futures', 'perpetual')
            db: 数据库session (可选)
            
        Returns:
            bool: 切换是否成功
        """
        try:
            logger.info(f"切换交易所: {exchange_name} ({market_type})")
            
            # 创建数据库session (如果未提供)
            use_context_manager = db is None
            
            async def update_db(session: AsyncSession):
                # 1. 更新数据库配置
                # 先将所有交易所设为非激活
                await session.execute(
                    select(ExchangeConfig).filter(ExchangeConfig.is_active == True)
                )
                all_active = await session.execute(select(ExchangeConfig))
                for config in all_active.scalars():
                    config.is_active = False
                
                # 找到目标交易所配置
                result = await session.execute(
                    select(ExchangeConfig).filter_by(name=exchange_name)
                )
                target_config = result.scalar_one_or_none()
                
                if not target_config:
                    # 如果配置不存在,创建新配置
                    target_config = ExchangeConfig(
                        name=exchange_name,
                        display_name=exchange_name.capitalize(),
                        is_active=True,
                        market_type=market_type,
                        testnet=False
                    )
                    session.add(target_config)
                else:
                    # 更新配置
                    target_config.is_active = True
                    target_config.market_type = market_type
                
                await session.commit()
                logger.info(f"数据库配置已更新: {exchange_name} ({market_type})")
            
            if use_context_manager:
                async with AsyncSessionLocal() as db:
                    await update_db(db)
            else:
                await update_db(db)
            
            # 2. 关闭当前适配器连接
            if cls._current_adapter:
                if hasattr(cls._current_adapter, 'close'):
                    await cls._current_adapter.close()
                cls._current_adapter = None
            
            # 3. 创建新适配器 (需要获取target_config)
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(ExchangeConfig).filter_by(name=exchange_name)
                )
                target_config = result.scalar_one_or_none()
                
                if exchange_name == 'binance':
                    adapter = await cls._create_binance_adapter(target_config)
                elif exchange_name == 'hyperliquid':
                    adapter = await cls._create_hyperliquid_adapter(target_config)
                else:
                    raise ValueError(f"不支持的交易所: {exchange_name}")
            
            # 4. 更新缓存
            cls._current_adapter = adapter
            cls._active_exchange_name = exchange_name
            cls._active_market_type = market_type
            
            logger.info(f"✅ 成功切换到 {exchange_name} ({market_type})")
            return True
                    
        except Exception as e:
            logger.error(f"切换交易所失败: {e}", exc_info=True)
            return False
    
    @classmethod
    def get_active_exchange_info(cls) -> dict:
        """
        获取当前激活的交易所信息
        
        Returns:
            dict: 交易所信息
        """
        return {
            'name': cls._active_exchange_name or 'unknown',
            'market_type': cls._active_market_type or 'unknown',
            'is_initialized': cls._current_adapter.is_initialized if cls._current_adapter else False
        }
    
    @classmethod
    async def reload_adapter(cls):
        """重新加载适配器"""
        logger.info("重新加载交易所适配器...")
        cls._current_adapter = None
        return await cls.get_active_exchange()
    
    @classmethod
    def list_supported_exchanges(cls) -> list:
        """列出支持的交易所"""
        return [
            {
                'name': 'binance',
                'display_name': 'Binance',
                'supports_spot': True,
                'supports_futures': True
            },
            {
                'name': 'hyperliquid',
                'display_name': 'Hyperliquid',
                'supports_spot': False,
                'supports_futures': True
            }
        ]


# 创建全局单例
exchange_factory = ExchangeFactory()

