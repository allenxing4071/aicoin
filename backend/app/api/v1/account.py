"""Account API endpoints"""

from fastapi import APIRouter, HTTPException
import logging

from app.schemas.account import AccountInfo, PositionInfo
from app.services.market.hyperliquid_client import hyperliquid_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/info", response_model=AccountInfo)
async def get_account_info():
    """
    获取账户信息
    
    Returns:
        账户信息(余额、持仓等)
    """
    try:
        # 获取账户余额
        balance_data = await hyperliquid_client.get_account_balance()
        
        # 获取持仓
        positions_data = await hyperliquid_client.get_positions()
        
        positions = [PositionInfo(**p) for p in positions_data] if positions_data else []
        
        return AccountInfo(
            balance=balance_data['balance'],
            equity=balance_data['equity'],
            unrealized_pnl=balance_data.get('unrealized_pnl', '0'),
            realized_pnl=balance_data.get('realized_pnl', '0'),
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
        positions_data = await hyperliquid_client.get_positions()
        return [PositionInfo(**p) for p in positions_data] if positions_data else []
        
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

