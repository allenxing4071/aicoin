"""Account API endpoints"""

from fastapi import APIRouter, HTTPException
import logging

from app.schemas.account import AccountInfo, PositionInfo
from app.services.market.hyperliquid_client import hyperliquid_client

router = APIRouter()
logger = logging.getLogger(__name__)


def get_hyperliquid_client():
    """获取Hyperliquid client实例（优先使用全局缓存的）"""
    from app.main_v2 import hyperliquid_client_global, trading_service_global
    if hyperliquid_client_global is not None:
        return hyperliquid_client_global
    # Fallback: 创建临时实例
    logger.warning("⚠️ Global client not available, creating temporary instance (slow!)")
    from app.services.market.hyperliquid_client import HyperliquidClient
    return HyperliquidClient(trading_service=trading_service_global)


@router.get("/info", response_model=AccountInfo)
async def get_account_info():
    """
    获取账户信息
    
    Returns:
        账户信息(余额、持仓等)
    """
    try:
        client = get_hyperliquid_client()
        
        # 获取账户余额
        balance_data = await client.get_account_balance()
        
        # 获取持仓
        positions_data = await client.get_positions()
        
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

