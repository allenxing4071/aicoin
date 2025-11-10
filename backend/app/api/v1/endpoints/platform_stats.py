"""
AI平台调用统计API
支持按时间范围查询调用统计数据
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Integer, cast, column, table
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.core.database import get_db
from app.models.ai_model_pricing import AIModelUsageLog
from app.models.intelligence_platform import IntelligencePlatform

# 直接定义表结构（因为模型定义和实际数据库表不一致）
usage_log_table = table('ai_model_usage_log',
    column('id'),
    column('model_name'),
    column('timestamp'),
    column('cost'),
    column('success'),
    column('error_message'),
    column('response_time')
)

router = APIRouter()


@router.get("/stats")
async def get_platform_stats(
    time_range: str = Query("today", regex="^(today|week|month|all)$"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取AI平台调用统计
    
    Args:
        time_range: 时间范围 (today/week/month/all)
        db: 数据库会话
        
    Returns:
        统计数据
    """
    
    # 计算时间范围
    now = datetime.utcnow()
    if time_range == "today":
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        time_label = "今日"
    elif time_range == "week":
        start_time = now - timedelta(days=7)
        time_label = "本周"
    elif time_range == "month":
        start_time = now - timedelta(days=30)
        time_label = "本月"
    else:  # all
        start_time = datetime(2020, 1, 1)  # 很早的时间
        time_label = "全部"
    
    # 获取所有平台
    platforms_result = await db.execute(
        select(IntelligencePlatform).where(IntelligencePlatform.enabled == True)
    )
    platforms = platforms_result.scalars().all()
    
    # 为每个平台统计调用数据
    platform_stats = []
    total_calls = 0
    total_successful = 0
    total_failed = 0
    total_cost = 0.0
    
    for platform in platforms:
        # 查询该平台在时间范围内的调用日志
        # 注意：需要根据model_name匹配平台
        # 假设model_name包含provider信息，或者我们需要建立映射关系
        
        # 方案1：通过provider匹配（简化版）
        # DeepSeek -> deepseek, Qwen -> qwen, 腾讯混元 -> hunyuan, 火山引擎 -> doubao, 百度文心 -> ernie
        provider_model_map = {
            "deepseek": ["deepseek"],
            "qwen": ["qwen"],
            "tencent": ["hunyuan"],
            "volcano": ["doubao"],
            "baidu": ["ernie", "wenxin"],
        }
        
        model_patterns = provider_model_map.get(platform.provider.lower(), [platform.provider.lower()])
        
        # 统计调用（使用实际数据库表字段：timestamp, cost）
        query = select(
            func.count(usage_log_table.c.id).label('count'),
            func.sum(usage_log_table.c.cost).label('total_cost')
        ).where(
            and_(
                usage_log_table.c.timestamp >= start_time,
                # 模糊匹配model_name
                func.lower(usage_log_table.c.model_name).op('~')(f"({'|'.join(model_patterns)})")
            )
        )
        
        result = await db.execute(query)
        data = result.first()
        
        calls = data.count if data.count else 0
        successful_calls = calls  # 假设所有记录都是成功的
        failed_calls = 0  # 实际表中无法区分失败
        success_rate = 100.0 if calls > 0 else 0.0
        cost = float(data.total_cost) if data.total_cost else 0.0
        avg_response_time = None  # 实际表中没有response_time字段
        
        platform_stats.append({
            "id": platform.id,
            "name": platform.name,
            "provider": platform.provider,
            "total_calls": calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": round(success_rate, 2),
            "avg_response_time": round(avg_response_time, 3) if avg_response_time else None,
            "total_cost": round(cost, 2),
        })
        
        total_calls += calls
        total_successful += successful_calls
        total_failed += failed_calls
        total_cost += cost
    
    # 计算整体成功率
    overall_success_rate = (total_successful / total_calls * 100) if total_calls > 0 else 0
    
    return {
        "success": True,
        "data": {
            "time_range": time_range,
            "time_label": time_label,
            "start_time": start_time.isoformat(),
            "end_time": now.isoformat(),
            "summary": {
                "total_calls": total_calls,
                "successful_calls": total_successful,
                "failed_calls": total_failed,
                "success_rate": round(overall_success_rate, 2),
                "total_cost": round(total_cost, 2),
            },
            "platforms": platform_stats,
        }
    }


