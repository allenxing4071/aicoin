"""
AI调用使用日志记录服务
用于记录每次AI调用的详细信息，支持真实数据统计
"""
import time
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update, select
from app.models.ai_model_pricing import AIModelUsageLog
from app.models.intelligence_platform import IntelligencePlatform
import logging

logger = logging.getLogger(__name__)


class AIUsageLogger:
    """AI使用日志记录器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_usage(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        success: bool = True,
        error_message: Optional[str] = None,
        response_time: Optional[float] = None,
        purpose: Optional[str] = None,
        symbol: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        """
        记录AI调用日志
        
        Args:
            model_name: 模型名称
            input_tokens: 输入tokens数量
            output_tokens: 输出tokens数量
            cost: 本次花费（元）
            success: 是否成功
            error_message: 错误信息（如果失败）
            response_time: 响应时间（秒）
            purpose: 调用目的（decision/intelligence/analysis）
            symbol: 交易对（如果适用）
            request_id: 请求ID
        """
        try:
            # 插入日志记录
            stmt = insert(AIModelUsageLog).values(
                model_name=model_name,
                request_id=request_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                response_time=response_time,
                success=success,
                error_message=error_message,
                purpose=purpose,
                symbol=symbol,
                created_at=datetime.utcnow()
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            logger.debug(
                f"记录AI调用日志: {model_name} | "
                f"Tokens: {input_tokens}→{output_tokens} | "
                f"Cost: ¥{cost:.4f} | "
                f"Success: {success}"
            )
            
        except Exception as e:
            logger.error(f"记录AI使用日志失败: {e}", exc_info=True)
            await self.db.rollback()
    
    async def update_platform_stats(
        self,
        platform_id: int,
        success: bool,
        cost: float,
        response_time: Optional[float] = None
    ) -> None:
        """
        更新平台统计信息
        
        Args:
            platform_id: 平台ID
            success: 是否成功
            cost: 本次花费
            response_time: 响应时间（秒）
        """
        try:
            # 获取当前平台数据
            result = await self.db.execute(
                select(IntelligencePlatform).where(IntelligencePlatform.id == platform_id)
            )
            platform = result.scalar_one_or_none()
            
            if not platform:
                logger.warning(f"平台ID {platform_id} 不存在")
                return
            
            # 更新统计
            platform.total_calls += 1
            if success:
                platform.successful_calls += 1
            else:
                platform.failed_calls += 1
            
            platform.total_cost += cost
            
            # 更新平均响应时间
            if response_time is not None:
                if platform.avg_response_time is None:
                    platform.avg_response_time = response_time
                else:
                    # 加权平均
                    total_calls = platform.total_calls
                    platform.avg_response_time = (
                        (platform.avg_response_time * (total_calls - 1) + response_time)
                        / total_calls
                    )
            
            platform.updated_at = datetime.utcnow()
            platform.last_health_check = datetime.utcnow()
            platform.health_status = 'healthy' if platform.successful_calls / platform.total_calls > 0.9 else 'degraded'
            
            await self.db.commit()
            
            logger.debug(
                f"更新平台统计: {platform.name} | "
                f"Total: {platform.total_calls} | "
                f"Success Rate: {platform.successful_calls / platform.total_calls * 100:.1f}%"
            )
            
        except Exception as e:
            logger.error(f"更新平台统计失败: {e}", exc_info=True)
            await self.db.rollback()


@asynccontextmanager
async def track_ai_usage(
    db: AsyncSession,
    model_name: str,
    platform_id: Optional[int] = None,
    purpose: Optional[str] = None,
    symbol: Optional[str] = None,
    request_id: Optional[str] = None,
):
    """
    上下文管理器，用于跟踪AI调用
    
    使用示例:
    ```python
    async with track_ai_usage(
        db=db,
        model_name="deepseek-chat",
        platform_id=1,
        purpose="decision",
        symbol="BTCUSDT"
    ) as tracker:
        # 调用AI
        response = await ai_service.call_model(...)
        
        # 记录结果
        tracker.set_result(
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost=response.cost
        )
    ```
    """
    logger_instance = AIUsageLogger(db)
    start_time = time.time()
    
    # 初始化跟踪器
    tracker = {
        'input_tokens': 0,
        'output_tokens': 0,
        'cost': 0.0,
        'success': True,
        'error_message': None,
    }
    
    def set_result(input_tokens: int, output_tokens: int, cost: float):
        """设置调用结果"""
        tracker['input_tokens'] = input_tokens
        tracker['output_tokens'] = output_tokens
        tracker['cost'] = cost
    
    def set_error(error_message: str):
        """设置错误信息"""
        tracker['success'] = False
        tracker['error_message'] = error_message
    
    # 添加方法到tracker
    tracker['set_result'] = set_result
    tracker['set_error'] = set_error
    
    try:
        yield tracker
        
    except Exception as e:
        # 捕获异常，标记为失败
        tracker['success'] = False
        tracker['error_message'] = str(e)
        raise
        
    finally:
        # 计算响应时间
        response_time = time.time() - start_time
        
        # 记录日志
        await logger_instance.log_usage(
            model_name=model_name,
            input_tokens=tracker['input_tokens'],
            output_tokens=tracker['output_tokens'],
            cost=tracker['cost'],
            success=tracker['success'],
            error_message=tracker['error_message'],
            response_time=response_time,
            purpose=purpose,
            symbol=symbol,
            request_id=request_id,
        )
        
        # 更新平台统计
        if platform_id:
            await logger_instance.update_platform_stats(
                platform_id=platform_id,
                success=tracker['success'],
                cost=tracker['cost'],
                response_time=response_time
            )


async def log_ai_call(
    db: AsyncSession,
    model_name: str,
    input_tokens: int,
    output_tokens: int,
    cost: float,
    platform_id: Optional[int] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    response_time: Optional[float] = None,
    purpose: Optional[str] = None,
    symbol: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """
    直接记录AI调用（不使用上下文管理器）
    
    Args:
        db: 数据库会话
        model_name: 模型名称
        input_tokens: 输入tokens
        output_tokens: 输出tokens
        cost: 成本
        platform_id: 平台ID
        success: 是否成功
        error_message: 错误信息
        response_time: 响应时间（秒）
        purpose: 调用目的
        symbol: 交易对
        request_id: 请求ID
    """
    logger_instance = AIUsageLogger(db)
    
    # 记录日志
    await logger_instance.log_usage(
        model_name=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        success=success,
        error_message=error_message,
        response_time=response_time,
        purpose=purpose,
        symbol=symbol,
        request_id=request_id,
    )
    
    # 更新平台统计
    if platform_id:
        await logger_instance.update_platform_stats(
            platform_id=platform_id,
            success=success,
            cost=cost,
            response_time=response_time
        )

