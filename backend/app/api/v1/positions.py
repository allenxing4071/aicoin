"""Positions API endpoints"""

from fastapi import APIRouter, HTTPException
from typing import List
import logging

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


@router.get("")
async def get_positions():
    """
    获取当前持仓（从Hyperliquid获取真实持仓）
    
    Returns:
        持仓列表
    """
    try:
        client = get_hyperliquid_client()
        
        # 从Hyperliquid获取持仓
        logger.info("Fetching positions from Hyperliquid")
        positions_data = await client.get_positions()
        
        if not positions_data:
            logger.info("No positions found")
            return {
                "success": True,
                "positions": [],
                "count": 0
            }
        
        # 转换为前端需要的格式
        positions = []
        for pos in positions_data:
            try:
                szi = float(pos.get("szi", 0))
                position = {
                    "coin": pos.get("coin", ""),
                    "side": "long" if szi > 0 else "short",
                    "size": abs(szi),
                    "entry_price": float(pos.get("entryPx", 0)),
                    "current_price": float(pos.get("markPx", 0)),
                    "unrealized_pnl": float(pos.get("unrealizedPnl", 0)),
                    "realized_pnl": float(pos.get("realizedPnl", 0)),
                    "leverage": float(pos.get("leverage", {}).get("value", 1)) if isinstance(pos.get("leverage"), dict) else 1.0,
                    "liquidation_price": float(pos.get("liquidationPx", 0)) if pos.get("liquidationPx") else None,
                    "margin_used": float(pos.get("marginUsed", 0)),
                }
                positions.append(position)
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid position data: {e}")
                continue
        
        logger.info(f"✅ Found {len(positions)} positions")
        
        return {
            "success": True,
            "positions": positions,
            "count": len(positions)
        }
        
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

