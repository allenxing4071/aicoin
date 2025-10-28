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
    DECISION_INTERVAL: int = 300  # 5 minutes
    
    # Risk Management
    MAX_POSITION_PCT: float = 0.20  # 20% max per position
    MAX_DAILY_LOSS_PCT: float = 0.05  # 5% daily loss limit
    MAX_DRAWDOWN_PCT: float = 0.10  # 10% max drawdown
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


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings

