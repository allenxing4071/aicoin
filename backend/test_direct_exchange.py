"""
直接测试Exchange对象，但使用系统的配置
"""
import os
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

# 从环境变量读取配置（系统的配置）
WALLET_ADDRESS = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")

print("=" * 80)
print("🧪 使用系统配置测试Exchange")
print("=" * 80)

print(f"\n配置:")
print(f"  WALLET_ADDRESS: {WALLET_ADDRESS}")
print(f"  PRIVATE_KEY: {PRIVATE_KEY[:10]}...{PRIVATE_KEY[-10:]}")

# 初始化Exchange
wallet = Account.from_key(PRIVATE_KEY)
exchange = Exchange(
    wallet=wallet,
    base_url=constants.MAINNET_API_URL
)

print(f"\n✅ Exchange初始化成功")
print(f"   wallet.address: {wallet.address}")

# 测试1: 下一个0.0001 BTC的单
print(f"\n📤 测试1: BUY 0.0001 BTC")
result1 = exchange.market_open("BTC", True, 0.0001)
print(f"   结果: {result1}")

# 测试2: 下一个0.0022 BTC的单（系统尝试的大小）
print(f"\n📤 测试2: BUY 0.0022 BTC")
result2 = exchange.market_open("BTC", True, 0.0022)
print(f"   结果: {result2}")

print(f"\n🏁 测试完成")

