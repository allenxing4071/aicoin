"""Admin API endpoints for database viewing"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, text
from typing import Optional, List
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.trade import Trade
from app.models.order import Order
from app.models.account import AccountSnapshot
from app.models.ai_decision import AIDecision
from app.models.market_data import MarketDataKline
from app.models.risk_event import RiskEvent
from app.models.memory import AILesson, AIStrategy, MarketPattern
from app.schemas.admin import (
    AdminResponse,
    PaginationMeta,
    TableInfo,
    TradeRecord,
    OrderRecord,
    AccountSnapshotRecord,
    AIDecisionRecord,
    MarketDataKlineRecord,
    RiskEventRecord,
    SystemStats,
    TableStats,
    AILessonRecord,
    AIStrategyRecord,
    MarketPatternRecord,
    ShortTermMemoryStats,
    LongTermMemoryStats,
    MemorySystemOverview,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ============= 辅助函数 =============

def calculate_pagination(total: int, page: int, page_size: int) -> PaginationMeta:
    """计算分页元数据"""
    total_pages = (total + page_size - 1) // page_size
    return PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


async def get_table_count(db: AsyncSession, model) -> int:
    """获取表记录数"""
    try:
        result = await db.execute(select(func.count()).select_from(model))
        return result.scalar() or 0
    except Exception as e:
        logger.error(f"Error counting records for {model.__tablename__}: {e}")
        return 0


# ============= API端点 =============

@router.get("/tables", response_model=AdminResponse)
async def list_tables(db: AsyncSession = Depends(get_db)):
    """
    列出所有可查看的数据表
    
    返回系统中所有数据表的基本信息,包括表名、描述和记录数
    """
    try:
        tables = [
            TableInfo(
                name="trades",
                display_name="交易记录",
                description="所有已执行的交易记录,包含价格、数量、PnL等信息",
                record_count=await get_table_count(db, Trade),
                endpoint="/api/v1/admin/trades"
            ),
            TableInfo(
                name="orders",
                display_name="订单记录",
                description="所有订单记录,包含订单状态、类型等信息",
                record_count=await get_table_count(db, Order),
                endpoint="/api/v1/admin/orders"
            ),
            TableInfo(
                name="account_snapshots",
                display_name="账户快照",
                description="账户状态快照,包含余额、净值、绩效指标等",
                record_count=await get_table_count(db, AccountSnapshot),
                endpoint="/api/v1/admin/accounts"
            ),
            TableInfo(
                name="ai_decisions",
                display_name="AI决策日志",
                description="AI决策记录,包含市场数据、决策结果、执行状态等",
                record_count=await get_table_count(db, AIDecision),
                endpoint="/api/v1/admin/ai-decisions"
            ),
            TableInfo(
                name="market_data_kline",
                display_name="K线数据",
                description="市场K线数据,包含OHLCV等信息",
                record_count=await get_table_count(db, MarketDataKline),
                endpoint="/api/v1/admin/market-data"
            ),
            TableInfo(
                name="risk_events",
                display_name="风控事件",
                description="风控事件记录,包含事件类型、严重程度、处理措施等",
                record_count=await get_table_count(db, RiskEvent),
                endpoint="/api/v1/admin/risk-events"
            ),
            TableInfo(
                name="ai_lessons",
                display_name="AI经验教训 (L3知识库)",
                description="从历史交易中提取的经验教训,包含成功案例和失败教训",
                record_count=await get_table_count(db, AILesson),
                endpoint="/api/v1/admin/memory/lessons"
            ),
            TableInfo(
                name="ai_strategies",
                display_name="AI策略评估 (L3知识库)",
                description="AI交易策略的性能评估,包含胜率、夏普比率等指标",
                record_count=await get_table_count(db, AIStrategy),
                endpoint="/api/v1/admin/memory/strategies"
            ),
            TableInfo(
                name="market_patterns",
                display_name="市场模式 (L3知识库)",
                description="识别的市场模式,包含趋势反转、突破、盘整等模式",
                record_count=await get_table_count(db, MarketPattern),
                endpoint="/api/v1/admin/memory/patterns"
            ),
        ]
        
        return AdminResponse(
            success=True,
            data=tables,
            message="成功获取数据表列表"
        )
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=AdminResponse)
async def get_system_stats(db: AsyncSession = Depends(get_db)):
    """
    获取系统统计概览
    
    返回系统整体统计信息,包括各表记录数、最新账户状态等
    """
    try:
        # 获取各表统计
        total_trades = await get_table_count(db, Trade)
        total_orders = await get_table_count(db, Order)
        total_ai_decisions = await get_table_count(db, AIDecision)
        total_risk_events = await get_table_count(db, RiskEvent)
        
        # 获取最新账户快照
        latest_account = None
        latest_balance = None
        latest_equity = None
        
        result = await db.execute(
            select(AccountSnapshot)
            .order_by(desc(AccountSnapshot.timestamp))
            .limit(1)
        )
        latest_account = result.scalar_one_or_none()
        
        if latest_account:
            latest_balance = latest_account.balance
            latest_equity = latest_account.equity
        
        # 获取各表详细统计
        table_stats = []
        
        for model, name in [
            (Trade, "trades"),
            (Order, "orders"),
            (AccountSnapshot, "account_snapshots"),
            (AIDecision, "ai_decisions"),
            (MarketDataKline, "market_data_kline"),
            (RiskEvent, "risk_events"),
        ]:
            count = await get_table_count(db, model)
            
            # 获取最新和最早记录时间
            latest_time = None
            oldest_time = None
            
            if count > 0:
                # 尝试获取timestamp字段
                time_field = None
                if hasattr(model, 'timestamp'):
                    time_field = model.timestamp
                elif hasattr(model, 'created_at'):
                    time_field = model.created_at
                
                if time_field is not None:
                    result = await db.execute(
                        select(func.max(time_field), func.min(time_field))
                    )
                    latest_time, oldest_time = result.one()
            
            table_stats.append(TableStats(
                table_name=name,
                total_records=count,
                latest_record_time=latest_time,
                oldest_record_time=oldest_time
            ))
        
        stats = SystemStats(
            total_trades=total_trades,
            total_orders=total_orders,
            total_ai_decisions=total_ai_decisions,
            total_risk_events=total_risk_events,
            latest_account_balance=latest_balance,
            latest_account_equity=latest_equity,
            tables=table_stats
        )
        
        return AdminResponse(
            success=True,
            data=stats,
            message="成功获取系统统计"
        )
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades", response_model=AdminResponse)
async def get_trades(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=500, description="每页大小"),
    symbol: Optional[str] = Query(None, description="交易品种筛选"),
    side: Optional[str] = Query(None, description="交易方向筛选 (BUY/SELL)"),
    model: Optional[str] = Query(None, description="AI模型筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    sort_by: str = Query("timestamp", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 (asc/desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    查看交易记录
    
    支持分页、筛选、排序功能
    """
    try:
        # 构建查询
        query = select(Trade)
        
        # 添加筛选条件
        if symbol:
            query = query.where(Trade.symbol == symbol)
        if side:
            query = query.where(Trade.side == side.upper())
        if model:
            query = query.where(Trade.model == model)
        if start_time:
            query = query.where(Trade.timestamp >= start_time)
        if end_time:
            query = query.where(Trade.timestamp <= end_time)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 添加排序
        sort_field = getattr(Trade, sort_by, Trade.timestamp)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        trades = result.scalars().all()
        
        # 转换为响应模型
        trade_records = [TradeRecord.model_validate(trade) for trade in trades]
        
        return AdminResponse(
            success=True,
            data=trade_records,
            meta=calculate_pagination(total, page, page_size),
            message=f"成功获取 {len(trade_records)} 条交易记录"
        )
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=AdminResponse)
async def get_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=500, description="每页大小"),
    symbol: Optional[str] = Query(None, description="交易品种筛选"),
    side: Optional[str] = Query(None, description="交易方向筛选 (BUY/SELL)"),
    status: Optional[str] = Query(None, description="订单状态筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 (asc/desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    查看订单记录
    
    支持分页、筛选、排序功能
    """
    try:
        # 构建查询
        query = select(Order)
        
        # 添加筛选条件
        if symbol:
            query = query.where(Order.symbol == symbol)
        if side:
            query = query.where(Order.side == side.upper())
        if status:
            query = query.where(Order.status == status.upper())
        if start_time:
            query = query.where(Order.created_at >= start_time)
        if end_time:
            query = query.where(Order.created_at <= end_time)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 添加排序
        sort_field = getattr(Order, sort_by, Order.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        orders = result.scalars().all()
        
        # 转换为响应模型
        order_records = [OrderRecord.model_validate(order) for order in orders]
        
        return AdminResponse(
            success=True,
            data=order_records,
            meta=calculate_pagination(total, page, page_size),
            message=f"成功获取 {len(order_records)} 条订单记录"
        )
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts", response_model=AdminResponse)
async def get_account_snapshots(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=500, description="每页大小"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    sort_by: str = Query("timestamp", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 (asc/desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    查看账户快照
    
    支持分页、时间范围筛选、排序功能
    """
    try:
        # 构建查询
        query = select(AccountSnapshot)
        
        # 添加筛选条件
        if start_time:
            query = query.where(AccountSnapshot.timestamp >= start_time)
        if end_time:
            query = query.where(AccountSnapshot.timestamp <= end_time)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 添加排序
        sort_field = getattr(AccountSnapshot, sort_by, AccountSnapshot.timestamp)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        snapshots = result.scalars().all()
        
        # 转换为响应模型
        snapshot_records = [AccountSnapshotRecord.model_validate(s) for s in snapshots]
        
        return AdminResponse(
            success=True,
            data=snapshot_records,
            meta=calculate_pagination(total, page, page_size),
            message=f"成功获取 {len(snapshot_records)} 条账户快照"
        )
    except Exception as e:
        logger.error(f"Error getting account snapshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-decisions", response_model=AdminResponse)
async def get_ai_decisions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=500, description="每页大小"),
    symbol: Optional[str] = Query(None, description="交易品种筛选"),
    executed: Optional[bool] = Query(None, description="是否已执行"),
    model_name: Optional[str] = Query(None, description="模型名称筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    sort_by: str = Query("timestamp", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 (asc/desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    查看AI决策日志
    
    支持分页、筛选、排序功能
    """
    try:
        # 构建查询
        query = select(AIDecision)
        
        # 添加筛选条件
        if symbol:
            query = query.where(AIDecision.symbol == symbol)
        if executed is not None:
            query = query.where(AIDecision.executed == executed)
        if model_name:
            query = query.where(AIDecision.model_name == model_name)
        if start_time:
            query = query.where(AIDecision.timestamp >= start_time)
        if end_time:
            query = query.where(AIDecision.timestamp <= end_time)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 添加排序
        sort_field = getattr(AIDecision, sort_by, AIDecision.timestamp)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        decisions = result.scalars().all()
        
        # 转换为响应模型
        decision_records = [AIDecisionRecord.model_validate(d) for d in decisions]
        
        return AdminResponse(
            success=True,
            data=decision_records,
            meta=calculate_pagination(total, page, page_size),
            message=f"成功获取 {len(decision_records)} 条AI决策记录"
        )
    except Exception as e:
        logger.error(f"Error getting AI decisions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-data", response_model=AdminResponse)
async def get_market_data(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=500, description="每页大小"),
    symbol: Optional[str] = Query(None, description="交易品种筛选"),
    interval: Optional[str] = Query(None, description="K线周期筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    sort_by: str = Query("open_time", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 (asc/desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    查看K线数据
    
    支持分页、筛选、排序功能
    """
    try:
        # 构建查询
        query = select(MarketDataKline)
        
        # 添加筛选条件
        if symbol:
            query = query.where(MarketDataKline.symbol == symbol)
        if interval:
            query = query.where(MarketDataKline.interval == interval)
        if start_time:
            query = query.where(MarketDataKline.open_time >= start_time)
        if end_time:
            query = query.where(MarketDataKline.open_time <= end_time)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 添加排序
        sort_field = getattr(MarketDataKline, sort_by, MarketDataKline.open_time)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        klines = result.scalars().all()
        
        # 转换为响应模型
        kline_records = [MarketDataKlineRecord.model_validate(k) for k in klines]
        
        return AdminResponse(
            success=True,
            data=kline_records,
            meta=calculate_pagination(total, page, page_size),
            message=f"成功获取 {len(kline_records)} 条K线数据"
        )
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-events", response_model=AdminResponse)
async def get_risk_events(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=500, description="每页大小"),
    event_type: Optional[str] = Query(None, description="事件类型筛选"),
    severity: Optional[str] = Query(None, description="严重程度筛选"),
    resolved: Optional[bool] = Query(None, description="是否已解决"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    sort_by: str = Query("timestamp", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 (asc/desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    查看风控事件
    
    支持分页、筛选、排序功能
    """
    try:
        # 构建查询
        query = select(RiskEvent)
        
        # 添加筛选条件
        if event_type:
            query = query.where(RiskEvent.event_type == event_type)
        if severity:
            query = query.where(RiskEvent.severity == severity.upper())
        if resolved is not None:
            query = query.where(RiskEvent.resolved == resolved)
        if start_time:
            query = query.where(RiskEvent.timestamp >= start_time)
        if end_time:
            query = query.where(RiskEvent.timestamp <= end_time)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 添加排序
        sort_field = getattr(RiskEvent, sort_by, RiskEvent.timestamp)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        events = result.scalars().all()
        
        # 转换为响应模型
        event_records = [RiskEventRecord.model_validate(e) for e in events]
        
        return AdminResponse(
            success=True,
            data=event_records,
            meta=calculate_pagination(total, page, page_size),
            message=f"成功获取 {len(event_records)} 条风控事件"
        )
    except Exception as e:
        logger.error(f"Error getting risk events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= 三层记忆系统接口 =============

@router.get("/memory/overview", response_model=AdminResponse)
async def get_memory_system_overview(db: AsyncSession = Depends(get_db)):
    """
    获取三层记忆系统概览
    
    返回短期记忆(Redis)、长期记忆(Qdrant)、知识库(PostgreSQL)的统计信息
    """
    try:
        # 短期记忆统计 (Redis) - 模拟数据
        short_term_stats = ShortTermMemoryStats(
            recent_decisions_count=0,
            today_trade_count=0,
            performance_7d={},
            performance_30d={},
            latest_decisions=[]
        )
        
        # 长期记忆统计 (Qdrant) - 模拟数据
        long_term_stats = LongTermMemoryStats(
            total_vectors=0,
            collection_status="not_initialized",
            index_size_mb=0.0,
            last_updated=None
        )
        
        # 知识库统计 (PostgreSQL)
        lessons_count = await get_table_count(db, AILesson)
        strategies_count = await get_table_count(db, AIStrategy)
        patterns_count = await get_table_count(db, MarketPattern)
        
        overview = MemorySystemOverview(
            short_term_memory=short_term_stats,
            long_term_memory=long_term_stats,
            knowledge_base_lessons=lessons_count,
            knowledge_base_strategies=strategies_count,
            knowledge_base_patterns=patterns_count
        )
        
        return AdminResponse(
            success=True,
            data=overview,
            message="成功获取记忆系统概览"
        )
    except Exception as e:
        logger.error(f"Error getting memory overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/lessons", response_model=AdminResponse)
async def get_ai_lessons(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=500, description="每页大小"),
    lesson_type: Optional[str] = Query(None, description="教训类型 (success/failure/insight)"),
    market_regime: Optional[str] = Query(None, description="市场状态"),
    validated: Optional[bool] = Query(None, description="是否已验证"),
    sort_by: str = Query("confidence_score", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 (asc/desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    查看AI经验教训 (知识库 L3)
    
    支持分页、筛选、排序功能
    """
    try:
        # 构建查询
        query = select(AILesson)
        
        # 添加筛选条件
        if lesson_type:
            query = query.where(AILesson.lesson_type == lesson_type)
        if market_regime:
            query = query.where(AILesson.market_regime == market_regime)
        if validated is not None:
            query = query.where(AILesson.validated == validated)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 添加排序
        sort_field = getattr(AILesson, sort_by, AILesson.confidence_score)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        lessons = result.scalars().all()
        
        # 转换为响应模型
        lesson_records = [AILessonRecord.model_validate(lesson) for lesson in lessons]
        
        return AdminResponse(
            success=True,
            data=lesson_records,
            meta=calculate_pagination(total, page, page_size),
            message=f"成功获取 {len(lesson_records)} 条AI经验教训"
        )
    except Exception as e:
        logger.error(f"Error getting AI lessons: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/strategies", response_model=AdminResponse)
async def get_ai_strategies(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=500, description="每页大小"),
    status: Optional[str] = Query(None, description="策略状态 (active/deprecated/testing)"),
    market_regime: Optional[str] = Query(None, description="市场状态"),
    sort_by: str = Query("win_rate", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 (asc/desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    查看AI策略评估 (知识库 L3)
    
    支持分页、筛选、排序功能
    """
    try:
        # 构建查询
        query = select(AIStrategy)
        
        # 添加筛选条件
        if status:
            query = query.where(AIStrategy.status == status)
        if market_regime:
            query = query.where(AIStrategy.market_regime == market_regime)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 添加排序
        sort_field = getattr(AIStrategy, sort_by, AIStrategy.win_rate)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        strategies = result.scalars().all()
        
        # 转换为响应模型
        strategy_records = [AIStrategyRecord.model_validate(strategy) for strategy in strategies]
        
        return AdminResponse(
            success=True,
            data=strategy_records,
            meta=calculate_pagination(total, page, page_size),
            message=f"成功获取 {len(strategy_records)} 条AI策略"
        )
    except Exception as e:
        logger.error(f"Error getting AI strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/patterns", response_model=AdminResponse)
async def get_market_patterns(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=500, description="每页大小"),
    pattern_type: Optional[str] = Query(None, description="模式类型"),
    symbol: Optional[str] = Query(None, description="交易品种"),
    sort_by: str = Query("last_seen_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 (asc/desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    查看市场模式 (知识库 L3)
    
    支持分页、筛选、排序功能
    """
    try:
        # 构建查询
        query = select(MarketPattern)
        
        # 添加筛选条件
        if pattern_type:
            query = query.where(MarketPattern.pattern_type == pattern_type)
        if symbol:
            query = query.where(MarketPattern.symbol == symbol)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 添加排序
        sort_field = getattr(MarketPattern, sort_by, MarketPattern.last_seen_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        patterns = result.scalars().all()
        
        # 转换为响应模型
        pattern_records = [MarketPatternRecord.model_validate(pattern) for pattern in patterns]
        
        return AdminResponse(
            success=True,
            data=pattern_records,
            meta=calculate_pagination(total, page, page_size),
            message=f"成功获取 {len(pattern_records)} 条市场模式"
        )
    except Exception as e:
        logger.error(f"Error getting market patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

