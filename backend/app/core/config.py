"""Application configuration"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AIcoin Trading System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://admin:changeme123@localhost:5432/aicoin"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Qdrant (Vector Database)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "trading_memories"
    
    # LLM API Keys
    DEEPSEEK_API_KEY: Optional[str] = None
    QWEN_API_KEY: Optional[str] = None
    GROK_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Hyperliquid
    HYPERLIQUID_WALLET_ADDRESS: Optional[str] = None
    HYPERLIQUID_PRIVATE_KEY: Optional[str] = None
    HYPERLIQUID_VAULT_ADDRESS: Optional[str] = None  # 主钱包地址(资金来源)
    HYPERLIQUID_TESTNET: bool = False
    HYPERLIQUID_API_URL: str = "https://api.hyperliquid-testnet.xyz"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Trading Configuration
    DEFAULT_SYMBOL: str = "BTC-PERP"
    TRADING_ENABLED: bool = True  # 启用交易
    DECISION_INTERVAL: int = 60  # 1 minute (60秒) - 激进模式快速交易
    
    # Supported Trading Symbols (可交易币种池 - DeepSeek自主选择)
    TRADING_SYMBOLS: list = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB"]  # 6个币种池
    
    # Permission System (L0-L5)
    INITIAL_PERMISSION_LEVEL: str = "L1"  # 初始权限等级
    ENABLE_AUTO_UPGRADE: bool = True      # 是否启用自动升级
    ENABLE_AUTO_DOWNGRADE: bool = True    # 是否启用自动降级
    
    # Risk Management (Hard Constraints) - 主网$200资金配置
    MIN_MARGIN_RATIO: float = 0.20           # 最低保证金率20%
    FORCED_LIQUIDATION_THRESHOLD: float = 0.15  # 15%强制平仓
    MAX_TOTAL_DRAWDOWN: float = 0.15         # 总账户最大回撤15%（$30）
    MAX_SINGLE_TRADE_LOSS: float = 0.05      # 单笔最大亏损5%（$10）
    MAX_DAILY_LOSS_PCT: float = 0.05         # 单日最大亏损5%（$10）
    ABSOLUTE_MAX_LEVERAGE: int = 2           # 绝对最大杠杆2x（保守）
    MIN_CASH_RESERVE: float = 0.10           # 至少保留10%现金
    MAX_SINGLE_ASSET_EXPOSURE: float = 0.10  # 单一资产最大10%（$20）
    
    # 主网专用风控参数
    MAX_SINGLE_POSITION: float = 0.10        # 单仓位最多10%
    MAX_TOTAL_POSITION: float = 0.30         # 总持仓最多30%
    MAX_LEVERAGE: int = 2                    # 最大杠杆2x
    MAX_DAILY_LOSS: float = 0.05            # 单日最大亏损5%
    MAX_DRAWDOWN: float = 0.15              # 最大回撤15%
    MIN_ACCOUNT_VALUE: float = 150.0        # 最低账户价值$150
    
    # 交易频率限制（激进模式 - 快速积累经验）
    MAX_DAILY_TRADES: int = 10              # 每天最多10笔 - 提升至L2/L3需要更多交易
    MIN_TRADE_INTERVAL: int = 60            # 最少间隔1分钟 - 加快交易频率
    
    # 止损止盈
    STOP_LOSS_PERCENTAGE: float = 0.05      # 止损5%
    TAKE_PROFIT_PERCENTAGE: float = 0.10    # 止盈10%
    
    # 最小置信度（激进模式 - 快速交易）
    MIN_CONFIDENCE: float = 0.50            # 降低到50%以增加交易机会
    
    # 告警阈值
    ALERT_MIN_ACCOUNT_VALUE: float = 180.0  # 低于$180告警
    ALERT_DAILY_LOSS: float = 0.05         # 单日亏损5%告警
    ALERT_DRAWDOWN: float = 0.10           # 回撤10%告警
    
    # Legacy (保留兼容性)
    MAX_POSITION_PCT: float = 0.20
    MAX_DRAWDOWN_PCT: float = 0.10
    MAX_CONSECUTIVE_LOSSES: int = 3
    
    # LLM Settings
    LLM_MODEL: str = "deepseek-chat"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 500
    LLM_TIMEOUT: int = 10  # seconds
    
    # Qwen Intelligence Officer Settings
    QWEN_MODEL: str = "qwen-plus"
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    INTELLIGENCE_UPDATE_INTERVAL: int = 1800  # 30 minutes
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # 允许额外字段（向后兼容）


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings

