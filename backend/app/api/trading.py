"""交易API端点"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app.core.config import settings
from app.core.redis_client import redis_client
from app.services.hyperliquid_trading import HyperliquidTradingService
from app.services.ai_trading_orchestrator import AITradingOrchestrator
from app.services.hyperliquid_market_data import HyperliquidMarketData

router = APIRouter()

# 全局服务实例
trading_service: Optional[HyperliquidTradingService] = None
ai_orchestrator: Optional[AITradingOrchestrator] = None
market_data_service: Optional[HyperliquidMarketData] = None


def get_trading_service() -> HyperliquidTradingService:
    """获取交易服务实例"""
    global trading_service
    if trading_service is None:
        trading_service = HyperliquidTradingService(redis_client, testnet=True)
    return trading_service


def get_ai_orchestrator() -> AITradingOrchestrator:
    """获取AI编排器实例"""
    global ai_orchestrator, trading_service, market_data_service
    if ai_orchestrator is None:
        if trading_service is None:
            trading_service = HyperliquidTradingService(redis_client, testnet=True)
        if market_data_service is None:
            market_data_service = HyperliquidMarketData(redis_client, testnet=True)
        ai_orchestrator = AITradingOrchestrator(
            redis_client, trading_service, market_data_service, testnet=True
        )
    return ai_orchestrator


def set_trading_service(service: HyperliquidTradingService):
    """设置交易服务实例"""
    global trading_service
    trading_service = service


def set_ai_orchestrator(orchestrator: AITradingOrchestrator):
    """设置AI编排器实例"""
    global ai_orchestrator
    ai_orchestrator = orchestrator


@router.get("/account")
async def get_account_info(service: HyperliquidTradingService = Depends(get_trading_service)):
    """获取账户信息"""
    try:
        account_info = await service.get_account_info()
        return {
            "success": True,
            "data": account_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get account info: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch account info")


@router.get("/positions")
async def get_positions(service: HyperliquidTradingService = Depends(get_trading_service)):
    """获取当前持仓"""
    try:
        positions = await service.get_positions()
        return {
            "success": True,
            "data": positions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get positions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch positions")


@router.post("/orders")
async def place_order(
    symbol: str,
    side: str,
    size: float,
    price: Optional[float] = None,
    order_type: str = "market",
    service: HyperliquidTradingService = Depends(get_trading_service)
):
    """下单"""
    try:
        result = await service.place_order(
            symbol=symbol,
            side=side,
            size=size,
            price=price,
            order_type=order_type
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Order failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to place order: {e}")
        raise HTTPException(status_code=500, detail="Failed to place order")


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    service: HyperliquidTradingService = Depends(get_trading_service)
):
    """取消订单"""
    try:
        result = await service.cancel_order(order_id)
        
        if result.get("success"):
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Cancel failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel order: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel order")


@router.get("/orders/{order_id}")
async def get_order_status(
    order_id: str,
    service: HyperliquidTradingService = Depends(get_trading_service)
):
    """获取订单状态"""
    try:
        result = await service.get_order_status(order_id)
        
        if result.get("success"):
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Order not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get order status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get order status")


@router.get("/stats")
async def get_trading_stats(service: HyperliquidTradingService = Depends(get_trading_service)):
    """获取交易统计"""
    try:
        stats = await service.get_trading_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get trading stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch trading stats")


@router.post("/ai/start")
async def start_ai_trading(orchestrator: AITradingOrchestrator = Depends(get_ai_orchestrator)):
    """启动AI交易"""
    try:
        await orchestrator.start_trading()
        return {
            "success": True,
            "message": "AI trading started successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to start AI trading: {e}")
        raise HTTPException(status_code=500, detail="Failed to start AI trading")


@router.post("/ai/stop")
async def stop_ai_trading(orchestrator: AITradingOrchestrator = Depends(get_ai_orchestrator)):
    """停止AI交易"""
    try:
        await orchestrator.stop_trading()
        return {
            "success": True,
            "message": "AI trading stopped successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to stop AI trading: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop AI trading")


@router.get("/ai/status")
async def get_ai_trading_status(orchestrator: AITradingOrchestrator = Depends(get_ai_orchestrator)):
    """获取AI交易状态"""
    try:
        status = await orchestrator.get_trading_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get AI trading status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI trading status")


@router.get("/ai/performance")
async def get_ai_performance(orchestrator: AITradingOrchestrator = Depends(get_ai_orchestrator)):
    """获取AI性能"""
    try:
        performance = await orchestrator.get_ai_performance()
        return {
            "success": True,
            "data": performance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get AI performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI performance")


@router.get("/ai/decisions")
async def get_ai_decisions(
    limit: int = 10,
    orchestrator: AITradingOrchestrator = Depends(get_ai_orchestrator)
):
    """获取AI决策历史"""
    try:
        # 获取DeepSeek决策历史
        deepseek_decisions = await orchestrator.deepseek_engine.get_decision_history(limit)
        
        # 获取Qwen决策历史
        qwen_decisions = await orchestrator.qwen_engine.get_decision_history(limit)
        
        return {
            "success": True,
            "data": {
                "deepseek": deepseek_decisions,
                "qwen": qwen_decisions,
                "total": len(deepseek_decisions) + len(qwen_decisions)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get AI decisions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI decisions")


@router.post("/ai/analyze")
async def analyze_market(
    orchestrator: AITradingOrchestrator = Depends(get_ai_orchestrator)
):
    """手动触发市场分析"""
    try:
        # 获取市场数据
        market_data = await orchestrator._get_market_data()
        
        # 获取AI决策
        decisions = await orchestrator._get_ai_decisions(market_data)
        
        return {
            "success": True,
            "data": {
                "market_data": market_data,
                "decisions": decisions,
                "decision_count": len(decisions)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to analyze market: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze market")
