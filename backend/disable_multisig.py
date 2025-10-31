#!/usr/bin/env python3
"""
Hyperliquid禁用多签脚本

警告: 此操作将移除账户的多签保护！
确保您了解这个操作的影响。
"""

from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from eth_account import Account
import os
import json

def disable_multisig():
    """禁用多签功能"""
    
    WALLET_ADDRESS = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
    PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")
    
    print("=" * 80)
    print("🔧 Hyperliquid多签禁用工具")
    print("=" * 80)
    print(f"\n账户地址: {WALLET_ADDRESS}")
    
    # 创建账户和Exchange实例
    account = Account.from_key(PRIVATE_KEY)
    exchange = Exchange(account, base_url="https://api.hyperliquid.xyz")
    info = Info(base_url="https://api.hyperliquid.xyz", skip_ws=True)
    
    # 1. 检查当前多签状态
    print("\n1️⃣  检查当前多签状态...")
    multisig_info = info.query_user_to_multi_sig_signers(WALLET_ADDRESS)
    
    if not multisig_info or not multisig_info.get('authorizedUsers'):
        print("   ✅ 账户未启用多签或已禁用")
        return
    
    print(f"   当前多签配置:")
    print(f"      授权用户: {multisig_info.get('authorizedUsers')}")
    print(f"      阈值: {multisig_info.get('threshold')}")
    
    # 2. 尝试禁用多签
    print("\n2️⃣  尝试禁用多签...")
    
    # 检查Exchange类是否有禁用多签的方法
    if hasattr(exchange, 'convert_to_normal_user'):
        print("   找到convert_to_normal_user方法")
        try:
            result = exchange.convert_to_normal_user()
            print(f"   ✅ 结果: {result}")
        except Exception as e:
            print(f"   ❌ 失败: {e}")
    else:
        print("   ⚠️  SDK中未找到直接禁用多签的方法")
        print("\n   📋 可用的多签相关方法:")
        methods = [m for m in dir(exchange) if 'multi' in m.lower() or 'sig' in m.lower()]
        for m in methods:
            print(f"      • {m}")
        
        print("\n   💡 建议:")
        print("      1. 在Hyperliquid网页UI手动操作")
        print("      2. 或联系Hyperliquid支持")
        print("      3. Discord: https://discord.gg/hyperliquid")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        disable_multisig()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

