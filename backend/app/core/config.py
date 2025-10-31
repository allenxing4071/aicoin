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
    TRADING_ENABLED: bool = False
    DECISION_INTERVAL: int = 300  # 5 minutes (300秒)
    
    # Permission System (L0-L5)
    INITIAL_PERMISSION_LEVEL: str = "L1"  # 初始权限等级
    ENABLE_AUTO_UPGRADE: bool = True      # 是否启用自动升级
    ENABLE_AUTO_DOWNGRADE: bool = True    # 是否启用自动降级
    
    # Risk Management (Hard Constraints)
    MIN_MARGIN_RATIO: float = 0.20           # 最低保证金率20%
    FORCED_LIQUIDATION_THRESHOLD: float = 0.15  # 15%强制平仓
    MAX_TOTAL_DRAWDOWN: float = 0.10         # 总账户最大回撤10%
    MAX_SINGLE_TRADE_LOSS: float = 0.03      # 单笔最大亏损3%
    MAX_DAILY_LOSS_PCT: float = 0.05         # 单日最大亏损5%
    ABSOLUTE_MAX_LEVERAGE: int = 5           # 绝对最大杠杆5x
    MIN_CASH_RESERVE: float = 0.10           # 至少保留10%现金
    MAX_SINGLE_ASSET_EXPOSURE: float = 0.30  # 单一资产最大30%
    
    # Legacy (保留兼容性)
    MAX_POSITION_PCT: float = 0.20
    MAX_DRAWDOWN_PCT: float = 0.10
    MAX_CONSECUTIVE_LOSSES: int = 3
    
    # LLM Settings
    LLM_MODEL: str = "deepseek-chat"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 500
    LLM_TIMEOUT: int = 10  # seconds
    
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

