"""Trading API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from decimal import Decimal
import logging

from app.core.database import get_db
from app.models.trade import Trade
from app.schemas.trade import TradeResponse, TradeList
from app.schemas.decision import AIDecisionRequest, AIDecisionResponse
from app.services.ai.decision_engine import decision_engine
from app.services.trading.risk_manager import risk_manager
from app.services.trading.trade_executor import trade_executor
from app.services.market.hyperliquid_client import hyperliquid_client
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/decision", response_model=AIDecisionResponse)
async def trigger_ai_decision(
    request: AIDecisionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    触发AI交易决策
    
    Args:
        request: 决策请求参数
        db: 数据库会话
        
    Returns:
        AI决策结果
    """
    try:
        logger.info(f"Triggering AI decision for {request.symbol}")
        
        # 检查交易是否启用
        if not settings.TRADING_ENABLED and not request.force:
            raise HTTPException(
                status_code=403,
                detail="Trading is disabled. Set TRADING_ENABLED=true or use force=true"
            )
        
        # 获取市场数据
        klines = await hyperliquid_client.get_klines(request.symbol, interval="1h", limit=24)
        orderbook = await hyperliquid_client.get_orderbook(request.symbol, depth=20)
        ticker = await hyperliquid_client.get_ticker(request.symbol)
        
        current_price = Decimal(ticker['price'])
        
        market_data = {
            'current_price': current_price,
            'klines': klines,
            'orderbook': orderbook,
            'ticker': ticker
        }
        
        # 获取账户信息
        account_balance_data = await hyperliquid_client.get_account_balance()
        positions = await hyperliquid_client.get_positions()
        
        account_info = {
            'balance': Decimal(account_balance_data['balance']),
            'position': positions[0] if positions else {}
        }
        
        # AI决策
        decision, latency_ms = await decision_engine.make_decision(
            symbol=request.symbol,
            market_data=market_data,
            account_info=account_info
        )
        
        # 风控验证
        is_valid, reject_reason = await risk_manager.validate_decision(
            decision=decision,
            account_balance=account_info['balance'],
            current_price=current_price,
            position_size=Decimal(str(positions[0].get('size', 0))) if positions else Decimal(0),
            db=db
        )
        
        executed = False
        
        # 如果通过风控，执行交易
        if is_valid and (settings.TRADING_ENABLED or request.force):
            execution_result = await trade_executor.execute_decision(
                decision=decision,
                symbol=request.symbol,
                current_price=current_price,
                db=db
            )
            executed = execution_result['success']
        elif not is_valid:
            logger.warning(f"Decision rejected by risk manager: {reject_reason}")
        
        # 返回响应
        return AIDecisionResponse(
            symbol=request.symbol,
            decision=decision,
            executed=executed,
            reject_reason=reject_reason,
            latency_ms=latency_ms,
            model_name="deepseek"
        )
        
    except Exception as e:
        logger.error(f"Error in AI decision endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades", response_model=TradeList)
async def get_trades(
    symbol: str = None,
    model: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    获取交易记录
    
    Args:
        symbol: 交易品种 (可选)
        model: AI模型名称 (可选, deepseek-chat-v3.1 或 qwen3-max)
        limit: 返回数量 (默认100)
        offset: 偏移量
        db: 数据库会话
        
    Returns:
        交易记录列表
    """
    try:
        # 构建查询
        query = select(Trade)
        
        if symbol:
            query = query.where(Trade.symbol == symbol)
        
        if model:
            query = query.where(Trade.model == model)
        
        query = query.order_by(Trade.timestamp.desc()).limit(limit).offset(offset)
        
        # 执行查询
        result = await db.execute(query)
        trades = result.scalars().all()
        
        # 计算总数
        count_query = select(func.count(Trade.id))
        if symbol:
            count_query = count_query.where(Trade.symbol == symbol)
        if model:
            count_query = count_query.where(Trade.model == model)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        return TradeList(
            trades=[TradeResponse.from_orm(t) for t in trades],
            total=total,
            page=offset // limit + 1,
            page_size=limit
        )
        
    except Exception as e:
        logger.error(f"Error fetching trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个交易详情
    
    Args:
        trade_id: 交易ID
        db: 数据库会话
        
    Returns:
        交易详情
    """
    try:
        result = await db.execute(
            select(Trade).where(Trade.id == trade_id)
        )
        trade = result.scalar_one_or_none()
        
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        return TradeResponse.from_orm(trade)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_positions(
    model: str = None
):
    """
    获取当前持仓
    
    Args:
        model: AI模型名称 (可选, deepseek-chat-v3.1 或 qwen3-max)
        
    Returns:
        当前持仓列表
    """
    try:
        from app.api import trading as hyperliquid_trading
        
        trading_service = hyperliquid_trading.get_trading_service()
        
        # 从Hyperliquid获取真实持仓
        positions = await trading_service.get_positions()
        
        # 格式化返回数据
        formatted_positions = []
        for pos in positions:
            formatted_positions.append({
                "symbol": pos.get("symbol", ""),
                "side": pos.get("side", ""),
                "size": pos.get("size", 0),
                "entry_price": pos.get("entry_price", 0),
                "unrealized_pnl": pos.get("unrealized_pnl", 0),
                "leverage": pos.get("leverage", 1),
                "liquidation_price": pos.get("liquidation_price"),
                # 注意：Hyperliquid的持仓是所有AI共享的，无法按model区分
                # 前端可以显示为"共享持仓"
                "model": "shared"  # 所有AI共享同一个钱包
            })
        
        return {
            "success": True,
            "positions": formatted_positions,
            "total": len(formatted_positions)
        }
        
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

