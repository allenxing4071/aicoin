"""
测试Agent模式下单
"""
import os
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

print("=" * 80)
print("🧪 测试Agent模式下单")
print("=" * 80)

API_WALLET = os.getenv("HYPERLIQUID_WALLET_ADDRESS", "0x4C0F5534CA0f0840a3F39aCD9DAB98cA1EE786Aa")
VAULT_WALLET = os.getenv("HYPERLIQUID_VAULT_ADDRESS", "0xec8443196D64A2d711801171BB7bDfAc448df5c6")
PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY", "")

print(f"\n📋 配置:")
print(f"  API钱包: {API_WALLET}")
print(f"  主钱包: {VAULT_WALLET}")

# 创建wallet对象
if not PRIVATE_KEY.startswith('0x'):
    PRIVATE_KEY = '0x' + PRIVATE_KEY

wallet = Account.from_key(PRIVATE_KEY)
print(f"  Wallet对象地址: {wallet.address}")

# 测试1: 查看主钱包的approvedAgents
print("\n" + "=" * 80)
print("测试1: 查看主钱包是否有授权的代理")
print("=" * 80)

try:
    info = Info(skip_ws=True)
    
    # 尝试获取主钱包的详细信息
    vault_state = info.user_state(VAULT_WALLET)
    
    print(f"\n主钱包状态:")
    print(f"  账户价值: ${vault_state.get('marginSummary', {}).get('accountValue', 'N/A')}")
    
    # 检查是否有approvedAgents字段
    if 'approvedAgents' in vault_state:
        print(f"  授权代理列表: {vault_state['approvedAgents']}")
    else:
        print(f"  ⚠️  主钱包状态中没有'approvedAgents'字段")
        print(f"  这可能意味着:")
        print(f"     1. Hyperliquid不在user_state中返回此信息")
        print(f"     2. 或者需要通过其他API查询")
    
    # 打印所有字段名
    print(f"\n  主钱包状态包含的字段:")
    for key in vault_state.keys():
        print(f"    - {key}")
        
except Exception as e:
    print(f"❌ 查询失败: {e}")

# 测试2: 初始化Exchange（Agent模式）
print("\n" + "=" * 80)
print("测试2: 初始化Exchange（Agent模式）")
print("=" * 80)

try:
    exchange = Exchange(
        wallet=wallet,
        base_url=constants.MAINNET_API_URL,
        vault_address=VAULT_WALLET
    )
    print(f"✅ Exchange初始化成功")
    print(f"  Exchange对象: {exchange}")
    print(f"  Exchange.wallet: {exchange.wallet.address if hasattr(exchange, 'wallet') else 'N/A'}")
    print(f"  Exchange.vault_address: {exchange.vault_address if hasattr(exchange, 'vault_address') else 'N/A'}")
    
except Exception as e:
    print(f"❌ Exchange初始化失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3: 尝试一个极小的市价单（不实际执行，只看错误信息）
print("\n" + "=" * 80)
print("测试3: 尝试下一个极小的测试单")
print("=" * 80)

try:
    exchange = Exchange(
        wallet=wallet,
        base_url=constants.MAINNET_API_URL,
        vault_address=VAULT_WALLET
    )
    
    print(f"\n准备下单:")
    print(f"  交易对: BTC")
    print(f"  方向: BUY")
    print(f"  数量: 0.0001 (极小测试)")
    print(f"  类型: MARKET")
    
    # 尝试下单
    print(f"\n📤 发送订单...")
    result = exchange.market_open("BTC", True, 0.0001)
    
    print(f"\n📥 订单响应:")
    print(f"  类型: {type(result)}")
    print(f"  内容: {result}")
    
    if isinstance(result, dict):
        if result.get("status") == "ok":
            print(f"✅ 订单成功！")
        else:
            print(f"❌ 订单失败:")
            print(f"  状态: {result.get('status')}")
            print(f"  响应: {result.get('response')}")
    
except Exception as e:
    print(f"❌ 下单失败: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 对比直接模式（使用API钱包自己的余额）
print("\n" + "=" * 80)
print("测试4: 对比 - 直接模式（不使用vault）")
print("=" * 80)

try:
    exchange_direct = Exchange(
        wallet=wallet,
        base_url=constants.MAINNET_API_URL
        # 不传vault_address
    )
    
    print(f"✅ Exchange初始化成功（直接模式）")
    
    # 查询API钱包自己的状态
    info = Info(skip_ws=True)
    api_state = info.user_state(API_WALLET)
    
    print(f"\nAPI钱包自己的状态:")
    print(f"  账户价值: ${api_state.get('marginSummary', {}).get('accountValue', 'N/A')}")
    
    if float(api_state.get('marginSummary', {}).get('accountValue', '0')) > 0:
        print(f"\n  API钱包有余额，尝试直接模式下单...")
        
        result = exchange_direct.market_open("BTC", True, 0.0001)
        
        print(f"\n📥 直接模式订单响应:")
        print(f"  类型: {type(result)}")
        print(f"  内容: {result}")
        
        if isinstance(result, dict):
            if result.get("status") == "ok":
                print(f"✅ 直接模式订单成功！")
                print(f"  这说明API钱包本身可以交易")
                print(f"  问题出在Agent模式的授权上")
            else:
                print(f"❌ 直接模式订单也失败:")
                print(f"  状态: {result.get('status')}")
                print(f"  响应: {result.get('response')}")
    else:
        print(f"  ⚠️  API钱包余额为0，无法测试直接模式")
        print(f"  (这是正常的，因为API钱包只是代理)")
    
except Exception as e:
    print(f"❌ 直接模式测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("🏁 测试完成")
print("=" * 80)

