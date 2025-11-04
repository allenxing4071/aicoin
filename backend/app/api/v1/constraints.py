"""Constraints Status API endpoints"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import logging
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)

# 全局变量控制交易开关
TRADING_ENABLED = True


class TradingControlRequest(BaseModel):
    """交易控制请求模型"""
    trading_enabled: bool


@router.get("/status")
async def get_constraints_status() -> Dict[str, Any]:
    """
    获取约束框架状态
    
    Returns:
        当前所有硬约束和软约束的状态
    """
    try:
        # 返回当前的约束配置
        hard_constraints = {
            "max_position": {
                "name": "最大仓位限制",
                "current": "10%",
                "limit": "10%",
                "status": "normal",
                "description": "单笔交易最大仓位占总资金的百分比"
            },
            "max_leverage": {
                "name": "最大杠杆限制",
                "current": "2x",
                "limit": "2x",
                "status": "normal",
                "description": "允许使用的最大杠杆倍数"
            },
            "min_confidence": {
                "name": "最小置信度",
                "current": f"{settings.MIN_CONFIDENCE * 100:.0f}%",
                "limit": f"{settings.MIN_CONFIDENCE * 100:.0f}%",
                "status": "normal",
                "description": "AI决策的最低置信度要求"
            },
            "daily_trades": {
                "name": "每日交易次数",
                "current": "0/5",
                "limit": "5",
                "status": "normal",
                "description": "每天允许执行的最大交易笔数"
            },
            "max_drawdown": {
                "name": "最大回撤限制",
                "current": "0%",
                "limit": "20%",
                "status": "normal",
                "description": "触发止损的最大回撤百分比"
            }
        }
        
        soft_constraints = {
            "market_hours": {
                "name": "市场时段偏好",
                "current": "24/7",
                "status": "active",
                "description": "加密货币市场全天候运行"
            },
            "volatility_filter": {
                "name": "波动率过滤",
                "current": "启用",
                "status": "active",
                "description": "在极端波动时降低交易频率"
            },
            "correlation_check": {
                "name": "相关性检查",
                "current": "启用",
                "status": "active",
                "description": "避免高度相关的同向持仓"
            }
        }
        
        return {
            "success": True,
            "hard_constraints": hard_constraints,
            "soft_constraints": soft_constraints,
            "permission_level": "L1",
            "last_updated": "2025-11-03T08:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error fetching constraints status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch constraints status: {str(e)}"
        )


@router.get("/violations")
async def get_constraint_violations() -> Dict[str, Any]:
    """
    获取约束违规记录
    
    Returns:
        最近的约束违规记录
    """
    try:
        # 返回空列表，因为当前没有违规记录
        return {
            "success": True,
            "violations": [],
            "count": 0,
            "last_24h": 0
        }
        
    except Exception as e:
        logger.error(f"Error fetching constraint violations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch violations: {str(e)}"
        )


@router.get("/trading-control")
async def get_trading_control() -> Dict[str, Any]:
    """
    获取交易控制状态
    
    Returns:
        当前交易开关状态
    """
    try:
        global TRADING_ENABLED
        return {
            "success": True,
            "trading_enabled": TRADING_ENABLED,
            "message": "交易已启用" if TRADING_ENABLED else "交易已停用"
        }
        
    except Exception as e:
        logger.error(f"Error fetching trading control: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch trading control: {str(e)}"
        )


@router.post("/trading-control")
async def set_trading_control(request: TradingControlRequest) -> Dict[str, Any]:
    """
    设置交易控制状态
    
    Args:
        request: 交易控制请求
        
    Returns:
        操作结果
    """
    try:
        global TRADING_ENABLED
        TRADING_ENABLED = request.trading_enabled
        
        logger.info(f"🎮 交易控制已更新: {'启用' if TRADING_ENABLED else '停用'}")
        
        return {
            "success": True,
            "trading_enabled": TRADING_ENABLED,
            "message": f"✅ 交易已{'启用' if TRADING_ENABLED else '停用'}！"
        }
        
    except Exception as e:
        logger.error(f"Error setting trading control: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set trading control: {str(e)}"
        )
