"""Admin schemas for database viewing"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from decimal import Decimal


# ============= 通用响应模型 =============

class PaginationMeta(BaseModel):
    """分页元数据"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")


class AdminResponse(BaseModel):
    """管理后台统一响应格式"""
    success: bool = Field(True, description="请求是否成功")
    data: Any = Field(..., description="响应数据")
    meta: Optional[PaginationMeta] = Field(None, description="分页信息")
    message: Optional[str] = Field(None, description="提示信息")


# ============= 数据表模型 =============

class TableInfo(BaseModel):
    """数据表信息"""
    name: str = Field(..., description="表名")
    display_name: str = Field(..., description="显示名称")
    description: str = Field(..., description="表描述")
    record_count: Optional[int] = Field(None, description="记录数")
    endpoint: str = Field(..., description="API端点")


class TradeRecord(BaseModel):
    """交易记录"""
    id: int
    order_id: Optional[int]
    symbol: str
    side: str
    price: Decimal
    size: Decimal
    pnl: Optional[Decimal]
    fee: Optional[Decimal]
    ai_reasoning: Optional[str]
    confidence: Optional[Decimal]
    model: Optional[str]
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class OrderRecord(BaseModel):
    """订单记录"""
    id: int
    trade_id: Optional[int]
    symbol: str
    side: str
    type: str
    price: Optional[Decimal]
    size: Decimal
    filled_size: Decimal
    status: str
    exchange_order_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountSnapshotRecord(BaseModel):
    """账户快照记录"""
    id: int
    timestamp: datetime
    balance: Decimal
    equity: Decimal
    unrealized_pnl: Optional[Decimal]
    realized_pnl: Optional[Decimal]
    sharpe_ratio: Optional[Decimal]
    max_drawdown: Optional[Decimal]
    total_trades: int
    win_rate: Optional[Decimal]
    created_at: datetime

    class Config:
        from_attributes = True


class AIDecisionRecord(BaseModel):
    """AI决策记录"""
    id: int
    timestamp: datetime
    symbol: str
    market_data: Dict[str, Any]
    decision: Dict[str, Any]
    executed: bool
    reject_reason: Optional[str]
    model_name: str
    latency_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class MarketDataKlineRecord(BaseModel):
    """K线数据记录"""
    id: int
    symbol: str
    interval: str
    open_time: datetime
    close_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class RiskEventRecord(BaseModel):
    """风控事件记录"""
    id: int
    timestamp: datetime
    event_type: str
    severity: str
    description: str
    related_trade_id: Optional[int]
    action_taken: Optional[str]
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============= 统计模型 =============

class TableStats(BaseModel):
    """数据表统计"""
    table_name: str
    total_records: int
    latest_record_time: Optional[datetime]
    oldest_record_time: Optional[datetime]


class SystemStats(BaseModel):
    """系统统计概览"""
    total_trades: int = Field(..., description="总交易数")
    total_orders: int = Field(..., description="总订单数")
    total_ai_decisions: int = Field(..., description="总AI决策数")
    total_risk_events: int = Field(..., description="总风控事件数")
    latest_account_balance: Optional[Decimal] = Field(None, description="最新账户余额")
    latest_account_equity: Optional[Decimal] = Field(None, description="最新账户净值")
    database_size_mb: Optional[float] = Field(None, description="数据库大小(MB)")
    tables: List[TableStats] = Field(default_factory=list, description="各表统计")


# ============= 查询参数 =============

class QueryParams(BaseModel):
    """通用查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(50, ge=1, le=500, description="每页大小")
    sort_by: Optional[str] = Field(None, description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向: asc/desc")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")


class TradeQueryParams(QueryParams):
    """交易记录查询参数"""
    symbol: Optional[str] = Field(None, description="交易品种")
    side: Optional[str] = Field(None, description="交易方向: BUY/SELL")
    model: Optional[str] = Field(None, description="AI模型")


class OrderQueryParams(QueryParams):
    """订单记录查询参数"""
    symbol: Optional[str] = Field(None, description="交易品种")
    side: Optional[str] = Field(None, description="交易方向: BUY/SELL")
    status: Optional[str] = Field(None, description="订单状态")


class AIDecisionQueryParams(QueryParams):
    """AI决策查询参数"""
    symbol: Optional[str] = Field(None, description="交易品种")
    executed: Optional[bool] = Field(None, description="是否已执行")
    model_name: Optional[str] = Field(None, description="模型名称")


class RiskEventQueryParams(QueryParams):
    """风控事件查询参数"""
    event_type: Optional[str] = Field(None, description="事件类型")
    severity: Optional[str] = Field(None, description="严重程度")
    resolved: Optional[bool] = Field(None, description="是否已解决")


class MarketDataQueryParams(QueryParams):
    """市场数据查询参数"""
    symbol: Optional[str] = Field(None, description="交易品种")
    interval: Optional[str] = Field(None, description="K线周期")


# ============= 三层记忆系统模型 =============

class AILessonRecord(BaseModel):
    """AI经验教训记录"""
    id: int
    created_at: datetime
    updated_at: datetime
    lesson_type: str
    market_regime: Optional[str]
    symbol: Optional[str]
    action: Optional[str]
    title: str
    description: str
    confidence_score: float
    sample_count: int
    validated: bool
    validation_trades: int
    validation_success_rate: float

    class Config:
        from_attributes = True


class AIStrategyRecord(BaseModel):
    """AI策略评估记录"""
    id: int
    created_at: datetime
    updated_at: datetime
    strategy_name: str
    description: Optional[str]
    market_regime: Optional[str]
    applicable_symbols: Optional[List[str]]
    total_trades: int
    winning_trades: int
    win_rate: float
    avg_pnl: float
    sharpe_ratio: float
    max_drawdown: float
    status: str
    last_used_at: Optional[datetime]

    class Config:
        from_attributes = True


class MarketPatternRecord(BaseModel):
    """市场模式记录"""
    id: int
    detected_at: datetime
    pattern_type: str
    symbol: str
    features: Dict[str, Any]
    occurrences: int
    success_rate: Optional[float]
    avg_profit: Optional[float]
    last_seen_at: datetime

    class Config:
        from_attributes = True


class ShortTermMemoryStats(BaseModel):
    """短期记忆统计 (Redis)"""
    recent_decisions_count: int
    today_trade_count: int
    performance_7d: Dict[str, Any]
    performance_30d: Dict[str, Any]
    latest_decisions: List[Dict[str, Any]]


class LongTermMemoryStats(BaseModel):
    """长期记忆统计 (Qdrant)"""
    total_vectors: int
    collection_status: str
    index_size_mb: float
    last_updated: Optional[datetime]


class MemorySystemOverview(BaseModel):
    """三层记忆系统概览"""
    short_term_memory: ShortTermMemoryStats
    long_term_memory: LongTermMemoryStats
    knowledge_base_lessons: int
    knowledge_base_strategies: int
    knowledge_base_patterns: int

