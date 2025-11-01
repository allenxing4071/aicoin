"""FastAPI main application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import redis_client
from app.api.v1 import market, account, performance, ai, admin
from app.api import websocket, market_data
from app.api import trading as hyperliquid_trading
from app.services.hyperliquid_market_data import HyperliquidMarketData
from app.services.hyperliquid_trading import HyperliquidTradingService
from app.services.ai_trading_orchestrator import AITradingOrchestrator
from app.websocket.manager import websocket_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## AIcoin 智能交易系统 API 文档

这是一个基于AI的加密货币自动交易系统,支持多模型决策、智能约束框架和完整的风控体系。

### 核心功能模块

* **市场数据 (Market Data)**: 实时市场数据获取、K线数据、订单簿等
* **账户管理 (Account)**: 账户信息查询、余额管理、持仓查看
* **交易执行 (Trading)**: 订单下单、撤单、交易历史查询
* **AI决策 (AI Status)**: AI决策状态、权限等级、决策日志
* **绩效分析 (Performance)**: 交易绩效统计、收益分析、风险指标
* **管理后台 (Admin)**: 数据库查看、系统统计、日志查询

### 管理后台功能

管理后台提供只读的数据库查看功能,可以查看:
- 交易记录 (Trades)
- 订单记录 (Orders)  
- 账户快照 (Account Snapshots)
- AI决策日志 (AI Decisions)
- K线数据 (Market Data)
- 风控事件 (Risk Events)

所有查询接口都支持分页、筛选、排序等功能。

### 认证说明

当前版本为开发环境,暂未启用认证。生产环境将使用JWT认证。

### 技术栈

- **框架**: FastAPI + SQLAlchemy + PostgreSQL
- **AI模型**: DeepSeek, Qwen, Claude等
- **交易所**: Hyperliquid (支持测试网和主网)
- **实时通信**: WebSocket
- **缓存**: Redis
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Market Data",
            "description": "市场数据查询接口,包括实时价格、K线数据等"
        },
        {
            "name": "Market Data - Real-time",
            "description": "实时市场数据推送服务"
        },
        {
            "name": "Account",
            "description": "账户信息管理,包括余额、持仓等"
        },
        {
            "name": "Hyperliquid Trading",
            "description": "Hyperliquid交易所交易接口,支持下单、撤单等操作"
        },
        {
            "name": "AI Status",
            "description": "AI决策系统状态查询,包括权限等级、决策历史等"
        },
        {
            "name": "Performance",
            "description": "交易绩效分析,包括收益率、夏普比率、最大回撤等指标"
        },
        {
            "name": "Admin - Database Viewer",
            "description": "管理后台数据库查看接口 (只读),支持查看所有核心数据表"
        },
        {
            "name": "WebSocket",
            "description": "WebSocket实时数据推送"
        }
    ]
)

# Global services
market_data_service = None
trading_service = None
ai_orchestrator = None

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    market.router,
    prefix=f"{settings.API_V1_PREFIX}/market",
    tags=["Market Data"]
)
app.include_router(
    account.router,
    prefix=f"{settings.API_V1_PREFIX}/account",
    tags=["Account"]
)
app.include_router(
    performance.router,
    prefix=f"{settings.API_V1_PREFIX}/performance",
    tags=["Performance"]
)
app.include_router(
    ai.router,
    prefix=f"{settings.API_V1_PREFIX}/ai",
    tags=["AI Status"]
)
app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Database Viewer"]
)

# Include new API routers
app.include_router(
    websocket.router,
    tags=["WebSocket"]
)
app.include_router(
    market_data.router,
    prefix=f"{settings.API_V1_PREFIX}/market-data",
    tags=["Market Data - Real-time"]
)
app.include_router(
    hyperliquid_trading.router,
    prefix=f"{settings.API_V1_PREFIX}/trading",
    tags=["Hyperliquid Trading"]
)


@app.on_event("startup")
async def startup_event():
    """Application startup"""
    global market_data_service, trading_service, ai_orchestrator
    logger.info("Starting AIcoin Trading System...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Initialize Redis
    try:
        await redis_client.connect()
        logger.info("Redis connected")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
    
    # Initialize Hyperliquid market data service
    try:
        market_data_service = HyperliquidMarketData(redis_client, testnet=True)
        await market_data_service.start()
        # Set the global service instance
        market_data.set_market_data_service(market_data_service)
        logger.info("Hyperliquid market data service started")
    except Exception as e:
        logger.error(f"Market data service initialization failed: {e}")
    
    # Initialize Hyperliquid trading service
    try:
        # 从配置读取testnet设置
        testnet = settings.HYPERLIQUID_TESTNET if hasattr(settings, 'HYPERLIQUID_TESTNET') else False
        trading_service = HyperliquidTradingService(redis_client, testnet=testnet)
        await trading_service.initialize()
        # Set the global service instance
        hyperliquid_trading.set_trading_service(trading_service)
        logger.info(f"Hyperliquid trading service initialized (testnet={testnet})")
    except Exception as e:
        logger.error(f"Trading service initialization failed: {e}")
    
    # Initialize AI trading orchestrator
    try:
        if market_data_service and trading_service:
            ai_orchestrator = AITradingOrchestrator(
                redis_client, trading_service, market_data_service, testnet=True
            )
            hyperliquid_trading.set_ai_orchestrator(ai_orchestrator)
            logger.info("AI trading orchestrator initialized")
            
            # Start the trading loop
            await ai_orchestrator.start_trading()
            logger.info("AI trading orchestrator started - autonomous trading enabled!")
    except Exception as e:
        logger.error(f"AI orchestrator initialization failed: {e}")
    
    # Start WebSocket manager
    try:
        await websocket_manager.start_broadcast_service()
        logger.info("WebSocket manager started")
    except Exception as e:
        logger.error(f"WebSocket manager initialization failed: {e}")
    
    logger.info(f"Application started successfully on {settings.APP_VERSION}")
    logger.info(f"Trading enabled: {settings.TRADING_ENABLED}")
    logger.info(f"Default symbol: {settings.DEFAULT_SYMBOL}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    global market_data_service, trading_service, ai_orchestrator
    logger.info("Shutting down AIcoin Trading System...")
    
    # Stop AI orchestrator
    if ai_orchestrator:
        try:
            await ai_orchestrator.stop_trading()
            logger.info("AI orchestrator stopped")
        except Exception as e:
            logger.error(f"AI orchestrator shutdown failed: {e}")
    
    # Stop trading service
    if trading_service:
        try:
            await trading_service.stop()
            logger.info("Trading service stopped")
        except Exception as e:
            logger.error(f"Trading service shutdown failed: {e}")
    
    # Stop market data service
    if market_data_service:
        try:
            await market_data_service.stop()
            logger.info("Market data service stopped")
        except Exception as e:
            logger.error(f"Market data service shutdown failed: {e}")
    
    # Stop WebSocket manager
    try:
        await websocket_manager.stop_broadcast_service()
        logger.info("WebSocket manager stopped")
    except Exception as e:
        logger.error(f"WebSocket manager shutdown failed: {e}")
    
    # Close Redis
    try:
        await redis_client.disconnect()
        logger.info("Redis disconnected")
    except Exception as e:
        logger.error(f"Redis disconnect failed: {e}")
    
    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "trading_enabled": settings.TRADING_ENABLED,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

