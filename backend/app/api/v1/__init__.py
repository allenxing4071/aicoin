"""API v1 routes"""

# 导出所有API路由模块,供main.py导入使用
from app.api.v1 import (
    market,
    account,
    performance,
    ai,
    admin_db,
    constraints,
    intelligence,
    exchanges,  # v3.1 新增
    market_extended,  # v3.1 新增
)

__all__ = [
    'market',
    'account',
    'performance',
    'ai',
    'admin_db',
    'constraints',
    'intelligence',
    'exchanges',
    'market_extended',
]
