"""Admin API endpoints for log management"""

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import os
import logging

from app.api.v1.admin_db import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

LOG_DIR = Path("logs")


@router.get("/files")
async def get_log_files(current_user: Dict = Depends(get_current_user)) -> Dict[str, Any]:
    """获取所有日志文件列表"""
    try:
        if not LOG_DIR.exists():
            return {"success": True, "data": []}
        
        files = []
        for log_file in sorted(LOG_DIR.glob("*.log*"), key=lambda x: x.stat().st_mtime, reverse=True):
            stat = log_file.stat()
            
            # 统计行数
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = sum(1 for _ in f)
            except:
                lines = 0
            
            files.append({
                "name": log_file.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                "lines": lines
            })
        
        return {"success": True, "data": files}
    
    except Exception as e:
        logger.error(f"获取日志文件列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_log_stats(current_user: Dict = Depends(get_current_user)) -> Dict[str, Any]:
    """获取日志统计信息（包含报警统计）"""
    try:
        if not LOG_DIR.exists():
            return {"success": True, "data": {"total_files": 0, "total_size": 0, "log_types": {}, "alerts": {}}}
        
        log_types = {
            "all": {"files": 0, "size": 0},
            "error": {"files": 0, "size": 0},
            "ai_decisions": {"files": 0, "size": 0},
            "trading": {"files": 0, "size": 0}
        }
        
        total_files = 0
        total_size = 0
        
        # 报警统计
        error_count = 0
        warning_count = 0
        critical_count = 0
        recent_errors = []
        
        for log_file in LOG_DIR.glob("*.log*"):
            size = log_file.stat().st_size
            total_files += 1
            total_size += size
            
            if "error" in log_file.name:
                log_types["error"]["files"] += 1
                log_types["error"]["size"] += size
                
                # 分析错误日志内容
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for line in lines:
                            if 'CRITICAL' in line or '严重' in line:
                                critical_count += 1
                            elif 'ERROR' in line or '错误' in line:
                                error_count += 1
                        
                        # 获取最近5条严重错误
                        for line in reversed(lines[-100:]):
                            if 'ERROR' in line or 'CRITICAL' in line:
                                # 提取时间戳和消息
                                message = line.strip()[:300]  # 截取前300字符
                                level = "CRITICAL" if "CRITICAL" in line else "ERROR"
                                recent_errors.append({
                                    "message": message,
                                    "level": level
                                })
                                if len(recent_errors) >= 5:
                                    break
                except Exception as e:
                    logger.warning(f"分析错误日志失败 {log_file.name}: {e}")
            
            elif "all" in log_file.name:
                log_types["all"]["files"] += 1
                log_types["all"]["size"] += size
                
                # 统计所有日志中的WARNING
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if 'WARNING' in line or '警告' in line:
                                warning_count += 1
                except Exception as e:
                    logger.warning(f"分析日志失败 {log_file.name}: {e}")
            
            elif "ai_decision" in log_file.name:
                log_types["ai_decisions"]["files"] += 1
                log_types["ai_decisions"]["size"] += size
            elif "trading" in log_file.name:
                log_types["trading"]["files"] += 1
                log_types["trading"]["size"] += size
        
        return {
            "success": True,
            "data": {
                "total_files": total_files,
                "total_size": total_size,
                "log_types": log_types,
                "alerts": {
                    "error_count": error_count,
                    "warning_count": warning_count,
                    "critical_count": critical_count,
                    "recent_errors": recent_errors
                }
            }
        }
    
    except Exception as e:
        logger.error(f"获取日志统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view")
async def view_log(
    filename: str = Query(..., description="日志文件名"),
    lines: int = Query(100, description="读取行数"),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """查看日志文件内容（最后N行）"""
    try:
        log_file = LOG_DIR / filename
        
        if not log_file.exists():
            raise HTTPException(status_code=404, detail="日志文件不存在")
        
        # 读取最后N行
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            content = ''.join(all_lines[-lines:])
        
        return {
            "success": True,
            "data": {
                "filename": filename,
                "lines": len(all_lines),
                "content": content
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"读取日志文件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download")
async def download_log(
    filename: str = Query(..., description="日志文件名"),
    current_user: Dict = Depends(get_current_user)
):
    """下载日志文件"""
    try:
        log_file = LOG_DIR / filename
        
        if not log_file.exists():
            raise HTTPException(status_code=404, detail="日志文件不存在")
        
        return FileResponse(
            path=log_file,
            filename=filename,
            media_type='text/plain'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载日志文件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/level")
async def get_log_level(current_user: Dict = Depends(get_current_user)) -> Dict[str, Any]:
    """获取当前日志级别"""
    try:
        level = os.getenv("LOG_LEVEL", "INFO")
        return {"success": True, "data": {"level": level}}
    
    except Exception as e:
        logger.error(f"获取日志级别失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/level")
async def update_log_level(
    request: Dict[str, str],
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """更新日志级别（需要重启服务）"""
    try:
        level = request.get("level", "INFO")
        
        if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise HTTPException(status_code=400, detail="无效的日志级别")
        
        # 更新环境变量（仅当前进程）
        os.environ["LOG_LEVEL"] = level
        
        # 注意：需要重启服务才能完全生效
        logger.info(f"日志级别已更新为: {level}（需要重启服务）")
        
        return {
            "success": True,
            "message": f"日志级别已更新为 {level}，请重启后端服务使配置生效"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新日志级别失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_logs(current_user: Dict = Depends(get_current_user)) -> Dict[str, Any]:
    """清理过期日志"""
    try:
        import time
        
        RETENTION_DAYS = 90
        cutoff_time = time.time() - (RETENTION_DAYS * 24 * 60 * 60)
        
        deleted_count = 0
        freed_space = 0
        
        if LOG_DIR.exists():
            for log_file in LOG_DIR.glob("*.log.*"):  # 只删除轮转的日志
                try:
                    file_mtime = log_file.stat().st_mtime
                    file_size = log_file.stat().st_size
                    
                    if file_mtime < cutoff_time:
                        log_file.unlink()
                        deleted_count += 1
                        freed_space += file_size
                        logger.info(f"删除过期日志: {log_file.name}")
                except Exception as e:
                    logger.error(f"删除日志文件失败 {log_file.name}: {e}")
        
        return {
            "success": True,
            "data": {
                "deleted_count": deleted_count,
                "freed_space": freed_space
            }
        }
    
    except Exception as e:
        logger.error(f"清理日志失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

