"""drop users table and add trades comment

Revision ID: 012
Revises: 011
Create Date: 2025-11-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    1. 删除遗留的 users 表（已被 admin_users 替代）
    2. 为 trades 表添加表注释
    """
    
    # 1. 删除 users 表
    op.drop_table('users')
    
    # 2. 为 trades 表添加注释
    op.execute("""
        COMMENT ON TABLE trades IS '💰 成交记录 - 记录所有已成交的交易明细，包括价格、数量、盈亏、AI决策依据等完整信息'
    """)


def downgrade() -> None:
    """回滚操作"""
    
    # 1. 重新创建 users 表（如果需要回滚）
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='trader'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # 2. 移除 trades 表注释
    op.execute("COMMENT ON TABLE trades IS NULL")

