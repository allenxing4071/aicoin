"""
聪明钱跟单数据模型

用于追踪和分析聪明钱钱包的交易行为
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class SmartMoneyWallet(Base):
    """聪明钱钱包表"""
    __tablename__ = "smart_money_wallets"
    __table_args__ = {'comment': '👛 聪明钱钱包 - 管理被标记为聪明钱的钱包地址列表及其历史表现和信誉评分'}

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(200), nullable=False, unique=True, index=True, comment="钱包地址")
    nickname = Column(String(200), comment="昵称/标签")
    chain = Column(String(50), nullable=False, comment="区块链：ethereum/bsc/arbitrum等")
    total_profit = Column(Numeric(20, 8), default=0, comment="总收益（USD）")
    win_rate = Column(Float, default=0.0, comment="胜率")
    avg_holding_time = Column(Integer, comment="平均持仓时间（秒）")
    tracked_since = Column(DateTime(timezone=True), server_default=func.now(), comment="开始跟踪时间")
    enabled = Column(Boolean, default=True, comment="是否启用")
    tags = Column(JSON, comment="标签（JSON数组，如'DeFi高手'、'NFT玩家'）")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    transactions = relationship("SmartMoneyTransaction", back_populates="wallet", cascade="all, delete-orphan")


class SmartMoneyTransaction(Base):
    """聪明钱交易表"""
    __tablename__ = "smart_money_transactions"
    __table_args__ = {'comment': '💎 聪明钱交易 - 追踪大户和聪明钱地址的链上交易行为，用于跟单和市场情绪分析'}

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("smart_money_wallets.id", ondelete="CASCADE"), nullable=False)
    tx_hash = Column(String(200), nullable=False, unique=True, index=True, comment="交易哈希")
    action = Column(String(20), nullable=False, comment="操作类型：buy/sell/swap")
    token_in = Column(String(100), comment="输入代币")
    token_out = Column(String(100), comment="输出代币")
    amount_in = Column(Numeric(30, 18), comment="输入数量")
    amount_out = Column(Numeric(30, 18), comment="输出数量")
    price_usd = Column(Numeric(20, 8), comment="美元价格")
    profit_usd = Column(Numeric(20, 8), comment="收益（如果已平仓）")
    dex = Column(String(100), comment="交易所：Uniswap/PancakeSwap等")
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, comment="交易时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    wallet = relationship("SmartMoneyWallet", back_populates="transactions")

