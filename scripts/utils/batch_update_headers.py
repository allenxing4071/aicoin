#!/usr/bin/env python3
"""
批量更新所有admin页面的标题,使其风格统一
"""

import re
import os

# 页面配置映射
PAGE_CONFIGS = {
    'intelligence/page.tsx': {
        'icon': '🕵️‍♀️',
        'title': 'Qwen情报系统管理',
        'description': '配置和监控市场情报收集系统、云平台管理',
        'color': 'orange',
    },
    'trading/page.tsx': {
        'icon': '📊',
        'title': '交易系统管理',
        'description': '策略配置、交易监控、风险控制、绩效分析',
        'color': 'pink',
    },
    'memory/page.tsx': {
        'icon': '🤖',
        'title': 'AI记忆系统',
        'description': '查看DeepSeek交易员和Qwen情报员的多层存储状态',
        'color': 'purple',
    },
}

def update_page_import(filepath, config):
    """添加PageHeader导入"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经导入
    if 'import PageHeader' in content:
        print(f"  ✓ {filepath} - 已导入PageHeader")
        return
    
    # 在第一个import后添加
    import_line = "import PageHeader from '../../components/common/PageHeader';"
    
    # 找到最后一个import
    lines = content.split('\n')
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('import '):
            last_import_idx = i
    
    # 插入导入
    lines.insert(last_import_idx + 1, import_line)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"  ✓ {filepath} - 已添加导入")

# 更新每个页面
base_path = 'frontend/app/admin'
for page_path, config in PAGE_CONFIGS.items():
    full_path = os.path.join(base_path, page_path)
    if os.path.exists(full_path):
        print(f"\n更新: {page_path}")
        print(f"  图标: {config['icon']}")
        print(f"  标题: {config['title']}")
        print(f"  颜色: {config['color']}")
        update_page_import(full_path, config)
    else:
        print(f"  ✗ 文件不存在: {full_path}")

print("\n✅ 导入添加完成!")
print("💡 提示: 标题替换需要手动处理,因为每个页面的结构不同")
