"""Debate system Pydantic schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DebateConfigBase(BaseModel):
    """辩论配置基础模型"""
    config_key: str = Field(..., description="配置键")
    config_value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置说明")


class DebateConfigCreate(DebateConfigBase):
    """创建辩论配置"""
    pass


class DebateConfigUpdate(BaseModel):
    """更新辩论配置"""
    config_value: str = Field(..., description="配置值")


class DebateConfigResponse(DebateConfigBase):
    """辩论配置响应"""
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DebateHistoryBase(BaseModel):
    """辩论历史基础模型"""
    decision_id: str = Field(..., description="关联的决策ID")
    symbol: str = Field(..., description="交易标的")
    debate_rounds: int = Field(1, description="辩论轮次")


class DebateHistoryCreate(DebateHistoryBase):
    """创建辩论历史"""
    bull_arguments: Optional[str] = Field(None, description="多头论点")
    bear_arguments: Optional[str] = Field(None, description="空头论点")
    debate_full_history: Optional[str] = Field(None, description="完整辩论历史")
    final_recommendation: Optional[str] = Field(None, description="最终推荐")
    confidence: Optional[float] = Field(None, description="置信度")
    consensus_level: Optional[float] = Field(None, description="共识度")
    debate_duration_seconds: Optional[int] = Field(None, description="辩论耗时")


class DebateHistoryResponse(DebateHistoryBase):
    """辩论历史响应"""
    id: int
    bull_arguments: Optional[str]
    bear_arguments: Optional[str]
    debate_full_history: Optional[str]
    final_recommendation: Optional[str]
    confidence: Optional[float]
    consensus_level: Optional[float]
    debate_duration_seconds: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DebateHistoryListResponse(BaseModel):
    """辩论历史列表响应"""
    total: int
    items: List[DebateHistoryResponse]


class DebateStatisticsBase(BaseModel):
    """辩论统计基础模型"""
    date: datetime = Field(..., description="统计日期")
    total_debates: int = Field(0, description="总辩论次数")
    bull_wins: int = Field(0, description="多头胜利次数")
    bear_wins: int = Field(0, description="空头胜利次数")
    holds: int = Field(0, description="持有次数")
    avg_consensus: Optional[float] = Field(None, description="平均共识度")
    avg_confidence: Optional[float] = Field(None, description="平均置信度")
    avg_duration: Optional[float] = Field(None, description="平均辩论时长")


class DebateStatisticsResponse(DebateStatisticsBase):
    """辩论统计响应"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DebateTriggerRequest(BaseModel):
    """手动触发辩论请求"""
    symbol: str = Field(..., description="交易标的")
    market_data: dict = Field(..., description="市场数据")
    intelligence_report: Optional[dict] = Field(None, description="情报报告")


class DebateTriggerResponse(BaseModel):
    """手动触发辩论响应"""
    success: bool
    debate_id: Optional[int] = None
    debate_result: Optional[dict] = None
    error: Optional[str] = None


class DebateMemoryStats(BaseModel):
    """辩论记忆统计"""
    bull_memory_count: int = Field(0, description="多头记忆数量")
    bear_memory_count: int = Field(0, description="空头记忆数量")
    manager_memory_count: int = Field(0, description="经理记忆数量")
    total_memory_count: int = Field(0, description="总记忆数量")

