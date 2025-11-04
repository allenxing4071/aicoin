"""add permission level configs table

Revision ID: 003
Revises: 002
Create Date: 2025-11-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create permission_level_configs table
    op.create_table(
        'permission_level_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('level', sa.String(10), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Trading params
        sa.Column('max_position_pct', sa.Float(), nullable=False, server_default='0.10'),
        sa.Column('max_leverage', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('confidence_threshold', sa.Float(), nullable=False, server_default='0.70'),
        sa.Column('max_daily_trades', sa.Integer(), nullable=False, server_default='5'),
        
        # Upgrade conditions
        sa.Column('upgrade_win_rate_7d', sa.Float(), nullable=True),
        sa.Column('upgrade_win_rate_30d', sa.Float(), nullable=True),
        sa.Column('upgrade_sharpe_ratio', sa.Float(), nullable=True),
        sa.Column('upgrade_min_trades', sa.Integer(), nullable=True),
        sa.Column('upgrade_min_days', sa.Integer(), nullable=True),
        
        # Downgrade conditions
        sa.Column('downgrade_max_drawdown', sa.Float(), nullable=True),
        sa.Column('downgrade_consecutive_losses', sa.Integer(), nullable=True),
        sa.Column('downgrade_win_rate_7d', sa.Float(), nullable=True),
        
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('level')
    )
    
    # Create indexes
    op.create_index('ix_permission_level_configs_level', 'permission_level_configs', ['level'])
    op.create_index('ix_permission_level_configs_is_default', 'permission_level_configs', ['is_default'])
    
    # Insert default data
    op.execute("""
        INSERT INTO permission_level_configs 
        (level, name, description, max_position_pct, max_leverage, confidence_threshold, max_daily_trades, 
         upgrade_win_rate_7d, upgrade_min_trades, upgrade_min_days, downgrade_max_drawdown, downgrade_consecutive_losses, is_default)
        VALUES 
        ('L0', '保护模式', '触发风控红线后的保护模式，禁止所有交易', 0.0, 1, 1.0, 0, NULL, NULL, NULL, NULL, NULL, false),
        ('L1', '新手级', '初始等级，严格限制仓位和杠杆', 0.10, 2, 0.50, 10, 0.55, 5, 3, 0.10, 3, true),
        ('L2', '成长级', '表现良好，适度放宽限制', 0.12, 2, 0.75, 2, 0.60, 10, NULL, NULL, 4, false),
        ('L3', '稳定级', '稳定盈利，获得更多权限', 0.15, 3, 0.70, 4, NULL, 20, NULL, 0.15, NULL, false),
        ('L4', '熟练级', '经验丰富，较高自由度', 0.20, 4, 0.65, 6, NULL, 50, NULL, NULL, NULL, false),
        ('L5', '专家级', '最高等级，几乎无限制', 0.25, 5, 0.60, 999, NULL, NULL, NULL, 0.20, NULL, false)
    """)


def downgrade():
    op.drop_index('ix_permission_level_configs_is_default', table_name='permission_level_configs')
    op.drop_index('ix_permission_level_configs_level', table_name='permission_level_configs')
    op.drop_table('permission_level_configs')

