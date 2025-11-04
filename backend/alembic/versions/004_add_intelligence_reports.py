"""add intelligence reports table

Revision ID: 004
Revises: 003
Create Date: 2025-11-04 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """创建intelligence_reports表"""
    op.create_table(
        'intelligence_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('market_sentiment', sa.String(length=20), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('key_news', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('whale_signals', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('on_chain_metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('risk_factors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('opportunities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('qwen_analysis', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('timestamp')
    )
    
    # 创建索引
    op.create_index('idx_intelligence_timestamp', 'intelligence_reports', ['timestamp'])
    op.create_index('idx_intelligence_sentiment', 'intelligence_reports', ['market_sentiment'])
    op.create_index('idx_intelligence_created', 'intelligence_reports', ['created_at'])
    op.create_index('idx_intelligence_confidence', 'intelligence_reports', ['confidence'])
    
    # 创建自增序列的索引
    op.create_index(op.f('ix_intelligence_reports_id'), 'intelligence_reports', ['id'], unique=False)


def downgrade():
    """删除intelligence_reports表"""
    op.drop_index(op.f('ix_intelligence_reports_id'), table_name='intelligence_reports')
    op.drop_index('idx_intelligence_confidence', table_name='intelligence_reports')
    op.drop_index('idx_intelligence_created', table_name='intelligence_reports')
    op.drop_index('idx_intelligence_sentiment', table_name='intelligence_reports')
    op.drop_index('idx_intelligence_timestamp', table_name='intelligence_reports')
    op.drop_table('intelligence_reports')

