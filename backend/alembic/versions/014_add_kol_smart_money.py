"""add kol and smart money tables

Revision ID: 014_add_kol_smart_money
Revises: 013
Create Date: 2025-01-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '014_add_kol_smart_money'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade():
    # 创建KOL数据源表
    op.create_table(
        'kol_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False, comment='KOL名称'),
        sa.Column('platform', sa.String(length=50), nullable=False, comment='平台类型：twitter/telegram'),
        sa.Column('channel_id', sa.String(length=200), nullable=False, comment='频道ID或用户名'),
        sa.Column('influence_score', sa.Float(), server_default='0.0', comment='影响力评分（0-100）'),
        sa.Column('accuracy_rate', sa.Float(), server_default='0.0', comment='历史准确率'),
        sa.Column('enabled', sa.Boolean(), server_default='true', comment='是否启用'),
        sa.Column('last_update', sa.DateTime(timezone=True), comment='最后更新时间'),
        sa.Column('total_posts', sa.Integer(), server_default='0', comment='总发帖数'),
        sa.Column('successful_predictions', sa.Integer(), server_default='0', comment='成功预测数'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_kol_sources_id', 'kol_sources', ['id'])

    # 创建KOL意见表
    op.create_table(
        'kol_opinions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kol_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False, comment='来源平台'),
        sa.Column('content', sa.Text(), nullable=False, comment='意见内容'),
        sa.Column('sentiment', sa.String(length=20), comment='情绪：bullish/bearish/neutral'),
        sa.Column('mentioned_coins', postgresql.JSON(astext_type=sa.Text()), comment='提及的币种（JSON数组）'),
        sa.Column('confidence', sa.Float(), comment='置信度'),
        sa.Column('post_url', sa.String(length=500), comment='原文链接'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['kol_id'], ['kol_sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_kol_opinions_id', 'kol_opinions', ['id'])
    op.create_index('ix_kol_opinions_created_at', 'kol_opinions', ['created_at'])

    # 创建聪明钱钱包表
    op.create_table(
        'smart_money_wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wallet_address', sa.String(length=200), nullable=False, comment='钱包地址'),
        sa.Column('nickname', sa.String(length=200), comment='昵称/标签'),
        sa.Column('chain', sa.String(length=50), nullable=False, comment='区块链：ethereum/bsc/arbitrum等'),
        sa.Column('total_profit', sa.Numeric(precision=20, scale=8), server_default='0', comment='总收益（USD）'),
        sa.Column('win_rate', sa.Float(), server_default='0.0', comment='胜率'),
        sa.Column('avg_holding_time', sa.Integer(), comment='平均持仓时间（秒）'),
        sa.Column('tracked_since', sa.DateTime(timezone=True), server_default=sa.text('now()'), comment='开始跟踪时间'),
        sa.Column('enabled', sa.Boolean(), server_default='true', comment='是否启用'),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), comment='标签（JSON数组）'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wallet_address')
    )
    op.create_index('ix_smart_money_wallets_id', 'smart_money_wallets', ['id'])
    op.create_index('ix_smart_money_wallets_wallet_address', 'smart_money_wallets', ['wallet_address'])

    # 创建聪明钱交易表
    op.create_table(
        'smart_money_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=False),
        sa.Column('tx_hash', sa.String(length=200), nullable=False, comment='交易哈希'),
        sa.Column('action', sa.String(length=20), nullable=False, comment='操作类型：buy/sell/swap'),
        sa.Column('token_in', sa.String(length=100), comment='输入代币'),
        sa.Column('token_out', sa.String(length=100), comment='输出代币'),
        sa.Column('amount_in', sa.Numeric(precision=30, scale=18), comment='输入数量'),
        sa.Column('amount_out', sa.Numeric(precision=30, scale=18), comment='输出数量'),
        sa.Column('price_usd', sa.Numeric(precision=20, scale=8), comment='美元价格'),
        sa.Column('profit_usd', sa.Numeric(precision=20, scale=8), comment='收益（如果已平仓）'),
        sa.Column('dex', sa.String(length=100), comment='交易所：Uniswap/PancakeSwap等'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, comment='交易时间'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['wallet_id'], ['smart_money_wallets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tx_hash')
    )
    op.create_index('ix_smart_money_transactions_id', 'smart_money_transactions', ['id'])
    op.create_index('ix_smart_money_transactions_tx_hash', 'smart_money_transactions', ['tx_hash'])
    op.create_index('ix_smart_money_transactions_timestamp', 'smart_money_transactions', ['timestamp'])


def downgrade():
    # 删除表
    op.drop_table('smart_money_transactions')
    op.drop_table('smart_money_wallets')
    op.drop_table('kol_opinions')
    op.drop_table('kol_sources')

