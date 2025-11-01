"""AI Health and Status API endpoints"""

from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime
from typing import Optional
import logging
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def get_ai_health():
    """
    获取AI模型健康状态
    
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
        from sqlalchemy import desc
        
        # 从数据库查询决策记录
        query = db.query(AIDecision).order_by(desc(AIDecision.created_at))
        
        # 如果指定了model，添加筛选
        if model and model != 'all':
            query = query.filter(AIDecision.model_name == model)
        
        decisions = query.limit(limit).all()
        
        # 转换为聊天消息格式
        messages = []
        for decision in decisions:
            # 从JSONB字段解析决策数据
            decision_data = decision.decision if isinstance(decision.decision, dict) else {}
            action_str = decision_data.get("action", "HOLD")
            
            # 确定action类型
            action = "— HOLD"
            if action_str and action_str.upper() in ["BUY", "LONG"]:
                action = "↗ BUY"
            elif action_str and action_str.upper() in ["SELL", "SHORT"]:
                action = "↘ SELL"
            
            # 获取confidence（可能是0-1的浮点数或0-100的整数）
            confidence_raw = decision_data.get("confidence", 0.5)
            confidence = int(confidence_raw * 100) if confidence_raw <= 1 else int(confidence_raw)
            
            message = {
                "model": decision.model_name or "DEEPSEEK",
                "timestamp": decision.created_at.isoformat() if decision.created_at else datetime.now().isoformat(),
                "action": action,
                "symbol": decision.symbol or "BTC-PERP",
                "confidence": confidence,
                "reasoning": decision_data.get("reasoning", decision.reject_reason or "No reasoning provided")
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

