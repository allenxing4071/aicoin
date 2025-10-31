#!/usr/bin/env python3
"""
生成新的Hyperliquid钱包
"""

from eth_account import Account
import secrets

def generate_new_wallet():
    """生成全新的钱包（不使用助记词）"""
    
    print("=" * 80)
    print("🔐 生成新的Hyperliquid钱包")
    print("=" * 80)
    
    # 生成随机私钥
    private_key = "0x" + secrets.token_hex(32)
    
    # 创建账户
    account = Account.from_key(private_key)
    
    print(f"\n✅ 新钱包已生成！")
    print(f"\n地址: {account.address}")
    print(f"私钥: {private_key}")
    
    # 保存到文件
    with open("new_wallet_credentials.txt", "w") as f:
        f.write("=" * 80 + "\n")
        f.write("新Hyperliquid钱包凭证\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"地址: {account.address}\n")
        f.write(f"私钥: {private_key}\n")
        f.write("\n" + "=" * 80 + "\n")
        f.write("⚠️  请妥善保管私钥，不要泄露给任何人！\n")
        f.write("=" * 80 + "\n")
    
    print(f"\n✅ 凭证已保存到: new_wallet_credentials.txt")
    print("\n" + "=" * 80)
    print("⚠️  请妥善保管私钥，不要泄露给任何人！")
    print("=" * 80)
    
    return account.address, private_key

if __name__ == "__main__":
    generate_new_wallet()

