"""Trades history API endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from datetime import datetime

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
async def get_trades(
    model: Optional[str] = Query(None, description="Filter by model name"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of trades")
):
    """
    获取交易历史（从Hyperliquid获取真实交易记录）
    
    Args:
        model: 模型名称筛选 (可选)
        symbol: 交易品种筛选 (可选)
        limit: 返回数量
        
    Returns:
        交易历史列表
    """
    try:
        client = get_hyperliquid_client()
        
        # 从Hyperliquid获取用户交易历史
        logger.info(f"Fetching trade history from Hyperliquid (limit={limit})")
        user_fills = await client.get_user_fills(limit=limit)
        
        if not user_fills:
            logger.info("No trades found")
            return {
                "success": True,
                "trades": [],
                "count": 0
            }
        
        # 转换为前端需要的格式
        trades = []
        for fill in user_fills:
            trade = {
                "id": fill.get("oid", ""),  # order id
                "model": "deepseek-chat-v3.1",  # 目前只有一个模型
                "side": fill.get("side", "").lower(),  # "buy" or "sell"
                "symbol": fill.get("coin", ""),
                "price": fill.get("px", "0"),
                "size": fill.get("sz", "0"),
                "timestamp": datetime.fromtimestamp(fill.get("time", 0) / 1000).isoformat() if fill.get("time") else datetime.now().isoformat(),
                "fee": fill.get("fee", "0"),
                "closed_pnl": fill.get("closedPnl", "0"),
            }
            
            # 如果有symbol筛选，只返回匹配的
            if symbol and trade["symbol"].upper() != symbol.upper():
                continue
                
            trades.append(trade)
        
        logger.info(f"✅ Found {len(trades)} trades")
        
        return {
            "success": True,
            "trades": trades[:limit],  # 确保不超过limit
            "count": len(trades[:limit])
        }
        
    except Exception as e:
        logger.error(f"Error fetching trade history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_trade_stats(
    model: Optional[str] = Query(None, description="Filter by model name"),
    days: int = Query(30, ge=1, le=365, description="Time period in days")
):
    """
    获取交易统计
    
    Args:
        model: 模型名称筛选 (可选)
        days: 统计天数
        
    Returns:
        交易统计数据
    """
    try:
        client = get_hyperliquid_client()
        
        # 从Hyperliquid获取用户交易历史
        user_fills = await client.get_user_fills(limit=500)
        
        if not user_fills:
            return {
                "success": True,
                "stats": {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0.0,
                    "total_pnl": 0.0,
                    "avg_pnl_per_trade": 0.0,
                }
            }
        
        # 统计交易数据
        total_trades = len(user_fills)
        winning_trades = sum(1 for fill in user_fills if float(fill.get("closedPnl", 0)) > 0)
        losing_trades = sum(1 for fill in user_fills if float(fill.get("closedPnl", 0)) < 0)
        total_pnl = sum(float(fill.get("closedPnl", 0)) for fill in user_fills)
        
        stats = {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": (winning_trades / total_trades * 100) if total_trades > 0 else 0.0,
            "total_pnl": total_pnl,
            "avg_pnl_per_trade": (total_pnl / total_trades) if total_trades > 0 else 0.0,
        }
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error fetching trade stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

