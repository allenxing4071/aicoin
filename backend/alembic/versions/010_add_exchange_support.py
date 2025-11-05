"""add exchange support

Revision ID: 010
Revises: 009
Create Date: 2025-11-05 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    # 创建交易所配置表
    op.create_table(
        'exchange_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('market_type', sa.String(length=20), nullable=True, server_default='spot'),
        sa.Column('api_key_encrypted', sa.Text(), nullable=True),
        sa.Column('api_secret_encrypted', sa.Text(), nullable=True),
        sa.Column('testnet', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('config_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_exchange_name')
    )
    op.create_index(op.f('ix_exchange_configs_id'), 'exchange_configs', ['id'], unique=False)
    op.create_index(op.f('ix_exchange_configs_name'), 'exchange_configs', ['name'], unique=False)
    
    # 创建部分唯一索引: 同一时刻只能有一个交易所为active
    op.execute("""
        CREATE UNIQUE INDEX idx_active_exchange 
        ON exchange_configs (is_active) 
        WHERE is_active = true
    """)
    
    # 扩展K线表 - 添加交易所和市场类型字段
    op.add_column('market_data_kline', sa.Column('exchange', sa.String(length=50), nullable=True, server_default='hyperliquid'))
    op.add_column('market_data_kline', sa.Column('market_type', sa.String(length=20), nullable=True, server_default='perpetual'))
    op.add_column('market_data_kline', sa.Column('funding_rate', sa.Numeric(precision=10, scale=6), nullable=True))
    op.add_column('market_data_kline', sa.Column('open_interest', sa.Numeric(precision=18, scale=2), nullable=True))
    
    # 创建索引以提高查询性能
    op.create_index(
        'idx_kline_exchange', 
        'market_data_kline', 
        ['exchange', 'symbol', 'interval'], 
        unique=False
    )
    
    # 插入默认交易所配置(Hyperliquid)
    op.execute("""
        INSERT INTO exchange_configs (name, display_name, is_active, market_type, testnet, config_json)
        VALUES ('hyperliquid', 'Hyperliquid', true, 'perpetual', false, '{}')
    """)


def downgrade():
    # 删除K线表的新增字段
    op.drop_index('idx_kline_exchange', table_name='market_data_kline')
    op.drop_column('market_data_kline', 'open_interest')
    op.drop_column('market_data_kline', 'funding_rate')
    op.drop_column('market_data_kline', 'market_type')
    op.drop_column('market_data_kline', 'exchange')
    
    # 删除交易所配置表
    op.execute("DROP INDEX IF EXISTS idx_active_exchange")
    op.drop_index(op.f('ix_exchange_configs_name'), table_name='exchange_configs')
    op.drop_index(op.f('ix_exchange_configs_id'), table_name='exchange_configs')
    op.drop_table('exchange_configs')

