"""
Hyperliquid API授权诊断脚本
逐步测试API钱包的各个方面
"""
import os
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
import json

print("=" * 80)
print("🔍 Hyperliquid API授权诊断")
print("=" * 80)

# 读取配置
API_WALLET = os.getenv("HYPERLIQUID_WALLET_ADDRESS", "0x4C0F5534CA0f0840a3F39aCD9DAB98cA1EE786Aa")
VAULT_WALLET = os.getenv("HYPERLIQUID_VAULT_ADDRESS", "0xec8443196D64A2d711801171BB7bDfAc448df5c6")
PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY", "")

print(f"\n📋 配置信息:")
print(f"  API钱包地址: {API_WALLET}")
print(f"  主钱包地址: {VAULT_WALLET}")
print(f"  私钥已配置: {'✅ 是' if PRIVATE_KEY else '❌ 否'}")

# 步骤1: 测试Info API（不需要授权）
print("\n" + "=" * 80)
print("步骤1: 测试Info API（公开接口，不需要授权）")
print("=" * 80)

try:
    info = Info(skip_ws=True)
    
    # 测试获取主钱包信息
    print(f"\n🔍 查询主钱包状态: {VAULT_WALLET}")
    vault_state = info.user_state(VAULT_WALLET)
    
    if vault_state:
        print(f"✅ 主钱包存在！")
        print(f"   账户价值: ${vault_state.get('marginSummary', {}).get('accountValue', 'N/A')}")
        print(f"   持仓数量: {len(vault_state.get('assetPositions', []))}")
    else:
        print(f"❌ 无法获取主钱包信息")
    
    # 测试获取API钱包信息
    print(f"\n🔍 查询API钱包状态: {API_WALLET}")
    api_wallet_state = info.user_state(API_WALLET)
    
    if api_wallet_state:
        print(f"✅ API钱包存在！")
        print(f"   账户价值: ${api_wallet_state.get('marginSummary', {}).get('accountValue', 'N/A')}")
        print(f"   持仓数量: {len(api_wallet_state.get('assetPositions', []))}")
    else:
        print(f"❌ 无法获取API钱包信息")
        print(f"   这可能意味着API钱包还未在Hyperliquid上激活")
    
except Exception as e:
    print(f"❌ Info API测试失败: {e}")

# 步骤2: 测试私钥和地址匹配
print("\n" + "=" * 80)
print("步骤2: 验证私钥和API钱包地址是否匹配")
print("=" * 80)

if PRIVATE_KEY:
    try:
        # 确保私钥格式正确
        if not PRIVATE_KEY.startswith('0x'):
            private_key = '0x' + PRIVATE_KEY
        else:
            private_key = PRIVATE_KEY
            
        account = Account.from_key(private_key)
        derived_address = account.address
        
        print(f"从私钥派生的地址: {derived_address}")
        print(f"配置的API钱包地址: {API_WALLET}")
        
        if derived_address.lower() == API_WALLET.lower():
            print(f"✅ 私钥和地址匹配！")
        else:
            print(f"❌ 私钥和地址不匹配！这是一个严重问题！")
    except Exception as e:
        print(f"❌ 私钥验证失败: {e}")
else:
    print(f"❌ 未配置私钥")

# 步骤3: 测试Exchange API初始化（需要授权）
print("\n" + "=" * 80)
print("步骤3: 测试Exchange API初始化")
print("=" * 80)

if PRIVATE_KEY:
    try:
        # 不使用vault模式
        print("\n🔍 测试1: 直接使用API钱包（不使用vault）")
        exchange_direct = Exchange(
            account=Account.from_key(PRIVATE_KEY if PRIVATE_KEY.startswith('0x') else '0x' + PRIVATE_KEY),
            base_url="https://api.hyperliquid.xyz",
            skip_ws=True
        )
        print("✅ Exchange API初始化成功（直接模式）")
        
        # 使用vault模式
        print(f"\n🔍 测试2: 使用Agent模式（API钱包代理主钱包）")
        exchange_agent = Exchange(
            account=Account.from_key(PRIVATE_KEY if PRIVATE_KEY.startswith('0x') else '0x' + PRIVATE_KEY),
            base_url="https://api.hyperliquid.xyz",
            skip_ws=True,
            vault_address=VAULT_WALLET
        )
        print("✅ Exchange API初始化成功（Agent模式）")
        
    except Exception as e:
        print(f"❌ Exchange API初始化失败: {e}")
else:
    print(f"❌ 未配置私钥，无法测试Exchange API")

# 步骤4: 尝试查询授权状态
print("\n" + "=" * 80)
print("步骤4: 查询API钱包的授权状态")
print("=" * 80)

try:
    info = Info(skip_ws=True)
    
    # 尝试获取主钱包的授权代理列表
    print(f"\n🔍 查询主钱包 {VAULT_WALLET} 的授权代理...")
    
    # Hyperliquid可能有一个API来查询授权的代理
    # 但这个API可能不是公开的，我们尝试通过user_state来推断
    
    vault_state = info.user_state(VAULT_WALLET)
    if vault_state:
        print(f"✅ 成功获取主钱包状态")
        # 打印完整状态以查看是否有授权信息
        print(f"\n📊 主钱包完整状态:")
        print(json.dumps(vault_state, indent=2, default=str))
    
except Exception as e:
    print(f"❌ 查询授权状态失败: {e}")

# 步骤5: 尝试一个简单的只读操作
print("\n" + "=" * 80)
print("步骤5: 测试只读操作（不实际下单）")
print("=" * 80)

if PRIVATE_KEY:
    try:
        exchange = Exchange(
            account=Account.from_key(PRIVATE_KEY if PRIVATE_KEY.startswith('0x') else '0x' + PRIVATE_KEY),
            base_url="https://api.hyperliquid.xyz",
            skip_ws=True,
            vault_address=VAULT_WALLET
        )
        
        # 尝试获取账户状态（这是一个只读操作）
        print(f"\n🔍 尝试通过Exchange API获取账户状态...")
        # 注意：这里我们不能直接调用，因为可能会触发授权检查
        print("⚠️  跳过此测试，因为可能会触发授权检查")
        
    except Exception as e:
        print(f"❌ 只读操作失败: {e}")

print("\n" + "=" * 80)
print("🏁 诊断完成")
print("=" * 80)
print("\n📋 下一步建议:")
print("1. 如果API钱包在Info API中不存在，说明需要先激活")
print("2. 如果私钥和地址不匹配，需要重新生成配置")
print("3. 如果Exchange API初始化失败，可能是网络或配置问题")
print("4. 如果主钱包状态中没有授权信息，可能需要在Hyperliquid网站上完成授权")

