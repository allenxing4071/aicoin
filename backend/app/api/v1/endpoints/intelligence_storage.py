"""Intelligence Storage Management API - Qwen情报员存储管理接口"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from app.core.redis_client import redis_client
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.intelligence_source_weight import IntelligenceSourceWeight

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
async def get_storage_stats(db: AsyncSession = Depends(get_db)):
    """
    获取Qwen情报员存储统计信息
    
    返回4层存储的统计数据：
    - L1: Redis短期缓存
    - L2: 中期分析层
    - L3: PostgreSQL长期存储
    - L4: Qdrant向量知识库
    """
    try:
        # === L1: Redis统计 ===
        redis = redis_client
        
        # 统计Redis中的情报报告
        report_keys = await redis.keys("qwen:intelligence:report:*")
        total_reports = len(report_keys)
        
        # 今日报告数（模拟，实际需要根据timestamp过滤）
        today_reports = 0
        for key in report_keys:
            report_data = await redis.get(key)
            if report_data and isinstance(report_data, dict):
                timestamp_str = report_data.get("timestamp", "")
                if timestamp_str:
                    try:
                        report_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        if report_time.date() == datetime.utcnow().date():
                            today_reports += 1
                    except:
                        pass
        
        # 缓存命中率（模拟）
        cache_hit_rate = 0.85
        avg_query_time_ms = 8
        
        l1_stats = {
            "total_reports": total_reports,
            "cache_hit_rate": cache_hit_rate,
            "today_reports": today_reports,
            "avg_query_time_ms": avg_query_time_ms
        }
        
        # === L2: 分析层统计 ===
        # 从数据库获取信息源权重数据
        result = await db.execute(
            select(IntelligenceSourceWeight)
        )
        sources = result.scalars().all()
        
        sources_tracked = len(sources)
        avg_weight = sum(s.dynamic_weight for s in sources) / sources_tracked if sources_tracked > 0 else 0.0
        behavior_records = sum(s.usage_count for s in sources)
        
        last_optimization = max((s.updated_at for s in sources), default=datetime.utcnow())
        
        l2_stats = {
            "sources_tracked": sources_tracked,
            "avg_weight": round(avg_weight, 2),
            "behavior_records": behavior_records,
            "last_optimization": last_optimization.isoformat() if last_optimization else None
        }
        
        # === L3: PostgreSQL统计 ===
        # TODO: 当实际的intelligence_reports表创建后，从这里查询
        # 目前使用模拟数据
        l3_stats = {
            "total_reports": total_reports,  # 应该从PG查询
            "oldest_report": (datetime.utcnow() - timedelta(days=60)).isoformat(),  # 模拟
            "storage_size_mb": 45.3  # 模拟
        }
        
        # === L4: Qdrant向量知识库统计 ===
        # TODO: 当Qdrant集成完成后，从这里查询
        # 目前使用模拟数据
        l4_stats = {
            "vectorized_count": total_reports,  # 模拟，应该从Qdrant查询
            "collection_size": 1536,  # 向量维度
            "last_vectorization": (datetime.utcnow() - timedelta(hours=17)).isoformat()  # 模拟
        }
        
        return {
            "success": True,
            "data": {
                "l1_redis": l1_stats,
                "l2_analyzer": l2_stats,
                "l3_postgres": l3_stats,
                "l4_qdrant": l4_stats
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取存储统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取存储统计失败: {str(e)}")


@router.get("/recent", response_model=Dict[str, Any])
async def get_recent_reports(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    获取最近的情报报告列表
    
    Args:
        limit: 返回数量限制
    """
    try:
        redis = redis_client
        
        # 获取最近的报告keys
        report_keys = await redis.keys("qwen:intelligence:report:*")
        
        # 获取报告数据并排序
        reports = []
        for key in report_keys[:limit]:
            report_data = await redis.get(key)
            if report_data and isinstance(report_data, dict):
                # 提取关键信息
                report = {
                    "report_id": key.split(":")[-1],
                    "timestamp": report_data.get("timestamp"),
                    "market_sentiment": report_data.get("market_sentiment", "neutral"),
                    "sentiment_score": report_data.get("sentiment_score", 0.0),
                    "sources_used": report_data.get("key_news", [])[:3],  # 前3个来源
                    "in_redis": True,
                    "in_postgres": False,  # TODO: 查询PostgreSQL
                    "vectorized": False  # TODO: 查询Qdrant
                }
                reports.append(report)
        
        # 按时间戳排序
        reports.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "success": True,
            "data": {
                "reports": reports[:limit],
                "total": len(report_keys),
                "limit": limit
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取最近报告失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取最近报告失败: {str(e)}")


@router.get("/weights", response_model=Dict[str, Any])
async def get_source_weights(db: AsyncSession = Depends(get_db)):
    """
    获取信息源权重列表
    
    展示各个信息源的权重、使用次数、效果评分等
    """
    try:
        result = await db.execute(
            select(IntelligenceSourceWeight)
            .order_by(IntelligenceSourceWeight.dynamic_weight.desc())
        )
        sources = result.scalars().all()
        
        source_list = []
        for source in sources:
            source_list.append({
                "source_name": source.source_name,
                "source_type": source.source_type,
                "weight": round(source.dynamic_weight, 2),
                "usage_count": source.usage_count,
                "effectiveness_score": round(source.effectiveness_score, 2),
                "last_updated": source.updated_at.isoformat() if source.updated_at else None
            })
        
        return {
            "success": True,
            "data": {
                "sources": source_list,
                "total": len(source_list)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取信息源权重失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取信息源权重失败: {str(e)}")


@router.get("/health", response_model=Dict[str, Any])
async def check_storage_health(db: AsyncSession = Depends(get_db)):
    """
    检查各存储层的健康状态
    
    返回：
    - Redis连接状态
    - PostgreSQL连接状态
    - Qdrant连接状态
    - 各层存储使用率
    """
    try:
        health_status = {
            "redis": {"status": "unknown", "latency_ms": 0},
            "postgres": {"status": "unknown", "latency_ms": 0},
            "qdrant": {"status": "unknown", "latency_ms": 0}
        }
        
        # === 检查Redis ===
        try:
            redis = redis_client
            start_time = datetime.now()
            await redis.ping()
            redis_latency = (datetime.now() - start_time).total_seconds() * 1000
            health_status["redis"] = {
                "status": "healthy",
                "latency_ms": round(redis_latency, 2)
            }
        except Exception as e:
            health_status["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # === 检查PostgreSQL ===
        try:
            start_time = datetime.now()
            await db.execute(select(1))
            pg_latency = (datetime.now() - start_time).total_seconds() * 1000
            health_status["postgres"] = {
                "status": "healthy",
                "latency_ms": round(pg_latency, 2)
            }
        except Exception as e:
            health_status["postgres"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # === 检查Qdrant ===
        # TODO: 当Qdrant集成完成后实现
        health_status["qdrant"] = {
            "status": "not_configured",
            "message": "Qdrant未配置或未启用"
        }
        
        overall_healthy = (
            health_status["redis"]["status"] == "healthy" and
            health_status["postgres"]["status"] == "healthy"
        )
        
        return {
            "success": True,
            "data": {
                "overall_status": "healthy" if overall_healthy else "degraded",
                "storage_layers": health_status
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.get("/system/health", response_model=Dict[str, Any])
async def get_system_health(db: AsyncSession = Depends(get_db)):
    """
    获取情报系统完整健康状态
    
    包含：
    - L1-L4各层健康状态
    - 多平台协调器状态
    - 总体健康评估
    """
    try:
        from app.services.intelligence.monitoring import IntelligenceMonitor
        
        monitor = IntelligenceMonitor(redis_client, db)
        health = await monitor.get_system_health()
        
        return {
            "success": True,
            "data": health,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取系统健康状态失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取系统健康状态失败: {str(e)}")


@router.get("/system/metrics", response_model=Dict[str, Any])
async def get_system_metrics(db: AsyncSession = Depends(get_db)):
    """
    获取情报系统性能指标
    
    包含：
    - 情报收集指标
    - 缓存性能指标
    - 平台调用指标
    - 存储层指标
    """
    try:
        from app.services.intelligence.monitoring import IntelligenceMonitor
        
        monitor = IntelligenceMonitor(redis_client, db)
        metrics = await monitor.get_performance_metrics()
        
        return {
            "success": True,
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取系统指标失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取系统指标失败: {str(e)}")


@router.get("/system/summary", response_model=Dict[str, Any])
async def get_system_summary(db: AsyncSession = Depends(get_db)):
    """
    获取情报系统摘要（健康+性能）
    
    一站式获取系统整体状态
    """
    try:
        from app.services.intelligence.monitoring import IntelligenceMonitor
        
        monitor = IntelligenceMonitor(redis_client, db)
        summary = await monitor.get_system_summary()
        
        return {
            "success": True,
            "data": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取系统摘要失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取系统摘要失败: {str(e)}")


@router.get("/reports/latest", response_model=Dict[str, Any])
async def get_latest_report_with_verification(db: AsyncSession = Depends(get_db)):
    """
    获取最新情报报告（包含多平台验证信息）
    
    返回增强的情报报告，包含：
    - 基础情报数据
    - 多平台贡献信息
    - 平台共识度
    - 验证元数据
    """
    try:
        from app.services.intelligence.intelligence_coordinator import IntelligenceCoordinator
        
        coordinator = IntelligenceCoordinator(redis_client, db)
        report = await coordinator.get_latest_intelligence()
        
        if not report:
            return {
                "success": False,
                "message": "暂无情报报告",
                "data": None
            }
        
        # 转换为字典格式
        report_dict = {
            "timestamp": report.timestamp.isoformat(),
            "market_sentiment": report.market_sentiment.value,
            "sentiment_score": report.sentiment_score,
            "confidence": report.confidence,
            "qwen_analysis": report.qwen_analysis,
            "risk_factors": report.risk_factors,
            "opportunities": report.opportunities,
            "key_news_count": len(report.key_news) if report.key_news else 0,
            "whale_signals_count": len(report.whale_signals) if report.whale_signals else 0,
        }
        
        # 添加多平台验证信息
        if hasattr(report, 'platform_contributions'):
            report_dict['platform_contributions'] = report.platform_contributions
        if hasattr(report, 'platform_consensus'):
            report_dict['platform_consensus'] = report.platform_consensus
        if hasattr(report, 'verification_metadata'):
            report_dict['verification_metadata'] = report.verification_metadata
        if hasattr(report, 'summary'):
            report_dict['summary'] = report.summary
        
        return {
            "success": True,
            "data": report_dict,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取最新报告失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取最新报告失败: {str(e)}")

