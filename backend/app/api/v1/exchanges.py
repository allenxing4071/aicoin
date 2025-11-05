"""交易所管理API端点"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.services.exchange.exchange_factory import exchange_factory
from app.models.exchange_config import ExchangeConfig

router = APIRouter()


@router.get("")
async def get_all_exchanges(db: AsyncSession = Depends(get_db)):
    """
    获取所有交易所配置
    
    Returns:
        List[Dict]: 交易所配置列表
    """
    try:
        result = await db.execute(select(ExchangeConfig))
        configs = result.scalars().all()
        return {
            "success": True,
            "data": [config.to_dict() for config in configs],
            "count": len(configs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易所配置失败: {str(e)}")


@router.get("/active")
async def get_active_exchange():
    """
    获取当前激活的交易所
    
    Returns:
        Dict: 当前交易所信息
    """
    try:
        info = exchange_factory.get_active_exchange_info()
        
        # 获取适配器详细信息
        adapter = await exchange_factory.get_active_exchange()
        
        return {
            "success": True,
            "data": {
                "name": info['name'],
                "market_type": info['market_type'],
                "is_initialized": info['is_initialized'],
                "supports_spot": adapter.supports_spot(),
                "supports_futures": adapter.supports_futures(),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取当前交易所失败: {str(e)}")


@router.get("/supported")
async def get_supported_exchanges():
    """
    获取支持的交易所列表
    
    Returns:
        List[Dict]: 支持的交易所
    """
    try:
        supported = exchange_factory.list_supported_exchanges()
        return {
            "success": True,
            "data": supported
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取支持的交易所失败: {str(e)}")


@router.post("/switch")
async def switch_exchange(
    exchange_name: str = Query(..., description="交易所名称 (binance|hyperliquid)"),
    market_type: str = Query("spot", description="市场类型 (spot|futures|perpetual)"),
    db: AsyncSession = Depends(get_db)
):
    """
    切换交易所
    
    Args:
        exchange_name: 交易所名称
        market_type: 市场类型
        
    Returns:
        Dict: 切换结果
    """
    try:
        # 验证交易所名称
        if exchange_name not in ['binance', 'hyperliquid']:
            raise HTTPException(status_code=400, detail=f"不支持的交易所: {exchange_name}")
        
        # 验证市场类型
        if market_type not in ['spot', 'futures', 'perpetual']:
            raise HTTPException(status_code=400, detail=f"不支持的市场类型: {market_type}")
        
        # Hyperliquid只支持永续合约
        if exchange_name == 'hyperliquid' and market_type != 'perpetual':
            raise HTTPException(status_code=400, detail="Hyperliquid仅支持永续合约(perpetual)")
        
        # 执行切换
        success = await exchange_factory.switch_exchange(
            exchange_name=exchange_name,
            market_type=market_type,
            db=db
        )
        
        if success:
            return {
                "success": True,
                "message": f"成功切换到 {exchange_name} ({market_type})",
                "data": {
                    "exchange": exchange_name,
                    "market_type": market_type
                }
            }
        else:
            raise HTTPException(status_code=500, detail="切换交易所失败")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换交易所失败: {str(e)}")


@router.post("/reload")
async def reload_exchange():
    """
    重新加载当前交易所适配器
    
    Returns:
        Dict: 重载结果
    """
    try:
        adapter = await exchange_factory.reload_adapter()
        
        return {
            "success": True,
            "message": f"成功重新加载 {adapter.name} 适配器",
            "data": {
                "name": adapter.name,
                "is_initialized": adapter.is_initialized
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新加载适配器失败: {str(e)}")


@router.get("/{exchange_id}")
async def get_exchange_config(
    exchange_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定交易所配置
    
    Args:
        exchange_id: 交易所ID
        
    Returns:
        Dict: 交易所配置
    """
    try:
        result = await db.execute(
            select(ExchangeConfig).filter_by(id=exchange_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(status_code=404, detail="交易所配置不存在")
        
        return {
            "success": True,
            "data": config.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易所配置失败: {str(e)}")


@router.put("/{exchange_id}")
async def update_exchange_config(
    exchange_id: int,
    display_name: Optional[str] = None,
    market_type: Optional[str] = None,
    testnet: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    更新交易所配置
    
    Args:
        exchange_id: 交易所ID
        display_name: 显示名称
        market_type: 市场类型
        testnet: 是否测试网
        
    Returns:
        Dict: 更新结果
    """
    try:
        result = await db.execute(
            select(ExchangeConfig).filter_by(id=exchange_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(status_code=404, detail="交易所配置不存在")
        
        # 更新字段
        if display_name is not None:
            config.display_name = display_name
        if market_type is not None:
            config.market_type = market_type
        if testnet is not None:
            config.testnet = testnet
        
        await db.commit()
        await db.refresh(config)
        
        return {
            "success": True,
            "message": "交易所配置已更新",
            "data": config.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新交易所配置失败: {str(e)}")


@router.delete("/{exchange_id}")
async def delete_exchange_config(
    exchange_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除交易所配置
    
    Args:
        exchange_id: 交易所ID
        
    Returns:
        Dict: 删除结果
    """
    try:
        result = await db.execute(
            select(ExchangeConfig).filter_by(id=exchange_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(status_code=404, detail="交易所配置不存在")
        
        # 不允许删除激活的交易所
        if config.is_active:
            raise HTTPException(status_code=400, detail="不能删除激活中的交易所,请先切换到其他交易所")
        
        await db.delete(config)
        await db.commit()
        
        return {
            "success": True,
            "message": f"交易所配置 {config.name} 已删除"
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除交易所配置失败: {str(e)}")

