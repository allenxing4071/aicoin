"""
重新计算平台成本
使用新的定价管理器重新计算所有平台的历史成本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.models.intelligence_platform import IntelligencePlatform
from app.models.ai_model_usage_log import AIModelUsageLog
from app.services.ai_pricing import get_pricing_manager
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def recalculate_platform_costs():
    """重新计算所有平台的成本"""
    
    logger.info("🔄 开始重新计算平台成本...")
    
    pricing_manager = get_pricing_manager()
    
    async with async_session_maker() as db:
        # 获取所有平台
        result = await db.execute(
            select(IntelligencePlatform).where(IntelligencePlatform.enabled == True)
        )
        platforms = result.scalars().all()
        
        logger.info(f"📊 找到 {len(platforms)} 个启用的平台")
        
        for platform in platforms:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔍 处理平台: {platform.name} ({platform.provider})")
            logger.info(f"   旧成本: ¥{platform.total_cost:.4f}")
            logger.info(f"   调用次数: {platform.total_calls}")
            
            # 查询该平台的所有使用记录
            usage_result = await db.execute(
                select(AIModelUsageLog).where(
                    AIModelUsageLog.model_name.like(f"%{platform.provider}%")
                ).order_by(AIModelUsageLog.created_at.desc())
            )
            usage_logs = usage_result.scalars().all()
            
            if not usage_logs:
                logger.warning(f"   ⚠️  未找到使用记录，保持原成本")
                continue
            
            # 重新计算总成本
            new_total_cost = 0.0
            recalculated_count = 0
            
            for log in usage_logs:
                # 使用新的定价管理器重新计算
                try:
                    # 从 model_name 中提取 provider 和 model
                    # 例如: "qwen_qwen-plus" -> provider="qwen", model="qwen-plus"
                    parts = log.model_name.split('_', 1)
                    if len(parts) == 2:
                        provider, model = parts
                    else:
                        provider = platform.provider
                        model = log.model_name
                    
                    # 使用新价格重新计算
                    cost = pricing_manager.calculate_cost(
                        provider=provider,
                        model=model,
                        input_tokens=log.input_tokens or 0,
                        output_tokens=log.output_tokens or 0
                    )
                    
                    new_total_cost += cost
                    recalculated_count += 1
                    
                except Exception as e:
                    logger.warning(f"   ⚠️  记录 {log.id} 计算失败: {e}")
                    # 如果计算失败，使用原始成本
                    new_total_cost += (log.cost or 0)
            
            # 更新平台成本
            old_cost = platform.total_cost
            platform.total_cost = new_total_cost
            platform.updated_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info(f"   ✅ 重新计算完成:")
            logger.info(f"      - 处理记录: {recalculated_count}/{len(usage_logs)}")
            logger.info(f"      - 旧成本: ¥{old_cost:.4f}")
            logger.info(f"      - 新成本: ¥{new_total_cost:.4f}")
            logger.info(f"      - 差异: ¥{new_total_cost - old_cost:.4f} ({((new_total_cost - old_cost) / old_cost * 100) if old_cost > 0 else 0:.2f}%)")
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ 所有平台成本重新计算完成！")


async def reset_all_costs():
    """重置所有平台成本为0（谨慎使用）"""
    
    logger.warning("⚠️  警告：即将重置所有平台成本为0！")
    logger.warning("⚠️  这将清除所有历史成本数据！")
    
    confirm = input("确认重置？输入 'YES' 继续: ")
    if confirm != "YES":
        logger.info("❌ 操作已取消")
        return
    
    async with async_session_maker() as db:
        result = await db.execute(select(IntelligencePlatform))
        platforms = result.scalars().all()
        
        for platform in platforms:
            logger.info(f"🔄 重置 {platform.name}: ¥{platform.total_cost:.4f} -> ¥0.00")
            platform.total_cost = 0.0
            platform.updated_at = datetime.utcnow()
        
        await db.commit()
        logger.info("✅ 所有平台成本已重置为0")


async def show_current_costs():
    """显示当前所有平台的成本"""
    
    logger.info("📊 当前平台成本统计:")
    logger.info(f"{'='*80}")
    
    async with async_session_maker() as db:
        result = await db.execute(
            select(IntelligencePlatform).order_by(IntelligencePlatform.total_cost.desc())
        )
        platforms = result.scalars().all()
        
        total_cost = 0.0
        
        for i, platform in enumerate(platforms, 1):
            logger.info(
                f"{i:2d}. {platform.name:30s} | "
                f"¥{platform.total_cost:8.4f} | "
                f"调用:{platform.total_calls:6d} | "
                f"成功率:{(platform.successful_calls/platform.total_calls*100) if platform.total_calls > 0 else 0:5.1f}%"
            )
            total_cost += platform.total_cost
        
        logger.info(f"{'='*80}")
        logger.info(f"总成本: ¥{total_cost:.4f}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="重新计算平台成本")
    parser.add_argument(
        "action",
        choices=["recalculate", "reset", "show"],
        help="操作类型: recalculate(重新计算), reset(重置为0), show(显示当前)"
    )
    
    args = parser.parse_args()
    
    if args.action == "recalculate":
        asyncio.run(recalculate_platform_costs())
    elif args.action == "reset":
        asyncio.run(reset_all_costs())
    elif args.action == "show":
        asyncio.run(show_current_costs())

