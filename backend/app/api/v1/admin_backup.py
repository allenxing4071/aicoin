"""数据备份和清理管理API"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, text
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import subprocess
import os
from pathlib import Path

from app.core.database import get_db
from app.api.v1.admin_db import get_current_user
from app.models.trade import Trade
from app.models.order import Order
from app.models.account import AccountSnapshot
from app.models.ai_decision import AIDecision
from app.models.market_data import MarketDataKline
from app.models.risk_event import RiskEvent

router = APIRouter()
logger = logging.getLogger(__name__)

# 备份目录配置
BACKUP_DIR = Path("/app/backups")
BACKUP_DIR.mkdir(exist_ok=True)


class BackupRequest(BaseModel):
    """备份请求"""
    include_tables: List[str] = ["all"]  # all, trades, orders, accounts, ai_decisions, market_data, risk_events
    compress: bool = True


class CleanupRequest(BaseModel):
    """清理请求"""
    table: str  # trades, orders, accounts, ai_decisions, market_data, risk_events
    days_to_keep: int = 30  # 保留最近N天的数据
    confirm: bool = False  # 必须确认才能执行


class BackupInfo(BaseModel):
    """备份信息"""
    filename: str
    size: str
    created_at: str
    tables: List[str]


class CleanupResult(BaseModel):
    """清理结果"""
    table: str
    deleted_count: int
    kept_count: int
    message: str


@router.post("/backup")
async def create_backup(
    request: BackupRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    创建数据库备份
    
    支持：
    - 全量备份
    - 指定表备份
    - 压缩备份
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"aicoin_backup_{timestamp}.sql"
        
        if request.compress:
            backup_filename += ".gz"
        
        backup_path = BACKUP_DIR / backup_filename
        
        # 构建pg_dump命令
        tables = []
        if "all" not in request.include_tables:
            # 指定表备份
            table_mapping = {
                "trades": "trades",
                "orders": "orders",
                "accounts": "account_snapshots",
                "ai_decisions": "ai_decisions",
                "market_data": "market_data_klines",
                "risk_events": "risk_events"
            }
            tables = [table_mapping.get(t, t) for t in request.include_tables]
        
        # 获取数据库连接信息
        db_url = os.getenv("DATABASE_URL", "postgresql://aicoin:password@postgres:5432/aicoin")
        # 解析数据库URL
        import re
        match = re.match(r'postgresql\+?.*://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
        if not match:
            raise ValueError("Invalid DATABASE_URL format")
        
        user, password, host, port, database = match.groups()
        
        # 构建备份命令
        cmd = [
            "pg_dump",
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", database,
            "--clean",
            "--if-exists"
        ]
        
        # 添加表过滤
        for table in tables:
            cmd.extend(["-t", table])
        
        # 执行备份
        env = os.environ.copy()
        env["PGPASSWORD"] = password
        
        logger.info(f"开始备份数据库: {backup_filename}")
        
        with open(backup_path, "wb") as f:
            if request.compress:
                # 使用gzip压缩
                import gzip
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"Backup failed: {stderr.decode()}")
                
                with gzip.open(backup_path, "wb") as gz:
                    gz.write(stdout)
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    env=env
                )
                _, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"Backup failed: {stderr.decode()}")
        
        # 获取备份文件大小
        size = backup_path.stat().st_size
        size_str = f"{size / 1024 / 1024:.2f} MB" if size > 1024 * 1024 else f"{size / 1024:.2f} KB"
        
        logger.info(f"备份完成: {backup_filename} ({size_str})")
        
        return {
            "success": True,
            "data": {
                "filename": backup_filename,
                "size": size_str,
                "path": str(backup_path),
                "tables": request.include_tables,
                "created_at": datetime.now().isoformat()
            },
            "message": "备份创建成功"
        }
        
    except Exception as e:
        logger.error(f"创建备份失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"备份失败: {str(e)}")


@router.get("/backups")
async def list_backups(
    current_user: str = Depends(get_current_user)
):
    """
    列出所有备份文件
    """
    try:
        backups = []
        
        for backup_file in BACKUP_DIR.glob("aicoin_backup_*.sql*"):
            stat = backup_file.stat()
            size = stat.st_size
            size_str = f"{size / 1024 / 1024:.2f} MB" if size > 1024 * 1024 else f"{size / 1024:.2f} KB"
            
            backups.append({
                "filename": backup_file.name,
                "size": size_str,
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(backup_file)
            })
        
        # 按创建时间倒序排列
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "data": backups,
            "total": len(backups)
        }
        
    except Exception as e:
        logger.error(f"列出备份失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出备份失败: {str(e)}")


@router.delete("/delete/{filename}")
async def delete_backup(
    filename: str,
    current_user: str = Depends(get_current_user)
):
    """
    删除指定的备份文件
    """
    try:
        # 安全检查：只允许删除备份文件
        if not filename.startswith("aicoin_backup_"):
            raise HTTPException(status_code=400, detail="无效的备份文件名")
        
        backup_path = BACKUP_DIR / filename
        
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="备份文件不存在")
        
        # 删除文件
        backup_path.unlink()
        
        logger.info(f"备份文件已删除: {filename}")
        
        return {
            "success": True,
            "message": f"备份文件 {filename} 已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除备份失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除备份失败: {str(e)}")


@router.post("/auto-cleanup")
async def auto_cleanup_old_backups(
    max_backups: int = 7,
    current_user: str = Depends(get_current_user)
):
    """
    自动清理旧备份，只保留最近的N个
    """
    try:
        backups = sorted(
            BACKUP_DIR.glob("aicoin_backup_*.sql*"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        deleted_count = 0
        if len(backups) > max_backups:
            for backup in backups[max_backups:]:
                backup.unlink()
                logger.info(f"自动删除旧备份: {backup.name}")
                deleted_count += 1
        
        return {
            "success": True,
            "data": {
                "total_backups": len(backups),
                "deleted_count": deleted_count,
                "kept_count": min(len(backups), max_backups)
            },
            "message": f"已清理 {deleted_count} 个旧备份"
        }
        
    except Exception as e:
        logger.error(f"清理旧备份失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"清理旧备份失败: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_data(
    request: CleanupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    清理旧数据
    
    ⚠️ 危险操作！需要确认
    """
    try:
        if not request.confirm:
            raise HTTPException(
                status_code=400,
                detail="必须确认才能执行清理操作 (confirm=true)"
            )
        
        # 计算截止日期
        cutoff_date = datetime.utcnow() - timedelta(days=request.days_to_keep)
        
        # 根据表名选择模型
        model_mapping = {
            "trades": Trade,
            "orders": Order,
            "accounts": AccountSnapshot,
            "ai_decisions": AIDecision,
            "market_data": MarketDataKline,
            "risk_events": RiskEvent
        }
        
        # 支持清理所有表
        if request.table == "all":
            total_deleted = 0
            total_kept = 0
            results = {}
            
            for table_name, model in model_mapping.items():
                # 统计要删除的记录数
                count_query = select(func.count()).select_from(model).where(
                    model.created_at < cutoff_date
                )
                result = await db.execute(count_query)
                delete_count = result.scalar()
                
                # 统计保留的记录数
                keep_query = select(func.count()).select_from(model).where(
                    model.created_at >= cutoff_date
                )
                result = await db.execute(keep_query)
                keep_count = result.scalar()
                
                # 执行删除
                if delete_count > 0:
                    delete_stmt = delete(model).where(model.created_at < cutoff_date)
                    await db.execute(delete_stmt)
                
                total_deleted += delete_count
                total_kept += keep_count
                results[table_name] = {
                    "deleted": delete_count,
                    "kept": keep_count
                }
                
                logger.info(f"清理 {table_name}: 删除 {delete_count} 条, 保留 {keep_count} 条")
            
            await db.commit()
            
            return {
                "success": True,
                "data": {
                    "table": "all",
                    "deleted_count": total_deleted,
                    "kept_count": total_kept,
                    "cutoff_date": cutoff_date.isoformat(),
                    "days_kept": request.days_to_keep,
                    "details": results
                },
                "message": f"成功清理所有表，共删除 {total_deleted} 条旧数据"
            }
        
        # 清理单个表
        if request.table not in model_mapping:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的表名: {request.table}。支持的表: {', '.join(model_mapping.keys())}, all"
            )
        
        model = model_mapping[request.table]
        
        # 统计要删除的记录数
        count_query = select(func.count()).select_from(model).where(
            model.created_at < cutoff_date
        )
        result = await db.execute(count_query)
        delete_count = result.scalar()
        
        # 统计保留的记录数
        keep_query = select(func.count()).select_from(model).where(
            model.created_at >= cutoff_date
        )
        result = await db.execute(keep_query)
        keep_count = result.scalar()
        
        # 执行删除
        delete_stmt = delete(model).where(model.created_at < cutoff_date)
        await db.execute(delete_stmt)
        await db.commit()
        
        logger.info(f"清理完成: {request.table}, 删除 {delete_count} 条, 保留 {keep_count} 条")
        
        return {
            "success": True,
            "data": {
                "table": request.table,
                "deleted_count": delete_count,
                "kept_count": keep_count,
                "cutoff_date": cutoff_date.isoformat(),
                "days_kept": request.days_to_keep
            },
            "message": f"成功清理 {delete_count} 条旧数据"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"清理数据失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")


