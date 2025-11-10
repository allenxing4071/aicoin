"""
直接创建KOL和聪明钱相关表的脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def create_tables():
    """创建KOL和聪明钱相关表"""
    async with AsyncSessionLocal() as db:
        try:
            # 创建KOL数据源表
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS kol_sources (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    platform VARCHAR(50) NOT NULL,
                    channel_id VARCHAR(200) NOT NULL,
                    influence_score FLOAT DEFAULT 0.0,
                    accuracy_rate FLOAT DEFAULT 0.0,
                    enabled BOOLEAN DEFAULT true,
                    last_update TIMESTAMP WITH TIME ZONE,
                    total_posts INTEGER DEFAULT 0,
                    successful_predictions INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            print("✅ 创建 kol_sources 表成功")

            # 创建KOL意见表
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS kol_opinions (
                    id SERIAL PRIMARY KEY,
                    kol_id INTEGER NOT NULL REFERENCES kol_sources(id) ON DELETE CASCADE,
                    platform VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    sentiment VARCHAR(20),
                    mentioned_coins JSONB,
                    confidence FLOAT,
                    post_url VARCHAR(500),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            print("✅ 创建 kol_opinions 表成功")
            
            await db.execute(text("CREATE INDEX IF NOT EXISTS idx_kol_opinions_created_at ON kol_opinions(created_at)"))
            await db.execute(text("CREATE INDEX IF NOT EXISTS idx_kol_opinions_kol_id ON kol_opinions(kol_id)"))
            print("✅ 创建 kol_opinions 索引成功")

            # 创建聪明钱钱包表
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS smart_money_wallets (
                    id SERIAL PRIMARY KEY,
                    wallet_address VARCHAR(200) NOT NULL UNIQUE,
                    nickname VARCHAR(200),
                    chain VARCHAR(50) NOT NULL,
                    total_profit NUMERIC(20, 8) DEFAULT 0,
                    win_rate FLOAT DEFAULT 0.0,
                    avg_holding_time INTEGER,
                    tracked_since TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    enabled BOOLEAN DEFAULT true,
                    tags JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            print("✅ 创建 smart_money_wallets 表成功")
            
            await db.execute(text("CREATE INDEX IF NOT EXISTS idx_smart_money_wallets_address ON smart_money_wallets(wallet_address)"))
            print("✅ 创建 smart_money_wallets 索引成功")

            # 创建聪明钱交易表
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS smart_money_transactions (
                    id SERIAL PRIMARY KEY,
                    wallet_id INTEGER NOT NULL REFERENCES smart_money_wallets(id) ON DELETE CASCADE,
                    tx_hash VARCHAR(200) NOT NULL UNIQUE,
                    action VARCHAR(20) NOT NULL,
                    token_in VARCHAR(100),
                    token_out VARCHAR(100),
                    amount_in NUMERIC(30, 18),
                    amount_out NUMERIC(30, 18),
                    price_usd NUMERIC(20, 8),
                    profit_usd NUMERIC(20, 8),
                    dex VARCHAR(100),
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            print("✅ 创建 smart_money_transactions 表成功")
            
            await db.execute(text("CREATE INDEX IF NOT EXISTS idx_smart_money_tx_hash ON smart_money_transactions(tx_hash)"))
            await db.execute(text("CREATE INDEX IF NOT EXISTS idx_smart_money_tx_timestamp ON smart_money_transactions(timestamp)"))
            await db.execute(text("CREATE INDEX IF NOT EXISTS idx_smart_money_tx_wallet_id ON smart_money_transactions(wallet_id)"))
            print("✅ 创建 smart_money_transactions 索引成功")

            await db.commit()
            print("\n🎉 所有表创建成功！")

        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(create_tables())

