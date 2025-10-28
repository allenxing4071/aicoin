"""
测试主钱包和私钥
"""
import os
from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

WALLET_ADDRESS = "0xec8443196D64A2d711801171BB7bDfAc448df5c6"
PRIVATE_KEY = "0x3f2a59605269d7ff7ce67d31d3cbcb52cdb88c26bcd90724cb6cc4019d56849d"

print("=" * 80)
print("🔍 测试主钱包")
print("=" * 80)

print(f"\n配置的钱包地址: {WALLET_ADDRESS}")
print(f"配置的私钥: {PRIVATE_KEY[:10]}...{PRIVATE_KEY[-10:]}")

# 1. 验证私钥和地址匹配
print("\n" + "=" * 80)
print("步骤1: 验证私钥和地址是否匹配")
print("=" * 80)

try:
    account = Account.from_key(PRIVATE_KEY)
    derived_address = account.address
    
    print(f"从私钥派生的地址: {derived_address}")
    print(f"配置的钱包地址: {WALLET_ADDRESS}")
    
    if derived_address.lower() == WALLET_ADDRESS.lower():
        print(f"✅ 私钥和地址匹配！")
    else:
        print(f"❌ 私钥和地址不匹配！")
        print(f"   这是问题的根源！")
except Exception as e:
    print(f"❌ 验证失败: {e}")

# 2. 查询钱包状态
print("\n" + "=" * 80)
print("步骤2: 查询钱包在Hyperliquid上的状态")
print("=" * 80)

try:
    info = Info(skip_ws=True)
    state = info.user_state(WALLET_ADDRESS)
    
    if state:
        print(f"✅ 钱包存在！")
        print(f"   账户价值: ${state.get('marginSummary', {}).get('accountValue', 'N/A')}")
    else:
        print(f"❌ 钱包不存在或无法查询")
except Exception as e:
    print(f"❌ 查询失败: {e}")

# 3. 尝试初始化Exchange并下单
print("\n" + "=" * 80)
print("步骤3: 尝试初始化Exchange并测试下单")
print("=" * 80)

try:
    wallet = Account.from_key(PRIVATE_KEY)
    exchange = Exchange(
        wallet=wallet,
        base_url=constants.MAINNET_API_URL
    )
    
    print(f"✅ Exchange初始化成功")
    print(f"   Exchange.wallet.address: {exchange.wallet.address}")
    
    # 尝试下一个极小的测试单
    print(f"\n📤 尝试下单: BUY 0.0001 BTC (市价)")
    result = exchange.market_open("BTC", True, 0.0001)
    
    print(f"\n📥 订单响应:")
    print(f"   类型: {type(result)}")
    print(f"   内容: {result}")
    
    if isinstance(result, dict):
        if result.get("status") == "ok":
            print(f"✅ 订单成功！")
        else:
            print(f"❌ 订单失败:")
            print(f"   状态: {result.get('status')}")
            print(f"   响应: {result.get('response')}")
    
except Exception as e:
    print(f"❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("🏁 测试完成")
print("=" * 80)

