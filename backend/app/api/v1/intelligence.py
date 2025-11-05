"""Intelligence Report API Endpoints"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
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
async def refresh_intelligence():
    """手动触发情报收集"""
    try:
        # 导入并调用情报收集服务
        from app.services.intelligence.qwen_engine import qwen_intelligence_officer
        
        logger.info("🔄 手动触发情报收集...")
        
        # 执行情报收集
        report = await qwen_intelligence_officer.collect_intelligence()
        
        if not report:
            raise HTTPException(status_code=500, detail="情报收集失败，请检查日志")
        
        return {
            "success": True,
            "message": "情报收集成功",
            "data": report.to_dict()
        }
    
    except Exception as e:
        logger.error(f"手动收集情报失败: {e}")
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
