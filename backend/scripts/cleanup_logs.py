"""
日志清理脚本
定期清理过期日志文件
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta

LOG_DIR = Path("logs")
RETENTION_DAYS = 90  # 保留90天


def cleanup_old_logs():
    """清理过期日志"""
    if not LOG_DIR.exists():
        print(f"⚠️  日志目录不存在: {LOG_DIR}")
        return
    
    cutoff_time = time.time() - (RETENTION_DAYS * 24 * 60 * 60)
    deleted_count = 0
    deleted_size = 0
    
    print(f"🔍 开始清理 {RETENTION_DAYS} 天前的日志...")
    print(f"📁 日志目录: {LOG_DIR.absolute()}")
    print(f"📅 截止时间: {datetime.fromtimestamp(cutoff_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    for log_file in LOG_DIR.glob("*.log*"):
        try:
            file_mtime = log_file.stat().st_mtime
            file_size = log_file.stat().st_size
            
            if file_mtime < cutoff_time:
                file_date = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d')
                log_file.unlink()
                deleted_count += 1
                deleted_size += file_size
                print(f"🗑️  删除: {log_file.name} ({file_date}, {file_size / 1024:.2f} KB)")
        except Exception as e:
            print(f"❌ 删除失败 {log_file.name}: {e}")
    
    print("-" * 60)
    print(f"✅ 清理完成！")
    print(f"📊 删除文件: {deleted_count} 个")
    print(f"💾 释放空间: {deleted_size / 1024 / 1024:.2f} MB")
    
    # 显示当前日志文件统计
    current_files = list(LOG_DIR.glob("*.log*"))
    if current_files:
        total_size = sum(f.stat().st_size for f in current_files)
        print(f"📁 当前日志: {len(current_files)} 个文件, {total_size / 1024 / 1024:.2f} MB")


def show_log_stats():
    """显示日志统计信息"""
    if not LOG_DIR.exists():
        print(f"⚠️  日志目录不存在: {LOG_DIR}")
        return
    
    print("=" * 60)
    print("📊 日志文件统计")
    print("=" * 60)
    
    log_types = {
        "aicoin_all.log*": "所有日志",
        "aicoin_error.log*": "错误日志",
        "ai_decisions.log*": "AI决策日志",
        "trading.log*": "交易日志"
    }
    
    for pattern, name in log_types.items():
        files = list(LOG_DIR.glob(pattern))
        if files:
            total_size = sum(f.stat().st_size for f in files)
            print(f"{name:12s}: {len(files):3d} 个文件, {total_size / 1024 / 1024:8.2f} MB")
    
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        show_log_stats()
    else:
        cleanup_old_logs()

