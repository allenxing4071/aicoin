"""验证数据库表注释"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def verify_table_comments():
    """验证表注释是否已更新"""
    
    print("🔍 正在验证数据库表注释...\n")
    
    async with AsyncSessionLocal() as db:
        # 查询表注释
        sql = text("""
            SELECT 
                table_name, 
                obj_description((table_schema||'.'||table_name)::regclass) as comment
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN (
                'intelligence_platforms',
                'intelligence_source_weights',
                'intelligence_feedback',
                'intelligence_reports',
                'exchange_configs'
            )
            ORDER BY table_name;
        """)
        
        result = await db.execute(sql)
        rows = result.fetchall()
        
        if not rows:
            print("❌ 未找到任何表或注释未更新")
            return
        
        print("📊 数据库表注释状态：\n")
        print("-" * 80)
        
        for row in rows:
            table_name = row[0]
            comment = row[1] if row[1] else "❌ 无注释"
            
            print(f"表名: {table_name}")
            print(f"注释: {comment}")
            print("-" * 80)
        
        print(f"\n✅ 共检查了 {len(rows)} 个表")


if __name__ == "__main__":
    asyncio.run(verify_table_comments())

