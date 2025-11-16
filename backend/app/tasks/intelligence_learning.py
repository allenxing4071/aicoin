"""Intelligence Learning Tasks - Qwen情报系统持续学习定时任务"""

from celery import Celery
from celery.schedules import crontab
import logging
from datetime import datetime, timedelta

from app.core.redis_client import redis_client
from app.core.database import get_db
from app.services.intelligence.storage_layers import (
    MidTermIntelligenceAnalyzer,
    LongTermIntelligenceStore,
    IntelligenceVectorKB
)
from app.services.intelligence.source_weight_optimizer import SourceWeightOptimizer

logger = logging.getLogger(__name__)

# Celery app配置
celery_app = Celery("intelligence_learning")

# 定时任务调度配置
celery_app.conf.beat_schedule = {
    # 每小时更新信息源权重
    'optimize-source-weights-hourly': {
        'task': 'app.tasks.intelligence_learning.optimize_source_weights',
        'schedule': crontab(minute=0),  # 每小时整点
    },
    
    # 每小时分析用户行为
    'analyze-user-behavior-hourly': {
        'task': 'app.tasks.intelligence_learning.analyze_user_behavior',
        'schedule': crontab(minute=15),  # 每小时15分
    },
    
    # 每日向量化任务
    'vectorize-intelligence-daily': {
        'task': 'app.tasks.intelligence_learning.vectorize_daily_intelligence',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点
    },
    
    # 每日情报质量评估
    'evaluate-intelligence-quality-daily': {
        'task': 'app.tasks.intelligence_learning.evaluate_intelligence_quality',
        'schedule': crontab(hour=3, minute=0),  # 每天凌晨3点
    },
    
    # 每周模式分析
    'analyze-patterns-weekly': {
        'task': 'app.tasks.intelligence_learning.analyze_patterns_weekly',
        'schedule': crontab(day_of_week=1, hour=4, minute=0),  # 每周一凌晨4点
    },
    
    # 每周生成优化报告
    'generate-optimization-report-weekly': {
        'task': 'app.tasks.intelligence_learning.generate_optimization_report',
        'schedule': crontab(day_of_week=0, hour=23, minute=0),  # 每周日23点
    },
    
    # 每4小时自动生成辩论报告
    'auto-generate-debate-report': {
        'task': 'app.tasks.intelligence_learning.auto_generate_debate_report',
        'schedule': crontab(minute=0, hour='*/4'),  # 每4小时
    },
}


