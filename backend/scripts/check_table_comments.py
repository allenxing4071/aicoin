#!/usr/bin/env python3
"""检查数据库表注释是否包含 emoji"""
import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def check_comments():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("""
            SELECT tablename, obj_description((schemaname || '.' || tablename)::regclass) 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('trades', 'orders', 'market_data_kline', 'risk_events', 
                             'admin_users', 'ai_decisions', 'intelligence_reports')
            ORDER BY tablename
        """))
        rows = result.fetchall()
        
        print("\n📊 数据库表注释检查:")
        print("=" * 80)
        
        has_emoji = False
        for table, comment in rows:
            if comment:
                # 检查是否包含 emoji (Unicode 范围)
                contains_emoji = any(ord(c) > 0x1F300 for c in comment)
                status = "❌ 包含emoji" if contains_emoji else "✅ 纯文字"
                if contains_emoji:
                    has_emoji = True
            else:
                status = "⚠️  无注释"
                comment = "(空)"
            
            print(f"{status} | {table:25s} | {comment[:60]}")
        
        print("=" * 80)
        if has_emoji:
            print("⚠️  发现包含 emoji 的表注释，需要更新")
        else:
            print("✅ 所有表注释都是纯文字，无需更新")

if __name__ == '__main__':
    asyncio.run(check_comments())