@router.get("/stats")
async def get_data_stats(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    获取数据统计信息
    """
    try:
        stats = {}
        
        # 统计各表的记录数和最早/最新记录时间
        models = {
            "trades": Trade,
            "orders": Order,
            "accounts": AccountSnapshot,
            "ai_decisions": AIDecision,
            "market_data": MarketDataKline,
            "risk_events": RiskEvent
        }
        
        for table_name, model in models.items():
            # 总记录数
            count_query = select(func.count()).select_from(model)
            result = await db.execute(count_query)
            total = result.scalar()
            
            # 最早记录
            min_query = select(func.min(model.created_at)).select_from(model)
            result = await db.execute(min_query)
            oldest = result.scalar()
            
            # 最新记录
            max_query = select(func.max(model.created_at)).select_from(model)
            result = await db.execute(max_query)
            newest = result.scalar()
            
            stats[table_name] = {
                "total": total,
                "oldest": oldest.isoformat() if oldest else None,
                "newest": newest.isoformat() if newest else None,
                "days_span": (newest - oldest).days if oldest and newest else 0
            }
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.post("/auto-cleanup")
async def setup_auto_cleanup(
    enabled: bool,
    days_to_keep: int = 30,
    schedule: str = "daily",  # daily, weekly, monthly
    current_user: str = Depends(get_current_user)
):
    """
    配置自动清理任务
    
    TODO: 实现定时任务调度
    """
    return {
        "success": True,
        "message": "自动清理功能待实现",
        "config": {
            "enabled": enabled,
            "days_to_keep": days_to_keep,
            "schedule": schedule
        }
    }