@celery_app.task(name='app.tasks.intelligence_learning.optimize_source_weights')
def optimize_source_weights():
    """
    每小时优化信息源权重
    
    职责：
    1. 收集最近1小时的反馈数据
    2. 重新计算各源权重
    3. 更新到数据库
    4. 缓存到Redis
    """
    try:
        logger.info("🔧 开始执行信息源权重优化任务...")
        
        # 初始化优化器
        db = next(get_db())
        optimizer = SourceWeightOptimizer(
            redis_client=redis_client,
            db_session=db
        )
        
        # 执行优化（30天窗口）
        import asyncio
        optimized_weights = asyncio.run(
            optimizer.optimize_weights(time_window_days=30)
        )
        
        logger.info(
            f"✅ 信息源权重优化完成: "
            f"更新了 {len(optimized_weights)} 个源的权重"
        )
        
        return {
            "status": "success",
            "sources_optimized": len(optimized_weights),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 信息源权重优化任务失败: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(name='app.tasks.intelligence_learning.analyze_user_behavior')
def analyze_user_behavior():
    """
    每小时分析用户行为模式
    
    职责：
    1. 统计用户交互行为
    2. 识别高价值行为模式
    3. 计算参与度指标
    """
    try:
        logger.info("📊 开始分析用户行为模式...")
        
        db = next(get_db())
        analyzer = MidTermIntelligenceAnalyzer(
            redis_client=redis_client,
            db_session=db
        )
        
        # 执行分析（24小时窗口）
        import asyncio
        behavior_analysis = asyncio.run(
            analyzer.analyze_user_behavior(time_window_hours=24)
        )
        
        logger.info(
            f"✅ 用户行为分析完成: "
            f"总交互{behavior_analysis.get('total_interactions', 0)}次, "
            f"参与度{behavior_analysis.get('engagement_rate', 0):.1f}%"
        )
        
        return {
            "status": "success",
            "analysis": behavior_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 用户行为分析任务失败: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(name='app.tasks.intelligence_learning.vectorize_daily_intelligence')
def vectorize_daily_intelligence():
    """
    每日向量化任务
    
    职责：
    1. 获取昨日的高价值情报
    2. 向量化并存储到Qdrant
    3. 建立知识积累
    """
    try:
        logger.info("🔮 开始每日情报向量化任务...")
        
        db = next(get_db())
        analyzer = MidTermIntelligenceAnalyzer(
            redis_client=redis_client,
            db_session=db
        )
        
        # 获取向量化候选
        import asyncio
        candidates = asyncio.run(
            analyzer.prepare_vectorization_candidates(min_interaction_threshold=3)
        )
        
        if not candidates:
            logger.info("✓ 无需向量化的候选")
            return {
                "status": "success",
                "vectorized_count": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # 初始化向量知识库
        from app.core.config import settings
        vector_kb = IntelligenceVectorKB(
            qdrant_host=settings.QDRANT_HOST,
            qdrant_port=settings.QDRANT_PORT,
            embedding_provider="qwen"
        )
        
        # 向量化每个候选
        vectorized_count = 0
        for candidate in candidates:
            report_data = candidate.get("report_data", {})
            report_id = candidate.get("report_id", "")
            
            # 提取内容
            content = report_data.get("analysis", "")
            if len(content) < 20:  # 内容太短跳过
                continue
            
            # 构建元数据
            metadata = {
                "source": "multi_platform",
                "category": "intelligence_report",
                "sentiment": report_data.get("market_sentiment", "neutral"),
                "importance": candidate.get("priority", 0.5) / 10,  # 归一化到0-1
                "timestamp": report_data.get("timestamp", datetime.now())
            }
            
            # 向量化
            success = asyncio.run(
                vector_kb.vectorize_intelligence(
                    intelligence_id=report_id,
                    content=content,
                    metadata=metadata
                )
            )
            
            if success:
                vectorized_count += 1
        
        logger.info(f"✅ 情报向量化完成: 成功向量化 {vectorized_count}/{len(candidates)} 个情报")
        
        return {
            "status": "success",
            "candidates_count": len(candidates),
            "vectorized_count": vectorized_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 情报向量化任务失败: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(name='app.tasks.intelligence_learning.evaluate_intelligence_quality')
def evaluate_intelligence_quality():
    """
    每日情报质量评估
    
    职责：
    1. 评估昨日情报的准确性
    2. 统计各源的效果
    3. 生成质量报告
    """
    try:
        logger.info("📈 开始每日情报质量评估...")
        
        db = next(get_db())
        store = LongTermIntelligenceStore(db_session=db)
        
        # 获取Top源
        import asyncio
        top_sources = asyncio.run(
            store.get_top_sources(limit=20, metric="effectiveness")
        )
        
        # 生成质量报告
        quality_report = {
            "date": datetime.now().date().isoformat(),
            "top_sources": top_sources,
            "total_sources_evaluated": len(top_sources),
            "avg_effectiveness": (
                sum(s["effectiveness"] for s in top_sources) / len(top_sources)
                if top_sources else 0
            )
        }
        
        logger.info(
            f"✅ 情报质量评估完成: "
            f"评估{len(top_sources)}个源, "
            f"平均效果{quality_report['avg_effectiveness']:.2f}"
        )
        
        return {
            "status": "success",
            "report": quality_report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 情报质量评估任务失败: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(name='app.tasks.intelligence_learning.analyze_patterns_weekly')
def analyze_patterns_weekly():
    """
    每周模式分析
    
    职责：
    1. 分析过去7天的情报模式
    2. 识别重复出现的主题
    3. 发现市场趋势
    """
    try:
        logger.info("🔍 开始每周模式分析...")
        
        from app.core.config import settings
        vector_kb = IntelligenceVectorKB(
            qdrant_host=settings.QDRANT_HOST,
            qdrant_port=settings.QDRANT_PORT
        )
        
        # 查找不同类别的模式
        categories = ["news", "whale", "onchain", "analysis"]
        all_patterns = []
        
        import asyncio
        for category in categories:
            patterns = asyncio.run(
                vector_kb.find_patterns(
                    category=category,
                    min_importance=0.6,
                    days=7
                )
            )
            all_patterns.extend(patterns)
        
        logger.info(f"✅ 每周模式分析完成: 识别到 {len(all_patterns)} 个模式")
        
        return {
            "status": "success",
            "patterns_found": len(all_patterns),
            "categories_analyzed": categories,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 每周模式分析任务失败: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(name='app.tasks.intelligence_learning.generate_optimization_report')
def generate_optimization_report():
    """
    每周生成优化报告
    
    职责：
    1. 汇总本周优化数据
    2. 生成改进建议
    3. 发送报告（可选）
    """
    try:
        logger.info("📝 开始生成每周优化报告...")
        
        db = next(get_db())
        optimizer = SourceWeightOptimizer(
            redis_client=redis_client,
            db_session=db
        )
        
        # 获取优化报告
        import asyncio
        report = asyncio.run(
            optimizer.get_optimization_report()
        )
        
        # 获取改进建议
        suggestions = asyncio.run(
            optimizer.suggest_improvements()
        )
        
        weekly_report = {
            "week_ending": datetime.now().date().isoformat(),
            "optimization_summary": report,
            "improvement_suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }
        
        logger.info(
            f"✅ 每周优化报告生成完成: "
            f"{len(suggestions)} 条改进建议"
        )
        
        # TODO: 可选地发送报告到管理员邮箱或Telegram
        
        return {
            "status": "success",
            "report": weekly_report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 生成优化报告任务失败: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(name='app.tasks.intelligence_learning.auto_generate_debate_report')
def auto_generate_debate_report():
    """
    每4小时自动生成辩论报告
    
    职责：
    1. 检查是否有新的情报报告
    2. 自动触发辩论生成
    3. 缓存结果到Redis
    4. 避免用户每次都手动触发
    
    优势：
    - 用户访问时直接从缓存读取，无需等待
    - 定期更新，保持报告时效性
    - 降低API调用成本（避免重复生成）
    """
    try:
        logger.info("🤖 开始自动辩论报告生成任务...")
        
        # 检查Redis缓存是否已过期（超过30分钟）
        from app.core.redis_client import redis_client
        import asyncio
        
        async def check_and_generate():
            try:
                # 检查缓存
                cached_report = await redis_client.get("debated_report:latest")
                
                if cached_report:
                    # 检查缓存时间（通过TTL）
                    ttl = await redis_client.ttl("debated_report:latest")
                    remaining_time = ttl if ttl > 0 else 0
                    
                    # 如果缓存剩余时间 > 10分钟，跳过生成
                    if remaining_time > 600:  # 10分钟
                        logger.info(f"⏸️  缓存仍然有效（剩余{remaining_time//60}分钟），跳过生成")
                        return {
                            "status": "skipped",
                            "reason": "cache_still_valid",
                            "remaining_seconds": remaining_time
                        }
                
                # 执行辩论生成
                logger.info("🔄 缓存已过期或不存在，开始生成新的辩论报告...")
                
                from app.core.database import AsyncSessionLocal
                from app.api.v1.intelligence import _execute_debate_and_cache
                
                async with AsyncSessionLocal() as db:
                    await _execute_debate_and_cache(db)
                
                logger.info("✅ 自动辩论报告生成成功")
                
                return {
                    "status": "success",
                    "message": "辩论报告已自动生成并缓存",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ 自动生成辩论报告失败: {e}", exc_info=True)
                raise
        
        result = asyncio.run(check_and_generate())
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 自动辩论报告任务失败: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# 手动触发任务的辅助函数
def trigger_weight_optimization():
    """手动触发权重优化"""
    return optimize_source_weights.delay()


def trigger_debate_generation():
    """手动触发辩论报告生成"""
    return auto_generate_debate_report.delay()


def trigger_behavior_analysis():
    """手动触发行为分析"""
    return analyze_user_behavior.delay()


def trigger_vectorization():
    """手动触发向量化"""
    return vectorize_daily_intelligence.delay()

