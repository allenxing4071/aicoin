"""Dashboard API - 统一的仪表板数据接口"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_api_status_data() -> Dict[str, Any]:
    """获取API状态"""
    try:
        from app.services.orchestrator_v2 import orchestrator
        
        status_info = orchestrator.get_status()
        return {
            "status": "healthy",
            "app": "AIcoin Trading System",
            "version": "1.0.0",
            "orchestrator_status": {
                "is_running": status_info.get("is_running", False),
                "permission_level": status_info.get("permission_level", "L0"),
                "runtime_hours": status_info.get("runtime_hours", 0),
                "total_decisions": status_info.get("total_decisions", 0),
                "approved_decisions": status_info.get("approved_decisions", 0),
                "approval_rate": status_info.get("approval_rate", 0),
                "decision_interval": status_info.get("decision_interval", 60)
            }
        }
    except Exception as e:
        logger.error(f"获取API状态失败: {e}")
        return {
            "status": "unavailable",
            "version": "N/A"
        }


async def get_account_data(db: AsyncSession) -> Dict[str, Any]:
    """获取账户信息 (带缓存优化)"""
    try:
        from app.services.hyperliquid_trading import HyperliquidTradingService
        from app.core.redis_client import redis_client
        from app.core.config import settings
        
        # 尝试从缓存获取 (30秒缓存)
        cache_key = "dashboard:account_info"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            logger.debug("✅ 从缓存获取账户数据")
            return cached_data
        
        # 缓存未命中,查询数据
        testnet = getattr(settings, 'HYPERLIQUID_TESTNET', False)
        trading_service = HyperliquidTradingService(redis_client, testnet=testnet)
        await trading_service.initialize()
        account_info = trading_service.get_account_info()
        
        result = {
            "equity": account_info.get("equity", 0),
            "balance": account_info.get("balance", 0),
            "margin_used": account_info.get("margin_used", 0),
            "unrealized_pnl": account_info.get("unrealized_pnl", 0),
            "total_return": account_info.get("total_return", 0)
        }
        
        # 缓存结果 (30秒)
        await redis_client.set(cache_key, result, expire=30)
        logger.debug("✅ 账户数据已缓存")
        
        return result
    except Exception as e:
        logger.error(f"获取账户数据失败: {e}")
        return {
            "equity": 0,
            "balance": 0,
            "error": str(e)
        }


async def get_models_list_data(db: AsyncSession) -> list:
    """获取模型列表"""
    try:
        from app.services.hyperliquid_trading import HyperliquidTradingService
        from app.core.redis_client import redis_client
        from app.core.config import settings
        
        testnet = getattr(settings, 'HYPERLIQUID_TESTNET', False)
        trading_service = HyperliquidTradingService(redis_client, testnet=testnet)
        await trading_service.initialize()
        account_info = trading_service.get_account_info()
        real_balance = float(account_info.get("equity", account_info.get("balance", 0)))
        
        return [
            {
                "name": "DEEPSEEK CHAT V3.1",
                "slug": "deepseek-chat-v3.1",
                "value": real_balance,
                "change": 0,  # TODO: 计算真实收益率
                "color": "#3b82f6",
                "icon": "deepseek"
            }
        ]
    except Exception as e:
        logger.error(f"获取模型数据失败: {e}")
        return []


async def get_ai_health_data(db: AsyncSession) -> Dict[str, Any]:
    """获取AI健康状态"""
    try:
        from app.services.orchestrator_v2 import orchestrator
        from app.services.decision.engine_v2 import DecisionEngineV2
        
        orchestrator_status = orchestrator.get_status()
        
        # 获取决策引擎状态
        engine = DecisionEngineV2()
        
        return {
            "orchestrator": {
                "is_running": orchestrator_status.get("is_running", False),
                "permission_level": orchestrator_status.get("permission_level", "L0"),
                "runtime_hours": orchestrator_status.get("runtime_hours", 0),
                "total_decisions": orchestrator_status.get("total_decisions", 0),
                "approval_rate": orchestrator_status.get("approval_rate", 0),
                "next_decision_at": orchestrator_status.get("next_decision_at")
            },
            "deepseek": {
                "status": "active",
                "model": "deepseek-chat",
                "last_used": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"获取AI健康数据失败: {e}")
        return {
            "orchestrator": {
                "is_running": False,
                "permission_level": "L0"
            }
        }


@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """
    获取仪表板摘要数据 (一次性获取所有数据)
    
    优化: 合并4个API调用为1个
    - /health
    - /account/info
    - /models/data
    - /ai/health
    
    Returns:
        Dict: 包含所有仪表板数据
        {
            "success": true,
            "data": {
                "api_status": {...},
                "account": {...},
                "models": [...],
                "ai_health": {...}
            },
            "timestamp": "2025-11-05T22:00:00"
        }
    """
    try:
        logger.info("📊 获取仪表板摘要数据...")
        
        # 并发执行所有查询,提升性能
        api_status, account, models, ai_health = await asyncio.gather(
            get_api_status_data(),
            get_account_data(db),
            get_models_list_data(db),
            get_ai_health_data(db),
            return_exceptions=True  # 单个失败不影响整体
        )
        
        # 处理异常结果
        if isinstance(api_status, Exception):
            logger.error(f"API状态查询失败: {api_status}")
            api_status = {"status": "error", "version": "N/A"}
        
        if isinstance(account, Exception):
            logger.error(f"账户数据查询失败: {account}")
            account = {"equity": 0, "balance": 0}
        
        if isinstance(models, Exception):
            logger.error(f"模型数据查询失败: {models}")
            models = []
        
        if isinstance(ai_health, Exception):
            logger.error(f"AI健康数据查询失败: {ai_health}")
            ai_health = {"orchestrator": {"is_running": False}}
        
        logger.info("✅ 仪表板摘要数据获取成功")
        
        return {
            "success": True,
            "data": {
                "api_status": api_status,
                "account": account,
                "models": models,
                "ai_health": ai_health
            },
            "timestamp": datetime.now().isoformat(),
            "cache_hint": "可缓存30秒"
        }
        
    except Exception as e:
        logger.error(f"❌ 获取仪表板摘要失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取仪表板摘要失败: {str(e)}"
        )


@router.get("/quick")
async def get_dashboard_quick():
    """
    快速仪表板数据 (仅返回关键信息,不查询数据库)
    
    用途: 页面初始加载,立即显示基本信息
    
    Returns:
        Dict: 最小化的仪表板数据
    """
    try:
        from app.services.orchestrator_v2 import orchestrator
        
        status = orchestrator.get_status()
        
        return {
            "success": True,
            "data": {
                "is_running": status.get("is_running", False),
                "permission_level": status.get("permission_level", "L0"),
                "app_version": "1.0.0"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取快速仪表板数据失败: {e}")
        return {
            "success": False,
            "data": {
                "is_running": False,
                "permission_level": "L0"
            }
        }

