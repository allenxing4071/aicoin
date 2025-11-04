"""Intelligence Configuration Management API

这个API用于管理Qwen情报系统的配置和监控。

核心功能：
1. 数据源配置（新闻源、链上数据源、巨鲸追踪）
2. 更新频率配置
3. 情报收集状态监控
4. 数据源健康检查
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.core.redis_client import redis_client
from app.services.intelligence.storage import IntelligenceStorage
from app.services.intelligence.qwen_engine import QwenIntelligenceEngine

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== 数据模型 ====================

class DataSourceConfig(BaseModel):
    """数据源配置"""
    type: str  # "news", "whale", "onchain"
    name: str
    url: Optional[str] = None
    api_key: Optional[str] = None
    enabled: bool = True
    update_interval: int = 1800  # seconds
    description: str = ""


class IntelligenceConfig(BaseModel):
    """情报系统配置"""
    enabled: bool = True
    update_interval: int = 1800  # 30 minutes
    qwen_model: str = "qwen-plus"
    data_sources: List[DataSourceConfig] = []
    mock_mode: bool = True  # 是否使用模拟数据


class DataSourceStatus(BaseModel):
    """数据源状态"""
    name: str
    type: str
    status: str  # "active", "error", "disabled"
    last_update: Optional[datetime] = None
    last_error: Optional[str] = None
    total_calls: int = 0
    success_rate: float = 100.0
    data_source_url: Optional[str] = None
    description: str = ""


# ==================== 默认配置 ====================

DEFAULT_CONFIG = IntelligenceConfig(
    enabled=True,
    update_interval=1800,
    qwen_model="qwen-plus",
    mock_mode=True,  # 默认使用模拟数据
    data_sources=[
        DataSourceConfig(
            type="news",
            name="CoinDesk RSS",
            url="https://www.coindesk.com/arc/outboundfeeds/rss/",
            enabled=False,  # 未配置API
            update_interval=1800,
            description="CoinDesk新闻RSS订阅 - 需要配置"
        ),
        DataSourceConfig(
            type="news",
            name="CoinTelegraph RSS",
            url="https://cointelegraph.com/rss",
            enabled=False,
            update_interval=1800,
            description="CoinTelegraph新闻RSS订阅 - 需要配置"
        ),
        DataSourceConfig(
            type="whale",
            name="Whale Alert API",
            url="https://api.whale-alert.io/v1/transactions",
            enabled=False,
            update_interval=600,
            description="巨鲸交易监控 - 需要API Key"
        ),
        DataSourceConfig(
            type="onchain",
            name="Etherscan API",
            url="https://api.etherscan.io/api",
            enabled=False,
            update_interval=1800,
            description="以太坊链上数据 - 需要API Key"
        ),
        DataSourceConfig(
            type="onchain",
            name="Glassnode API",
            url="https://api.glassnode.com/v1/metrics",
            enabled=False,
            update_interval=3600,
            description="Glassnode链上指标 - 需要API Key"
        ),
        DataSourceConfig(
            type="mock",
            name="模拟数据源",
            url="internal://mock",
            enabled=True,  # 默认启用
            update_interval=1800,
            description="模拟的市场数据、新闻和巨鲸活动 - 用于测试"
        )
    ]
)


# ==================== API端点 ====================

@router.get("/config")
async def get_intelligence_config() -> Dict[str, Any]:
    """获取情报系统配置
    
    返回当前的情报系统配置，包括：
    - 是否启用
    - 更新频率
    - Qwen模型
    - 数据源列表及其配置
    - 是否使用模拟数据
    """
    try:
        # 从Redis获取配置（如果存在）
        config_data = await redis_client.get("intelligence:config")
        
        if config_data:
            config = IntelligenceConfig(**config_data)
        else:
            # 使用默认配置
            config = DEFAULT_CONFIG
            # 保存到Redis
            await redis_client.set("intelligence:config", config.dict(), expire=86400 * 30)
        
        return {
            "success": True,
            "data": config.dict()
        }
    
    except Exception as e:
        logger.error(f"获取情报配置失败: {e}")
        return {
            "success": False,
            "message": f"获取配置失败: {str(e)}",
            "data": DEFAULT_CONFIG.dict()
        }


@router.post("/config")
async def update_intelligence_config(config: IntelligenceConfig) -> Dict[str, Any]:
    """更新情报系统配置
    
    允许管理员更新：
    - 启用/禁用情报系统
    - 修改更新频率
    - 配置数据源（API key、URL等）
    - 切换模拟/真实数据
    """
    try:
        # 保存到Redis
        await redis_client.set("intelligence:config", config.dict(), expire=86400 * 30)
        
        logger.info(f"✅ 情报配置已更新: 启用={config.enabled}, 模拟模式={config.mock_mode}")
        
        return {
            "success": True,
            "message": "配置已更新，将在下次情报收集时生效",
            "data": config.dict()
        }
    
    except Exception as e:
        logger.error(f"更新情报配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.get("/status")
async def get_intelligence_status() -> Dict[str, Any]:
    """获取情报系统运行状态
    
    返回：
    - 最后一次收集时间
    - 收集成功/失败次数
    - 各数据源状态
    - 最新情报报告摘要
    """
    try:
        storage = IntelligenceStorage(redis_client)
        
        # 获取最新报告
        latest_report = await storage.get_latest_report()
        
        # 获取统计信息
        stats_data = await redis_client.get("intelligence:stats")
        if not stats_data:
            stats_data = {
                "total_collections": 0,
                "successful_collections": 0,
                "failed_collections": 0,
                "last_collection_time": None,
                "last_success_time": None,
                "last_error": None
            }
        
        # 获取数据源状态
        sources_status = await get_data_sources_status()
        
        return {
            "success": True,
            "data": {
                "is_running": True,  # TODO: 从orchestrator获取真实状态
                "stats": stats_data,
                "data_sources": sources_status,
                "latest_report": {
                    "timestamp": latest_report.timestamp.isoformat() if latest_report else None,
                    "sentiment": latest_report.market_sentiment.value if latest_report else None,
                    "summary": latest_report.qwen_analysis if latest_report else "暂无情报报告"
                } if latest_report else None
            }
        }
    
    except Exception as e:
        logger.error(f"获取情报状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.get("/data-sources/status")
async def get_data_sources_status() -> List[DataSourceStatus]:
    """获取所有数据源的状态
    
    显示每个数据源的：
    - 运行状态（活跃/错误/禁用）
    - 最后更新时间
    - 成功率
    - 数据来源URL
    """
    try:
        # 获取配置
        config_data = await redis_client.get("intelligence:config")
        config = IntelligenceConfig(**config_data) if config_data else DEFAULT_CONFIG
        
        statuses = []
        
        for source in config.data_sources:
            # 获取数据源统计
            source_stats_key = f"intelligence:source:{source.name}:stats"
            source_stats = await redis_client.get(source_stats_key)
            
            if not source_stats:
                source_stats = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "last_update": None,
                    "last_error": None
                }
            
            success_rate = 100.0
            if source_stats["total_calls"] > 0:
                success_rate = (source_stats["successful_calls"] / source_stats["total_calls"]) * 100
            
            status_obj = DataSourceStatus(
                name=source.name,
                type=source.type,
                status="active" if source.enabled else "disabled",
                last_update=datetime.fromisoformat(source_stats["last_update"]) if source_stats.get("last_update") else None,
                last_error=source_stats.get("last_error"),
                total_calls=source_stats["total_calls"],
                success_rate=round(success_rate, 2),
                data_source_url=source.url,
                description=source.description
            )
            
            statuses.append(status_obj)
        
        return statuses
    
    except Exception as e:
        logger.error(f"获取数据源状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据源状态失败: {str(e)}")


@router.post("/data-sources/{source_name}/toggle")
async def toggle_data_source(source_name: str, enabled: bool) -> Dict[str, Any]:
    """启用/禁用指定数据源
    
    Args:
        source_name: 数据源名称
        enabled: True启用，False禁用
    """
    try:
        # 获取配置
        config_data = await redis_client.get("intelligence:config")
        config = IntelligenceConfig(**config_data) if config_data else DEFAULT_CONFIG
        
        # 查找并更新数据源
        found = False
        for source in config.data_sources:
            if source.name == source_name:
                source.enabled = enabled
                found = True
                break
        
        if not found:
            raise HTTPException(status_code=404, detail=f"数据源 '{source_name}' 不存在")
        
        # 保存配置
        await redis_client.set("intelligence:config", config.dict(), expire=86400 * 30)
        
        logger.info(f"✅ 数据源 '{source_name}' 已{'启用' if enabled else '禁用'}")
        
        return {
            "success": True,
            "message": f"数据源 '{source_name}' 已{'启用' if enabled else '禁用'}",
            "data": config.dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换数据源失败: {e}")
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.post("/test-collection")
async def test_intelligence_collection() -> Dict[str, Any]:
    """手动触发一次情报收集（用于测试）
    
    立即执行一次情报收集，返回收集结果和详细信息。
    """
    try:
        logger.info("🧪 手动触发情报收集...")
        
        # TODO: 调用QwenIntelligenceEngine进行收集
        # engine = QwenIntelligenceEngine(redis_client)
        # report = await engine.collect_intelligence()
        
        return {
            "success": True,
            "message": "情报收集功能正在开发中",
            "data": {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "pending"
            }
        }
    
    except Exception as e:
        logger.error(f"测试收集失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


@router.post("/data-sources/{source_name}/test-connection")
async def test_data_source_connection(source_name: str) -> Dict[str, Any]:
    """测试数据源连接
    
    测试指定数据源的API Key是否有效，连接是否正常。
    
    Args:
        source_name: 数据源名称
    
    Returns:
        测试结果，包括连接状态、响应时间、错误信息等
    """
    try:
        logger.info(f"🧪 测试数据源连接: {source_name}")
        
        # 获取配置
        config_data = await redis_client.get("intelligence:config")
        config = IntelligenceConfig(**config_data) if config_data else DEFAULT_CONFIG
        
        # 查找数据源
        source = None
        for s in config.data_sources:
            if s.name == source_name:
                source = s
                break
        
        if not source:
            raise HTTPException(status_code=404, detail=f"数据源 '{source_name}' 不存在")
        
        # 检查是否有API Key
        if not source.api_key and source.type != "news":
            return {
                "success": False,
                "message": "未配置API Key",
                "data": {
                    "status": "no_api_key",
                    "requires_api_key": True
                }
            }
        
        # 根据数据源类型进行测试
        import aiohttp
        import time
        
        start_time = time.time()
        
        if source.type == "news":
            # RSS源测试
            async with aiohttp.ClientSession() as session:
                async with session.get(source.url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        content = await response.text()
                        return {
                            "success": True,
                            "message": "连接成功",
                            "data": {
                                "status": "connected",
                                "response_time_ms": round(response_time * 1000, 2),
                                "status_code": response.status,
                                "content_length": len(content),
                                "source_type": "RSS Feed"
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"连接失败 (HTTP {response.status})",
                            "data": {
                                "status": "error",
                                "status_code": response.status,
                                "response_time_ms": round(response_time * 1000, 2)
                            }
                        }
        
        elif source.type == "whale":
            # Whale Alert API测试
            test_url = f"{source.url}?api_key={source.api_key}&limit=1"
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "message": "API Key有效，连接成功",
                            "data": {
                                "status": "connected",
                                "response_time_ms": round(response_time * 1000, 2),
                                "status_code": response.status,
                                "api_valid": True,
                                "sample_data_count": len(data.get("transactions", []))
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"API Key无效或连接失败 (HTTP {response.status})",
                            "data": {
                                "status": "error",
                                "status_code": response.status,
                                "response_time_ms": round(response_time * 1000, 2),
                                "api_valid": False
                            }
                        }
        
        elif source.type == "onchain":
            # Etherscan/Glassnode API测试
            if "etherscan" in source.name.lower():
                test_url = f"{source.url}?module=stats&action=ethsupply&apikey={source.api_key}"
            else:  # Glassnode
                test_url = source.url  # TODO: 构建Glassnode测试URL
            
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "message": "API Key有效，连接成功",
                            "data": {
                                "status": "connected",
                                "response_time_ms": round(response_time * 1000, 2),
                                "status_code": response.status,
                                "api_valid": True
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"API Key无效或连接失败 (HTTP {response.status})",
                            "data": {
                                "status": "error",
                                "status_code": response.status,
                                "response_time_ms": round(response_time * 1000, 2),
                                "api_valid": False
                            }
                        }
        
        else:
            return {
                "success": False,
                "message": "不支持的数据源类型",
                "data": {
                    "status": "unsupported_type",
                    "source_type": source.type
                }
            }
    
    except aiohttp.ClientTimeout:
        return {
            "success": False,
            "message": "连接超时",
            "data": {
                "status": "timeout",
                "timeout_seconds": 10
            }
        }
    except aiohttp.ClientError as e:
        return {
            "success": False,
            "message": f"网络错误: {str(e)}",
            "data": {
                "status": "network_error",
                "error": str(e)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试连接失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")

