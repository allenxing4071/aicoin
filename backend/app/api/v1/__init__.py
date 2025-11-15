"""API v1 routes"""

# 导出所有API路由模块,供main.py导入使用
from app.api.v1 import (
    market,
    account,
    performance,
    ai,
    admin_db,
    admin_backup,  # 备份和清理功能
    constraints,
    intelligence,
    exchanges,  # v3.1 新增
    market_extended,  # v3.1 新增
    debate,  # v3.4 新增 - 辩论系统
    prompts,  # v3.5 新增 - Prompt模板管理
)

__all__ = [
    'market',
    'account',
    'performance',
    'ai',
    'admin_db',
    'admin_backup',
    'constraints',
    'intelligence',
    'exchanges',
    'market_extended',
    'debate',
    'prompts',
]
