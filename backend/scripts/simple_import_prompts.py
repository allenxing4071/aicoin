"""
简化版Prompt导入脚本（使用同步psycopg2）
"""

import sys
import os
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import psycopg2
from app.core.config import settings

def import_prompts():
    """导入Prompt数据"""
    print("\n" + "="*60)
    print("开始导入Prompt数据")
    print("="*60)
    
    conn = psycopg2.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    
    prompts_dir = project_root / "prompts"
    
    # 定义要导入的Prompt
    prompts_to_import = [
        # Decision类别
        ("decision", "default", None, "prompts/decision/default.txt"),
        ("decision", "default", "L0", "prompts/decision/l0_conservative.txt"),
        ("decision", "default", "L1", "prompts/decision/l1_moderate.txt"),
        ("decision", "default", "L2", "prompts/decision/l2_balanced.txt"),
        ("decision", "default", "L3", "prompts/decision/l3_aggressive.txt"),
        ("decision", "default", "L4", "prompts/decision/l4_high_risk.txt"),
        ("decision", "default", "L5", "prompts/decision/l5_extreme.txt"),
        # Debate类别
        ("debate", "bull_analyst", None, "prompts/debate/bull_analyst.txt"),
        ("debate", "bear_analyst", None, "prompts/debate/bear_analyst.txt"),
        ("debate", "research_manager", None, "prompts/debate/research_manager.txt"),
    ]
    
    imported_count = 0
    
    for category, name, level, file_path in prompts_to_import:
        full_path = project_root / file_path
        
        if not full_path.exists():
            print(f"⚠️  文件不存在: {file_path}")
            continue
        
        # 读取内容
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 插入数据库
        try:
            cur.execute("""
                INSERT INTO prompt_templates 
                (name, category, permission_level, content, version, is_active)
                VALUES (%s, %s, %s, %s, 1, TRUE)
                ON CONFLICT DO NOTHING
            """, (name, category, level, content))
            
            level_str = level or "通用"
            print(f"✅ {category}/{name}/{level_str}")
            imported_count += 1
            
        except Exception as e:
            print(f"❌ {category}/{name}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n" + "="*60)
    print(f"✅ 导入完成！共导入 {imported_count} 个Prompt")
    print("="*60)
    
    return imported_count


if __name__ == "__main__":
    try:
        count = import_prompts()
        sys.exit(0 if count > 0 else 1)
    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

