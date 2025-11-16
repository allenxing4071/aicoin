"""Intelligence Report API Endpoints"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc

from app.core.database import get_db
from app.models.intelligence import IntelligenceReport
from app.services.intelligence.storage import intelligence_storage

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/latest")
async def get_latest_intelligence():
    """获取最新情报（快捷路径）"""
    try:
        report = await intelligence_storage.get_latest_report()
        if not report:
            raise HTTPException(status_code=404, detail="暂无最新情报报告")
        
        return {
            "success": True,
            "data": report.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取最新情报失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_intelligence(db: AsyncSession = Depends(get_db)):
    """手动触发情报收集（使用新的IntelligenceCoordinator）"""
    try:
        # 使用新的统一协调器
        from app.services.intelligence.intelligence_coordinator import IntelligenceCoordinator
        from app.core.redis_client import redis_client
        
        logger.info("🔄 手动触发情报收集（使用IntelligenceCoordinator）...")
        
        # 创建协调器并执行收集
        coordinator = IntelligenceCoordinator(redis_client, db)
        report = await coordinator.collect_intelligence()
        
        if not report:
            raise HTTPException(status_code=500, detail="情报收集失败，请检查日志")
        
        return {
            "success": True,
            "message": "情报收集成功（多平台验证+四层存储）",
            "data": report.to_dict()
        }
    
    except Exception as e:
        logger.error(f"手动收集情报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports")
async def get_reports(
    limit: int = Query(default=20, ge=1, le=100, description="返回记录数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取情报报告列表（简化版本）
    用于前端页面快速获取最新报告
    """
    try:
        from sqlalchemy import select
        # 查询最新的报告
        stmt = select(IntelligenceReport)\
                .order_by(desc(IntelligenceReport.timestamp))\
                .limit(limit)
        result = await db.execute(stmt)
        reports = result.scalars().all()
        
        return {
            "success": True,
            "data": [r.to_dict() for r in reports],
            "total": len(reports)
        }
    
    except Exception as e:
        logger.error(f"获取情报报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/latest")
async def get_latest_report():
    """获取最新的情报报告（来自Redis缓存）"""
    try:
        report = await intelligence_storage.get_latest_report()
        if not report:
            raise HTTPException(status_code=404, detail="暂无最新情报报告")
        
        return {
            "success": True,
            "data": report.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取最新情报报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/history")
async def get_report_history(
    limit: int = Query(default=10, ge=1, le=100, description="返回记录数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
    start_date: Optional[datetime] = Query(default=None, description="起始时间"),
    end_date: Optional[datetime] = Query(default=None, description="结束时间"),
    sentiment: Optional[str] = Query(default=None, description="情绪类型: BULLISH/BEARISH/NEUTRAL"),
    min_confidence: Optional[float] = Query(default=None, ge=0.0, le=1.0, description="最小置信度"),
    db: Session = Depends(get_db)
):
    """
    获取历史情报报告（来自PostgreSQL持久化存储）
    
    支持多种筛选条件：
    - 时间范围
    - 情绪类型
    - 最小置信度
    """
    try:
        # 构建查询
        query = db.query(IntelligenceReport)
        
        # 时间范围筛选
        if start_date:
            query = query.filter(IntelligenceReport.timestamp >= start_date)
        if end_date:
            query = query.filter(IntelligenceReport.timestamp <= end_date)
        
        # 情绪类型筛选
        if sentiment:
            query = query.filter(IntelligenceReport.market_sentiment == sentiment.upper())
        
        # 置信度筛选
        if min_confidence is not None:
            query = query.filter(IntelligenceReport.confidence >= min_confidence)
        
        # 排序和分页
        total = query.count()
        reports = query.order_by(desc(IntelligenceReport.timestamp))\
                      .offset(offset)\
                      .limit(limit)\
                      .all()
        
        return {
            "success": True,
            "data": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "reports": [r.to_dict() for r in reports]
            }
        }
    
    except Exception as e:
        logger.error(f"获取历史情报报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}")
async def get_report_by_id(
    report_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取特定情报报告"""
    try:
        report = db.query(IntelligenceReport).filter(
            IntelligenceReport.id == report_id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail=f"情报报告不存在: ID={report_id}")
        
        return {
            "success": True,
            "data": report.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取情报报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/summary")
async def get_analytics_summary(
    days: int = Query(default=7, ge=1, le=90, description="统计天数"),
    db: Session = Depends(get_db)
):
    """
    获取情报分析统计摘要
    
    包括：
    - 总报告数
    - 情绪分布
    - 平均置信度
    - 趋势分析
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # 基础统计
        total_reports = db.query(func.count(IntelligenceReport.id))\
            .filter(IntelligenceReport.timestamp >= start_date)\
            .scalar()
        
        # 情绪分布
        sentiment_stats = db.query(
            IntelligenceReport.market_sentiment,
            func.count(IntelligenceReport.id).label('count')
        ).filter(
            IntelligenceReport.timestamp >= start_date
        ).group_by(
            IntelligenceReport.market_sentiment
        ).all()
        
        sentiment_distribution = {
            s[0]: s[1] for s in sentiment_stats
        }
        
        # 平均置信度
        avg_confidence = db.query(
            func.avg(IntelligenceReport.confidence)
        ).filter(
            IntelligenceReport.timestamp >= start_date
        ).scalar()
        
        # 每日报告数
        daily_reports = db.query(
            func.date(IntelligenceReport.timestamp).label('date'),
            func.count(IntelligenceReport.id).label('count')
        ).filter(
            IntelligenceReport.timestamp >= start_date
        ).group_by(
            func.date(IntelligenceReport.timestamp)
        ).order_by(
            desc('date')
        ).all()
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().isoformat(),
                "total_reports": total_reports or 0,
                "sentiment_distribution": sentiment_distribution,
                "average_confidence": float(avg_confidence) if avg_confidence else 0.0,
                "daily_reports": [
                    {
                        "date": str(d[0]),
                        "count": d[1]
                    }
                    for d in daily_reports
                ]
            }
        }
    
    except Exception as e:
        logger.error(f"获取统计摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/sentiment-trend")
