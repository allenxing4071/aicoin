#!/usr/bin/env python3
"""Test AI decision - standalone script"""

import asyncio
import sys
import os
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/backend')

from app.services.ai.decision_engine import decision_engine
from app.services.market.hyperliquid_client import hyperliquid_client

async def main():
    print("=" * 60)
    print("AIcoin - Testing AI Decision Engine")
    print("=" * 60)
    
    try:
        symbol = "BTC-PERP"
        
        # 1. Get market data
        print(f"\n📊 Fetching market data for {symbol}...")
        klines = await hyperliquid_client.get_klines(symbol, interval="1h", limit=24)
        orderbook = await hyperliquid_client.get_orderbook(symbol, depth=20)
        ticker = await hyperliquid_client.get_ticker(symbol)
        
        current_price = Decimal(ticker['price'])
        print(f"✅ Current price: ${current_price}")
        
        market_data = {
            'current_price': current_price,
            'klines': klines,
            'orderbook': orderbook,
            'ticker': ticker
        }
        
        # 2. Get account info
        print(f"\n💰 Fetching account info...")
        account_balance_data = await hyperliquid_client.get_account_balance()
        positions = await hyperliquid_client.get_positions()
        
        balance = Decimal(account_balance_data['balance'])
        print(f"✅ Balance: ${balance}")
        
        account_info = {
            'balance': balance,
            'position': positions[0] if positions else {}
        }
        
        # 3. Make AI decision
        print(f"\n🤖 Making AI decision...")
        decision, latency_ms = await decision_engine.make_decision(
            symbol=symbol,
            market_data=market_data,
            account_info=account_info
        )
        
        print("\n" + "=" * 60)
        print("AI DECISION RESULT")
        print("=" * 60)
        print(f"Action:     {decision.action}")
        print(f"Size:       {decision.size}")
        print(f"Confidence: {decision.confidence}")
        print(f"Reasoning:  {decision.reasoning}")
        print(f"Latency:    {latency_ms}ms")
        print("=" * 60)
        
        # Close client
        await hyperliquid_client.close()
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

