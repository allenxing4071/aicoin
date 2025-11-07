"""Exchange configuration model"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class ExchangeConfig(Base):
    """交易所配置表"""
    
    __tablename__ = "exchange_configs"
    __table_args__ = {
        'comment': '🏦 交易所配置 - 存储币安等交易所的API密钥和连接配置'
    }
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    display_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=False)
    market_type = Column(String(20), default='spot')  # spot, futures, perpetual
    api_key_encrypted = Column(Text, nullable=True)
    api_secret_encrypted = Column(Text, nullable=True)
    testnet = Column(Boolean, default=False)
    config_json = Column(JSONB, nullable=True)  # 额外配置
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ExchangeConfig(name={self.name}, active={self.is_active}, market_type={self.market_type})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "market_type": self.market_type,
            "testnet": self.testnet,
            "config": self.config_json or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @staticmethod
    def encrypt_api_key(api_key: str) -> str:
        """加密API密钥 (简单实现,生产环境应使用Fernet)"""
        # TODO: 实现真正的加密
        return api_key
    
    @staticmethod
    def decrypt_api_key(encrypted_key: str) -> str:
        """解密API密钥"""
        # TODO: 实现真正的解密
        return encrypted_key

