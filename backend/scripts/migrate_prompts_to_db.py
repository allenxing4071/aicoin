"""
Prompt数据迁移脚本
将.txt文件导入PostgreSQL数据库
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.prompt_template import PromptTemplate, PromptTemplateVersion
from app.core.database import Base

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_level_from_name(name: str) -> str:
    """
    从文件名提取权限等级
    
    例如：
    - l0_conservative.txt -> L0
    - l1_moderate.txt -> L1
    - default.txt -> None
    """
    if name.startswith('l') and len(name) > 1 and name[1].isdigit():
        return f"L{name[1]}"
    return None


async def migrate_prompts():
    """执行Prompt迁移"""
    logger.info("=" * 50)
    logger.info("开始Prompt数据迁移")
    logger.info("=" * 50)
    
    # 创建数据库引擎（使用asyncpg驱动）
    db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        try:
            # 定义Prompt目录
            prompts_dir = Path(__file__).parent.parent / "prompts"
            categories = ["decision", "debate", "intelligence"]
            
            total_migrated = 0
            
            for category in categories:
                category_dir = prompts_dir / category
                
                if not category_dir.exists():
                    logger.warning(f"⚠️  目录不存在: {category_dir}")
                    continue
                
                logger.info(f"\n📂 处理类别: {category}")
                
                # 扫描所有.txt文件
                txt_files = list(category_dir.glob("*.txt"))
                
                if not txt_files:
                    logger.warning(f"⚠️  类别 {category} 中没有找到.txt文件")
                    continue
                
                for txt_file in txt_files:
                    try:
                        # 读取文件内容
                        content = txt_file.read_text(encoding='utf-8')
                        
                        # 提取文件名（不含扩展名）
                        template_name = txt_file.stem
                        
                        # 提取权限等级
                        permission_level = extract_level_from_name(template_name)
                        
                        # 检查是否已存在
                        existing = await db.execute(
                            f"""
                            SELECT id FROM prompt_templates 
                            WHERE category = '{category}' 
                            AND name = '{template_name}'
                            AND permission_level {'IS NULL' if permission_level is None else f"= '{permission_level}'"}
                            """
                        )
                        
                        if existing.scalar():
                            logger.info(f"  ⏭️  跳过已存在: {category}/{template_name} ({permission_level or '通用'})")
                            continue
                        
                        # 创建Prompt模板
                        template = PromptTemplate(
                            name=template_name,
                            category=category,
                            permission_level=permission_level,
                            content=content,
                            version=1,
                            is_active=True,
                            created_by=1  # admin用户
                        )
                        
                        db.add(template)
                        await db.flush()  # 获取ID
                        
                        # 创建版本历史记录
                        version_history = PromptTemplateVersion(
                            template_id=template.id,
                            version=1,
                            content=content,
                            change_summary="初始版本（从.txt文件迁移）",
                            created_by=1
                        )
                        
                        db.add(version_history)
                        
                        logger.info(f"  ✅ 迁移成功: {category}/{template_name} ({permission_level or '通用'})")
                        total_migrated += 1
                    
                    except Exception as e:
                        logger.error(f"  ❌ 迁移失败 {txt_file.name}: {e}")
                        continue
            
            # 提交事务
            await db.commit()
            
            logger.info("\n" + "=" * 50)
            logger.info(f"✅ 迁移完成！共迁移 {total_migrated} 个Prompt模板")
            logger.info("=" * 50)
        
        except Exception as e:
            logger.error(f"❌ 迁移过程中发生错误: {e}")
            await db.rollback()
            raise
        
        finally:
            await engine.dispose()


async def verify_migration():
    """验证迁移结果"""
    logger.info("\n" + "=" * 50)
    logger.info("验证迁移结果")
    logger.info("=" * 50)
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        try:
            # 统计各类别的Prompt数量
            result = await db.execute(
                """
                SELECT category, permission_level, COUNT(*) as count
                FROM prompt_templates
                WHERE is_active = TRUE
                GROUP BY category, permission_level
                ORDER BY category, permission_level
                """
            )
            
            rows = result.fetchall()
            
            logger.info("\n📊 Prompt统计：")
            for row in rows:
                category, level, count = row
                logger.info(f"  - {category} ({level or '通用'}): {count}个")
            
            # 统计总数
            total_result = await db.execute(
                "SELECT COUNT(*) FROM prompt_templates WHERE is_active = TRUE"
            )
            total = total_result.scalar()
            
            logger.info(f"\n✅ 总计: {total}个激活的Prompt模板")
        
        finally:
            await engine.dispose()


if __name__ == "__main__":
    # 执行迁移
    asyncio.run(migrate_prompts())
    
    # 验证结果
    asyncio.run(verify_migration())

