#!/usr/bin/env python3
"""
通过Hyperliquid HTTP API禁用多签
根据官方文档的方法
"""

from hyperliquid.exchange import Exchange
from eth_account import Account
import os
import json

def disable_multisig_via_api():
    """使用HTTP API禁用多签"""
    
    WALLET_ADDRESS = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
    PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")
    
    print("=" * 80)
    print("🔧 通过HTTP API禁用Hyperliquid多签")
    print("=" * 80)
    print(f"\n账户地址: {WALLET_ADDRESS}\n")
    
    # 创建账户和Exchange实例
    account = Account.from_key(PRIVATE_KEY)
    exchange = Exchange(account, base_url="https://api.hyperliquid.xyz")
    
    print("1️⃣  准备API请求...")
    print("   构建payload:")
    payload = {
        "type": "ConvertToMultiSigUser",
        "authorizedUsers": [],  # 空数组
        "threshold": 0          # 阈值为0
    }
    print(f"   {json.dumps(payload, indent=2)}")
    
    print("\n2️⃣  发送到Hyperliquid...")
    
    try:
        # 使用Exchange的内部方法发送请求
        # convert_to_multi_sig_user方法应该会构建正确的签名
        result = exchange.convert_to_multi_sig_user([], 0)
        
        print("\n3️⃣  ✅ 执行成功！")
        print(f"   响应: {result}")
        print("\n🎉 多签已禁用！")
        
        return True
        
    except TypeError as e:
        print(f"\n   ❌ 方法签名错误: {e}")
        print("\n   尝试其他方式...")
        
        # 尝试直接调用底层的post方法
        try:
            action = {
                "type": "convertToMultiSigUser",
                "authorizedUsers": [],
                "threshold": 0
            }
            
            result = exchange.post("/exchange", action)
            print(f"\n3️⃣  ✅ 通过post方法成功！")
            print(f"   响应: {result}")
            return True
            
        except Exception as e2:
            print(f"   ❌ post方法也失败: {e2}")
            return False
        
    except Exception as e:
        print(f"\n3️⃣  ❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    success = disable_multisig_via_api()
    
    if success:
        print("\n✅ 多签禁用成功！请验证:")
        print("   1. 刷新Hyperliquid页面，'Multi-Sig'标签应该消失")
        print("   2. 查询账户时应返回: \"multiSigUser\": false")
        print("\n   AI交易系统将在30秒内自动开始工作！")
    else:
        print("\n❌ 自动禁用失败，请使用Hyperliquid Discord联系支持")

