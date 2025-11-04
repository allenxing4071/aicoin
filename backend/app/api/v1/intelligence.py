"""Intelligence API - Qwen情报官接口"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

from app.services.intelligence.storage import intelligence_storage
from app.services.intelligence.qwen_engine import qwen_intelligence_engine

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/latest")
async def get_latest_intelligence() -> Dict[str, Any]:
    """获取最新的情报报告"""
    try:
        report = await intelligence_storage.get_latest_report()
        
        if not report:
            return {
                "success": False,
                "message": "暂无情报报告",
                "data": None
            }
        
        return {
            "success": True,
            "data": report.to_dict()
        }
    
    except Exception as e:
        logger.error(f"获取最新情报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_intelligence_history(limit: int = 10) -> Dict[str, Any]:
    """获取历史情报报告"""
    try:
        if limit < 1 or limit > 50:
            limit = 10
        
        reports = await intelligence_storage.get_report_history(limit=limit)
        
        return {
            "success": True,
            "data": {
                "total": len(reports),
                "reports": [r.to_dict() for r in reports]
            }
        }
    
    except Exception as e:
        logger.error(f"获取历史情报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_intelligence() -> Dict[str, Any]:
    """手动触发情报收集（立即刷新）"""
    try:
        logger.info("🔄 手动触发情报收集...")
        
        # 检查是否正在运行
        if not qwen_intelligence_engine.is_running:
            return {
                "success": False,
                "message": "Qwen情报引擎未运行"
            }
        
        # 执行情报收集
        report = await qwen_intelligence_engine.collect_intelligence()
        
        return {
            "success": True,
            "message": "情报收集完成",
            "data": report.to_dict()
        }
    
    except Exception as e:
        logger.error(f"手动刷新情报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_intelligence_status() -> Dict[str, Any]:
    """获取Qwen情报引擎状态"""
    try:
        is_running = qwen_intelligence_engine.is_running
        last_report_time = qwen_intelligence_engine.last_report_time
        
        # 检查最新报告的新鲜度
        is_fresh = await intelligence_storage.is_report_fresh(max_age_minutes=30)
        
        return {
            "success": True,
            "data": {
                "is_running": is_running,
                "last_report_time": last_report_time.isoformat() if last_report_time else None,
                "is_fresh": is_fresh,
                "update_interval_seconds": 1800  # 30 minutes
            }
        }
    
    except Exception as e:
        logger.error(f"获取情报状态失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

