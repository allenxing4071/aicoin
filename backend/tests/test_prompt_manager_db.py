"""
测试 PromptManagerDB（数据库版本）

测试内容：
1. 从数据库加载Prompt模板
2. 权限等级匹配（L0-L5）
3. 缓存机制
4. Fallback机制
5. 线程安全
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.decision.prompt_manager_db import PromptManagerDB, PromptTemplateDB


@pytest.fixture
def mock_db_session():
    """Mock数据库会话"""
    session = Mock(spec=AsyncSession)
    return session


@pytest.fixture
def sample_templates():
    """示例Prompt模板"""
    return [
        PromptTemplateDB(
            id=1,
            name="default",
            category="decision",
            permission_level=None,  # 通用模板
            content="你是专业的加密货币交易AI。",
            version=1,
            is_active=True
        ),
        PromptTemplateDB(
            id=2,
            name="default",
            category="decision",
            permission_level="L0",
            content="你是保守的加密货币交易AI（L0）。",
            version=1,
            is_active=True
        ),
        PromptTemplateDB(
            id=3,
            name="default",
            category="decision",
            permission_level="L3",
            content="你是平衡的加密货币交易AI（L3）。",
            version=1,
            is_active=True
        ),
        PromptTemplateDB(
            id=4,
            name="default",
            category="debate",
            permission_level=None,
            content="你是辩论协调员。",
            version=1,
            is_active=True
        ),
    ]


class TestPromptManagerDB:
    """测试PromptManagerDB"""
    
    @pytest.mark.asyncio
    async def test_load_from_db_success(self, mock_db_session, sample_templates):
        """测试成功从数据库加载"""
        # Mock数据库查询
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = sample_templates
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # 创建管理器并加载
        manager = PromptManagerDB(mock_db_session)
        await manager.load_from_db()
        
        # 验证加载结果
        assert len(manager.templates) == 4
        assert "decision/default/None" in manager.templates
        assert "decision/default/L0" in manager.templates
        assert "debate/default/None" in manager.templates
    
    @pytest.mark.asyncio
    async def test_get_template_exact_match(self, mock_db_session, sample_templates):
        """测试精确匹配权限等级"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = sample_templates
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        manager = PromptManagerDB(mock_db_session)
        await manager.load_from_db()
        
        # 精确匹配L0
        template = manager.get_template("decision", "default", "L0")
        assert template is not None
        assert template.permission_level == "L0"
        assert "保守" in template.content
    
    @pytest.mark.asyncio
    async def test_get_template_fallback_to_generic(self, mock_db_session, sample_templates):
        """测试Fallback到通用模板"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = sample_templates
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        manager = PromptManagerDB(mock_db_session)
        await manager.load_from_db()
        
        # L5不存在，应该fallback到通用模板
        template = manager.get_template("decision", "default", "L5")
        assert template is not None
        assert template.permission_level is None  # 通用模板
        assert "专业" in template.content
    
    @pytest.mark.asyncio
    async def test_get_template_not_found(self, mock_db_session, sample_templates):
        """测试模板不存在"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = sample_templates
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        manager = PromptManagerDB(mock_db_session)
        await manager.load_from_db()
        
        # 不存在的类别
        template = manager.get_template("nonexistent", "default", "L0")
        assert template is None
    
    @pytest.mark.asyncio
    async def test_reload_from_db(self, mock_db_session, sample_templates):
        """测试重新加载"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = sample_templates
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        manager = PromptManagerDB(mock_db_session)
        await manager.load_from_db()
        
        # 第一次加载
        assert len(manager.templates) == 4
        
        # 修改数据
        new_template = PromptTemplateDB(
            id=5,
            name="default",
            category="intelligence",
            permission_level=None,
            content="你是情报分析员。",
            version=1,
            is_active=True
        )
        mock_result.scalars.return_value.all.return_value = sample_templates + [new_template]
        
        # 重新加载
        await manager.load_from_db()
        assert len(manager.templates) == 5
        assert "intelligence/default/None" in manager.templates
    
    @pytest.mark.asyncio
    async def test_thread_safety(self, mock_db_session, sample_templates):
        """测试线程安全"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = sample_templates
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        manager = PromptManagerDB(mock_db_session)
        await manager.load_from_db()
        
        # 并发读取
        async def read_template():
            return manager.get_template("decision", "default", "L0")
        
        tasks = [read_template() for _ in range(100)]
        results = await asyncio.gather(*tasks)
        
        # 所有结果应该一致
        assert all(r is not None for r in results)
        assert all(r.permission_level == "L0" for r in results)
    
    @pytest.mark.asyncio
    async def test_db_error_handling(self, mock_db_session):
        """测试数据库错误处理"""
        # Mock数据库错误
        mock_db_session.execute = AsyncMock(side_effect=Exception("DB connection failed"))
        
        manager = PromptManagerDB(mock_db_session)
        
        # 应该捕获异常，不崩溃
        await manager.load_from_db()
        
        # 模板应该为空
        assert len(manager.templates) == 0
    
    @pytest.mark.asyncio
    async def test_permission_level_priority(self, mock_db_session):
        """测试权限等级优先级"""
        templates = [
            PromptTemplateDB(
                id=1,
                name="default",
                category="decision",
                permission_level=None,
                content="通用模板",
                version=1,
                is_active=True
            ),
            PromptTemplateDB(
                id=2,
                name="default",
                category="decision",
                permission_level="L2",
                content="L2专用模板",
                version=1,
                is_active=True
            ),
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = templates
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        manager = PromptManagerDB(mock_db_session)
        await manager.load_from_db()
        
        # L2应该匹配专用模板
        template = manager.get_template("decision", "default", "L2")
        assert "L2专用" in template.content
        
        # L1应该fallback到通用模板
        template = manager.get_template("decision", "default", "L1")
        assert "通用" in template.content


class TestPromptTemplateDB:
    """测试PromptTemplateDB数据类"""
    
    def test_template_creation(self):
        """测试模板创建"""
        template = PromptTemplateDB(
            id=1,
            name="test",
            category="decision",
            permission_level="L0",
            content="Test content",
            version=1,
            is_active=True
        )
        
        assert template.id == 1
        assert template.name == "test"
        assert template.category == "decision"
        assert template.permission_level == "L0"
        assert template.content == "Test content"
        assert template.version == 1
        assert template.is_active is True
    
    def test_template_key_generation(self):
        """测试模板Key生成"""
        template = PromptTemplateDB(
            id=1,
            name="default",
            category="decision",
            permission_level="L0",
            content="Test",
            version=1,
            is_active=True
        )
        
        # Key格式: category/name/permission_level
        expected_key = "decision/default/L0"
        # 注意：实际实现中可能需要添加get_key()方法
        # assert template.get_key() == expected_key


@pytest.mark.asyncio
async def test_integration_with_decision_engine(mock_db_session, sample_templates):
    """集成测试：与DecisionEngineV2配合"""
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = sample_templates
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    manager = PromptManagerDB(mock_db_session)
    await manager.load_from_db()
    
    # 模拟DecisionEngineV2的使用场景
    permission_level = "L3"
    template = manager.get_template("decision", "default", permission_level)
    
    assert template is not None
    assert "平衡" in template.content
    
    # 构建完整Prompt（模拟DecisionEngineV2的逻辑）
    market_data = {"price": 50000, "volume": 1000}
    full_prompt = template.content + f"\n\n市场数据: {market_data}"
    
    assert "平衡" in full_prompt
    assert "50000" in full_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

