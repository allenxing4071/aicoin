"""add admin users table

Revision ID: 005
Revises: 004
Create Date: 2025-11-04 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def upgrade() -> None:
    # 创建admin_users表
    op.create_table(
        'admin_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_admin_users_id', 'admin_users', ['id'], unique=False)
    op.create_index('ix_admin_users_username', 'admin_users', ['username'], unique=True)
    op.create_index('ix_admin_users_email', 'admin_users', ['email'], unique=True)
    
    # 插入默认管理员账号
    admin_users_table = sa.table(
        'admin_users',
        sa.column('username', sa.String),
        sa.column('email', sa.String),
        sa.column('hashed_password', sa.String),
        sa.column('role', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )
    
    now = datetime.utcnow()
    op.bulk_insert(
        admin_users_table,
        [
            {
                'username': 'admin',
                'email': 'admin@aicoin.com',
                'hashed_password': pwd_context.hash('admin123'),
                'role': 'admin',
                'is_active': True,
                'created_at': now,
                'updated_at': now,
            }
        ]
    )


def downgrade() -> None:
    op.drop_index('ix_admin_users_email', table_name='admin_users')
    op.drop_index('ix_admin_users_username', table_name='admin_users')
    op.drop_index('ix_admin_users_id', table_name='admin_users')
    op.drop_table('admin_users')

