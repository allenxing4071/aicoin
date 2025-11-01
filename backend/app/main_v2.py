"""FastAPI main application - v2.0"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import init_db, get_db
from app.core.redis_client import redis_client
from app.api.v1 import market, account, performance, ai, trades, positions, admin
from app.api.v1 import constraints, decisions, permission
from app.api import websocket, market_data
# from app.api import trading as hyperliquid_trading  # 暂时禁用，待修复
from app.services.hyperliquid_market_data import HyperliquidMarketData
from app.services.hyperliquid_trading import HyperliquidTradingService
from app.services.orchestrator_v2 import AITradingOrchestratorV2
from app.websocket.manager import websocket_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global service instances
trading_service_global = None
hyperliquid_client_global = None

# Create FastAPI app
app = FastAPI(
    title=f"{settings.APP_NAME} v2.0",
    version="2.0.0",
    description="AI-powered cryptocurrency trading system with advanced risk management",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global services
market_data_service = None
trading_service = None
ai_orchestrator_v2 = None
db_session = None

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
    constraints.router,
    prefix=f"{settings.API_V1_PREFIX}/constraints",
    tags=["Constraints"]
)
app.include_router(
    decisions.router,
    prefix=f"{settings.API_V1_PREFIX}/ai/decisions",
    tags=["AI Decisions"]
)
app.include_router(
    permission.router,
    prefix=f"{settings.API_V1_PREFIX}/ai/permission",
    tags=["AI Permission"]
)
app.include_router(
    trades.router,
    prefix=f"{settings.API_V1_PREFIX}/trading/trades",
    tags=["Trades"]
)
app.include_router(
    positions.router,
    prefix=f"{settings.API_V1_PREFIX}/trading/positions",
    tags=["Positions"]
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
# app.include_router(
#     hyperliquid_trading.router,
#     prefix=f"{settings.API_V1_PREFIX}/trading",
#     tags=["Hyperliquid Trading"]
# )


@app.on_event("startup")
async def startup_event():
    """Application startup - v2.0"""
    global market_data_service, trading_service, ai_orchestrator_v2, db_session, trading_service_global, hyperliquid_client_global
    
    logger.info("="*60)
    logger.info("🚀 Starting AIcoin Trading System v2.0")
    logger.info("="*60)
    
    # Initialize database
    try:
        await init_db()
        # Get database session (注意：这里简化处理，实际应该用dependency injection)
        db_session = next(get_db())
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        db_session = None
    
    # Initialize Redis
    try:
        await redis_client.connect()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
    
    # Initialize Hyperliquid market data service
    try:
        testnet = getattr(settings, 'HYPERLIQUID_TESTNET', True)  # 默认使用测试网
        market_data_service = HyperliquidMarketData(redis_client, testnet=testnet)
        await market_data_service.start()
        market_data.set_market_data_service(market_data_service)
        logger.info(f"✅ Hyperliquid market data service started (testnet={testnet})")
    except Exception as e:
        logger.error(f"❌ Market data service initialization failed: {e}")
    
    # Initialize Hyperliquid trading service
    try:
        testnet = getattr(settings, 'HYPERLIQUID_TESTNET', True)
        trading_service = HyperliquidTradingService(redis_client, testnet=testnet)
        await trading_service.initialize()
        trading_service_global = trading_service  # Set global instance
        
        # Create hyperliquid_client with trading_service to avoid re-initialization
        from app.services.market.hyperliquid_client import HyperliquidClient
        hyperliquid_client_global = HyperliquidClient(trading_service=trading_service, use_mainnet_for_market_data=True)
        
        logger.info(f"✅ Hyperliquid trading service initialized (testnet={testnet})")
        logger.info("✅ Hyperliquid client created with cached trading service")
    except Exception as e:
        logger.error(f"❌ Trading service initialization failed: {e}")
    
    # Initialize AI trading orchestrator v2
    try:
        if market_data_service and trading_service and settings.TRADING_ENABLED:
            logger.info("🤖 Initializing AITradingOrchestratorV2...")
            
            ai_orchestrator_v2 = AITradingOrchestratorV2(
                redis_client=redis_client,
                trading_service=trading_service,
                market_data_service=market_data_service,
                db_session=db_session,
                decision_interval=settings.DECISION_INTERVAL
            )
            
            # 设置全局实例
            # hyperliquid_trading.set_ai_orchestrator(ai_orchestrator_v2)
            
            # 启动交易系统
            await ai_orchestrator_v2.start()
            
            logger.info("✅ AITradingOrchestratorV2 started")
            logger.info(f"   - Permission Level: {ai_orchestrator_v2.decision_engine.current_permission_level}")
            logger.info(f"   - Decision Interval: {settings.DECISION_INTERVAL}s")
            logger.info(f"   - Trading Enabled: {settings.TRADING_ENABLED}")
        else:
            logger.warning("⚠️  AI Orchestrator not started:")
            if not market_data_service:
                logger.warning("   - Market data service not available")
            if not trading_service:
                logger.warning("   - Trading service not available")
            if not settings.TRADING_ENABLED:
                logger.warning("   - Trading is disabled (TRADING_ENABLED=false)")
    except Exception as e:
        logger.error(f"❌ AI orchestrator initialization failed: {e}", exc_info=True)
    
    # Start WebSocket manager
    try:
        await websocket_manager.start_broadcast_service()
        logger.info("✅ WebSocket manager started")
    except Exception as e:
        logger.error(f"❌ WebSocket manager initialization failed: {e}")
    
    logger.info("="*60)
    logger.info("🎉 AIcoin v2.0 Started Successfully")
    logger.info("="*60)
    logger.info(f"📊 API Docs: http://localhost:8000/docs")
    logger.info(f"🔐 Permission Level: {ai_orchestrator_v2.decision_engine.current_permission_level if ai_orchestrator_v2 else 'N/A'}")
    logger.info(f"⚙️  Trading: {'ENABLED' if settings.TRADING_ENABLED else 'DISABLED'}")
    logger.info("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown - v2.0"""
    global market_data_service, trading_service, ai_orchestrator_v2
    
    logger.info("="*60)
    logger.info("🛑 Shutting down AIcoin Trading System v2.0...")
    logger.info("="*60)
    
    # Stop AI orchestrator v2
    if ai_orchestrator_v2:
        try:
            await ai_orchestrator_v2.stop()
            logger.info("✅ AI orchestrator v2 stopped")
        except Exception as e:
            logger.error(f"❌ AI orchestrator shutdown failed: {e}")
    
    # Stop trading service
    if trading_service:
        try:
            await trading_service.stop()
            logger.info("✅ Trading service stopped")
        except Exception as e:
            logger.error(f"❌ Trading service shutdown failed: {e}")
    
    # Stop market data service
    if market_data_service:
        try:
            await market_data_service.stop()
            logger.info("✅ Market data service stopped")
        except Exception as e:
            logger.error(f"❌ Market data service shutdown failed: {e}")
    
    # Stop WebSocket manager
    try:
        await websocket_manager.stop_broadcast_service()
        logger.info("✅ WebSocket manager stopped")
    except Exception as e:
        logger.error(f"❌ WebSocket manager shutdown failed: {e}")
    
    # Close Redis
    try:
        await redis_client.disconnect()
        logger.info("✅ Redis disconnected")
    except Exception as e:
        logger.error(f"❌ Redis disconnect failed: {e}")
    
    logger.info("="*60)
    logger.info("✅ Shutdown complete")
    logger.info("="*60)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "status": "running",
        "trading_enabled": settings.TRADING_ENABLED,
        "permission_level": ai_orchestrator_v2.decision_engine.current_permission_level if ai_orchestrator_v2 else "N/A",
        "decision_interval": settings.DECISION_INTERVAL,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "services": {
            "redis": redis_client is not None,
            "market_data": market_data_service is not None,
            "trading": trading_service is not None,
            "ai_orchestrator": ai_orchestrator_v2 is not None,
        }
    }
    
    if ai_orchestrator_v2:
        health_status["orchestrator_status"] = ai_orchestrator_v2.get_status()
    
    return health_status


@app.get("/api/v1/status")
async def system_status():
    """System status endpoint"""
    if ai_orchestrator_v2:
        return {
            "version": "2.0.0",
            "orchestrator": ai_orchestrator_v2.get_status(),
            "permission_summary": ai_orchestrator_v2.decision_engine.permission_mgr.get_permission_summary(
                ai_orchestrator_v2.decision_engine.current_permission_level
            ),
            "constraints": ai_orchestrator_v2.decision_engine.constraint_validator.get_constraint_summary()
        }
    else:
        return {
            "version": "2.0.0",
            "status": "AI Orchestrator not initialized",
            "trading_enabled": settings.TRADING_ENABLED
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

