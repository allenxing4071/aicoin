"""权限等级配置管理 API - 后台管理"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.permission_config import PermissionLevelConfig

router = APIRouter(prefix="/admin/permissions", tags=["Admin - Permissions"])


# === Pydantic Models ===

class TradingParams(BaseModel):
    """交易参数"""
    max_position_pct: float = Field(..., ge=0.0, le=1.0, description="单仓位最大占比")
    max_leverage: int = Field(..., ge=1, le=20, description="最大杠杆")
    confidence_threshold: float = Field(..., ge=0.0, le=1.0, description="置信度门槛")
    max_daily_trades: int = Field(..., ge=0, le=999, description="每日最大交易次数")


class UpgradeConditions(BaseModel):
    """升级条件"""
    win_rate_7d: Optional[float] = Field(None, ge=0.0, le=1.0, description="7日胜率要求")
    win_rate_30d: Optional[float] = Field(None, ge=0.0, le=1.0, description="30日胜率要求")
    sharpe_ratio: Optional[float] = Field(None, description="夏普比率要求")
    min_trades: Optional[int] = Field(None, ge=0, description="最少交易次数")
    min_days: Optional[int] = Field(None, ge=0, description="最少运行天数")


class DowngradeConditions(BaseModel):
    """降级条件"""
    max_drawdown: Optional[float] = Field(None, ge=0.0, le=1.0, description="最大回撤触发降级")
    consecutive_losses: Optional[int] = Field(None, ge=0, description="连续亏损次数")
    win_rate_7d: Optional[float] = Field(None, ge=0.0, le=1.0, description="7日胜率低于此值降级")


class PermissionLevelCreate(BaseModel):
    """创建权限等级"""
    level: str = Field(..., pattern="^L[0-5]$", description="等级代码 (L0-L5)")
    name: str = Field(..., min_length=1, max_length=50, description="等级名称")
    description: Optional[str] = Field(None, description="等级描述")
    trading_params: TradingParams
    upgrade_conditions: Optional[UpgradeConditions] = None
    downgrade_conditions: Optional[DowngradeConditions] = None
    is_active: bool = Field(True, description="是否启用")
    is_default: bool = Field(False, description="是否为默认等级")


class PermissionLevelUpdate(BaseModel):
    """更新权限等级"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    trading_params: Optional[TradingParams] = None
    upgrade_conditions: Optional[UpgradeConditions] = None
    downgrade_conditions: Optional[DowngradeConditions] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    # 新增：Prompt 关联
    decision_prompt_id: Optional[int] = Field(None, description="决策 Prompt ID")
    debate_prompt_id: Optional[int] = Field(None, description="辩论 Prompt ID")
    intelligence_prompt_id: Optional[int] = Field(None, description="情报 Prompt ID")


class PermissionLevelResponse(BaseModel):
    """权限等级响应"""
    id: int
    level: str
    name: str
    description: Optional[str]
    trading_params: dict
    upgrade_conditions: dict
    downgrade_conditions: dict
    is_active: bool
    is_default: bool
    created_at: str
    updated_at: str


# === API Endpoints ===

@router.get("/levels", response_model=List[PermissionLevelResponse])
async def get_all_permission_levels(
    db: AsyncSession = Depends(get_db)
):
    """获取所有权限等级配置"""
    try:
        stmt = select(PermissionLevelConfig).order_by(PermissionLevelConfig.level)
        result = await db.execute(stmt)
        configs = result.scalars().all()
        
        return [config.to_dict() for config in configs]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch permission levels: {str(e)}"
        )


@router.get("/levels/{level}", response_model=PermissionLevelResponse)
async def get_permission_level(
    level: str,
    db: AsyncSession = Depends(get_db)
):
    """获取指定权限等级配置"""
    try:
        stmt = select(PermissionLevelConfig).where(PermissionLevelConfig.level == level)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission level {level} not found"
            )
        
        return config.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch permission level: {str(e)}"
        )


