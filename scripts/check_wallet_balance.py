#!/usr/bin/env python3
"""
钱包余额检查脚本
用于监控新钱包的余额和状态
"""

import requests
import json
from datetime import datetime

# 新钱包地址
WALLET_ADDRESS = "0x5Be3c6B0AC337ed37f93297b7Fe0233e8bb3E741"

def print_header():
    print("\n" + "=" * 70)
    print("🔍 AIcoin 钱包余额检查")
    print("=" * 70)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"钱包地址: {WALLET_ADDRESS}")
    print("=" * 70 + "\n")

def check_hyperliquid_balance():
    """检查 Hyperliquid 账户余额"""
    print("📊 Hyperliquid 账户状态")
    print("-" * 70)
    
    try:
        response = requests.post(
            "https://api.hyperliquid.xyz/info",
            headers={"Content-Type": "application/json"},
            json={"type": "clearinghouseState", "user": WALLET_ADDRESS},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            margin_summary = data.get("marginSummary", {})
            
            account_value = float(margin_summary.get("accountValue", 0))
            total_margin = float(margin_summary.get("totalMarginUsed", 0))
            available = account_value - total_margin
            
            print(f"✅ 连接成功")
            print(f"账户总价值: ${account_value:.2f} USDC")
            print(f"已使用保证金: ${total_margin:.2f} USDC")
            print(f"可用余额: ${available:.2f} USDC")
            
            # 持仓信息
            positions = data.get("assetPositions", [])
            print(f"\n当前持仓: {len(positions)} 个")
            
            if positions:
                for pos in positions:
                    position = pos.get("position", {})
                    coin = position.get("coin", "Unknown")
                    size = float(position.get("szi", 0))
                    entry_px = float(position.get("entryPx", 0))
                    unrealized_pnl = float(position.get("unrealizedPnl", 0))
                    
                    pnl_emoji = "📈" if unrealized_pnl > 0 else "📉"
                    print(f"  {pnl_emoji} {coin}: {size} @ ${entry_px:.4f} (PnL: ${unrealized_pnl:.2f})")
            else:
                print("  无持仓")
            
            return True
        else:
            print(f"❌ API错误: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def check_arbitrum_balance():
    """检查 Arbitrum 链上余额"""
    print("\n📊 Arbitrum 链上余额")
    print("-" * 70)
    
    try:
        # 检查 ETH 余额
        response = requests.post(
            "https://arb1.arbitrum.io/rpc",
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [WALLET_ADDRESS, "latest"],
                "id": 1
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json().get("result", "0x0")
            eth_balance = int(result, 16) / 1e18
            print(f"ETH 余额: {eth_balance:.6f} ETH")
        
        # 检查 USDC 余额 (Arbitrum USDC: 0xaf88d065e77c8cC2239327C5EDb3A432268e5831)
        usdc_contract = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"
        data = "0x70a08231000000000000000000000000" + WALLET_ADDRESS[2:].lower()
        
        response = requests.post(
            "https://arb1.arbitrum.io/rpc",
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [{"to": usdc_contract, "data": data}, "latest"],
                "id": 2
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json().get("result", "0x0")
            usdc_balance = int(result, 16) / 1e6  # USDC has 6 decimals
            print(f"USDC 余额: {usdc_balance:.2f} USDC")
        
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def check_system_status():
    """检查系统API状态"""
    print("\n📊 系统API状态")
    print("-" * 70)
    
    try:
        # 检查性能指标API
        response = requests.get("http://localhost:8000/api/v1/performance/metrics", timeout=5)
        if response.status_code == 200:
            print("✅ 性能指标API: 正常")
        else:
            print(f"⚠️ 性能指标API: 错误 ({response.status_code})")
        
        # 检查约束状态API
        response = requests.get("http://localhost:8000/api/v1/constraints/status", timeout=5)
        if response.status_code == 200:
            print("✅ 约束状态API: 正常")
        else:
            print(f"⚠️ 约束状态API: 错误 ({response.status_code})")
        
        # 检查持仓API
        response = requests.get("http://localhost:8000/api/v1/trading/positions", timeout=5)
        if response.status_code == 200:
            print("✅ 持仓API: 正常")
        else:
            print(f"⚠️ 持仓API: 错误 ({response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统API连接失败: {e}")
        print("提示: 请确保Docker容器正在运行")
        return False

def print_footer():
    print("\n" + "=" * 70)
    print("✅ 检查完成")
    print("=" * 70)
    print("\n提示:")
    print("  - 定期运行此脚本以监控钱包状态")
    print("  - 如发现异常，请立即检查")
    print("  - 保护好私钥，不要泄露")
    print("\n")

def main():
    print_header()
    
    # 检查 Hyperliquid
    hyperliquid_ok = check_hyperliquid_balance()
    
    # 检查 Arbitrum
    arbitrum_ok = check_arbitrum_balance()
    
    # 检查系统API
    system_ok = check_system_status()
    
    print_footer()
    
    # 返回状态码
    if hyperliquid_ok and arbitrum_ok and system_ok:
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main())
