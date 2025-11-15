"""
部署前环境检查脚本

检查项：
1. PostgreSQL数据库连接
2. Redis连接
3. Qdrant连接
4. Python依赖包
5. 环境变量配置
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_imports():
    """检查Python依赖包"""
    print("\n" + "="*60)
    print("1️⃣  检查Python依赖包")
    print("="*60)
    
    required_packages = [
        ("sqlalchemy", "SQLAlchemy"),
        ("alembic", "Alembic"),
        ("redis", "Redis"),
        ("qdrant_client", "Qdrant Client"),
        ("openai", "OpenAI"),
        ("fastapi", "FastAPI"),
        ("psycopg2", "psycopg2"),
    ]
    
    all_ok = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - 未安装")
            all_ok = False
    
    return all_ok


def check_env_vars():
    """检查环境变量"""
    print("\n" + "="*60)
    print("2️⃣  检查环境变量")
    print("="*60)
    
    try:
        from app.core.config import settings
        
        checks = [
            ("DATABASE_URL", settings.DATABASE_URL, "postgresql://"),
            ("REDIS_URL", settings.REDIS_URL, "redis://"),
            ("QDRANT_HOST", settings.QDRANT_HOST, None),
            ("DEEPSEEK_API_KEY", settings.DEEPSEEK_API_KEY, None),
        ]
        
        all_ok = True
        for name, value, prefix in checks:
            if value:
                if prefix and not str(value).startswith(prefix):
                    print(f"⚠️  {name}: {value} (格式可能不正确)")
                else:
                    # 隐藏敏感信息
                    if "KEY" in name or "PASSWORD" in name:
                        display = f"{str(value)[:10]}..." if len(str(value)) > 10 else "***"
                    else:
                        display = value
                    print(f"✅ {name}: {display}")
            else:
                print(f"❌ {name}: 未配置")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"❌ 无法加载配置: {e}")
        return False


def check_database():
    """检查数据库连接"""
    print("\n" + "="*60)
    print("3️⃣  检查PostgreSQL连接")
    print("="*60)
    
    try:
        from app.core.config import settings
        import psycopg2
        
        # 解析DATABASE_URL
        db_url = settings.DATABASE_URL
        print(f"\n📍 数据库URL: {db_url}")
        
        # 尝试连接
        print("\n🔌 尝试连接数据库...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # 检查数据库版本
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL版本: {version.split(',')[0]}")
        
        # 检查数据库名称
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"✅ 当前数据库: {db_name}")
        
        # 检查表是否存在
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('prompt_templates', 'prompt_template_versions', 'prompt_performance', 'prompt_ab_tests')
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"\n📊 Prompt系统表:")
        expected_tables = ['prompt_ab_tests', 'prompt_performance', 'prompt_template_versions', 'prompt_templates']
        for table_name in expected_tables:
            if any(t[0] == table_name for t in tables):
                print(f"   ✅ {table_name}")
            else:
                print(f"   ❌ {table_name} (需要运行迁移)")
        
        cursor.close()
        conn.close()
        
        return len(tables) == 4  # 所有表都存在
        
    except Exception as e:
        print(f"\n❌ 数据库连接失败: {e}")
        print("\n💡 可能的原因:")
        print("   1. PostgreSQL服务未启动")
        print("   2. 数据库配置不正确")
        print("   3. 数据库不存在")
        print("\n🔧 解决方法:")
        print("   1. 启动PostgreSQL: brew services start postgresql")
        print("   2. 创建数据库: createdb aicoin")
        print("   3. 检查DATABASE_URL配置")
        return False


def check_redis():
    """检查Redis连接"""
    print("\n" + "="*60)
    print("4️⃣  检查Redis连接")
    print("="*60)
    
    try:
        from app.core.config import settings
        import redis
        
        print(f"\n📍 Redis URL: {settings.REDIS_URL}")
        
        # 尝试连接
        print("\n🔌 尝试连接Redis...")
        r = redis.from_url(settings.REDIS_URL)
        
        # 测试ping
        r.ping()
        print("✅ Redis连接成功")
        
        # 检查Redis版本
        info = r.info()
        print(f"✅ Redis版本: {info['redis_version']}")
        
        # 测试读写
        r.set("test_key", "test_value", ex=10)
        value = r.get("test_key")
        if value == b"test_value":
            print("✅ Redis读写正常")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Redis连接失败: {e}")
        print("\n💡 可能的原因:")
        print("   1. Redis服务未启动")
        print("   2. Redis配置不正确")
        print("\n🔧 解决方法:")
        print("   1. 启动Redis: brew services start redis")
        print("   2. 检查REDIS_URL配置")
        return False


def check_qdrant():
    """检查Qdrant连接"""
    print("\n" + "="*60)
    print("5️⃣  检查Qdrant连接")
    print("="*60)
    
    try:
        from app.core.config import settings
        from qdrant_client import QdrantClient
        
        print(f"\n📍 Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        
        # 尝试连接
        print("\n🔌 尝试连接Qdrant...")
        client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        
        # 检查collections
        collections = client.get_collections().collections
        print(f"✅ Qdrant连接成功")
        print(f"✅ Collections数量: {len(collections)}")
        
        # 检查prompt相关collection
        collection_names = [c.name for c in collections]
        if "prompt_performance_vectors" in collection_names:
            print("✅ prompt_performance_vectors collection存在")
        else:
            print("⚠️  prompt_performance_vectors collection不存在（首次运行会自动创建）")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Qdrant连接失败: {e}")
        print("\n💡 可能的原因:")
        print("   1. Qdrant服务未启动")
        print("   2. Qdrant配置不正确")
        print("\n🔧 解决方法:")
        print("   1. 启动Qdrant: docker run -p 6333:6333 qdrant/qdrant")
        print("   2. 检查QDRANT_HOST和QDRANT_PORT配置")
        return False


def main():
    """主函数"""
    print("\n" + "🎯"*30)
    print("Prompt系统部署前环境检查")
    print("🎯"*30)
    
    results = []
    
    # 1. 检查Python依赖
    results.append(("Python依赖", check_imports()))
    
    # 2. 检查环境变量
    results.append(("环境变量", check_env_vars()))
    
    # 3. 检查数据库
    results.append(("PostgreSQL", check_database()))
    
    # 4. 检查Redis
    results.append(("Redis", check_redis()))
    
    # 5. 检查Qdrant
    results.append(("Qdrant", check_qdrant()))
    
    # 输出总结
    print("\n" + "="*60)
    print("📊 检查总结")
    print("="*60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    all_passed = all(r for _, r in results)
    
    if all_passed:
        print("\n" + "🎉"*30)
        print("所有检查通过！可以开始部署！")
        print("🎉"*30)
        print("\n📝 下一步:")
        print("   1. cd backend")
        print("   2. python3 -m alembic upgrade head")
        print("   3. python3 scripts/migrate_prompts_to_db.py")
        print("   4. python3 scripts/verify_prompt_system.py")
        return 0
    else:
        print("\n" + "⚠️"*30)
        print("部分检查失败，请先解决上述问题")
        print("⚠️"*30)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

