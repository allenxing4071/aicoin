"""AI Health and Status API endpoints"""

from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime
from typing import Optional
import logging
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status")
async def get_ai_status(db = Depends(get_db)):
    """
    获取AI完整状态（包含orchestrator信息）
    
    Returns:
        AI orchestrator完整状态信息
    """
    try:
        # 尝试从main.py获取全局orchestrator
        from app.main import ai_orchestrator
        from app.core.config import settings
        
        # 从数据库获取当前默认权限等级及其配置
        async def get_default_permission_info():
            try:
                from app.models.permission_config import PermissionLevelConfig
                from sqlalchemy import select
                
                stmt = select(PermissionLevelConfig).where(
                    PermissionLevelConfig.is_default == True,
                    PermissionLevelConfig.is_active == True
                ).limit(1)
                
                result = await db.execute(stmt)
                default_config = result.scalars().first()
                
                if default_config:
                    return {
                        "level": default_config.level,
                        "name": default_config.name,
                        "max_position_pct": default_config.max_position_pct,
                        "max_leverage": default_config.max_leverage,
                        "confidence_threshold": default_config.confidence_threshold,
                        "max_daily_trades": default_config.max_daily_trades
                    }
                else:
                    return {
                        "level": settings.INITIAL_PERMISSION_LEVEL,
                        "name": "新手级",
                        "max_position_pct": 0.10,
                        "max_leverage": 2,
                        "confidence_threshold": 0.50,
                        "max_daily_trades": 10
                    }
            except Exception as e:
                logger.error(f"获取默认权限等级失败: {e}")
                return {
                    "level": settings.INITIAL_PERMISSION_LEVEL,
                    "name": "新手级",
                    "max_position_pct": 0.10,
                    "max_leverage": 2,
                    "confidence_threshold": 0.50,
                    "max_daily_trades": 10
                }
        
        permission_info = await get_default_permission_info()
        current_permission_level = permission_info["level"]
        
        logger.info(f"📌 从数据库读取的默认权限等级: {current_permission_level}")
        
        if ai_orchestrator:
            # 同步更新decision_engine的权限等级（如果数据库中的默认等级已改变）
            if hasattr(ai_orchestrator, 'decision_engine') and hasattr(ai_orchestrator.decision_engine, 'current_permission_level'):
                logger.info(f"📌 DecisionEngine当前权限等级: {ai_orchestrator.decision_engine.current_permission_level}")
                if ai_orchestrator.decision_engine.current_permission_level != current_permission_level:
                    logger.info(f"🔄 同步更新DecisionEngine权限等级: {ai_orchestrator.decision_engine.current_permission_level} -> {current_permission_level}")
                    ai_orchestrator.decision_engine.current_permission_level = current_permission_level
                else:
                    logger.info(f"✅ DecisionEngine权限等级已是最新: {current_permission_level}")
            
            # 计算运行时长
            runtime_seconds = (datetime.now() - ai_orchestrator.start_time).total_seconds() if hasattr(ai_orchestrator, 'start_time') and ai_orchestrator.start_time else 0
            runtime_hours = runtime_seconds / 3600
            
            # 获取决策统计
            total_decisions = getattr(ai_orchestrator, 'total_decisions', 0)
            approved_decisions = getattr(ai_orchestrator, 'approved_decisions', 0)
            approval_rate = (approved_decisions / total_decisions * 100) if total_decisions > 0 else 0.0
            
            return {
                "success": True,
                "orchestrator": {
                    "is_running": getattr(ai_orchestrator, 'is_running', False),
                    "permission_level": current_permission_level,  # 从数据库获取
                    "permission_name": permission_info["name"],  # 权限等级名称
                    "permission_config": {  # 权限等级配置
                        "max_position_pct": permission_info["max_position_pct"],
                        "max_leverage": permission_info["max_leverage"],
                        "confidence_threshold": permission_info["confidence_threshold"],
                        "max_daily_trades": permission_info["max_daily_trades"]
                    },
                    "runtime_hours": runtime_hours,
                    "total_decisions": total_decisions,
                    "approved_decisions": approved_decisions,
                    "approval_rate": approval_rate,
                    "decision_interval": settings.DECISION_INTERVAL
                },
                "api_version": "1.0.0",
                "trading_enabled": True,
                "models": {
                    "deepseek-chat-v3.1": {
                        "status": "running" if getattr(ai_orchestrator, 'is_running', False) else "stopped",
                        "last_decision_time": None
                    }
                }
            }
        else:
            # orchestrator未初始化，返回默认值
            return {
                "success": True,
                "orchestrator": {
                    "is_running": False,
                    "permission_level": current_permission_level,  # 使用数据库中的默认等级
                    "permission_name": permission_info["name"],
                    "permission_config": {
                        "max_position_pct": permission_info["max_position_pct"],
                        "max_leverage": permission_info["max_leverage"],
                        "confidence_threshold": permission_info["confidence_threshold"],
                        "max_daily_trades": permission_info["max_daily_trades"]
                    },
                    "runtime_hours": 0.0,
                    "total_decisions": 0,
                    "approved_decisions": 0,
                    "approval_rate": 0.0,
                    "decision_interval": 300
                },
                "api_version": "1.0.0",
                "trading_enabled": False,
                "models": {
                    "deepseek-chat-v3.1": {
                        "status": "stopped",
                        "last_decision_time": None
                    }
                }
            }
        
    except Exception as e:
        logger.error(f"Error fetching AI status: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # 即使出错也返回一个合理的默认状态
        return {
            "success": False,
            "orchestrator": {
                "is_running": False,
                "permission_level": "L1",
                "permission_name": "新手级",
                "permission_config": {
                    "max_position_pct": 0.10,
                    "max_leverage": 2,
                    "confidence_threshold": 0.50,
                    "max_daily_trades": 10
                },
                "runtime_hours": 0.0,
                "total_decisions": 0,
                "approved_decisions": 0,
                "approval_rate": 0.0,
                "decision_interval": 300
            },
            "error": str(e)
        }


@router.get("/health")
async def get_ai_health():
    """
    获取AI模型健康状态（向后兼容）
    
    Returns:
        AI模型状态信息
    """
    try:
        from app.api import trading as hyperliquid_trading
        
        ai_orchestrator = hyperliquid_trading.get_ai_orchestrator()
        
        # 获取AI编排器状态
        is_running = ai_orchestrator.is_running
        total_trades = ai_orchestrator.total_trades
        successful_trades = ai_orchestrator.successful_trades
        
        # 获取最近的决策时间（从Redis或内存）
        deepseek_last_decision = None
        qwen_last_decision = None
        
        # 从decision_history获取最后决策时间
        if ai_orchestrator.decision_history:
            for decision in reversed(ai_orchestrator.decision_history):
                model = decision.get('model', '')
                timestamp = decision.get('timestamp', '')
                
                if 'deepseek' in model.lower() and not deepseek_last_decision:
                    deepseek_last_decision = timestamp
                elif 'qwen' in model.lower() and not qwen_last_decision:
                    qwen_last_decision = timestamp
                
                if deepseek_last_decision and qwen_last_decision:
                    break
        
        return {
            "success": True,
            "orchestrator_running": is_running,
            "models": {
                "deepseek-chat-v3.1": {
                    "status": "running" if is_running else "stopped",
                    "last_decision_time": deepseek_last_decision,
                    "error": None
                }
                # Qwen已禁用
            },
            "stats": {
                "total_trades": total_trades,
                "successful_trades": successful_trades,
                "success_rate": (successful_trades / total_trades * 100) if total_trades > 0 else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching AI health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/permission")
async def get_ai_permission():
    """
    获取AI权限等级状态
    
    Returns:
        当前权限等级和配置信息
    """
    try:
        from app.core.config import settings
        
        return {
            "success": True,
            "current_level": "L1",
            "display_name": "新手级",
            "config": {
                "max_position_pct": 0.10,  # 10%
                "max_leverage": 2,
                "confidence_threshold": settings.MIN_CONFIDENCE,  # 0.60
                "max_daily_trades": 5
            },
            "upgrade": {
                "can_upgrade": False,
                "target_level": "L2",
                "progress_pct": 0.0,
                "message": "继续交易积累经验，达到要求后可升级到L2"
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching AI permission: {e}")
        return {
            "success": False,
            "current_level": "L1",
            "display_name": "新手级",
            "config": {
                "max_position_pct": 0.10,
                "max_leverage": 2,
                "confidence_threshold": 0.60,
                "max_daily_trades": 5
            },
            "upgrade": {
                "can_upgrade": False,
                "target_level": "",
                "progress_pct": 0.0,
                "message": ""
            },
            "error": str(e)
        }


@router.get("/decisions")
async def get_ai_decisions(
    status: Optional[str] = Query(None, description="Filter by status: approved, rejected, or all"),
    limit: int = Query(25, ge=1, le=100, description="Maximum number of decisions"),
    db: Session = Depends(get_db)
):
    """
    获取AI决策历史记录
    
    Args:
        status: 状态筛选 (approved=已执行, rejected=已拒绝, all=全部)
        limit: 返回数量
        
    Returns:
        AI决策历史列表
    """
    try:
        from app.models.ai_decision import AIDecision
        from sqlalchemy import desc, select
        
        # 从数据库查询决策记录 (SQLAlchemy 2.0语法)
        stmt = select(AIDecision).order_by(desc(AIDecision.created_at))
        
        # 根据status筛选
        if status == 'approved':
            stmt = stmt.filter(AIDecision.executed == True)
        elif status == 'rejected':
            stmt = stmt.filter(AIDecision.executed == False)
        # status == 'all' 或 None 时不筛选
        
        stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        decisions_db = result.scalars().all()
        
        # 转换为前端需要的格式
        decisions = []
        for dec in decisions_db:
            decision_data = dec.decision if isinstance(dec.decision, dict) else {}
            market_data = dec.market_data if isinstance(dec.market_data, dict) else {}
            
            action_str = decision_data.get("action", "HOLD")
            confidence_raw = decision_data.get("confidence", 0.5)
            confidence = confidence_raw * 100 if confidence_raw <= 1 else confidence_raw
            
            decision_item = {
                "id": str(dec.id),
                "timestamp": dec.created_at.isoformat() if dec.created_at else datetime.now().isoformat(),
                "model": dec.model_name or "deepseek-chat-v3.1",
                "symbol": dec.symbol or "BTC-PERP",
                "action": action_str.upper(),
                "confidence": float(confidence),
                "status": "approved" if dec.executed else "rejected",
                "reasoning": decision_data.get("reasoning", dec.reject_reason or "No reasoning provided"),
                "price": market_data.get("price", 0),
                "permission_level": decision_data.get("permission_level", "L1"),
                "duration_ms": dec.latency_ms or 0
            }
            decisions.append(decision_item)
        
        logger.info(f"✅ Found {len(decisions)} decisions (filter: {status or 'all'})")
        
        return {
            "success": True,
            "decisions": decisions,
            "count": len(decisions)
        }
        
    except Exception as e:
        logger.error(f"Error fetching AI decisions: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # 返回空列表而不是抛出异常，避免前端报错
        return {
            "success": True,
            "decisions": [],
            "count": 0
        }


@router.get("/chat/history")
async def get_chat_history(
    model: Optional[str] = Query(None, description="Filter by model name"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of messages"),
    db: Session = Depends(get_db)
):
    """
    获取AI决策聊天历史（从decisions表获取）
    
    Args:
        model: 模型名称筛选 (可选)
        limit: 返回数量
        
    Returns:
        AI聊天历史列表
    """
    try:
        from app.models.ai_decision import AIDecision
        from sqlalchemy import desc, select
        
        # 从数据库查询决策记录 (SQLAlchemy 2.0语法)
        stmt = select(AIDecision).order_by(desc(AIDecision.created_at))
        
        # 如果指定了model，添加筛选
        if model and model != 'all':
            stmt = stmt.filter(AIDecision.model_name == model)
        
        stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        decisions = result.scalars().all()
        
        # 转换为聊天消息格式
        messages = []
        for decision in decisions:
            # 从JSONB字段解析决策数据
            decision_data = decision.decision if isinstance(decision.decision, dict) else {}
            action_str = decision_data.get("action", "HOLD")
            
            # 确定action类型（中文显示）
            action = "— 持仓观望"
            action_en = "none"
            if action_str and action_str.upper() in ["BUY", "LONG", "OPEN_LONG"]:
                action = "↗ 做多"
                action_en = "long"
            elif action_str and action_str.upper() in ["SELL", "SHORT", "OPEN_SHORT"]:
                action = "↘ 做空"
                action_en = "short"
            elif action_str and action_str.upper() in ["CLOSE"]:
                action = "✖ 平仓"
                action_en = "close"
            
            # 获取confidence（可能是0-1的浮点数或0-100的整数）
            confidence_raw = decision_data.get("confidence", 0.5)
            confidence = int(confidence_raw * 100) if confidence_raw <= 1 else int(confidence_raw)
            
            # DeepSeek已经直接输出中文，不需要翻译
            reasoning_text = decision_data.get("reasoning", decision.reject_reason or "暂无决策说明")
            
            message = {
                "model": decision.model_name or "deepseek-chat-v3.1",
                "timestamp": decision.created_at.isoformat() if decision.created_at else datetime.now().isoformat(),
                "action": action,
                "action_en": action_en,
                "symbol": decision.symbol or "BTC",
                "confidence": confidence,
                "reasoning": reasoning_text
            }
            messages.append(message)
        
        logger.info(f"✅ Found {len(messages)} chat messages")
        
        return {
            "success": True,
            "messages": messages,
            "count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        # 如果数据库查询失败，返回空列表而不是抛出异常
        return {
            "success": True,
            "messages": [],
            "count": 0
        }

