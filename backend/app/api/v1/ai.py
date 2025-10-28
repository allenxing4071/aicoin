"""AI Health and Status API endpoints"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

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

