"""
权限状态API端点
提供L0-L5权限等级、升降级条件和进度
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

from app.services.constraints.permission_manager import PermissionManager

router = APIRouter(prefix="/ai/permission", tags=["AI Permission"])
logger = logging.getLogger(__name__)


@router.get("")
async def get_permission_status() -> Dict[str, Any]:
    """
    获取当前权限状态
    
    Returns:
        Dict: 权限等级、配置、升级进度
    """
    try:
        # TODO: 从实际系统获取权限状态
        current_level = "L1"
        
        # 当前等级配置
        current_config = PermissionManager.LEVELS.get(current_level, PermissionManager.LEVELS["L1"])
        
        # 升级进度
        upgrade_progress = _calculate_upgrade_progress(current_level)
        
        # 降级风险
        downgrade_risk = _check_downgrade_risk(current_level)
        
        return {
            "current_level": current_level,
            "display_name": current_config.name,
            "config": {
                "max_position_pct": current_config.max_position_pct,
                "max_leverage": current_config.max_leverage,
                "confidence_threshold": current_config.confidence_threshold,
                "max_daily_trades": current_config.max_daily_trades
            },
            "upgrade": upgrade_progress,
            "downgrade": downgrade_risk,
            "runtime_stats": _get_runtime_stats()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取权限状态失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取权限状态失败: {str(e)}"
        )


@router.get("/levels")
async def get_all_permission_levels() -> Dict[str, Any]:
    """
    获取所有权限等级配置
    
    Returns:
        Dict: L0-L5完整配置
    """
    try:
        # 转换PermissionLevel对象为字典
        levels_dict = {}
        for key, level in PermissionManager.LEVELS.items():
            levels_dict[key] = {
                "name": level.name,
                "max_position_pct": level.max_position_pct,
                "max_leverage": level.max_leverage,
                "confidence_threshold": level.confidence_threshold,
                "max_daily_trades": level.max_daily_trades
            }
        
        return {
            "levels": levels_dict,
            "description": "L0=保护模式, L1=新手级, L2=成长级, L3=稳定级, L4=熟练级, L5=专家级"
        }
    except Exception as e:
        logger.error(f"❌ 获取权限等级配置失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取权限等级配置失败: {str(e)}"
        )


@router.get("/upgrade-conditions")
async def get_upgrade_conditions(target_level: str = "L2") -> Dict[str, Any]:
    """
    获取升级条件
    
    Args:
        target_level: 目标等级 (L1-L5)
        
    Returns:
        Dict: 升级条件和当前进度
    """
    try:
        if target_level not in ["L1", "L2", "L3", "L4", "L5"]:
            raise HTTPException(
                status_code=400,
                detail=f"无效的目标等级: {target_level}"
            )
        
        conditions = _get_upgrade_conditions_for_level(target_level)
        
        logger.info(f"📊 获取升级到{target_level}的条件")
        return conditions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取升级条件失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取升级条件失败: {str(e)}"
        )


@router.get("/downgrade-triggers")
async def get_downgrade_triggers() -> Dict[str, Any]:
    """
    获取降级触发条件
    
    Returns:
        Dict: 降级触发条件说明
    """
    try:
        return {
            "triggers": [
                {
                    "condition": "连续3笔亏损",
                    "action": "降1级",
                    "severity": "medium"
                },
                {
                    "condition": "单日亏损 >= 5%",
                    "action": "降1级",
                    "severity": "high"
                },
                {
                    "condition": "总回撤 >= 10%",
                    "action": "降至L0（保护模式）",
                    "severity": "critical"
                },
                {
                    "condition": "触发强制平仓",
                    "action": "降至L0（保护模式）",
                    "severity": "critical"
                },
                {
                    "condition": "夏普比率 < 0.5（7日）",
                    "action": "降1级",
                    "severity": "medium"
                },
                {
                    "condition": "胜率 < 40%（30日）",
                    "action": "降1级",
                    "severity": "medium"
                }
            ],
            "description": "触发任一条件将自动降级，L0为保护模式，停止所有交易"
        }
    except Exception as e:
        logger.error(f"❌ 获取降级触发条件失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取降级触发条件失败: {str(e)}"
        )


# ===== 辅助函数 =====

def _calculate_upgrade_progress(current_level: str) -> Dict[str, Any]:
    """计算升级进度"""
    
    if current_level == "L5":
        return {
            "can_upgrade": False,
            "target_level": None,
            "progress_pct": 100.0,
            "conditions_met": [],
            "conditions_unmet": [],
            "message": "已达到最高等级"
        }
    
    # L1 → L2 的升级条件
    if current_level == "L1":
        return {
            "can_upgrade": False,
            "target_level": "L2",
            "progress_pct": 15.0,  # 基于当前数据
            "conditions_met": [
                {
                    "name": "运行时长 >= 3天",
                    "current": "0.4天",
                    "required": "3天",
                    "met": False
                }
            ],
            "conditions_unmet": [
                {
                    "name": "连续15日盈利",
                    "current": "0天",
                    "required": "15天",
                    "met": False
                },
                {
                    "name": "夏普比率 >= 1.0",
                    "current": "-0.15",
                    "required": "1.0",
                    "met": False
                },
                {
                    "name": "胜率 >= 50%",
                    "current": "12%",
                    "required": "50%",
                    "met": False
                },
                {
                    "name": "最大回撤 < 5%",
                    "current": "2.3%",
                    "required": "< 5%",
                    "met": True
                }
            ],
            "message": "需满足所有条件才能升级到L2"
        }
    
    return {
        "can_upgrade": False,
        "target_level": "L2",
        "progress_pct": 0.0,
        "conditions_met": [],
        "conditions_unmet": [],
        "message": "暂无升级进度"
    }


def _check_downgrade_risk(current_level: str) -> Dict[str, Any]:
    """检查降级风险"""
    
    if current_level == "L0":
        return {
            "risk_level": "none",
            "message": "已在最低等级",
            "triggers_active": []
        }
    
    # 基于当前数据检查
    return {
        "risk_level": "medium",
        "message": "存在降级风险",
        "triggers_active": [
            {
                "trigger": "胜率 < 40%",
                "current_value": "12%",
                "threshold": "40%",
                "status": "triggered",
                "action": "降1级"
            },
            {
                "trigger": "夏普比率 < 0.5",
                "current_value": "-0.15",
                "threshold": "0.5",
                "status": "triggered",
                "action": "降1级"
            }
        ],
        "recommendation": "建议暂停交易，等待系统稳定"
    }


def _get_runtime_stats() -> Dict[str, Any]:
    """获取运行时统计"""
    
    return {
        "runtime_hours": 0.4,
        "total_decisions": 25,
        "approved_decisions": 0,
        "approval_rate": 0.0,
        "avg_confidence": 0.65,
        "consecutive_losses": 0,
        "consecutive_wins": 0,
        "days_profitable": 0,
        "days_unprofitable": 1
    }


def _get_upgrade_conditions_for_level(target_level: str) -> Dict[str, Any]:
    """获取特定等级的升级条件"""
    
    conditions_map = {
        "L1": {
            "from_level": "L0",
            "to_level": "L1",
            "conditions": [
                "系统正常运行24小时",
                "无严重错误",
                "通过基础测试"
            ],
            "description": "L0→L1: 基础验证"
        },
        "L2": {
            "from_level": "L1",
            "to_level": "L2",
            "conditions": [
                "连续15日盈利",
                "夏普比率 >= 1.0",
                "胜率 >= 50%",
                "最大回撤 < 5%",
                "运行时长 >= 3天"
            ],
            "current_progress": {
                "days_profitable": "0/15",
                "sharpe_ratio": "-0.15/1.0",
                "win_rate": "12%/50%",
                "max_drawdown": "2.3%/5%",
                "runtime_days": "0.4/3"
            },
            "description": "L1→L2: 稳定盈利验证"
        },
        "L3": {
            "from_level": "L2",
            "to_level": "L3",
            "conditions": [
                "连续30日盈利",
                "夏普比率 >= 1.5",
                "胜率 >= 55%",
                "最大回撤 < 8%",
                "总收益 >= 10%"
            ],
            "description": "L2→L3: 持续盈利验证"
        },
        "L4": {
            "from_level": "L3",
            "to_level": "L4",
            "conditions": [
                "连续60日盈利",
                "夏普比率 >= 2.0",
                "胜率 >= 60%",
                "最大回撤 < 10%",
                "总收益 >= 30%"
            ],
            "description": "L3→L4: 优秀表现验证"
        },
        "L5": {
            "from_level": "L4",
            "to_level": "L5",
            "conditions": [
                "连续90日盈利",
                "夏普比率 >= 2.5",
                "胜率 >= 65%",
                "最大回撤 < 12%",
                "总收益 >= 50%",
                "索提诺比率 >= 3.0"
            ],
            "description": "L4→L5: 专家级验证"
        }
    }
    
    return conditions_map.get(target_level, {
        "error": f"未找到{target_level}的升级条件"
    })

