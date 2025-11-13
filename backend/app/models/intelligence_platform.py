"""Intelligence Platform Model - 情报平台配置"""

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.core.database import Base


class IntelligencePlatform(Base):
    """情报平台配置模型"""
    __tablename__ = "intelligence_platforms"
    __table_args__ = {
        'comment': '☁️ ️ 情报平台配置 - 管理AI云平台（Qwen、腾讯混元、火山引擎等）的连接配置和性能指标'
    }
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 平台名称
    provider = Column(String, nullable=False, index=True)  # baidu/tencent/volcano/aws
    platform_type = Column(String, nullable=False)  # qwen_search/qwen_deep/free
    
    api_key = Column(String, nullable=True)  # API密钥
    base_url = Column(String, nullable=False)  # API基础URL
    enabled = Column(Boolean, nullable=False, default=True, index=True)  # 是否启用
    config_json = Column(JSONB, nullable=True)  # 额外配置
    
    # 性能指标
    total_calls = Column(Integer, nullable=False, default=0)
    successful_calls = Column(Integer, nullable=False, default=0)
    failed_calls = Column(Integer, nullable=False, default=0)
    avg_response_time = Column(Float, nullable=True)  # 平均响应时间（秒）
    total_cost = Column(Float, nullable=False, default=0.0)  # 累计成本
    
    # 健康状态
    last_health_check = Column(DateTime, nullable=True)
    health_status = Column(String, nullable=True)  # healthy/unhealthy/unknown
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "platform_type": self.platform_type,
            "base_url": self.base_url,
            "enabled": self.enabled,
            "config_json": self.config_json,
            "performance": {
                "total_calls": self.total_calls,
                "successful_calls": self.successful_calls,
                "failed_calls": self.failed_calls,
                "success_rate": self.successful_calls / self.total_calls if self.total_calls > 0 else 0,
                "avg_response_time": self.avg_response_time,
                "total_cost": self.total_cost
            },
            "health": {
                "last_check": self.last_health_check.isoformat() if self.last_health_check else None,
                "status": self.health_status
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

