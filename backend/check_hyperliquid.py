import asyncio
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account import Account
import os

WALLET_ADDRESS = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")

async def check_account():
    print("=" * 80)
    print("🔍 Hyperliquid账户详细检查")
    print("=" * 80)
    
    info = Info(base_url="https://api.hyperliquid.xyz", skip_ws=True)
    
    print(f"\n账户地址: {WALLET_ADDRESS}")
    
    # 获取账户状态
    print("\n1️⃣  账户状态...")
    user_state = info.user_state(WALLET_ADDRESS)
    
    margin_summary = user_state.get("marginSummary", {})
    print(f"   accountValue: ${margin_summary.get(\"accountValue\")}")
    print(f"   totalNtlPos: ${margin_summary.get(\"totalNtlPos\")}")
    print(f"   totalRawUsd: ${margin_summary.get(\"totalRawUsd\")}")
    
    # 检查withdrawable
    print(f"   withdrawable: ${user_state.get(\"withdrawable\")}")
    
    # 检查crossMarginSummary
    if "crossMarginSummary" in user_state:
        print("   ⚠️  有crossMarginSummary字段")
        print(f"      {user_state[\"crossMarginSummary\"]}")
    
    # 检查assetPositions
    positions = user_state.get("assetPositions", [])
    print(f"\n2️⃣  持仓数量: {len(positions)}")
    for pos in positions[:3]:
        print(f"   - {pos.get(\"position\", {}).get(\"coin\")}: {pos.get(\"position\", {}).get(\"szi\")}")
    
    # 创建Exchange测试
    print("\n3️⃣  Exchange配置...")
    account = Account.from_key(PRIVATE_KEY)
    
    # 测试1: 无vault
    exchange1 = Exchange(account, base_url="https://api.hyperliquid.xyz", vault_address=None)
    print(f"   模式1 (无vault):")
    print(f"      wallet: {exchange1.wallet}")
    print(f"      vault_address: {exchange1.vault_address}")
    print(f"      account_address: {exchange1.account_address}")
    
    # 测试2: 自己作为vault
    try:
        exchange2 = Exchange(account, base_url="https://api.hyperliquid.xyz", vault_address=WALLET_ADDRESS)
        print(f"   模式2 (自己为vault):")
        print(f"      wallet: {exchange2.wallet}")
        print(f"      vault_address: {exchange2.vault_address}")
        print(f"      account_address: {exchange2.account_address}")
    except Exception as e:
        print(f"   模式2失败: {e}")
    
    print("\n" + "=" * 80)
    
asyncio.run(check_account())
