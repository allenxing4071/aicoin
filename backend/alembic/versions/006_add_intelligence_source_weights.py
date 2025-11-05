"""add intelligence source weights

Revision ID: 006
Revises: 005
Create Date: 2025-11-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # 创建情报源权重表
    op.create_table(
        'intelligence_source_weights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('base_weight', sa.Float(), nullable=True, server_default='0.5'),
        sa.Column('dynamic_weight', sa.Float(), nullable=True, server_default='0.5'),
        sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('positive_feedback_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('effectiveness_score', sa.Float(), nullable=True, server_default='0.5'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_intelligence_source_weights_id'), 'intelligence_source_weights', ['id'], unique=False)
    op.create_index(op.f('ix_intelligence_source_weights_source_name'), 'intelligence_source_weights', ['source_name'], unique=True)
    op.create_index(op.f('ix_intelligence_source_weights_source_type'), 'intelligence_source_weights', ['source_type'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_intelligence_source_weights_source_type'), table_name='intelligence_source_weights')
    op.drop_index(op.f('ix_intelligence_source_weights_source_name'), table_name='intelligence_source_weights')
    op.drop_index(op.f('ix_intelligence_source_weights_id'), table_name='intelligence_source_weights')
    op.drop_table('intelligence_source_weights')

