"""扩展的市场数据API - 支持多周期K线和现货合约对比"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from app.services.exchange.exchange_factory import exchange_factory
from app.services.market.kline_aggregator import KlineAggregator

router = APIRouter()


@router.get("/klines/multi/{symbol}")
async def get_multi_timeframe_klines(
    symbol: str,
    market_type: str = Query("spot", description="市场类型 (spot|futures|perpetual)"),
    intervals: Optional[str] = Query(None, description="时间周期,逗号分隔 (如: 1m,5m,1h)")
):
    """
    获取多周期K线数据
    
    Args:
        symbol: 交易对符号 (如 BTC, ETH)
        market_type: 市场类型
        intervals: 时间周期列表,逗号分隔
        
    Returns:
        Dict: 多周期K线数据
            {
                "1m": [kline_data...],
                "5m": [kline_data...],
                ...
            }
    """
    try:
        # 获取当前交易所
        exchange = await exchange_factory.get_active_exchange()
        aggregator = KlineAggregator(exchange)
        
        # 解析时间周期
        interval_list = None
        if intervals:
            interval_list = [i.strip() for i in intervals.split(',')]
        
        # 获取多周期K线
        multi_klines = await aggregator.get_multi_timeframe_klines(
            symbol=symbol,
            market_type=market_type,
            intervals=interval_list
        )
        
        # 计算每个周期的摘要
        summaries = {}
        for interval, klines in multi_klines.items():
            if klines:
                summaries[interval] = aggregator.get_kline_summary(klines)
        
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "market_type": market_type,
                "exchange": exchange.name,
                "klines": multi_klines,
                "summaries": summaries
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取多周期K线失败: {str(e)}")


@router.get("/spot-futures-compare/{symbol}")
async def get_spot_futures_comparison(symbol: str):
    """
    现货vs合约价格对比分析
    
    Args:
        symbol: 交易对符号
        
    Returns:
        Dict: 对比分析结果
    """
    try:
        # 获取当前交易所
        exchange = await exchange_factory.get_active_exchange()
        
        # 检查是否支持现货和合约
        if not exchange.supports_both_markets():
            raise HTTPException(
                status_code=400,
                detail=f"{exchange.name} 不支持现货和合约同时查询"
            )
        
        aggregator = KlineAggregator(exchange)
        
        # 获取对比数据
        comparison = await aggregator.get_spot_futures_comparison(symbol)
        
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "exchange": exchange.name,
                "comparison": comparison
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"现货合约对比失败: {str(e)}")


@router.get("/market-analysis/{symbol}")
async def get_comprehensive_market_analysis(
    symbol: str,
    market_type: str = Query("spot", description="市场类型")
):
    """
    获取综合市场分析
    
    包括:
    1. 多周期K线
    2. 技术指标 (MA, RSI等)
    3. 现货合约对比 (如果支持)
    
    Args:
        symbol: 交易对符号
        market_type: 市场类型
        
    Returns:
        Dict: 综合市场分析结果
    """
    try:
        # 获取当前交易所
        exchange = await exchange_factory.get_active_exchange()
        aggregator = KlineAggregator(exchange)
        
        # 获取综合分析
        analysis = await aggregator.get_comprehensive_market_analysis(
            symbol=symbol,
            market_type=market_type
        )
        
        return {
            "success": True,
            "data": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"综合市场分析失败: {str(e)}")


@router.get("/technical-indicators/{symbol}")
async def get_technical_indicators(
    symbol: str,
    interval: str = Query("1h", description="K线周期"),
    market_type: str = Query("spot", description="市场类型")
):
    """
    获取技术指标
    
    Args:
        symbol: 交易对符号
        interval: K线周期
        market_type: 市场类型
        
    Returns:
        Dict: 技术指标数据
    """
    try:
        # 获取当前交易所
        exchange = await exchange_factory.get_active_exchange()
        
        # 获取K线数据
        klines = await exchange.get_klines(
            symbol=symbol,
            interval=interval,
            limit=100,
            market_type=market_type
        )
        
        if not klines:
            raise HTTPException(status_code=404, detail="无法获取K线数据")
        
        # 计算技术指标
        aggregator = KlineAggregator(exchange)
        indicators = aggregator.calculate_technical_indicators(klines)
        
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "interval": interval,
                "market_type": market_type,
                "indicators": indicators
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取技术指标失败: {str(e)}")


@router.get("/kline-summary/{symbol}")
async def get_kline_summary(
    symbol: str,
    interval: str = Query("1h", description="K线周期"),
    market_type: str = Query("spot", description="市场类型"),
    limit: int = Query(100, description="K线数量")
):
    """
    获取K线摘要信息
    
    Args:
        symbol: 交易对符号
        interval: K线周期
        market_type: 市场类型
        limit: K线数量
        
    Returns:
        Dict: K线摘要
    """
    try:
        # 获取当前交易所
        exchange = await exchange_factory.get_active_exchange()
        
        # 获取K线数据
        klines = await exchange.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            market_type=market_type
        )
        
        if not klines:
            raise HTTPException(status_code=404, detail="无法获取K线数据")
        
        # 计算摘要
        aggregator = KlineAggregator(exchange)
        summary = aggregator.get_kline_summary(klines)
        
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "interval": interval,
                "market_type": market_type,
                "summary": summary
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取K线摘要失败: {str(e)}")

