"""
AI决策历史API端点
提供决策列表、详情和10步流程展示
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

router = APIRouter(tags=["AI Decisions"])
logger = logging.getLogger(__name__)


@router.get("")
async def get_decisions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, regex="^(approved|rejected|all)$")
) -> Dict[str, Any]:
    """
    获取AI决策历史列表
    
    Args:
        limit: 返回数量 (1-200)
        offset: 偏移量
        status: 过滤状态 (approved/rejected/all)
        
    Returns:
        Dict: 决策列表和统计
    """
    try:
        # TODO: 从数据库查询实际决策记录
        decisions = _get_mock_decisions(limit, offset, status)
        
        # 统计
        total = len(decisions)
        approved = sum(1 for d in decisions if d["result"] == "approved")
        rejected = total - approved
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "approved": approved,
            "rejected": rejected,
            "decisions": decisions
        }
        
    except Exception as e:
        logger.error(f"❌ 获取决策列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取决策列表失败: {str(e)}"
        )


@router.get("/{decision_id}")
async def get_decision_detail(decision_id: str) -> Dict[str, Any]:
    """
    获取单个决策的详细信息（包含10步流程）
    
    Args:
        decision_id: 决策ID
        
    Returns:
        Dict: 决策详情和10步流程
    """
    try:
        # TODO: 从数据库查询实际决策记录
        decision = _get_mock_decision_detail(decision_id)
        
        if not decision:
            raise HTTPException(
                status_code=404,
                detail=f"决策 {decision_id} 未找到"
            )
        
        logger.info(f"📊 获取决策详情: {decision_id}")
        return decision
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取决策详情失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取决策详情失败: {str(e)}"
        )


@router.get("/stats/summary")
async def get_decision_stats(days: int = Query(7, ge=1, le=90)) -> Dict[str, Any]:
    """
    获取决策统计摘要
    
    Args:
        days: 统计天数 (1-90)
        
    Returns:
        Dict: 统计摘要
    """
    try:
        # TODO: 从数据库查询实际统计
        stats = _get_mock_decision_stats(days)
        
        logger.info(f"📊 获取{days}天决策统计")
        return stats
        
    except Exception as e:
        logger.error(f"❌ 获取决策统计失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取决策统计失败: {str(e)}"
        )


# ===== 辅助函数 - Mock数据 =====

def _get_mock_decisions(limit: int, offset: int, status: Optional[str]) -> List[Dict[str, Any]]:
    """获取模拟决策列表"""
    
    # 基于当前系统生成25次决策（全部被拒绝）
    all_decisions = []
    base_time = datetime.now()
    
    for i in range(25):
        timestamp = base_time - timedelta(minutes=i*5)
        decision_id = f"dec_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        all_decisions.append({
            "decision_id": decision_id,
            "timestamp": timestamp.isoformat(),
            "type": "LONG" if i % 3 == 0 else "HOLD",
            "symbol": "BTC-PERP",
            "result": "rejected_soft",
            "reason": "置信度不足: 0.65 < 0.80",
            "confidence": 0.65,
            "permission_level": "L1",
            "duration_ms": 9600 + i * 100
        })
    
    # 过滤
    if status and status != "all":
        if status == "approved":
            all_decisions = [d for d in all_decisions if d["result"] == "approved"]
        elif status == "rejected":
            all_decisions = [d for d in all_decisions if d["result"].startswith("rejected")]
    
    # 分页
    return all_decisions[offset:offset+limit]


def _get_mock_decision_detail(decision_id: str) -> Optional[Dict[str, Any]]:
    """获取模拟决策详情（包含10步流程）"""
    
    return {
        "decision_id": decision_id,
        "timestamp": datetime.now().isoformat(),
        "result": "rejected_soft",
        "reason": "置信度不足: 0.65 < 0.80",
        
        # 10步决策流程
        "steps": [
            {
                "step": 1,
                "name": "获取市场数据",
                "status": "completed",
                "duration_ms": 500,
                "data": {
                    "symbol": "BTC-PERP",
                    "price": 95000.00,
                    "change_24h": 2.3,
                    "volume_24h": 1250000000
                }
            },
            {
                "step": 2,
                "name": "获取账户状态",
                "status": "completed",
                "duration_ms": 300,
                "data": {
                    "equity": 298.50,
                    "available": 248.50,
                    "margin_ratio": 0.45,
                    "positions": 0
                }
            },
            {
                "step": 3,
                "name": "权限检查",
                "status": "completed",
                "duration_ms": 50,
                "data": {
                    "level": "L1",
                    "max_position_pct": 0.10,
                    "max_leverage": 2,
                    "available_amount": 29.85
                }
            },
            {
                "step": 4,
                "name": "加载记忆系统",
                "status": "completed",
                "duration_ms": 200,
                "data": {
                    "short_term_decisions": 25,
                    "long_term_patterns": 0,
                    "knowledge_lessons": 0
                }
            },
            {
                "step": 5,
                "name": "构建Prompt",
                "status": "completed",
                "duration_ms": 100,
                "data": {
                    "total_tokens": 1500,
                    "includes": ["市场数据", "账户状态", "历史决策", "风控规则"]
                }
            },
            {
                "step": 6,
                "name": "调用AI模型",
                "status": "completed",
                "duration_ms": 3200,
                "data": {
                    "model": "deepseek-chat",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            {
                "step": 7,
                "name": "解析AI响应",
                "status": "completed",
                "duration_ms": 150,
                "data": {
                    "action": "LONG",
                    "symbol": "BTC-PERP",
                    "size": 0.002,
                    "confidence": 0.65,
                    "reasoning": "市场上涨趋势，但信号不够强"
                }
            },
            {
                "step": 8,
                "name": "软约束验证",
                "status": "failed",
                "duration_ms": 50,
                "data": {
                    "constraint": "confidence_threshold",
                    "required": 0.80,
                    "actual": 0.65,
                    "result": "rejected"
                }
            },
            {
                "step": 9,
                "name": "硬约束验证",
                "status": "skipped",
                "duration_ms": 0,
                "data": {
                    "reason": "软约束已拒绝"
                }
            },
            {
                "step": 10,
                "name": "执行交易",
                "status": "skipped",
                "duration_ms": 0,
                "data": {
                    "reason": "决策被拒绝"
                }
            }
        ],
        
        # 决策元数据
        "metadata": {
            "permission_level": "L1",
            "confidence": 0.65,
            "total_duration_ms": 4550,
            "ai_model": "deepseek-chat",
            "api_version": "v2.0"
        },
        
        # AI推理
        "reasoning": {
            "market_analysis": "BTC价格上涨2.3%，24小时成交量正常",
            "risk_assessment": "无持仓，风险可控",
            "decision_rationale": "上涨趋势明显，但量能不足，信号不够强烈",
            "confidence_explanation": "缺乏强烈的入场信号，置信度仅65%"
        }
    }


def _get_mock_decision_stats(days: int) -> Dict[str, Any]:
    """获取模拟决策统计"""
    
    total_decisions = 25
    approved = 0
    rejected = 25
    
    return {
        "period_days": days,
        "total_decisions": total_decisions,
        "approved": approved,
        "rejected": rejected,
        "approval_rate": 0.0,
        
        "rejection_reasons": {
            "confidence_below_threshold": 25,  # 100%
            "hard_constraint_violation": 0,
            "permission_denied": 0,
            "frequency_exceeded": 0
        },
        
        "decision_types": {
            "LONG": 9,
            "SHORT": 0,
            "CLOSE": 0,
            "HOLD": 16
        },
        
        "avg_confidence": 0.65,
        "avg_duration_ms": 4600,
        
        "by_permission_level": {
            "L1": 25,
            "L2": 0,
            "L3": 0,
            "L4": 0,
            "L5": 0
        }
    }

