#!/usr/bin/env python3
import json
import os
import re

# 读取配置
with open('page_configs.json', 'r', encoding='utf-8') as f:
    configs = json.load(f)

base_path = 'frontend/app/admin'

for page_path, config in configs.items():
    full_path = os.path.join(base_path, page_path)
    
    if not os.path.exists(full_path):
        print(f"⚠️  跳过不存在的文件: {page_path}")
        continue
    
    print(f"\n📝 处理: {page_path}")
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 添加导入(如果不存在)
    if 'import PageHeader' not in content:
        # 找到第一个import语句后添加
        lines = content.split('\n')
        import_added = False
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') and not import_added:
                # 找到最后一个import
                last_import_idx = i
                for j in range(i, len(lines)):
                    if lines[j].strip().startswith('import '):
                        last_import_idx = j
                    elif lines[j].strip() and not lines[j].strip().startswith('import'):
                        break
                
                # 在最后一个import后插入
                lines.insert(last_import_idx + 1, "import PageHeader from '../../components/common/PageHeader';")
                import_added = True
                break
        
        content = '\n'.join(lines)
        print(f"  ✅ 添加了PageHeader导入")
    else:
        print(f"  ✓ 已有PageHeader导入")
    
    # 保存
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  📊 配置: {config['icon']} {config['title']} ({config['color']})")

print("\n✅ 批量添加导入完成!")
print("💡 接下来需要手动替换每个页面的标题部分")