async def get_sentiment_trend(
    days: int = Query(default=30, ge=1, le=90, description="统计天数"),
    db: Session = Depends(get_db)
):
    """
    获取市场情绪趋势
    
    返回每日的情绪分布，用于趋势分析
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # 查询每日各情绪的数量
        trend_data = db.query(
            func.date(IntelligenceReport.timestamp).label('date'),
            IntelligenceReport.market_sentiment,
            func.count(IntelligenceReport.id).label('count'),
            func.avg(IntelligenceReport.sentiment_score).label('avg_score')
        ).filter(
            IntelligenceReport.timestamp >= start_date
        ).group_by(
            func.date(IntelligenceReport.timestamp),
            IntelligenceReport.market_sentiment
        ).order_by(
            'date'
        ).all()
        
        # 组织数据
        daily_data = {}
        for row in trend_data:
            date_str = str(row[0])
            if date_str not in daily_data:
                daily_data[date_str] = {
                    "date": date_str,
                    "sentiments": {},
                    "scores": {}
                }
            daily_data[date_str]["sentiments"][row[1]] = row[2]
            daily_data[date_str]["scores"][row[1]] = float(row[3]) if row[3] else 0.0
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "trend": list(daily_data.values())
            }
        }
    
    except Exception as e:
        logger.error(f"获取情绪趋势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/data-quality")
async def get_data_quality_stats(
    days: int = Query(default=7, ge=1, le=30, description="统计天数"),
    db: Session = Depends(get_db)
):
    """
    获取数据质量统计
    
    包括：
    - 各数据源的覆盖率
    - 置信度分布
    - 数据完整性
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        reports = db.query(IntelligenceReport).filter(
            IntelligenceReport.timestamp >= start_date
        ).all()
        
        if not reports:
            return {
                "success": True,
                "data": {
                    "period_days": days,
                    "total_reports": 0,
                    "data_coverage": {},
                    "confidence_distribution": {},
                    "completeness": 0.0
                }
            }
        
        # 数据覆盖率
        coverage = {
            "news": sum(1 for r in reports if r.key_news and len(r.key_news) > 0),
            "whale": sum(1 for r in reports if r.whale_signals and len(r.whale_signals) > 0),
            "onchain": sum(1 for r in reports if r.on_chain_metrics),
        }
        
        # 置信度分布
        confidence_ranges = {
            "0.0-0.3": 0,
            "0.3-0.5": 0,
            "0.5-0.7": 0,
            "0.7-0.9": 0,
            "0.9-1.0": 0
        }
        
        for r in reports:
            conf = r.confidence
            if conf < 0.3:
                confidence_ranges["0.0-0.3"] += 1
            elif conf < 0.5:
                confidence_ranges["0.3-0.5"] += 1
            elif conf < 0.7:
                confidence_ranges["0.5-0.7"] += 1
            elif conf < 0.9:
                confidence_ranges["0.7-0.9"] += 1
            else:
                confidence_ranges["0.9-1.0"] += 1
        
        # 完整性评分（有分析文本的比例）
        complete_reports = sum(
            1 for r in reports 
            if r.qwen_analysis and len(r.qwen_analysis) > 0
        )
        completeness = complete_reports / len(reports) if reports else 0.0
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "total_reports": len(reports),
                "data_coverage": {
                    "news_coverage": coverage["news"] / len(reports),
                    "whale_coverage": coverage["whale"] / len(reports),
                    "onchain_coverage": coverage["onchain"] / len(reports),
                },
                "confidence_distribution": confidence_ranges,
                "completeness_score": completeness
            }
        }
    
    except Exception as e:
        logger.error(f"获取数据质量统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debated-report")