@router.post("/levels", response_model=PermissionLevelResponse, status_code=status.HTTP_201_CREATED)
async def create_permission_level(
    data: PermissionLevelCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新的权限等级配置"""
    try:
        # 检查是否已存在
        stmt = select(PermissionLevelConfig).where(PermissionLevelConfig.level == data.level)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission level {data.level} already exists"
            )
        
        # 创建新配置
        config = PermissionLevelConfig(
            level=data.level,
            name=data.name,
            description=data.description,
            max_position_pct=data.trading_params.max_position_pct,
            max_leverage=data.trading_params.max_leverage,
            confidence_threshold=data.trading_params.confidence_threshold,
            max_daily_trades=data.trading_params.max_daily_trades,
            is_active=data.is_active,
            is_default=data.is_default
        )
        
        # 升级条件
        if data.upgrade_conditions:
            config.upgrade_win_rate_7d = data.upgrade_conditions.win_rate_7d
            config.upgrade_win_rate_30d = data.upgrade_conditions.win_rate_30d
            config.upgrade_sharpe_ratio = data.upgrade_conditions.sharpe_ratio
            config.upgrade_min_trades = data.upgrade_conditions.min_trades
            config.upgrade_min_days = data.upgrade_conditions.min_days
        
        # 降级条件
        if data.downgrade_conditions:
            config.downgrade_max_drawdown = data.downgrade_conditions.max_drawdown
            config.downgrade_consecutive_losses = data.downgrade_conditions.consecutive_losses
            config.downgrade_win_rate_7d = data.downgrade_conditions.win_rate_7d
        
        db.add(config)
        await db.commit()
        await db.refresh(config)
        
        return config.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create permission level: {str(e)}"
        )


@router.put("/levels/{level_id}", response_model=PermissionLevelResponse)
async def update_permission_level_by_id(
    level_id: int,
    data: PermissionLevelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """通过 ID 更新权限等级配置（支持 Prompt 关联）"""
    try:
        # 通过 ID 查询
        config = await db.get(PermissionLevelConfig, level_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission level with ID {level_id} not found"
            )
        
        # 更新基本信息
        if data.name is not None:
            config.name = data.name
        if data.description is not None:
            config.description = data.description
        if data.is_active is not None:
            config.is_active = data.is_active
        if data.is_default is not None:
            config.is_default = data.is_default
        
        # 更新 Prompt 关联
        if data.decision_prompt_id is not None:
            config.decision_prompt_id = data.decision_prompt_id
        if data.debate_prompt_id is not None:
            config.debate_prompt_id = data.debate_prompt_id
        if data.intelligence_prompt_id is not None:
            config.intelligence_prompt_id = data.intelligence_prompt_id
        
        # 更新交易参数
        if data.trading_params:
            config.max_position_pct = data.trading_params.max_position_pct
            config.max_leverage = data.trading_params.max_leverage
            config.confidence_threshold = data.trading_params.confidence_threshold
            config.max_daily_trades = data.trading_params.max_daily_trades
        
        # 更新升级条件
        if data.upgrade_conditions:
            config.upgrade_win_rate_7d = data.upgrade_conditions.win_rate_7d
            config.upgrade_win_rate_30d = data.upgrade_conditions.win_rate_30d
            config.upgrade_sharpe_ratio = data.upgrade_conditions.sharpe_ratio
            config.upgrade_min_trades = data.upgrade_conditions.min_trades
            config.upgrade_min_days = data.upgrade_conditions.min_days
        
        # 更新降级条件
        if data.downgrade_conditions:
            config.downgrade_max_drawdown = data.downgrade_conditions.max_drawdown
            config.downgrade_consecutive_losses = data.downgrade_conditions.consecutive_losses
            config.downgrade_win_rate_7d = data.downgrade_conditions.win_rate_7d
        
        await db.commit()
        await db.refresh(config)
        
        return config.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update permission level: {str(e)}"
        )


@router.put("/levels/by-name/{level}", response_model=PermissionLevelResponse)
async def update_permission_level_by_name(
    level: str,
    data: PermissionLevelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """通过 level 名称更新权限等级配置"""
    try:
        stmt = select(PermissionLevelConfig).where(PermissionLevelConfig.level == level)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission level {level} not found"
            )
        
        # 更新基本信息
        if data.name is not None:
            config.name = data.name
        if data.description is not None:
            config.description = data.description
        if data.is_active is not None:
            config.is_active = data.is_active
        if data.is_default is not None:
            config.is_default = data.is_default
        
        # 更新 Prompt 关联
        if data.decision_prompt_id is not None:
            config.decision_prompt_id = data.decision_prompt_id
        if data.debate_prompt_id is not None:
            config.debate_prompt_id = data.debate_prompt_id
        if data.intelligence_prompt_id is not None:
            config.intelligence_prompt_id = data.intelligence_prompt_id
        
        # 更新交易参数
        if data.trading_params:
            config.max_position_pct = data.trading_params.max_position_pct
            config.max_leverage = data.trading_params.max_leverage
            config.confidence_threshold = data.trading_params.confidence_threshold
            config.max_daily_trades = data.trading_params.max_daily_trades
        
        # 更新升级条件
        if data.upgrade_conditions:
            config.upgrade_win_rate_7d = data.upgrade_conditions.win_rate_7d
            config.upgrade_win_rate_30d = data.upgrade_conditions.win_rate_30d
            config.upgrade_sharpe_ratio = data.upgrade_conditions.sharpe_ratio
            config.upgrade_min_trades = data.upgrade_conditions.min_trades
            config.upgrade_min_days = data.upgrade_conditions.min_days
        
        # 更新降级条件
        if data.downgrade_conditions:
            config.downgrade_max_drawdown = data.downgrade_conditions.max_drawdown
            config.downgrade_consecutive_losses = data.downgrade_conditions.consecutive_losses
            config.downgrade_win_rate_7d = data.downgrade_conditions.win_rate_7d
        
        await db.commit()
        await db.refresh(config)
        
        return config.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update permission level: {str(e)}"
        )


@router.delete("/levels/{level}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission_level(
    level: str,
    db: AsyncSession = Depends(get_db)
):
    """删除权限等级配置"""
    try:
        stmt = select(PermissionLevelConfig).where(PermissionLevelConfig.level == level)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission level {level} not found"
            )
        
        await db.delete(config)
        await db.commit()
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete permission level: {str(e)}"
        )


@router.post("/levels/{level}/set-default", response_model=PermissionLevelResponse)
async def set_default_permission_level(
    level: str,
    db: AsyncSession = Depends(get_db)
):
    """设置默认权限等级"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # 取消所有默认等级
        stmt = update(PermissionLevelConfig).values(is_default=False)
        await db.execute(stmt)
        
        # 设置新的默认等级
        stmt = select(PermissionLevelConfig).where(PermissionLevelConfig.level == level)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission level {level} not found"
            )
        
        config.is_default = True
        await db.commit()
        await db.refresh(config)
        
        # 清除权限管理器的缓存
        try:
            from app.main import ai_orchestrator
            if ai_orchestrator and hasattr(ai_orchestrator, 'permission_manager'):
                ai_orchestrator.permission_manager.clear_cache()
                logger.info(f"✅ 已清除权限管理器缓存")
            
            # 更新DecisionEngine的权限等级
            if ai_orchestrator and hasattr(ai_orchestrator, 'decision_engine'):
                if hasattr(ai_orchestrator.decision_engine, 'current_permission_level'):
                    old_level = ai_orchestrator.decision_engine.current_permission_level
                    ai_orchestrator.decision_engine.current_permission_level = level
                    logger.info(f"✅ 已更新DecisionEngine权限等级: {old_level} -> {level}")
        except Exception as e:
            logger.warning(f"清除缓存或更新权限等级时出错: {e}")
        
        return config.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default permission level: {str(e)}"
        )


