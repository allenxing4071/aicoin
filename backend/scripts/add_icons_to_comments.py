"""
为数据库表注释添加图标
让数据库管理界面更美观、更直观
"""
import re
from pathlib import Path

# 表名到图标的映射
TABLE_ICONS = {
    # 用户和权限
    'role_permissions': '🔗',
    'roles': '👥',
    'admin_users': '👤',
    'permissions': '🔐',
    'permission_level_configs': '⚙️',
    
    # 交易相关
    'trades': '💰',
    'orders': '📝',
    'account_snapshots': '📊',
    
    # 市场数据
    'market_data_kline': '📈',
    
    # AI 决策和情报
    'ai_decisions': '🤖',
    'routing_decisions': '🔀',
    'intelligence_reports': '📰',
    'intelligence_platforms': '☁️',
    'intelligence_source_weights': '⚖️',
    
    # 风控和监控
    'risk_events': '⚠️',
    
    # 聪明钱追踪
    'smart_money_transactions': '💎',
    'smart_money_wallets': '👛',
    
    # 配置和系统
    'exchange_configs': '🏦',
    'ai_model_pricing': '💵',
    'model_performance': '📊',
    
    # 记忆系统
    'ai_lessons': '📚',
    'market_patterns': '🔍',
    
    # KOL 和舆情
    'kol_opinions': '💬',
}

def add_icon_to_file(file_path: Path):
    """为文件中的表注释添加图标"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # 获取表名
    table_name_match = re.search(r'__tablename__\s*=\s*["\'](\w+)["\']', content)
    if not table_name_match:
        return False
    
    table_name = table_name_match.group(1)
    icon = TABLE_ICONS.get(table_name)
    
    if not icon:
        return False
    
    # 查找并更新 comment
    pattern = r"(comment['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])"
    
    def add_icon(match):
        prefix = match.group(1)
        comment_text = match.group(2)
        suffix = match.group(3)
        
        # 如果已经有图标，先移除
        cleaned_text = re.sub(r'^[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F1E0-\U0001F1FF]+\s*', '', comment_text)
        
        # 添加新图标
        new_comment = f"{icon} {cleaned_text}"
        
        return f"{prefix}{new_comment}{suffix}"
    
    content = re.sub(pattern, add_icon, content)
    
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ 已更新: {file_path.name} -> {icon}")
        return True
    return False

def main():
    """主函数"""
    models_dir = Path(__file__).parent.parent / 'app' / 'models'
    
    print("🎨 开始为表注释添加图标...")
    print(f"目录: {models_dir}\n")
    
    updated_count = 0
    for py_file in models_dir.glob('*.py'):
        if py_file.name == '__init__.py':
            continue
        
        if add_icon_to_file(py_file):
            updated_count += 1
    
    print(f"\n✅ 完成！共更新 {updated_count} 个文件")
    print("\n📋 图标说明:")
    print("  👥 角色  👤 用户  🔐 权限  💰 交易  📝 订单")
    print("  📈 K线  🤖 AI  📰 情报  ⚠️ 风控  💎 聪明钱")

if __name__ == '__main__':
    main()

