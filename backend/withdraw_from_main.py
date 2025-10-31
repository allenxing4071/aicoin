#!/usr/bin/env python3
"""
从主账户提现授权地址的资金
"""

import os
import asyncio
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account import Account

async def withdraw_funds():
    """从主账户提现到新账户"""
    
    # 主账户
    MAIN_ADDRESS = "0xec8443196D64A2d711801171BB7bDfAc448df5c6"
    MAIN_PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")
    
    # 新账户
    NEW_ADDRESS = "0x91BF94f0A746657603B6E827c03B2B919e13C41e"
    
    print("=" * 80)
    print("💰 从主账户提现到新账户（Arbitrum链）")
    print("=" * 80)
    print(f"\n主账户: {MAIN_ADDRESS}")
    print(f"新账户: {NEW_ADDRESS}\n")
    
    # 创建主账户
    main_account = Account.from_key(MAIN_PRIVATE_KEY)
    
    # 创建Exchange实例（不使用vault_address）
    exchange = Exchange(
        wallet=main_account,
        base_url="https://api.hyperliquid.xyz"
    )
    
    info = Info(base_url="https://api.hyperliquid.xyz", skip_ws=True)
    
    # 1. 检查主账户状态
    print("1️⃣  检查主账户状态...")
    try:
        user_state = info.user_state(MAIN_ADDRESS)
        withdrawable = float(user_state.get("withdrawable", 0))
        
        print(f"   账户价值: ${user_state.get('marginSummary', {}).get('accountValue', 0)}")
        print(f"   可提现: ${withdrawable}")
        
        if withdrawable == 0:
            print("\n   ⚠️  主账户可提现余额为0")
            print("   这意味着资金确实被锁定在授权地址中")
            print("   需要授权地址的私钥才能操作")
            return False
            
    except Exception as e:
        print(f"   ❌ 获取账户状态失败: {e}")
        return False
    
    # 2. 如果有可提现余额，尝试提现
    if withdrawable > 0:
        print(f"\n2️⃣  尝试提现 ${withdrawable} 到新账户...")
        
        try:
            # 提现到Arbitrum链上
            result = exchange.withdraw_from_bridge(
                destination=NEW_ADDRESS,
                amount=withdrawable
            )
            
            print(f"   ✅ 提现请求已发送！")
            print(f"   结果: {result}")
            print(f"\n   请等待15-30分钟，资金会到达Arbitrum链上的新地址")
            print(f"   然后需要手动充值回Hyperliquid")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 提现失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return False

if __name__ == "__main__":
    success = asyncio.run(withdraw_funds())
    
    print("\n" + "=" * 80)
    if not success:
        print("❌ 操作失败")
        print("\n💡 结论:")
        print("   • 资金被锁定在授权地址中")
        print("   • 主账户私钥无法直接操作")
        print("   • 必须要授权地址的私钥")
        print("\n🎯 最终建议:")
        print("   1. 继续寻找授权地址私钥（检查所有钱包）")
        print("   2. 联系Hyperliquid支持: https://discord.gg/hyperliquid")
        print("   3. 先用新账户开始交易，$340慢慢找")
    print("=" * 80)

