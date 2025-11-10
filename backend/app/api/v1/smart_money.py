"""
聪明钱跟单API

提供聪明钱钱包管理和交易记录查询功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

from app.core.database import get_db
from app.models.smart_money import SmartMoneyWallet, SmartMoneyTransaction

router = APIRouter(prefix="/smart-money", tags=["聪明钱跟单"])


# Pydantic模型
class SmartMoneyWalletCreate(BaseModel):
    wallet_address: str
    nickname: Optional[str] = None
    chain: str  # ethereum/bsc/arbitrum
    tags: Optional[List[str]] = None
    enabled: bool = True


class SmartMoneyWalletUpdate(BaseModel):
    nickname: Optional[str] = None
    chain: Optional[str] = None
    tags: Optional[List[str]] = None
    enabled: Optional[bool] = None


class SmartMoneyWalletResponse(BaseModel):
    id: int
    wallet_address: str
    nickname: Optional[str]
    chain: str
    total_profit: float
    win_rate: float
    avg_holding_time: Optional[int]
    tracked_since: datetime
    enabled: bool
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class SmartMoneyTransactionResponse(BaseModel):
    id: int
    wallet_id: int
    wallet_address: str
    tx_hash: str
    action: str
    token_in: Optional[str]
    token_out: Optional[str]
    amount_in: Optional[float]
    amount_out: Optional[float]
    price_usd: Optional[float]
    profit_usd: Optional[float]
    dex: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


# API端点
@router.get("/wallets", response_model=List[SmartMoneyWalletResponse])
async def get_smart_money_wallets(
    chain: Optional[str] = None,
    enabled: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取聪明钱钱包列表"""
    try:
        stmt = select(SmartMoneyWallet)
        
        if chain:
            stmt = stmt.where(SmartMoneyWallet.chain == chain)
        if enabled is not None:
            stmt = stmt.where(SmartMoneyWallet.enabled == enabled)
        
        stmt = stmt.order_by(desc(SmartMoneyWallet.total_profit))
        
        result = await db.execute(stmt)
        wallets = result.scalars().all()
        
        # 转换Decimal为float
        wallets_data = []
        for wallet in wallets:
            wallet_dict = {
                "id": wallet.id,
                "wallet_address": wallet.wallet_address,
                "nickname": wallet.nickname,
                "chain": wallet.chain,
                "total_profit": float(wallet.total_profit) if wallet.total_profit else 0.0,
                "win_rate": wallet.win_rate,
                "avg_holding_time": wallet.avg_holding_time,
                "tracked_since": wallet.tracked_since,
                "enabled": wallet.enabled,
                "tags": wallet.tags,
                "created_at": wallet.created_at,
            }
            wallets_data.append(wallet_dict)
        
        return wallets_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取钱包列表失败: {str(e)}")


