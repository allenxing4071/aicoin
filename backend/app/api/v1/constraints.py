"""
约束状态API端点
提供硬约束和软约束的实时状态监控
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

from app.core.config import settings
from app.services.constraints.constraint_validator import (
    HARD_CONSTRAINTS,
    validate_hard_constraints,
    check_forced_liquidation
)

router = APIRouter(prefix="/constraints", tags=["constraints"])
logger = logging.getLogger(__name__)


@router.get("/status")
async def get_constraints_status() -> Dict[str, Any]:
    """
    获取约束状态
    
    Returns:
        Dict: 包含硬约束、软约束和违规记录
    """
    try:
        # 模拟当前账户状态（TODO: 从实际系统获取）
        mock_account_state = {
            "margin_ratio": 0.45,        # 45%
            "total_equity": 298.50,
            "used_margin": 50.0,
            "free_margin": 248.50,
            "total_drawdown": 0.023,     # 2.3%
            "daily_loss_pct": 0.008,     # 0.8%
            "current_leverage": 2.0,     # 2x
            "cash_reserve_pct": 0.83,    # 83%
            "max_single_asset_pct": 0.15 # 15%
        }
        
        # 检查硬约束
        hard_constraints_status = _check_hard_constraints_status(mock_account_state)
        
        # 检查软约束
        soft_constraints_status = _check_soft_constraints_status()
        
        # 检查是否触发强制平仓
        forced_liquidation = check_forced_liquidation(mock_account_state)
        
        # 统计状态
        total_hard = len(hard_constraints_status)
        passed_hard = sum(1 for c in hard_constraints_status.values() if c["status"] == "pass")
        warning_hard = sum(1 for c in hard_constraints_status.values() if c["status"] == "warning")
        violated_hard = sum(1 for c in hard_constraints_status.values() if c["status"] == "violated")
        
        response = {
            "hard_constraints": hard_constraints_status,
            "soft_constraints": soft_constraints_status,
            "forced_liquidation": {
                "triggered": forced_liquidation,
                "reason": "保证金率 < 15%" if forced_liquidation else None
            },
            "summary": {
                "total_constraints": total_hard,
                "passed": passed_hard,
                "warning": warning_hard,
                "violated": violated_hard,
                "overall_status": "healthy" if violated_hard == 0 else "warning" if warning_hard > 0 else "critical"
            },
            "account_state": mock_account_state
        }
        
        logger.info(f"📊 约束状态: {passed_hard}/{total_hard} 通过")
        return response
        
    except Exception as e:
        logger.error(f"❌ 获取约束状态失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取约束状态失败: {str(e)}"
        )


@router.get("/hard")
async def get_hard_constraints() -> Dict[str, Any]:
    """
    获取硬约束配置
    
    Returns:
        Dict: 硬约束配置和阈值
    """
    try:
        return {
            "constraints": HARD_CONSTRAINTS,
            "description": "8项硬约束红线，违反将强制拒绝交易或平仓"
        }
    except Exception as e:
        logger.error(f"❌ 获取硬约束配置失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取硬约束配置失败: {str(e)}"
        )


@router.get("/soft")
async def get_soft_constraints() -> Dict[str, Any]:
    """
    获取软约束配置
    
    Returns:
        Dict: 软约束配置
    """
    try:
        return {
            "confidence_threshold": {
                "L0": 1.00,
                "L1": 0.80,
                "L2": 0.75,
                "L3": 0.70,
                "L4": 0.65,
                "L5": 0.60
            },
            "frequency_guidance": {
                "L0": 0,
                "L1": 1,
                "L2": 2,
                "L3": 4,
                "L4": 6,
                "L5": 999
            },
            "description": "软约束根据权限等级动态调整，用于引导AI决策"
        }
    except Exception as e:
        logger.error(f"❌ 获取软约束配置失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取软约束配置失败: {str(e)}"
        )


@router.get("/violations")
async def get_violation_history(limit: int = 50) -> Dict[str, Any]:
    """
    获取违规历史记录
    
    Args:
        limit: 返回记录数量
        
    Returns:
        Dict: 违规历史
    """
    try:
        # TODO: 从数据库查询实际违规记录
        violations = _get_mock_violations(limit)
        
        return {
            "total": len(violations),
            "violations": violations
        }
    except Exception as e:
        logger.error(f"❌ 获取违规历史失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取违规历史失败: {str(e)}"
        )


# ===== 辅助函数 =====

def _check_hard_constraints_status(account_state: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """检查硬约束状态"""
    
    status = {}
    
    # 1. 保证金率
    margin_ratio = account_state.get("margin_ratio", 0)
    min_margin = settings.MIN_MARGIN_RATIO
    status["margin_ratio"] = {
        "name": "最低保证金率",
        "current": f"{margin_ratio*100:.1f}%",
        "threshold": f"{min_margin*100:.1f}%",
        "status": "pass" if margin_ratio >= min_margin else "violated",
        "description": f"当前 {margin_ratio*100:.1f}% {'✅' if margin_ratio >= min_margin else '❌'} 阈值 {min_margin*100:.1f}%"
    }
    
    # 2. 总回撤
    total_drawdown = account_state.get("total_drawdown", 0)
    max_dd = settings.MAX_TOTAL_DRAWDOWN
    status["max_drawdown"] = {
        "name": "最大总回撤",
        "current": f"{total_drawdown*100:.1f}%",
        "threshold": f"{max_dd*100:.1f}%",
        "status": "pass" if total_drawdown < max_dd else "warning" if total_drawdown < max_dd * 1.2 else "violated",
        "description": f"当前 {total_drawdown*100:.1f}% {'✅' if total_drawdown < max_dd else '⚠️' if total_drawdown < max_dd * 1.2 else '❌'} 阈值 {max_dd*100:.1f}%"
    }
    
    # 3. 单日亏损
    daily_loss = account_state.get("daily_loss_pct", 0)
    max_daily_loss = settings.MAX_DAILY_LOSS_PCT
    status["daily_loss"] = {
        "name": "单日最大亏损",
        "current": f"{daily_loss*100:.1f}%",
        "threshold": f"{max_daily_loss*100:.1f}%",
        "status": "pass" if daily_loss < max_daily_loss else "violated",
        "description": f"当前 {daily_loss*100:.1f}% {'✅' if daily_loss < max_daily_loss else '❌'} 阈值 {max_daily_loss*100:.1f}%"
    }
    
    # 4. 杠杆率
    leverage = account_state.get("current_leverage", 1)
    max_lev = settings.ABSOLUTE_MAX_LEVERAGE
    status["leverage"] = {
        "name": "最大杠杆",
        "current": f"{leverage:.1f}x",
        "threshold": f"{max_lev}x",
        "status": "pass" if leverage <= max_lev else "violated",
        "description": f"当前 {leverage:.1f}x {'✅' if leverage <= max_lev else '❌'} 阈值 {max_lev}x"
    }
    
    # 5. 现金储备
    cash_reserve = account_state.get("cash_reserve_pct", 0)
    min_cash = settings.MIN_CASH_RESERVE
    status["cash_reserve"] = {
        "name": "最低现金储备",
        "current": f"{cash_reserve*100:.1f}%",
        "threshold": f"{min_cash*100:.1f}%",
        "status": "pass" if cash_reserve >= min_cash else "warning" if cash_reserve >= min_cash * 0.8 else "violated",
        "description": f"当前 {cash_reserve*100:.1f}% {'✅' if cash_reserve >= min_cash else '⚠️' if cash_reserve >= min_cash * 0.8 else '❌'} 阈值 {min_cash*100:.1f}%"
    }
    
    # 6. 单一资产敞口
    max_asset = account_state.get("max_single_asset_pct", 0)
    max_single = settings.MAX_SINGLE_ASSET_EXPOSURE
    status["single_asset"] = {
        "name": "单一资产最大敞口",
        "current": f"{max_asset*100:.1f}%",
        "threshold": f"{max_single*100:.1f}%",
        "status": "pass" if max_asset <= max_single else "violated",
        "description": f"当前 {max_asset*100:.1f}% {'✅' if max_asset <= max_single else '❌'} 阈值 {max_single*100:.1f}%"
    }
    
    # 7. 强制平仓线
    forced_liq = settings.FORCED_LIQUIDATION_THRESHOLD
    status["forced_liquidation"] = {
        "name": "强制平仓线",
        "current": f"{margin_ratio*100:.1f}%",
        "threshold": f"{forced_liq*100:.1f}%",
        "status": "pass" if margin_ratio > forced_liq else "critical",
        "description": f"保证金率 {margin_ratio*100:.1f}% {'✅' if margin_ratio > forced_liq else '🚨'} 强平线 {forced_liq*100:.1f}%"
    }
    
    # 8. 单笔最大亏损（需要历史数据，当前用模拟）
    max_single_trade_loss = settings.MAX_SINGLE_TRADE_LOSS
    status["single_trade_loss"] = {
        "name": "单笔最大亏损",
        "current": "0.0%",
        "threshold": f"{max_single_trade_loss*100:.1f}%",
        "status": "pass",
        "description": f"当前无持仓 ✅ 阈值 {max_single_trade_loss*100:.1f}%"
    }
    
    return status


def _check_soft_constraints_status() -> Dict[str, Any]:
    """检查软约束状态"""
    
    return {
        "confidence_threshold": {
            "current_level": "L1",
            "required_confidence": 0.80,
            "recent_average": 0.65,
            "status": "below_threshold",
            "description": "AI置信度0.65 < L1要求0.80，决策被拒绝"
        },
        "frequency_limit": {
            "current_level": "L1",
            "max_daily_trades": 1,
            "today_trades": 0,
            "status": "within_limit",
            "description": "今日0笔 < L1限制1笔，可以交易"
        }
    }


def _get_mock_violations(limit: int) -> List[Dict[str, Any]]:
    """获取模拟违规记录"""
    
    return [
        {
            "timestamp": "2025-10-31T15:59:48Z",
            "constraint_type": "soft",
            "constraint_name": "confidence_threshold",
            "violation": "置信度0.65 < 0.80",
            "action": "rejected",
            "severity": "low"
        },
        {
            "timestamp": "2025-10-31T15:54:48Z",
            "constraint_type": "soft",
            "constraint_name": "confidence_threshold",
            "violation": "置信度0.65 < 0.80",
            "action": "rejected",
            "severity": "low"
        },
        {
            "timestamp": "2025-10-31T15:49:48Z",
            "constraint_type": "soft",
            "constraint_name": "confidence_threshold",
            "violation": "置信度0.65 < 0.80",
            "action": "rejected",
            "severity": "low"
        }
    ][:limit]

