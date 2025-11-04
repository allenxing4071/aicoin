"""Account API endpoints"""

from fastapi import APIRouter, HTTPException
import logging

from app.schemas.account import AccountInfo, PositionInfo
from app.services.market.hyperliquid_client import hyperliquid_client

router = APIRouter()
logger = logging.getLogger(__name__)


def get_trading_service():
    """获取全局的trading service"""
    from app.main import trading_service
    if trading_service is None:
        logger.error("❌ Trading service not initialized!")
        raise HTTPException(status_code=503, detail="Trading service not available")
    return trading_service


@router.get("/info", response_model=AccountInfo)
async def get_account_info():
    """
    获取账户信息
    
    Returns:
        账户信息(余额、持仓等)
    """
    try:
        service = get_trading_service()
        
        # 获取账户状态
        account_state = await service.get_account_state()
        
        # 正确解析Hyperliquid返回的数据结构
        margin_summary = account_state.get('marginSummary', {})
        balance = str(margin_summary.get('accountValue', '0'))
        equity = str(margin_summary.get('accountValue', '0'))
        unrealized_pnl = str(margin_summary.get('totalNtlPos', '0'))
        
        # 解析持仓
        asset_positions = account_state.get('assetPositions', [])
        positions = [PositionInfo(**p) for p in asset_positions] if asset_positions else []
        
        return AccountInfo(
            balance=balance,
            equity=equity,
            unrealized_pnl=unrealized_pnl,
            realized_pnl='0',
            positions=positions
        )
        
    except Exception as e:
        logger.error(f"Error fetching account info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions", response_model=list[PositionInfo])
async def get_positions():
    """
    获取持仓列表
    
    Returns:
        持仓列表
    """
    try:
        client = get_hyperliquid_client()
        positions_data = await client.get_positions()
        return [PositionInfo(**p) for p in positions_data] if positions_data else []
        
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/value")
async def get_account_value():
    """
    获取账户价值
    
    Returns:
        账户价值信息
    """
    try:
        client = get_hyperliquid_client()
        balance_data = await client.get_account_balance()
        
        return {
            "success": True,
            "total_value": float(balance_data.get('equity', '0')),
            "cash": float(balance_data.get('balance', '0')),
            "unrealized_pnl": float(balance_data.get('unrealized_pnl', '0'))
        }
        
    except Exception as e:
        logger.error(f"Error fetching account value: {e}")
        raise HTTPException(status_code=500, detail=str(e))