@router.post("/wallets", response_model=SmartMoneyWalletResponse)
async def create_smart_money_wallet(
    wallet: SmartMoneyWalletCreate,
    db: AsyncSession = Depends(get_db)
):
    """添加聪明钱钱包"""
    try:
        # 检查是否已存在
        stmt = select(SmartMoneyWallet).where(
            SmartMoneyWallet.wallet_address == wallet.wallet_address
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="该钱包已存在")
        
        # 创建新钱包
        db_wallet = SmartMoneyWallet(**wallet.model_dump())
        db.add(db_wallet)
        await db.commit()
        await db.refresh(db_wallet)
        
        # 转换返回数据
        return {
            "id": db_wallet.id,
            "wallet_address": db_wallet.wallet_address,
            "nickname": db_wallet.nickname,
            "chain": db_wallet.chain,
            "total_profit": float(db_wallet.total_profit) if db_wallet.total_profit else 0.0,
            "win_rate": db_wallet.win_rate,
            "avg_holding_time": db_wallet.avg_holding_time,
            "tracked_since": db_wallet.tracked_since,
            "enabled": db_wallet.enabled,
            "tags": db_wallet.tags,
            "created_at": db_wallet.created_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加钱包失败: {str(e)}")


@router.put("/wallets/{wallet_id}", response_model=SmartMoneyWalletResponse)
async def update_smart_money_wallet(
    wallet_id: int,
    wallet: SmartMoneyWalletUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新聪明钱钱包"""
    try:
        stmt = select(SmartMoneyWallet).where(SmartMoneyWallet.id == wallet_id)
        result = await db.execute(stmt)
        db_wallet = result.scalar_one_or_none()
        
        if not db_wallet:
            raise HTTPException(status_code=404, detail="钱包不存在")
        
        # 更新字段
        for key, value in wallet.model_dump(exclude_unset=True).items():
            setattr(db_wallet, key, value)
        
        await db.commit()
        await db.refresh(db_wallet)
        
        return {
            "id": db_wallet.id,
            "wallet_address": db_wallet.wallet_address,
            "nickname": db_wallet.nickname,
            "chain": db_wallet.chain,
            "total_profit": float(db_wallet.total_profit) if db_wallet.total_profit else 0.0,
            "win_rate": db_wallet.win_rate,
            "avg_holding_time": db_wallet.avg_holding_time,
            "tracked_since": db_wallet.tracked_since,
            "enabled": db_wallet.enabled,
            "tags": db_wallet.tags,
            "created_at": db_wallet.created_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新钱包失败: {str(e)}")


@router.delete("/wallets/{wallet_id}")
async def delete_smart_money_wallet(
    wallet_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除聪明钱钱包"""
    try:
        stmt = select(SmartMoneyWallet).where(SmartMoneyWallet.id == wallet_id)
        result = await db.execute(stmt)
        db_wallet = result.scalar_one_or_none()
        
        if not db_wallet:
            raise HTTPException(status_code=404, detail="钱包不存在")
        
        await db.delete(db_wallet)
        await db.commit()
        
        return {"success": True, "message": "钱包已删除"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除钱包失败: {str(e)}")


@router.get("/transactions")
async def get_smart_money_transactions(
    wallet_id: Optional[int] = None,
    action: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """获取聪明钱交易记录"""
    try:
        stmt = select(SmartMoneyTransaction, SmartMoneyWallet.wallet_address).join(
            SmartMoneyWallet, SmartMoneyTransaction.wallet_id == SmartMoneyWallet.id
        )
        
        if wallet_id:
            stmt = stmt.where(SmartMoneyTransaction.wallet_id == wallet_id)
        if action:
            stmt = stmt.where(SmartMoneyTransaction.action == action)
        
        stmt = stmt.order_by(desc(SmartMoneyTransaction.timestamp)).limit(limit)
        
        result = await db.execute(stmt)
        rows = result.all()
        
        transactions = [
            {
                "id": tx.id,
                "wallet_id": tx.wallet_id,
                "wallet_address": wallet_address,
                "tx_hash": tx.tx_hash,
                "action": tx.action,
                "token_in": tx.token_in,
                "token_out": tx.token_out,
                "amount_in": float(tx.amount_in) if tx.amount_in else None,
                "amount_out": float(tx.amount_out) if tx.amount_out else None,
                "price_usd": float(tx.price_usd) if tx.price_usd else None,
                "profit_usd": float(tx.profit_usd) if tx.profit_usd else None,
                "dex": tx.dex,
                "timestamp": tx.timestamp,
            }
            for tx, wallet_address in rows
        ]
        
        return {"success": True, "data": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易记录失败: {str(e)}")


@router.get("/statistics")
async def get_smart_money_statistics(db: AsyncSession = Depends(get_db)):
    """获取聪明钱统计数据"""
    try:
        # 总钱包数
        total_wallets_stmt = select(func.count(SmartMoneyWallet.id))
        total_wallets = await db.scalar(total_wallets_stmt) or 0
        
        # 启用的钱包数
        enabled_wallets_stmt = select(func.count(SmartMoneyWallet.id)).where(SmartMoneyWallet.enabled == True)
        enabled_wallets = await db.scalar(enabled_wallets_stmt) or 0
        
        # 总交易数
        total_transactions_stmt = select(func.count(SmartMoneyTransaction.id))
        total_transactions = await db.scalar(total_transactions_stmt) or 0
        
        # 平均胜率
        avg_win_rate_stmt = select(func.avg(SmartMoneyWallet.win_rate))
        avg_win_rate = await db.scalar(avg_win_rate_stmt) or 0
        
        # 总收益
        total_profit_stmt = select(func.sum(SmartMoneyWallet.total_profit))
        total_profit = await db.scalar(total_profit_stmt) or 0
        
        return {
            "success": True,
            "data": {
                "total_wallets": total_wallets,
                "enabled_wallets": enabled_wallets,
                "total_transactions": total_transactions,
                "avg_win_rate": float(avg_win_rate),
                "total_profit": float(total_profit),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