@router.post("/levels/init-defaults", status_code=status.HTTP_201_CREATED)
async def initialize_default_levels(
    db: AsyncSession = Depends(get_db)
):
    """初始化默认权限等级配置"""
    try:
        default_levels = [
            {
                "level": "L0",
                "name": "保护模式",
                "description": "触发风控红线后的保护模式，禁止所有交易",
                "max_position_pct": 0.0,
                "max_leverage": 1,
                "confidence_threshold": 1.0,
                "max_daily_trades": 0,
                "is_default": False
            },
            {
                "level": "L1",
                "name": "新手级",
                "description": "初始等级，严格限制仓位和杠杆",
                "max_position_pct": 0.10,
                "max_leverage": 2,
                "confidence_threshold": 0.50,
                "max_daily_trades": 10,
                "upgrade_win_rate_7d": 0.55,
                "upgrade_min_trades": 5,
                "upgrade_min_days": 3,
                "downgrade_max_drawdown": 0.10,
                "downgrade_consecutive_losses": 3,
                "is_default": True
            },
            {
                "level": "L2",
                "name": "成长级",
                "description": "表现良好，适度放宽限制",
                "max_position_pct": 0.12,
                "max_leverage": 2,
                "confidence_threshold": 0.75,
                "max_daily_trades": 2,
                "upgrade_win_rate_7d": 0.60,
                "upgrade_win_rate_30d": 0.55,
                "upgrade_sharpe_ratio": 1.0,
                "upgrade_min_trades": 10,
                "downgrade_win_rate_7d": 0.45,
                "downgrade_consecutive_losses": 4,
                "is_default": False
            },
            {
                "level": "L3",
                "name": "稳定级",
                "description": "稳定盈利，获得更多权限",
                "max_position_pct": 0.15,
                "max_leverage": 3,
                "confidence_threshold": 0.70,
                "max_daily_trades": 4,
                "upgrade_win_rate_30d": 0.60,
                "upgrade_sharpe_ratio": 1.5,
                "upgrade_min_trades": 20,
                "downgrade_win_rate_7d": 0.40,
                "downgrade_max_drawdown": 0.15,
                "is_default": False
            },
            {
                "level": "L4",
                "name": "熟练级",
                "description": "经验丰富，较高自由度",
                "max_position_pct": 0.20,
                "max_leverage": 4,
                "confidence_threshold": 0.65,
                "max_daily_trades": 6,
                "upgrade_win_rate_30d": 0.65,
                "upgrade_sharpe_ratio": 2.0,
                "upgrade_min_trades": 50,
                "downgrade_win_rate_7d": 0.35,
                "is_default": False
            },
            {
                "level": "L5",
                "name": "专家级",
                "description": "最高等级，几乎无限制",
                "max_position_pct": 0.25,
                "max_leverage": 5,
                "confidence_threshold": 0.60,
                "max_daily_trades": 999,
                "downgrade_win_rate_7d": 0.30,
                "downgrade_max_drawdown": 0.20,
                "is_default": False
            }
        ]
        
        created_count = 0
        for level_data in default_levels:
            # 检查是否已存在
            stmt = select(PermissionLevelConfig).where(
                PermissionLevelConfig.level == level_data["level"]
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if not existing:
                config = PermissionLevelConfig(**level_data)
                db.add(config)
                created_count += 1
        
        await db.commit()
        
        return {
            "message": f"Successfully initialized {created_count} default permission levels",
            "created_count": created_count
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize default levels: {str(e)}"
        )

