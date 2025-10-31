#!/usr/bin/env python3
"""
从授权地址转账到新账户
"""

import os
import asyncio
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account import Account

async def transfer_funds():
    """尝试从授权地址转账到新账户"""
    
    # 旧账户（主账户）
    OLD_ADDRESS = "0xec8443196D64A2d711801171BB7bDfAc448df5c6"
    OLD_PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")  # 旧账户私钥
    
    # 授权地址（资金所在地）
    AUTHORIZED_ADDRESS = "0x3f341bc48352f165e6c0506dd6602d5701bdef63"
    
    # 新账户（目标地址）
    NEW_ADDRESS = "0x91BF94f0A746657603B6E827c03B2B919e13C41e"
    
    print("=" * 80)
    print("💰 尝试从授权地址转账到新账户")
    print("=" * 80)
    print(f"\n主账户: {OLD_ADDRESS}")
    print(f"授权地址（资金所在）: {AUTHORIZED_ADDRESS}")
    print(f"新账户（目标）: {NEW_ADDRESS}\n")
    
    # 1. 检查授权地址余额
    info = Info(base_url="https://api.hyperliquid.xyz", skip_ws=True)
    
    print("1️⃣  检查授权地址余额...")
    try:
        auth_state = info.user_state(AUTHORIZED_ADDRESS)
        auth_balance = float(auth_state.get("withdrawable", 0))
        print(f"   授权地址余额: ${auth_balance}")
        
        if auth_balance == 0:
            print("   ⚠️  授权地址余额为0，无法转账")
            return
    except Exception as e:
        print(f"   ❌ 获取授权地址余额失败: {e}")
        return
    
    # 2. 尝试方法1: 用主账户私钥签名，从授权地址转账
    print("\n2️⃣  方法1: 用主账户私钥代表授权地址转账...")
    
    try:
        # 创建主账户
        main_account = Account.from_key(OLD_PRIVATE_KEY)
        
        # 创建Exchange实例，使用主账户私钥，但指定vault_address为授权地址
        exchange = Exchange(
            wallet=main_account,
            base_url="https://api.hyperliquid.xyz",
            vault_address=AUTHORIZED_ADDRESS  # 指定从授权地址转账
        )
        
        print(f"   Exchange配置:")
        print(f"      wallet: {exchange.wallet.address}")
        print(f"      vault_address: {exchange.vault_address}")
        print(f"      account_address: {exchange.account_address}")
        
        # 尝试内部转账
        transfer_amount = min(auth_balance, 340.0)  # 转账金额
        
        print(f"\n   尝试转账 ${transfer_amount} 到新账户...")
        
        # 使用Hyperliquid的usd_transfer方法（内部转账）
        # 注意: amount单位是USDC，需要乘以1e6
        result = exchange.usd_transfer(
            destination=NEW_ADDRESS,
            amount=transfer_amount
        )
        
        print(f"   ✅ 转账成功！")
        print(f"   结果: {result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 方法1失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 尝试方法2: 直接提现到新账户
    print("\n3️⃣  方法2: 直接提现到新账户...")
    
    try:
        # 使用withdraw API
        # 注意: Hyperliquid的withdraw是提现到链上，可能需要gas费
        
        print(f"   ⚠️  Hyperliquid提现需要:")
        print(f"      1. 将USDC从Hyperliquid转到Arbitrum链上")
        print(f"      2. 需要支付gas费")
        print(f"      3. 到账时间: 约15-30分钟")
        print(f"\n   暂不执行实际提现，需要您确认后执行")
        
        return False
        
    except Exception as e:
        print(f"   ❌ 方法2失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(transfer_funds())
    
    if success:
        print("\n" + "=" * 80)
        print("✅ 转账成功！请验证新账户余额")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ 转账失败")
        print("\n建议:")
        print("  1. 联系Hyperliquid支持")
        print("  2. 或先用新账户开始交易")
        print("=" * 80)