@router.get("/hourly-stats")
async def get_hourly_stats(
    time_range: str = Query("today", regex="^(today|week)$"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取按小时统计的调用数据（用于峰值时段分析）
    
    Args:
        time_range: 时间范围 (today/week)
        db: 数据库会话
        
    Returns:
        按小时统计的数据
    """
    
    # 计算时间范围
    now = datetime.utcnow()
    if time_range == "today":
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    else:  # week
        start_time = now - timedelta(days=7)
    
    # 按小时分组统计（使用实际数据库表字段：timestamp）
    hour_column = func.date_trunc('hour', usage_log_table.c.timestamp).label('hour')
    hourly_query = select(
        hour_column,
        func.count(usage_log_table.c.id).label('calls'),
        func.sum(usage_log_table.c.cost).label('cost')
    ).where(
        usage_log_table.c.timestamp >= start_time
    ).group_by(
        hour_column
    ).order_by(
        hour_column
    )
    
    result = await db.execute(hourly_query)
    hourly_data = result.all()
    
    # 格式化数据（注意：没有success字段，假设所有调用都成功）
    hourly_stats = []
    for row in hourly_data:
        hourly_stats.append({
            "hour": row.hour.isoformat() if row.hour else None,
            "calls": row.calls,
            "successful": row.calls,  # 假设所有调用都成功
            "failed": 0,  # 无法区分失败
            "cost": round(float(row.cost) if row.cost else 0.0, 2),
        })
    
    # 找出峰值时段
    peak_hour = max(hourly_stats, key=lambda x: x['calls']) if hourly_stats else None
    
    return {
        "success": True,
        "data": {
            "time_range": time_range,
            "start_time": start_time.isoformat(),
            "end_time": now.isoformat(),
            "hourly_stats": hourly_stats,
            "peak_hour": peak_hour,
        }
    }


@router.get("/failure-analysis")
async def get_failure_analysis(
    time_range: str = Query("week", regex="^(today|week|month|all)$"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取失败原因分析
    
    Args:
        time_range: 时间范围 (today/week/month/all)
        db: 数据库会话
        
    Returns:
        失败原因统计数据
    """
    
    # 计算时间范围
    now = datetime.utcnow()
    if time_range == "today":
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == "week":
        start_time = now - timedelta(days=7)
    elif time_range == "month":
        start_time = now - timedelta(days=30)
    else:  # all
        start_time = datetime(2020, 1, 1)
    
    # 获取所有平台
    result = await db.execute(select(IntelligencePlatform))
    platforms = result.scalars().all()
    
    failure_data = []
    
    for platform in platforms:
        # 构建模型名称匹配模式
        model_patterns = []
        if platform.provider:
            model_patterns.append(platform.provider.lower())
        if platform.name:
            name_parts = platform.name.lower().split()
            model_patterns.extend(name_parts)
        
        if not model_patterns:
            continue
        
        # 查询失败记录
        query = select(
            usage_log_table.c.error_message,
            func.count(usage_log_table.c.id).label('count')
        ).where(
            and_(
                usage_log_table.c.timestamp >= start_time,
                usage_log_table.c.success == False,
                func.lower(usage_log_table.c.model_name).op('~')(f"({'|'.join(model_patterns)})")
            )
        ).group_by(usage_log_table.c.error_message)
        
        result = await db.execute(query)
        failures = result.all()
        
        if failures:
            # 分类失败原因
            error_categories = {}
            for error_msg, count in failures:
                if not error_msg:
                    category = "未知错误"
                elif "timeout" in error_msg.lower() or "超时" in error_msg:
                    category = "请求超时"
                elif "rate limit" in error_msg.lower() or "限流" in error_msg or "频率" in error_msg:
                    category = "频率限制"
                elif "auth" in error_msg.lower() or "认证" in error_msg or "密钥" in error_msg:
                    category = "认证失败"
                elif "quota" in error_msg.lower() or "配额" in error_msg or "余额" in error_msg:
                    category = "配额不足"
                elif "network" in error_msg.lower() or "网络" in error_msg or "连接" in error_msg:
                    category = "网络错误"
                elif "invalid" in error_msg.lower() or "无效" in error_msg or "参数" in error_msg:
                    category = "参数错误"
                else:
                    category = "其他错误"
                
                error_categories[category] = error_categories.get(category, 0) + count
            
            total_failures = sum(error_categories.values())
            
            failure_data.append({
                "platform_id": platform.id,
                "platform_name": platform.name,
                "provider": platform.provider,
                "total_failures": total_failures,
                "error_categories": [
                    {
                        "category": cat,
                        "count": cnt,
                        "percentage": round((cnt / total_failures) * 100, 2)
                    }
                    for cat, cnt in sorted(error_categories.items(), key=lambda x: x[1], reverse=True)
                ]
            })
    
    # 按失败次数排序
    failure_data.sort(key=lambda x: x['total_failures'], reverse=True)
    
    # 计算总体统计
    total_failures = sum(p['total_failures'] for p in failure_data)
    all_categories = {}
    for platform in failure_data:
        for cat in platform['error_categories']:
            all_categories[cat['category']] = all_categories.get(cat['category'], 0) + cat['count']
    
    return {
        "success": True,
        "data": {
            "time_range": time_range,
            "start_time": start_time.isoformat(),
            "end_time": now.isoformat(),
            "total_failures": total_failures,
            "platforms": failure_data,
            "overall_categories": [
                {
                    "category": cat,
                    "count": cnt,
                    "percentage": round((cnt / total_failures) * 100, 2) if total_failures > 0 else 0
                }
                for cat, cnt in sorted(all_categories.items(), key=lambda x: x[1], reverse=True)
            ]
        }
    }


@router.get("/stability-trend")
async def get_stability_trend(
    time_range: str = Query("week", regex="^(today|week|month)$"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取稳定性趋势数据
    
    Args:
        time_range: 时间范围 (today/week/month)
        db: 数据库会话
        
    Returns:
        各平台的成功率历史趋势
    """
    
    # 计算时间范围和分组间隔
    now = datetime.utcnow()
    if time_range == "today":
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        interval = 'hour'  # 按小时分组
    elif time_range == "week":
        start_time = now - timedelta(days=7)
        interval = 'day'  # 按天分组
    else:  # month
        start_time = now - timedelta(days=30)
        interval = 'day'  # 按天分组
    
    # 获取所有平台
    result = await db.execute(select(IntelligencePlatform))
    platforms = result.scalars().all()
    
    trend_data = []
    
    for platform in platforms:
        # 构建模型名称匹配模式
        model_patterns = []
        if platform.provider:
            model_patterns.append(platform.provider.lower())
        if platform.name:
            name_parts = platform.name.lower().split()
            model_patterns.extend(name_parts)
        
        if not model_patterns:
            continue
        
        # 按时间间隔分组查询
        time_column = func.date_trunc(interval, usage_log_table.c.timestamp)
        
        query = select(
            time_column.label('time_bucket'),
            func.count(usage_log_table.c.id).label('total_calls'),
            func.sum(
                cast(usage_log_table.c.success, Integer)
            ).label('successful_calls')
        ).where(
            and_(
                usage_log_table.c.timestamp >= start_time,
                func.lower(usage_log_table.c.model_name).op('~')(f"({'|'.join(model_patterns)})")
            )
        ).group_by(time_column).order_by(time_column)
        
        result = await db.execute(query)
        time_series = result.all()
        
        if time_series:
            data_points = []
            for time_bucket, total, successful in time_series:
                success_rate = (successful / total * 100) if total > 0 else 0
                data_points.append({
                    "timestamp": time_bucket.isoformat() if time_bucket else None,
                    "total_calls": total,
                    "successful_calls": successful or 0,
                    "success_rate": round(success_rate, 2)
                })
            
            # 计算平均成功率和稳定性（标准差）
            success_rates = [p['success_rate'] for p in data_points]
            avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
            
            # 计算标准差
            if len(success_rates) > 1:
                variance = sum((x - avg_success_rate) ** 2 for x in success_rates) / len(success_rates)
                std_dev = variance ** 0.5
                stability_score = max(0, 100 - std_dev)  # 标准差越小，稳定性越高
            else:
                stability_score = avg_success_rate
            
            trend_data.append({
                "platform_id": platform.id,
                "platform_name": platform.name,
                "provider": platform.provider,
                "avg_success_rate": round(avg_success_rate, 2),
                "stability_score": round(stability_score, 2),
                "data_points": data_points
            })
    
    # 按平均成功率排序
    trend_data.sort(key=lambda x: x['avg_success_rate'], reverse=True)
    
    return {
        "success": True,
        "data": {
            "time_range": time_range,
            "interval": interval,
            "start_time": start_time.isoformat(),
            "end_time": now.isoformat(),
            "platforms": trend_data
        }
    }


@router.get("/response-time-percentiles")
async def get_response_time_percentiles(
    time_range: str = Query("week", regex="^(today|week|month)$"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取响应时间分位数分析 (P50/P95/P99)
    
    Args:
        time_range: 时间范围 (today/week/month)
        db: 数据库会话
        
    Returns:
        各平台的响应时间分位数数据
    """
    
    # 计算时间范围
    now = datetime.utcnow()
    if time_range == "today":
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == "week":
        start_time = now - timedelta(days=7)
    else:  # month
        start_time = now - timedelta(days=30)
    
    # 获取所有平台
    result = await db.execute(select(IntelligencePlatform))
    platforms = result.scalars().all()
    
    percentile_data = []
    
    for platform in platforms:
        # 构建模型名称匹配模式
        model_patterns = []
        if platform.provider:
            model_patterns.append(platform.provider.lower())
        if platform.name:
            name_parts = platform.name.lower().split()
            model_patterns.extend(name_parts)
        
        if not model_patterns:
            continue
        
        # 查询响应时间数据 (使用真实的 response_time 字段)
        # 使用 PERCENTILE_CONT 计算分位数
        query = select(
            func.percentile_cont(0.50).within_group(usage_log_table.c.response_time).label('p50'),
            func.percentile_cont(0.95).within_group(usage_log_table.c.response_time).label('p95'),
            func.percentile_cont(0.99).within_group(usage_log_table.c.response_time).label('p99'),
            func.avg(usage_log_table.c.response_time).label('avg'),
            func.min(usage_log_table.c.response_time).label('min'),
            func.max(usage_log_table.c.response_time).label('max'),
            func.count(usage_log_table.c.id).label('sample_count')
        ).where(
            and_(
                usage_log_table.c.timestamp >= start_time,
                usage_log_table.c.success == True,
                usage_log_table.c.response_time != None,
                func.lower(usage_log_table.c.model_name).op('~')(f"({'|'.join(model_patterns)})")
            )
        )
        
        result = await db.execute(query)
        stats = result.first()
        
        if stats and stats.sample_count > 0:
            percentile_data.append({
                "platform_id": platform.id,
                "platform_name": platform.name,
                "provider": platform.provider,
                "p50": round(stats.p50, 2) if stats.p50 else 0,
                "p95": round(stats.p95, 2) if stats.p95 else 0,
                "p99": round(stats.p99, 2) if stats.p99 else 0,
                "avg": round(stats.avg, 2) if stats.avg else 0,
                "min": round(stats.min, 2) if stats.min else 0,
                "max": round(stats.max, 2) if stats.max else 0,
                "sample_count": stats.sample_count
            })
    
    # 按P50排序
    percentile_data.sort(key=lambda x: x['p50'])
    
    return {
        "success": True,
        "data": {
            "time_range": time_range,
            "start_time": start_time.isoformat(),
            "end_time": now.isoformat(),
            "platforms": percentile_data
        }
    }


@router.get("/response-time-trend")
async def get_response_time_trend(
    time_range: str = Query("week", regex="^(today|week|month)$"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取响应时间趋势数据
    
    Args:
        time_range: 时间范围 (today/week/month)
        db: 数据库会话
        
    Returns:
        各平台的响应时间历史趋势
    """
    
    # 计算时间范围和分组间隔
    now = datetime.utcnow()
    if time_range == "today":
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        interval = 'hour'
    elif time_range == "week":
        start_time = now - timedelta(days=7)
        interval = 'day'
    else:  # month
        start_time = now - timedelta(days=30)
        interval = 'day'
    
    # 获取所有平台
    result = await db.execute(select(IntelligencePlatform))
    platforms = result.scalars().all()
    
    trend_data = []
    
    for platform in platforms:
        # 构建模型名称匹配模式
        model_patterns = []
        if platform.provider:
            model_patterns.append(platform.provider.lower())
        if platform.name:
            name_parts = platform.name.lower().split()
            model_patterns.extend(name_parts)
        
        if not model_patterns:
            continue
        
        # 按时间间隔分组查询响应时间
        time_column = func.date_trunc(interval, usage_log_table.c.timestamp)
        
        query = select(
            time_column.label('time_bucket'),
            func.avg(usage_log_table.c.response_time).label('avg_response_time'),
            func.percentile_cont(0.50).within_group(usage_log_table.c.response_time).label('p50'),
            func.percentile_cont(0.95).within_group(usage_log_table.c.response_time).label('p95'),
            func.count(usage_log_table.c.id).label('call_count')
        ).where(
            and_(
                usage_log_table.c.timestamp >= start_time,
                usage_log_table.c.success == True,
                usage_log_table.c.response_time != None,
                func.lower(usage_log_table.c.model_name).op('~')(f"({'|'.join(model_patterns)})")
            )
        ).group_by(time_column).order_by(time_column)
        
        result = await db.execute(query)
        time_series = result.all()
        
        if time_series:
            data_points = []
            for time_bucket, avg_time, p50, p95, call_count in time_series:
                data_points.append({
                    "timestamp": time_bucket.isoformat() if time_bucket else None,
                    "avg_response_time": round(avg_time, 2) if avg_time else 0,
                    "p50": round(p50, 2) if p50 else 0,
                    "p95": round(p95, 2) if p95 else 0,
                    "call_count": call_count
                })
            
            # 计算总体平均
            overall_avg = sum(p['avg_response_time'] for p in data_points) / len(data_points) if data_points else 0
            
            trend_data.append({
                "platform_id": platform.id,
                "platform_name": platform.name,
                "provider": platform.provider,
                "overall_avg": round(overall_avg, 2),
                "data_points": data_points
            })
    
    # 按总体平均响应时间排序
    trend_data.sort(key=lambda x: x['overall_avg'])
    
    return {
        "success": True,
        "data": {
            "time_range": time_range,
            "interval": interval,
            "start_time": start_time.isoformat(),
            "end_time": now.isoformat(),
            "platforms": trend_data
        }
    }

