"""
使用系统的HyperliquidTradingService测试下单
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.services.hyperliquid_trading import HyperliquidTradingService

async def test():
    print("=" * 80)
    print("🧪 使用系统的HyperliquidTradingService测试")
    print("=" * 80)
    
    # 初始化服务
    service = HyperliquidTradingService()
    await service.initialize()
    
    print(f"\n✅ 服务已初始化")
    print(f"   is_initialized: {service.is_initialized}")
    print(f"   wallet_address: {service.wallet_address}")
    print(f"   vault_address: {service.vault_address}")
    
    # 尝试下单
    print(f"\n📤 尝试下单: BUY 0.0001 BTC")
    result = await service.place_order(
        symbol="BTC",
        side="buy",
        size=0.0001,  # 直接传BTC数量
        order_type="market"
    )
    
    print(f"\n📥 订单结果:")
    print(f"   {result}")
    
    if result.get("success"):
        print(f"\n✅ 订单成功！")
    else:
        print(f"\n❌ 订单失败: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test())

