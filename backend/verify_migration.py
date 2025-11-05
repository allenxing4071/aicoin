#!/usr/bin/env python3
"""
验证v3.1迁移文件的正确性
不执行真实的数据库操作,只检查语法和结构
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def verify_migration_file():
    """验证迁移文件"""
    print("🔍 开始验证v3.1迁移文件...")
    print("="*60)
    
    migration_file = Path(__file__).parent / "alembic" / "versions" / "010_add_exchange_support.py"
    
    # 检查文件是否存在
    print(f"\n1. 检查文件存在性...")
    if not migration_file.exists():
        print(f"   ❌ 迁移文件不存在: {migration_file}")
        return False
    print(f"   ✅ 文件存在: {migration_file}")
    
    # 读取文件内容
    print(f"\n2. 读取文件内容...")
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"   ✅ 文件读取成功 ({len(content)} 字符)")
    except Exception as e:
        print(f"   ❌ 文件读取失败: {e}")
        return False
    
    # 检查关键内容
    print(f"\n3. 检查迁移文件结构...")
    checks = {
        "revision = '010'": "版本号",
        "down_revision = '009'": "父版本",
        "def upgrade()": "升级函数",
        "def downgrade()": "降级函数",
        "exchange_configs": "exchange_configs表",
        "market_data_kline": "market_data_kline表扩展",
    }
    
    all_passed = True
    for check_str, desc in checks.items():
        if check_str in content:
            print(f"   ✅ {desc}: 找到")
        else:
            print(f"   ❌ {desc}: 未找到 '{check_str}'")
            all_passed = False
    
    # 检查表结构
    print(f"\n4. 检查exchange_configs表结构...")
    table_fields = [
        "id",
        "name",
        "display_name",
        "is_active",
        "market_type",
        "api_key_encrypted",
        "api_secret_encrypted",
        "testnet",
        "config_json",
        "created_at",
        "updated_at",
    ]
    
    for field in table_fields:
        if field in content:
            print(f"   ✅ 字段 '{field}': 存在")
        else:
            print(f"   ⚠️  字段 '{field}': 未找到")
    
    # 检查market_data_kline扩展
    print(f"\n5. 检查market_data_kline表扩展...")
    new_fields = [
        "exchange",
        "market_type",
        "funding_rate",
        "open_interest",
    ]
    
    for field in new_fields:
        if f"add_column('market_data_kline', sa.Column('{field}'" in content:
            print(f"   ✅ 新增字段 '{field}': 找到")
        else:
            print(f"   ⚠️  新增字段 '{field}': 未找到")
    
    # 检查约束和索引
    print(f"\n6. 检查约束和索引...")
    constraints = {
        "uq_active_exchange": "唯一激活约束",
        "idx_active_exchange": "激活索引",
        "uq_kline_symbol_interval_time": "K线唯一约束",
        "idx_kline_symbol_interval_time": "K线索引",
    }
    
    for constraint, desc in constraints.items():
        if constraint in content:
            print(f"   ✅ {desc} ({constraint}): 找到")
        else:
            print(f"   ⚠️  {desc} ({constraint}): 未找到")
    
    # 语法检查
    print(f"\n7. 检查Python语法...")
    try:
        compile(content, migration_file, 'exec')
        print(f"   ✅ Python语法正确")
    except SyntaxError as e:
        print(f"   ❌ Python语法错误: {e}")
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ 验证通过! 迁移文件结构正确")
    else:
        print("⚠️  验证发现问题,请检查上述标记为❌的项")
    print("="*60)
    
    return all_passed


def verify_adapter_files():
    """验证适配器文件"""
    print("\n\n🔍 验证交易所适配器文件...")
    print("="*60)
    
    adapters = {
        "base_adapter.py": "基础适配器接口",
        "binance_adapter.py": "币安适配器",
        "hyperliquid_adapter.py": "Hyperliquid适配器",
        "exchange_factory.py": "交易所工厂",
        "__init__.py": "包初始化",
    }
    
    exchange_dir = Path(__file__).parent / "app" / "services" / "exchange"
    
    all_exist = True
    for filename, desc in adapters.items():
        filepath = exchange_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"   ✅ {desc}: {filename} ({size} 字节)")
        else:
            print(f"   ❌ {desc}: {filename} (不存在)")
            all_exist = False
    
    return all_exist


def verify_api_files():
    """验证API文件"""
    print("\n\n🔍 验证API端点文件...")
    print("="*60)
    
    apis = {
        "exchanges.py": "交易所管理API",
        "market_extended.py": "扩展市场数据API",
    }
    
    api_dir = Path(__file__).parent / "app" / "api" / "v1"
    
    all_exist = True
    for filename, desc in apis.items():
        filepath = api_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"   ✅ {desc}: {filename} ({size} 字节)")
        else:
            print(f"   ❌ {desc}: {filename} (不存在)")
            all_exist = False
    
    return all_exist


def verify_kline_aggregator():
    """验证K线聚合器"""
    print("\n\n🔍 验证K线聚合器...")
    print("="*60)
    
    filepath = Path(__file__).parent / "app" / "services" / "market" / "kline_aggregator.py"
    
    if filepath.exists():
        size = filepath.stat().st_size
        print(f"   ✅ K线聚合器: kline_aggregator.py ({size} 字节)")
        return True
    else:
        print(f"   ❌ K线聚合器: kline_aggregator.py (不存在)")
        return False


def verify_model_files():
    """验证模型文件"""
    print("\n\n🔍 验证数据库模型...")
    print("="*60)
    
    filepath = Path(__file__).parent / "app" / "models" / "exchange_config.py"
    
    if filepath.exists():
        size = filepath.stat().st_size
        print(f"   ✅ 交易所配置模型: exchange_config.py ({size} 字节)")
        
        # 检查__init__.py是否导出
        init_file = Path(__file__).parent / "app" / "models" / "__init__.py"
        if init_file.exists():
            with open(init_file, 'r') as f:
                content = f.read()
                if "ExchangeConfig" in content:
                    print(f"   ✅ ExchangeConfig已在__init__.py中导出")
                else:
                    print(f"   ⚠️  ExchangeConfig未在__init__.py中导出")
        return True
    else:
        print(f"   ❌ 交易所配置模型: exchange_config.py (不存在)")
        return False


def verify_main_app():
    """验证主应用配置"""
    print("\n\n🔍 验证主应用main.py...")
    print("="*60)
    
    filepath = Path(__file__).parent / "app" / "main.py"
    
    if not filepath.exists():
        print(f"   ❌ main.py不存在")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "exchanges": "导入exchanges模块",
        "market_extended": "导入market_extended模块",
        "exchanges.router": "注册exchanges路由",
        "market_extended.router": "注册market_extended路由",
    }
    
    all_passed = True
    for check_str, desc in checks.items():
        if check_str in content:
            print(f"   ✅ {desc}: 找到")
        else:
            print(f"   ❌ {desc}: 未找到")
            all_passed = False
    
    return all_passed


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  v3.1 币安集成 - 文件验证工具")
    print("="*60)
    
    results = {
        "迁移文件": verify_migration_file(),
        "适配器文件": verify_adapter_files(),
        "API文件": verify_api_files(),
        "K线聚合器": verify_kline_aggregator(),
        "数据模型": verify_model_files(),
        "主应用配置": verify_main_app(),
    }
    
    # 总结
    print("\n\n" + "="*60)
    print("  验证结果总结")
    print("="*60)
    
    all_passed = True
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status}  {name}")
        if not result:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("\n🎉 所有验证通过! v3.1代码结构完整")
        print("\n📝 下一步:")
        print("   1. 确认数据库连接配置")
        print("   2. 执行数据库迁移: python3 -m alembic upgrade head")
        print("   3. 启动后端服务器: python3 -m uvicorn app.main:app --reload")
        print("   4. 访问API文档: http://localhost:8000/docs")
    else:
        print("\n⚠️  部分验证失败,请检查上述标记为❌的项")
    print()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