async def get_debated_intelligence_report(db: AsyncSession = Depends(get_db)):
    """
    获取经过辩论验证的情报报告（从缓存读取）
    
    流程：
    1. 优先从 Redis 缓存读取最新的辩论报告
    2. 如果缓存不存在，返回最新的 Qwen 情报（未辩论）
    3. 建议：使用 POST /trigger-debate 在后台生成新的辩论报告
    """
    try:
        from app.core.redis_client import redis_client
        import json
        
        logger.info("🔄 获取辩论报告（从缓存）...")
        
        # 1. 尝试从 Redis 缓存获取
        cached_report = await redis_client.get("debated_report:latest")
        
        if cached_report:
            try:
                # 如果已经是字典，直接使用；否则解析JSON
                if isinstance(cached_report, dict):
                    debate_data = cached_report
                elif isinstance(cached_report, str):
                    debate_data = json.loads(cached_report)
                else:
                    # 尝试解码为字符串后再解析
                    debate_data = json.loads(str(cached_report))
                
                logger.info("✅ 从缓存返回辩论报告")
                return {
                    "success": True,
                    "data": debate_data,
                    "cached": True
                }
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.warning(f"缓存解析失败: {e}, 类型: {type(cached_report)}")
        
        # 2. 缓存不存在，返回原始情报 + 提示
        logger.info("⚠️  缓存中无辩论报告，返回原始情报")
        report = await intelligence_storage.get_latest_report()
        if not report:
            raise HTTPException(status_code=404, detail="暂无最新情报报告")
        
        # 准备情报字典
        intelligence_dict = {
            "market_sentiment": report.market_sentiment.value if hasattr(report.market_sentiment, 'value') else str(report.market_sentiment),
            "confidence": report.confidence,
            "summary": report.qwen_analysis[:500] if report.qwen_analysis else "",
            "key_news": report.key_news[:3] if report.key_news else [],
            "whale_signals": report.whale_signals[:3] if report.whale_signals else [],
            "platform_contributions": getattr(report, 'platform_contributions', {}),
            "platform_consensus": getattr(report, 'platform_consensus', 0.0),
        }
        
        return {
            "success": True,
            "data": {
                "original_intelligence": {
                    "market_sentiment": intelligence_dict["market_sentiment"],
                    "confidence": intelligence_dict["confidence"],
                    "summary": intelligence_dict["summary"],
                    "key_news": intelligence_dict["key_news"],
                    "whale_signals": intelligence_dict["whale_signals"],
                    "timestamp": report.timestamp.isoformat() if report.timestamp else None
                },
                "debate_result": None,  # 无辩论结果
                "enhanced_sentiment": intelligence_dict["market_sentiment"],
                "enhanced_confidence": intelligence_dict["confidence"],
                "is_debated": False
            },
            "cached": False,
            "message": "辩论报告未生成，请调用 POST /trigger-debate 生成"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取辩论报告失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


async def _execute_debate_and_cache(db: AsyncSession):
    """
    执行辩论并将结果缓存到 Redis（内部函数）
    """
    from app.services.decision.debate_system import DebateCoordinator
    from app.services.decision.prompt_manager_db import PromptManagerDB
    from app.core.redis_client import redis_client
    import openai
    import json
    from app.core.config import settings
    
    try:
        logger.info("🔄 开始执行辩论...")
        
        # 1. 获取最新的 Qwen 情报
        report = await intelligence_storage.get_latest_report()
        if not report:
            raise ValueError("暂无最新情报报告")
        
        logger.info(f"📊 获取到 Qwen 情报: 情绪={report.market_sentiment}, 置信度={report.confidence:.2%}")
        
        # 2. 准备市场数据（简化版，用于辩论）
        market_data = {
            "BTC": {
                "price": 95000,  # 可以从实际市场数据获取
                "change_24h": 2.5
            }
        }
        
        # 3. 准备情报字典（确保所有对象都可序列化）
        def serialize_news_item(item):
            """将 NewsItem 对象转换为字典"""
            if isinstance(item, dict):
                return item
            return {
                "title": getattr(item, 'title', ''),
                "source": getattr(item, 'source', ''),
                "url": getattr(item, 'url', ''),
                "published_at": str(getattr(item, 'published_at', '')),
                "content": getattr(item, 'content', ''),
                "impact": getattr(item, 'impact', 'medium'),
                "sentiment": getattr(item, 'sentiment', 'neutral')
            }
        
        def serialize_whale_signal(item):
            """将 WhaleSignal 对象转换为字典"""
            if isinstance(item, dict):
                return item
            return {
                "symbol": getattr(item, 'symbol', ''),
                "action": getattr(item, 'action', ''),
                "amount_usd": float(getattr(item, 'amount_usd', 0)),
                "address": getattr(item, 'address', ''),
                "timestamp": str(getattr(item, 'timestamp', '')),
                "exchange": getattr(item, 'exchange', None)
            }
        
        intelligence_dict = {
            "market_sentiment": report.market_sentiment.value if hasattr(report.market_sentiment, 'value') else str(report.market_sentiment),
            "confidence": float(report.confidence) if report.confidence else 0.0,
            "summary": report.qwen_analysis[:500] if report.qwen_analysis else "",
            "key_news": [serialize_news_item(item) for item in (report.key_news[:3] if report.key_news else [])],
            "whale_signals": [serialize_whale_signal(item) for item in (report.whale_signals[:3] if report.whale_signals else [])],
            "platform_contributions": getattr(report, 'platform_contributions', {}),
            "platform_consensus": float(getattr(report, 'platform_consensus', 0.0)),
        }
        
        # 4. 初始化辩论系统
        llm_client = openai.OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )
        
        prompt_manager = PromptManagerDB(db)
        
        debate_coordinator = DebateCoordinator(
            llm_client=llm_client,
            max_debate_rounds=1,  # 1轮辩论
            timeout_seconds=60,
            prompt_manager=prompt_manager
        )
        
        # 5. 执行辩论
        logger.info("⚔️  启动多空辩论...")
        debate_result = await debate_coordinator.conduct_debate(
            market_data=market_data,
            intelligence_report=intelligence_dict,
            past_memories=[]
        )
        
        logger.info(f"✅ 辩论完成: 推荐={debate_result['final_decision'].get('recommendation')}, "
                   f"共识度={debate_result['consensus_level']:.2f}")
        
        # 6. 构建结果数据（确保所有数值可序列化）
        result_data = {
            # 原始 Qwen 情报
            "original_intelligence": {
                "market_sentiment": intelligence_dict["market_sentiment"],
                "confidence": intelligence_dict["confidence"],
                "summary": intelligence_dict["summary"],
                "key_news": intelligence_dict["key_news"],
                "whale_signals": intelligence_dict["whale_signals"],
                "timestamp": report.timestamp.isoformat() if report.timestamp else None
            },
            # 辩论结果
            "debate_result": {
                "recommendation": str(debate_result['final_decision'].get('recommendation', 'HOLD')),
                "confidence": float(debate_result['final_decision'].get('confidence', 0.5)),
                "reasoning": str(debate_result['final_decision'].get('reasoning', '')),
                "bull_argument": debate_result['debate_history'].get('bull_arguments', []),
                "bear_argument": debate_result['debate_history'].get('bear_arguments', []),
                "consensus_level": float(debate_result.get('consensus_level', 0.0)),
                "total_rounds": int(debate_result.get('total_rounds', 0)),
                "duration_seconds": float(debate_result.get('duration_seconds', 0.0))
            },
            # 综合分析
            "enhanced_sentiment": str(debate_result['final_decision'].get('recommendation', 'HOLD')),
            "enhanced_confidence": float(debate_result['final_decision'].get('confidence', 0.5)),
            "is_debated": True
        }
        
        # 7. 保存到 Redis 缓存（30分钟过期）
        await redis_client.setex(
            "debated_report:latest",
            1800,  # 30分钟
            json.dumps(result_data, ensure_ascii=False)
        )
        
        logger.info("💾 辩论结果已缓存到 Redis")
        return result_data
        
    except Exception as e:
        logger.error(f"辩论执行失败: {e}", exc_info=True)
        raise


@router.post("/trigger-debate")
async def trigger_debate_manually(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """
    手动触发情报辩论（异步后台执行）
    
    用户可以点击按钮手动触发新一轮辩论
    辩论将在后台执行，避免超时
    """
    try:
        import asyncio
        
        logger.info("🚀 启动后台辩论任务...")
        
        # 在后台执行辩论
        async def run_debate_in_background():
            try:
                # 创建新的数据库会话
                from app.core.database import AsyncSessionLocal
                async with AsyncSessionLocal() as bg_db:
                    await _execute_debate_and_cache(bg_db)
                    logger.info("✅ 后台辩论任务完成")
            except Exception as e:
                logger.error(f"❌ 后台辩论任务失败: {e}", exc_info=True)
        
        # 启动后台任务
        asyncio.create_task(run_debate_in_background())
        
        return {
            "success": True,
            "message": "辩论已启动，正在后台执行中...",
            "status": "processing",
            "estimated_time": "60-90秒"
        }
    
    except Exception as e:
        logger.error(f"启动辩论任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
