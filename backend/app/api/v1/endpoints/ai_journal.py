"""AI Journal API - Qwen & DeepSeek Daily Journals"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date, timedelta
from typing import Optional
import logging

from app.core.database import get_db
from app.models.intelligence import IntelligenceReport
from app.models.ai_decision import AIDecision
from app.models.trade import Trade

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/daily-journal")
async def get_daily_journal(
    target_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取AI双引擎的每日日记
    
    Args:
        target_date: 目标日期 (YYYY-MM-DD)，默认今天
    
    Returns:
        {
            "date": "2025-11-06",
            "qwen_journal": "Qwen的日记内容...",
            "deepseek_journal": "DeepSeek的日记内容...",
            "data_summary": {统计数据}
        }
    """
    try:
        # 解析日期
        if target_date:
            query_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        else:
            query_date = date.today()
        
        logger.info(f"获取 {query_date} 的AI日记")
        
        # 1. 获取Qwen当天的情报报告
        qwen_result = await db.execute(
            select(IntelligenceReport).where(
                func.date(IntelligenceReport.timestamp) == query_date
            ).order_by(IntelligenceReport.timestamp)
        )
        qwen_reports = qwen_result.scalars().all()
        
        # 2. 获取DeepSeek当天的决策
        decisions_result = await db.execute(
            select(AIDecision).where(
                func.date(AIDecision.timestamp) == query_date
            ).order_by(AIDecision.timestamp)
        )
        decisions = decisions_result.scalars().all()
        
        # 3. 获取当天的交易记录
        trades_result = await db.execute(
            select(Trade).where(
                func.date(Trade.timestamp) == query_date
            ).order_by(Trade.timestamp)
        )
        trades = trades_result.scalars().all()
        
        # 4. 生成Qwen的日记
        qwen_journal = generate_qwen_journal(qwen_reports, query_date)
        
        # 5. 生成DeepSeek的日记
        deepseek_journal = generate_deepseek_journal(
            decisions, 
            trades,
            qwen_reports,
            query_date
        )
        
        # 6. 数据汇总（可折叠查看）
        data_summary = {
            "qwen_reports_count": len(qwen_reports),
            "news_count": sum(len(r.key_news or []) for r in qwen_reports),
            "whale_signals_count": sum(len(r.whale_signals or []) for r in qwen_reports),
            "decisions_count": len(decisions),
            "trades_count": len(trades),
            "total_pnl": float(sum(t.pnl or 0 for t in trades)),
            "executed_decisions": len([d for d in decisions if d.executed]),
            "rejected_decisions": len([d for d in decisions if not d.executed and d.reject_reason]),
        }
        
        return {
            "success": True,
            "date": query_date.isoformat(),
            "qwen_journal": qwen_journal,
            "deepseek_journal": deepseek_journal,
            "data_summary": data_summary,
        }
        
    except Exception as e:
        logger.error(f"获取AI日记失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def generate_qwen_journal(reports: list, query_date: date) -> str:
    """
    生成Qwen情报官的日记
    """
    if not reports:
        return f"""📅 {query_date.strftime('%Y年%m月%d日')}

今天我休息了，没有收集情报。

可能是因为：
• 市场比较平静，没有重要新闻
• 系统正在维护
• 或者我需要充电了 🔋

明天我会继续努力工作！"""
    
    # 统计数据
    total_news = sum(len(r.key_news or []) for r in reports)
    total_whales = sum(len(r.whale_signals or []) for r in reports)
    latest_sentiment = reports[-1].market_sentiment if reports else "NEUTRAL"
    sentiment_score = reports[-1].sentiment_score if reports else 0
    
    # 情绪描述
    sentiment_emoji = {
        "BULLISH": "😊 乐观",
        "BEARISH": "😟 悲观", 
        "NEUTRAL": "😐 中性"
    }.get(latest_sentiment, "😐 中性")
    
    # 构建日记
    journal = f"""📅 {query_date.strftime('%Y年%m月%d日')}

💼 今日工作总结

今天我在互联网上忙碌了一整天，为DeepSeek收集了很多有价值的情报。

🔍 情报收集情况：
• 生成情报报告：{len(reports)} 份
• 收集新闻数量：{total_news} 条
• 监控巨鲸活动：{total_whales} 次
• 最终市场情绪：{sentiment_emoji} (分数: {sentiment_score:.2f})

"""
    
    # 添加具体内容
    if total_news > 0:
        journal += f"""📰 重点新闻：
我发现了一些重要的市场新闻，主要集中在加密货币的价格波动和监管动态上。"""
        
        # 如果有新闻，展示第一条
        if reports[0].key_news and len(reports[0].key_news) > 0:
            first_news = reports[0].key_news[0]
            journal += f"""其中最引人注目的是："{first_news.get('title', '市场动态')}"。"""
        
        journal += "\n\n"
    
    if total_whales > 0:
        journal += f"""🐋 巨鲸监控：
我追踪到了 {total_whales} 次大资金的异动。这些巨鲸的行为往往能反映市场的真实动向，我已经把这些信息及时告知DeepSeek。

"""
    
    # 给DeepSeek的建议
    if latest_sentiment == "BULLISH":
        journal += """💡 我的建议：
根据情报分析，市场情绪偏向乐观，可能有不错的做多机会。但DeepSeek还需要结合技术面自己判断。"""
    elif latest_sentiment == "BEARISH":
        journal += """💡 我的建议：
市场情绪比较悲观，建议DeepSeek保持谨慎，或者考虑观望。风险控制永远是第一位的。"""
    else:
        journal += """💡 我的建议：
市场情绪比较中性，没有明确的方向。建议DeepSeek等待更清晰的信号。"""
    
    journal += f"""

📊 今日成果卡：
┌─────────────────────────┐
│ 情报报告：{len(reports):>2} 份          │
│ 收集新闻：{total_news:>2} 条          │
│ 巨鲸活动：{total_whales:>2} 次          │
│ 市场情绪：{sentiment_emoji:>8}   │
│ 置信度：  {reports[-1].confidence*100:>5.1f}%        │
└─────────────────────────┘

🎯 明日计划：
继续监控市场动态，特别关注重大新闻和巨鲸活动。如果市场出现异常波动，我会第一时间通知DeepSeek！"""
    
    return journal


def generate_deepseek_journal(
    decisions: list,
    trades: list, 
    qwen_reports: list,
    query_date: date
) -> str:
    """
    生成DeepSeek交易官的日记
    """
    if not decisions and not trades:
        return f"""📅 {query_date.strftime('%Y年%m月%d日')}

💭 今日心情：观望 😌

今天市场没有给我明确的信号，我选择休息，保存实力。

{"Qwen今天给我发了" + str(len(qwen_reports)) + "份情报，" if qwen_reports else ""}但我分析后觉得没有高确定性的机会，所以决定不交易。

有时候，不做决策也是一种智慧。耐心等待更好的机会。

📊 今日状态：
• 决策次数：0 次
• 执行交易：0 笔
• 盈亏：$0.00
• 状态：充电中 🔋"""
    
    # 计算统计数据
    total_pnl = float(sum(t.pnl or 0 for t in trades))
    win_trades = [t for t in trades if (t.pnl or 0) > 0]
    lose_trades = [t for t in trades if (t.pnl or 0) < 0]
    win_rate = len(win_trades) / len(trades) * 100 if trades else 0
    
    executed_count = len([d for d in decisions if d.executed])
    rejected_count = len([d for d in decisions if not d.executed and d.reject_reason])
    
    # 心情判断
    if total_pnl > 50:
        mood = "非常开心 😄"
    elif total_pnl > 0:
        mood = "满意 😊"
    elif total_pnl == 0:
        mood = "平静 😐"
    elif total_pnl > -20:
        mood = "有点沮丧 😔"
    else:
        mood = "需要反思 😞"
    
    # 构建日记
    journal = f"""📅 {query_date.strftime('%Y年%m月%d日')}

💭 今日心情：{mood}

"""
    
    # 如果有Qwen的情报
    if qwen_reports:
        latest_report = qwen_reports[-1]
        journal += f"""📬 今天早上，Qwen给我发来了情报，说市场情绪偏向{latest_report.market_sentiment}。"""
        if latest_report.key_news:
            journal += f"""还提到了一些重要新闻。"""
        journal += "\n\n"
    
    # 决策过程
    if decisions:
        journal += f"""🤔 决策过程：
我今天做了 {len(decisions)} 次决策分析。"""
        
        if executed_count > 0:
            journal += f"""其中 {executed_count} 次通过了权限检查，最终执行了交易。"""
        
        if rejected_count > 0:
            journal += f"""有 {rejected_count} 次因为各种原因（置信度不够、风控限制等）被拒绝了。"""
        
        journal += "\n\n"
        
        # 展示第一笔交易的推理
        if trades and trades[0].ai_reasoning:
            journal += f"""💡 第一笔交易的思考：
"{trades[0].ai_reasoning[:150]}..."

"""
    
    # 交易结果
    if trades:
        journal += f"""📈 交易结果：
• 执行交易：{len(trades)} 笔
• 盈利交易：{len(win_trades)} 笔
• 亏损交易：{len(lose_trades)} 笔
• 总盈亏：${total_pnl:.2f}
• 胜率：{win_rate:.1f}%

"""
    
    # 反思与总结
    if total_pnl > 0:
        journal += f"""💡 今日反思：
今天总体表现不错，盈利了 ${total_pnl:.2f}。但我不能骄傲，要继续保持冷静和纪律性。"""
        
        if qwen_reports:
            journal += f"""Qwen的情报帮助了我，让我能更好地把握市场情绪。"""
    elif total_pnl < 0:
        journal += f"""💡 今日反思：
今天亏损了 ${abs(total_pnl):.2f}，我需要认真反思。是判断错误，还是执行出了问题？每次失败都是学习的机会。"""
    else:
        journal += f"""💡 今日反思：
今天虽然没有盈利，但也没有亏损。保住本金就是胜利。"""
    
    # 成绩卡
    journal += f"""

📊 今日成绩卡：
┌─────────────────────────┐
│ AI决策：  {len(decisions):>2} 次          │
│ 执行交易：{len(trades):>2} 笔          │
│ 胜率：    {win_rate:>5.1f}%         │
│ 盈亏：    ${total_pnl:>7.2f}       │
└─────────────────────────┘

🎯 明日计划：
"""
    
    if total_pnl > 0:
        journal += "继续保持今天的状态，但要注意不要过度自信。风险控制永远是第一位的。"
    elif total_pnl < 0:
        journal += "暂时降低交易频率，等待更高确定性的机会。只做有把握的交易。"
    else:
        journal += "继续观察市场，寻找高质量的交易机会。"
    
    return journal

