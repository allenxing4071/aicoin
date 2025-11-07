"""FastAPI main application"""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import redis_client
from app.api.v1 import market, account, performance, ai, admin_db, constraints, intelligence
from app.api.v1 import exchanges, market_extended  # v3.1 新增
from app.api.v1.endpoints import intelligence_storage, intelligence_platforms, model_performance, ai_journal
from app.api.v1.admin import permissions as admin_permissions
from app.api.v1.admin import database as admin_database
from app.api.v1.admin import memory as admin_memory
from app.api.v1.admin import intelligence_config as admin_intelligence
from app.api.v1.admin import auth as admin_auth
from app.api.v1.admin import users as admin_users
from app.api import websocket, market_data
from app.api import trading as hyperliquid_trading
from app.services.hyperliquid_market_data import HyperliquidMarketData
from app.services.hyperliquid_trading import HyperliquidTradingService
from app.services.orchestrator_v2 import AITradingOrchestratorV2
from app.websocket.manager import websocket_manager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
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

# Simple status endpoint for frontend
@app.get(f"{settings.API_V1_PREFIX}/status")
async def get_system_status():
    """获取系统状态"""
    # AI orchestrator在startup中启动，这里直接返回运行状态
    return {
        "success": True,
        "orchestrator_running": True,  # AI在startup中已启动
        "api_version": "1.0.0",
        "trading_enabled": settings.TRADING_ENABLED,
        "models": {
            "deepseek-chat-v3.1": {
                "status": "running",
                "last_decision_time": None
            }
        }
    }

# Add CORS middleware
# 允许所有localhost端口（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_origin_regex=r"http://localhost:\d+"  # 允许所有localhost端口
)

# Include API routers
# Dashboard API - 性能优化: 合并多个API调用
from app.api.v1 import dashboard
app.include_router(
    dashboard.router,
    prefix=f"{settings.API_V1_PREFIX}/dashboard",
    tags=["Dashboard - Performance Optimized"]
)

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
    admin_db.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Database Viewer"]
)
app.include_router(
    constraints.router,
    prefix=f"{settings.API_V1_PREFIX}/constraints",
    tags=["Constraints"]
)
app.include_router(
    admin_permissions.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Admin - Permissions"]
)
app.include_router(
    admin_database.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Database Management"]
)
app.include_router(
    admin_memory.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/memory",
    tags=["Admin - Memory System"]
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
app.include_router(
    intelligence.router,
    prefix=f"{settings.API_V1_PREFIX}/intelligence",
    tags=["Intelligence - Qwen"]
)
app.include_router(
    intelligence_storage.router,
    prefix=f"{settings.API_V1_PREFIX}/intelligence/storage",
    tags=["Intelligence - Storage"]
)
app.include_router(
    intelligence_platforms.router,
    prefix=f"{settings.API_V1_PREFIX}/intelligence",
    tags=["Intelligence - Platforms"]
)
app.include_router(
    model_performance.router,
    prefix=f"{settings.API_V1_PREFIX}/decision",
    tags=["Decision - Performance"]
)
app.include_router(
    admin_intelligence.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/intelligence",
    tags=["Admin - Intelligence Config"]
)
app.include_router(
    admin_auth.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Auth"]
)
app.include_router(
    admin_users.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/users",
    tags=["Admin - Users"]
)

# v3.1: 交易所管理与多时间框架K线
app.include_router(
    exchanges.router,
    prefix=f"{settings.API_V1_PREFIX}/exchanges",
    tags=["Exchanges - Multi-Exchange Support"]
)
app.include_router(
    market_extended.router,
    prefix=f"{settings.API_V1_PREFIX}/market",
    tags=["Market Data - Extended"]
)

# AI日记系统 - 双引擎协作可视化
app.include_router(
    ai_journal.router,
    prefix=f"{settings.API_V1_PREFIX}/ai-journal",
    tags=["AI Journal - Qwen & DeepSeek Diary"]
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
    
    # Initialize AI trading orchestrator V2
    try:
        from app.core.database import AsyncSessionLocal
        db_session = AsyncSessionLocal()
        
        ai_orchestrator = AITradingOrchestratorV2(
            redis_client=redis_client,
            trading_service=trading_service,
            market_data_service=market_data_service,
            db_session=db_session,
            decision_interval=settings.DECISION_INTERVAL
        )
        hyperliquid_trading.set_ai_orchestrator(ai_orchestrator)
        logger.info("✅ AI trading orchestrator V2 initialized (global variable set)")
        
        # Start the trading loop in background
        import asyncio
        asyncio.create_task(ai_orchestrator.start())
        logger.info("🚀 AI trading orchestrator V2 started - autonomous trading enabled!")
        logger.info(f"📊 配置: 置信度阈值={settings.MIN_CONFIDENCE}, 每日交易限制={settings.MAX_DAILY_TRADES}, 决策间隔={settings.DECISION_INTERVAL}秒")
    except Exception as e:
        logger.error(f"❌ AI orchestrator V2 initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
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
    """Health check endpoint with orchestrator status"""
    global ai_orchestrator
    
    orchestrator_data = None
    try:
        # 使用全局变量ai_orchestrator
        orch = ai_orchestrator
        logger.info(f"[HEALTH] ai_orchestrator = {orch}")
        
        if orch:
            # 获取orchestrator的运行时统计
            runtime_seconds = (datetime.now() - orch.start_time).total_seconds() if hasattr(orch, 'start_time') and orch.start_time else 0
            runtime_hours = runtime_seconds / 3600
            
            total_decisions = getattr(orch, 'total_decisions', 0)
            approved_decisions = getattr(orch, 'approved_decisions', 0)
            approval_rate = (approved_decisions / total_decisions * 100) if total_decisions > 0 else 0.0
            
            orchestrator_data = {
                "is_running": orch.is_running if hasattr(orch, 'is_running') else True,
                "permission_level": settings.INITIAL_PERMISSION_LEVEL,
                "runtime_hours": runtime_hours,
                "total_decisions": total_decisions,
                "approved_decisions": approved_decisions,
                "approval_rate": approval_rate,
                "decision_interval": settings.DECISION_INTERVAL
            }
            logger.info(f"[HEALTH] orchestrator_data = {orchestrator_data}")
        else:
            logger.warning("[HEALTH] ai_orchestrator is None")
    except Exception as e:
        logger.error(f"[HEALTH] Error getting orchestrator status: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "orchestrator_status": orchestrator_data
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

