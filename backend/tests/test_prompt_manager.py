"""
Prompt Manager单元测试

借鉴NOFX的测试思路，验证核心功能
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

from app.services.decision.prompt_manager import PromptManager, PromptTemplate


class TestPromptManager:
    """PromptManager测试类"""
    
    @pytest.fixture
    def temp_prompts_dir(self):
        """创建临时Prompt目录"""
        temp_dir = tempfile.mkdtemp()
        
        # 创建目录结构
        decision_dir = Path(temp_dir) / "decision"
        debate_dir = Path(temp_dir) / "debate"
        decision_dir.mkdir()
        debate_dir.mkdir()
        
        # 创建测试文件
        (decision_dir / "default.txt").write_text("Default decision strategy")
        (decision_dir / "conservative.txt").write_text("Conservative strategy")
        (debate_dir / "bull_analyst.txt").write_text("Bull analyst prompt")
        
        yield temp_dir
        
        # 清理
        shutil.rmtree(temp_dir)
    
    def test_load_templates(self, temp_prompts_dir):
        """测试模板加载"""
        manager = PromptManager(temp_prompts_dir)
        
        # 验证decision类别
        decision_templates = manager.list_templates("decision")
        assert "default" in decision_templates
        assert "conservative" in decision_templates
        assert len(decision_templates) == 2
        
        # 验证debate类别
        debate_templates = manager.list_templates("debate")
        assert "bull_analyst" in debate_templates
        assert len(debate_templates) == 1
    
    def test_get_template(self, temp_prompts_dir):
        """测试获取模板"""
        manager = PromptManager(temp_prompts_dir)
        
        # 获取存在的模板
        template = manager.get_template("decision", "default")
        assert template.name == "default"
        assert template.category == "decision"
        assert template.content == "Default decision strategy"
        
        # 获取不存在的模板（应该降级到default）
        template = manager.get_template("decision", "nonexistent")
        assert template.name == "default"  # 降级到default
    
    def test_get_template_fallback(self, temp_prompts_dir):
        """测试优雅降级"""
        manager = PromptManager(temp_prompts_dir)
        
        # 请求不存在的类别和模板（应该返回内置版本）
        template = manager.get_template("nonexistent_category", "nonexistent")
        assert template.name == "nonexistent"
        assert template.file_path == "<builtin>"
        assert len(template.content) > 0  # 应该有内置内容
    
    def test_reload_templates(self, temp_prompts_dir):
        """测试热重载"""
        manager = PromptManager(temp_prompts_dir)
        
        # 初始加载
        template = manager.get_template("decision", "default")
        original_content = template.content
        
        # 修改文件
        decision_dir = Path(temp_prompts_dir) / "decision"
        (decision_dir / "default.txt").write_text("Updated decision strategy")
        
        # 重新加载
        manager.reload_templates("decision")
        
        # 验证内容已更新
        template = manager.get_template("decision", "default")
        assert template.content == "Updated decision strategy"
        assert template.content != original_content
    
    def test_template_exists(self, temp_prompts_dir):
        """测试模板存在性检查"""
        manager = PromptManager(temp_prompts_dir)
        
        assert manager.template_exists("decision", "default") == True
        assert manager.template_exists("decision", "conservative") == True
        assert manager.template_exists("decision", "nonexistent") == False
        assert manager.template_exists("nonexistent", "default") == False
    
    def test_get_all_templates(self, temp_prompts_dir):
        """测试获取所有模板"""
        manager = PromptManager(temp_prompts_dir)
        
        all_templates = manager.get_all_templates()
        assert len(all_templates) == 3  # 2 decision + 1 debate
        
        # 验证类型
        for template in all_templates:
            assert isinstance(template, PromptTemplate)
            assert template.name in ["default", "conservative", "bull_analyst"]
    
    def test_thread_safety(self, temp_prompts_dir):
        """测试线程安全（简单验证）"""
        import threading
        
        manager = PromptManager(temp_prompts_dir)
        results = []
        
        def load_template():
            template = manager.get_template("decision", "default")
            results.append(template.content)
        
        # 创建多个线程同时访问
        threads = [threading.Thread(target=load_template) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # 所有结果应该一致
        assert len(set(results)) == 1
        assert results[0] == "Default decision strategy"


class TestPromptTemplate:
    """PromptTemplate测试类"""
    
    def test_template_render(self):
        """测试模板渲染（简单字符串替换）"""
        from datetime import datetime
        
        template = PromptTemplate(
            name="test",
            category="test",
            content="Hello {name}, balance: {balance}",
            file_path="/test.txt",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 正常渲染
        result = template.render(name="Alice", balance=1000)
        assert result == "Hello Alice, balance: 1000"
    
    def test_template_render_missing_variable(self):
        """测试缺失变量的处理"""
        from datetime import datetime
        
        template = PromptTemplate(
            name="test",
            category="test",
            content="Hello {name}",
            file_path="/test.txt",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 缺失变量应该保留原始占位符
        result = template.render()  # 不提供name
        assert "{name}" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

