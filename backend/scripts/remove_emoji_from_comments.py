"""
移除数据库表注释中的 emoji 图标
保留纯文字说明，提高兼容性
"""
import re
from pathlib import Path

# emoji 到文字的映射
EMOJI_REPLACEMENTS = {
    '👤': '[用户]',
    '💰': '[交易]',
    '📝': '[记录]',
    '📈': '[数据]',
    '⚠️': '[警告]',
    '🔐': '[权限]',
    '📊': '[统计]',
    '🎯': '[目标]',
    '🌐': '[网络]',
    '💡': '[智能]',
    '🧠': '[AI]',
    '📚': '[知识]',
    '🔍': '[搜索]',
    '⚖️': '[权重]',
    '☁️': '[平台]',
}

def remove_emoji_from_file(file_path: Path):
    """移除文件中注释的 emoji"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # 查找所有 comment 字段
    pattern = r"(comment['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])"
    
    def replace_emoji(match):
        prefix = match.group(1)
        comment_text = match.group(2)
        suffix = match.group(3)
        
        # 移除 emoji（直接删除，不替换）
        # 使用正则匹配所有 emoji 字符
        cleaned_text = re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F1E0-\U0001F1FF]+\s*', '', comment_text)
        
        return f"{prefix}{cleaned_text}{suffix}"
    
    content = re.sub(pattern, replace_emoji, content)
    
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ 已更新: {file_path.relative_to(Path.cwd())}")
        return True
    return False

def main():
    """主函数"""
    models_dir = Path(__file__).parent.parent / 'app' / 'models'
    
    print("🔍 开始扫描 models 目录...")
    print(f"目录: {models_dir}\n")
    
    updated_count = 0
    for py_file in models_dir.glob('*.py'):
        if py_file.name == '__init__.py':
            continue
        
        if remove_emoji_from_file(py_file):
            updated_count += 1
    
    print(f"\n✅ 完成！共更新 {updated_count} 个文件")

if __name__ == '__main__':
    main()

