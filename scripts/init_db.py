#!/usr/bin/env python3
"""Initialize database - creates all tables"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/backend')

from app.core.database import init_db

async def main():
    print("Initializing database...")
    try:
        await init_db()
        print("✅ Database initialized successfully!")
        print("All tables created.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

