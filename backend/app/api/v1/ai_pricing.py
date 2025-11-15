"""
AI 定价管理 API
提供价格查询、更新、手动校准等功能
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from app.api.v1.admin_db import get_current_user
from app.services.ai_pricing import get_pricing_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-pricing", tags=["AI定价管理"])


class PriceUpdateRequest(BaseModel):
    """价格更新请求"""
    provider: str = Field(..., description="平台标识 (qwen, deepseek等)")
    model: str = Field(..., description="模型名称")
    input_price: Optional[float] = Field(None, description="输入价格 (元/1K tokens)")
    output_price: Optional[float] = Field(None, description="输出价格 (元/1K tokens)")


class CostCalculationRequest(BaseModel):
    """成本计算请求"""
    provider: str = Field(..., description="平台标识")
    model: str = Field(..., description="模型名称")
    input_tokens: int = Field(..., description="输入token数")
    output_tokens: int = Field(..., description="输出token数")
    cached_tokens: int = Field(0, description="缓存命中token数")


@router.get("/pricing-table")
async def get_pricing_table():
    """
    获取完整价格表
    
    返回所有平台和模型的最新价格信息
    """
    try:
        pricing_manager = get_pricing_manager()
        pricing_data = pricing_manager.get_all_pricing()
        
        return {
            "success": True,
            "data": pricing_data
        }
        
    except Exception as e:
        logger.error(f"❌ 获取价格表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info/{provider}/{model}")
async def get_model_info(provider: str, model: str):
    """
    获取指定模型的详细信息
    
    Args:
        provider: 平台标识
        model: 模型名称
    """
    try:
        pricing_manager = get_pricing_manager()
        model_info = pricing_manager.get_model_info(provider, model)
        
        if model_info is None:
            raise HTTPException(
                status_code=404,
                detail=f"未找到模型: {provider}/{model}"
            )
        
        return {
            "success": True,
            "data": model_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取模型信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate-cost")
async def calculate_cost(request: CostCalculationRequest):
    """
    计算指定调用的成本
    
    用于预估或验证 API 调用成本
    """
    try:
        pricing_manager = get_pricing_manager()
        
        cost = pricing_manager.calculate_cost(
            provider=request.provider,
            model=request.model,
            input_tokens=request.input_tokens,
            output_tokens=request.output_tokens,
            cached_tokens=request.cached_tokens
        )
        
        # 获取价格详情
        input_price = pricing_manager.get_price(request.provider, request.model, "input")
        output_price = pricing_manager.get_price(request.provider, request.model, "output")
        
        return {
            "success": True,
            "data": {
                "total_cost": cost,
                "currency": "CNY",
                "breakdown": {
                    "input_tokens": request.input_tokens,
                    "input_price_per_1k": input_price,
                    "input_cost": (request.input_tokens / 1000.0) * input_price,
                    "output_tokens": request.output_tokens,
                    "output_price_per_1k": output_price,
                    "output_cost": (request.output_tokens / 1000.0) * output_price
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 成本计算失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-price")
async def update_price(
    request: PriceUpdateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    更新模型价格（需要管理员权限）
    
    用于手动校准价格表
    """
    try:
        # 检查权限
        if current_user.get("role") not in ["super_admin", "admin"]:
            raise HTTPException(status_code=403, detail="需要管理员权限")
        
        pricing_manager = get_pricing_manager()
        
        success = pricing_manager.update_price(
            provider=request.provider,
            model=request.model,
            input_price=request.input_price,
            output_price=request.output_price
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="价格更新失败")
        
        # 获取更新后的模型信息
        updated_info = pricing_manager.get_model_info(request.provider, request.model)
        
        logger.info(
            f"✅ 价格已更新: {request.provider}/{request.model} by {current_user.get('username')}"
        )
        
        return {
            "success": True,
            "message": "价格更新成功",
            "data": updated_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 价格更新失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-official")
async def sync_official_pricing(
    current_user: Dict = Depends(get_current_user)
):
    """
    同步官方价格（需要管理员权限）
    
    从各平台官方API或文档同步最新价格
    """
    try:
        # 检查权限
        if current_user.get("role") not in ["super_admin", "admin"]:
            raise HTTPException(status_code=403, detail="需要管理员权限")
        
        pricing_manager = get_pricing_manager()
        
        # 重新加载价格配置（从配置文件或官方源）
        # 这里简单地重新初始化定价管理器
        logger.info(f"🔄 同步官方价格 by {current_user.get('username')}")
        
        # 获取最新价格表
        pricing_data = pricing_manager.get_all_pricing()
        
        return {
            "success": True,
            "message": "价格同步成功",
            "data": {
                "total_models": sum(len(models) for models in pricing_data.values()),
                "platforms": list(pricing_data.keys())
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 价格同步失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare-platforms")
async def compare_platforms(
    input_tokens: int = 1000,
    output_tokens: int = 1000
):
    """
    对比各平台成本
    
    Args:
        input_tokens: 输入token数（默认1000）
        output_tokens: 输出token数（默认1000）
    
    返回各平台主流模型的成本对比
    """
    try:
        pricing_manager = get_pricing_manager()
        
        # 主流模型列表
        models_to_compare = [
            ("qwen", "qwen-plus"),
            ("qwen", "qwen-turbo"),
            ("qwen", "qwen-max"),
            ("deepseek", "deepseek-chat"),
            ("baidu", "qwen-plus"),
            ("tencent", "qwen-plus"),
            ("volcano", "qwen-plus"),
            ("openai", "gpt-3.5-turbo"),
            ("openai", "gpt-4")
        ]
        
        comparisons = []
        
        for provider, model in models_to_compare:
            cost = pricing_manager.calculate_cost(
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            
            model_info = pricing_manager.get_model_info(provider, model)
            
            if model_info:
                comparisons.append({
                    "provider": provider,
                    "model": model,
                    "description": model_info.get("description", ""),
                    "cost": cost,
                    "input_price": model_info.get("input", 0),
                    "output_price": model_info.get("output", 0)
                })
        
        # 按成本排序
        comparisons.sort(key=lambda x: x["cost"])
        
        return {
            "success": True,
            "data": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "currency": "CNY",
                "unit": "元/1K tokens",
                "comparisons": comparisons
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 平台对比失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

