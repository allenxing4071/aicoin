"""
数据库管理 API
提供数据库连接信息、表结构和数据查看功能
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, inspect
from typing import List, Dict, Any
import logging

from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/database/stats", summary="获取数据库统计信息")
async def get_database_stats(db: AsyncSession = Depends(get_db)):
    """
    获取数据库连接状态和统计信息
    """
    try:
        # 获取数据库名称
        result = await db.execute(text("SELECT current_database()"))
        db_name = result.scalar()
        
        # 获取数据库大小
        result = await db.execute(text(
            "SELECT pg_size_pretty(pg_database_size(current_database()))"
        ))
        db_size = result.scalar()
        
        # 获取表数量
        result = await db.execute(text(
            """
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """
        ))
        table_count = result.scalar()
        
        return {
            "database_name": db_name,
            "database_size": db_size,
            "total_tables": table_count,
            "connection_status": "已连接"
        }
        
    except Exception as e:
        logger.error(f"获取数据库统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据库信息失败: {str(e)}")


@router.get("/database/tables", summary="获取所有数据表信息")
async def get_all_tables(db: AsyncSession = Depends(get_db)):
    """
    获取数据库中所有表的列表及其基本信息
    """
    try:
        # 首先获取所有表名
        tables_result = await db.execute(text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' 
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
        ))
        
        tables = []
        for row in tables_result:
            table_name = row[0]
            
            # 获取行数（每个表单独查询，更安全）
            try:
                count_result = await db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = count_result.scalar() or 0
            except Exception as e:
                logger.warning(f"无法获取表 {table_name} 的行数: {e}")
                row_count = 0
            
            # 获取表的列信息
            columns_result = await db.execute(text(
                """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                  AND table_name = :table_name
                ORDER BY ordinal_position
                """
            ), {"table_name": table_name})
            
            columns = [
                {
                    "column_name": col[0],
                    "data_type": col[1],
                    "is_nullable": col[2],
                    "column_default": col[3]
                }
                for col in columns_result
            ]
            
            tables.append({
                "table_name": table_name,
                "row_count": row_count,
                "columns": columns
            })
        
        return tables
        
    except Exception as e:
        logger.error(f"获取表列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取表列表失败: {str(e)}")


@router.get("/database/tables/{table_name}/data", summary="获取表数据")
async def get_table_data(
    table_name: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定表的数据（只读）
    
    参数:
    - table_name: 表名
    - limit: 返回的最大行数（默认50）
    - offset: 偏移量（用于分页）
    """
    try:
        # 安全检查：确保表名只包含字母、数字和下划线
        if not table_name.replace("_", "").isalnum():
            raise HTTPException(status_code=400, detail="无效的表名")
        
        # 查询数据
        query = text(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT :limit OFFSET :offset")
        result = await db.execute(query, {"limit": limit, "offset": offset})
        
        # 将结果转换为字典列表
        columns = result.keys()
        data = []
        for row in result:
            row_dict = {}
            for i, col_name in enumerate(columns):
                value = row[i]
                # 处理特殊类型
                if hasattr(value, 'isoformat'):  # datetime objects
                    value = value.isoformat()
                elif isinstance(value, (dict, list)):  # JSON objects
                    pass  # 保持原样
                row_dict[col_name] = value
            data.append(row_dict)
        
        return data
        
    except Exception as e:
        logger.error(f"获取表数据失败 ({table_name}): {e}")
        raise HTTPException(status_code=500, detail=f"获取表数据失败: {str(e)}")


@router.get("/database/tables/{table_name}/schema", summary="获取表结构")
async def get_table_schema(
    table_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定表的详细结构信息
    """
    try:
        # 安全检查
        if not table_name.replace("_", "").isalnum():
            raise HTTPException(status_code=400, detail="无效的表名")
        
        # 获取列信息
        result = await db.execute(text(
            """
            SELECT 
                c.column_name,
                c.data_type,
                c.character_maximum_length,
                c.is_nullable,
                c.column_default,
                pgd.description
            FROM information_schema.columns c
            LEFT JOIN pg_catalog.pg_statio_all_tables st 
                ON c.table_name = st.relname
            LEFT JOIN pg_catalog.pg_description pgd 
                ON pgd.objoid = st.relid 
                AND pgd.objsubid = c.ordinal_position
            WHERE c.table_schema = 'public' 
              AND c.table_name = :table_name
            ORDER BY c.ordinal_position
            """
        ), {"table_name": table_name})
        
        columns = [
            {
                "column_name": row[0],
                "data_type": row[1],
                "max_length": row[2],
                "is_nullable": row[3],
                "default_value": row[4],
                "description": row[5]
            }
            for row in result
        ]
        
        # 获取索引信息
        indexes_result = await db.execute(text(
            """
            SELECT
                i.indexname,
                i.indexdef
            FROM pg_indexes i
            WHERE i.schemaname = 'public' 
              AND i.tablename = :table_name
            """
        ), {"table_name": table_name})
        
        indexes = [
            {"index_name": row[0], "definition": row[1]}
            for row in indexes_result
        ]
        
        return {
            "table_name": table_name,
            "columns": columns,
            "indexes": indexes
        }
        
    except Exception as e:
        logger.error(f"获取表结构失败 ({table_name}): {e}")
        raise HTTPException(status_code=500, detail=f"获取表结构失败: {str(e)}")

