#!/usr/bin/env python3
"""测试v2.0配置和导入"""

import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """测试所有v2.0模块导入"""
    print("="*60)
    print("🧪 测试v2.0模块导入")
    print("="*60)
    print()
    
    tests = []
    
    # 1. 测试权限系统
    try:
        from app.services.constraints.permission_manager import PermissionManager, PerformanceData
        print("✅ PermissionManager导入成功")
        tests.append(("PermissionManager", True, None))
    except Exception as e:
        print(f"❌ PermissionManager导入失败: {e}")
        tests.append(("PermissionManager", False, str(e)))
    
    # 2. 测试约束验证
    try:
        from app.services.constraints.constraint_validator import ConstraintValidator
        print("✅ ConstraintValidator导入成功")
        tests.append(("ConstraintValidator", True, None))
    except Exception as e:
        print(f"❌ ConstraintValidator导入失败: {e}")
        tests.append(("ConstraintValidator", False, str(e)))
    
    # 3. 测试记忆系统
    try:
        from app.services.memory.short_term_memory import ShortTermMemory
        from app.services.memory.long_term_memory import LongTermMemory
        from app.services.memory.knowledge_base import KnowledgeBase
        print("✅ 记忆系统导入成功")
        tests.append(("Memory Systems", True, None))
    except Exception as e:
        print(f"❌ 记忆系统导入失败: {e}")
        tests.append(("Memory Systems", False, str(e)))
    
    # 4. 测试监控系统
    try:
        from app.services.monitoring.kpi_calculator import KPICalculator
        from app.services.monitoring.alert_manager import AlertManager
        print("✅ 监控系统导入成功")
        tests.append(("Monitoring Systems", True, None))
    except Exception as e:
        print(f"❌ 监控系统导入失败: {e}")
        tests.append(("Monitoring Systems", False, str(e)))
    
    # 5. 测试决策引擎v2
    try:
        from app.services.decision.prompt_templates import PromptTemplates
        from app.services.decision.decision_engine_v2 import DecisionEngineV2
        print("✅ DecisionEngineV2导入成功")
        tests.append(("DecisionEngineV2", True, None))
    except Exception as e:
        print(f"❌ DecisionEngineV2导入失败: {e}")
        tests.append(("DecisionEngineV2", False, str(e)))
    
    # 6. 测试编排器v2
    try:
        from app.services.orchestrator_v2 import AITradingOrchestratorV2
        print("✅ OrchestratorV2导入成功")
        tests.append(("OrchestratorV2", True, None))
    except Exception as e:
        print(f"❌ OrchestratorV2导入失败: {e}")
        tests.append(("OrchestratorV2", False, str(e)))
    
    # 7. 测试main_v2
    try:
        from app import main_v2
        print("✅ main_v2导入成功")
        tests.append(("main_v2", True, None))
    except Exception as e:
        print(f"❌ main_v2导入失败: {e}")
        tests.append(("main_v2", False, str(e)))
    
    print()
    print("="*60)
    print("📊 测试总结")
    print("="*60)
    print()
    
    passed = sum(1 for _, success, _ in tests if success)
    failed = len(tests) - passed
    
    print(f"总计: {len(tests)} 个测试")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print()
    
    if failed > 0:
        print("失败详情:")
        for name, success, error in tests:
            if not success:
                print(f"  - {name}: {error}")
        print()
        return False
    else:
        print("🎉 所有测试通过！v2.0模块配置正确")
        print()
        return True


def test_config():
    """测试配置"""
    print("="*60)
    print("⚙️  测试配置")
    print("="*60)
    print()
    
    try:
        from app.core.config import settings
        
        print("📋 关键配置:")
        print(f"   - APP_NAME: {settings.APP_NAME}")
        print(f"   - DECISION_INTERVAL: {settings.DECISION_INTERVAL}秒")
        print(f"   - TRADING_ENABLED: {settings.TRADING_ENABLED}")
        print(f"   - QDRANT_HOST: {getattr(settings, 'QDRANT_HOST', 'localhost')}")
        print(f"   - QDRANT_PORT: {getattr(settings, 'QDRANT_PORT', 6333)}")
        print(f"   - INITIAL_PERMISSION_LEVEL: {getattr(settings, 'INITIAL_PERMISSION_LEVEL', 'L1')}")
        print(f"   - ABSOLUTE_MAX_LEVERAGE: {getattr(settings, 'ABSOLUTE_MAX_LEVERAGE', 5)}")
        print()
        
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


if __name__ == "__main__":
    print()
    print("🧪 AIcoin v2.0 配置测试")
    print()
    
    import_success = test_imports()
    config_success = test_config()
    
    if import_success and config_success:
        print("="*60)
        print("✅ v2.0配置测试通过！可以启动测试网")
        print("="*60)
        print()
        print("下一步:")
        print("1. 配置 .env.testnet 文件")
        print("2. 运行: ./start_testnet.sh")
        print("3. 访问: http://localhost:8000/docs")
        print()
        sys.exit(0)
    else:
        print("="*60)
        print("❌ v2.0配置测试失败！请修复错误后重试")
        print("="*60)
        print()
        sys.exit(1)

