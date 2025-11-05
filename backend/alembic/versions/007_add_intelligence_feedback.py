"""add intelligence feedback

Revision ID: 007
Revises: 006
Create Date: 2025-11-05 12:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # 创建情报反馈表
    op.create_table(
        'intelligence_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.String(length=100), nullable=False),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('user_interaction', sa.String(length=50), nullable=True),
        sa.Column('effectiveness_rating', sa.Float(), nullable=True),
        sa.Column('decision_influenced', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('decision_outcome', sa.String(length=50), nullable=True),
        sa.Column('feedback_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_intelligence_feedback_id'), 'intelligence_feedback', ['id'], unique=False)
    op.create_index(op.f('ix_intelligence_feedback_report_id'), 'intelligence_feedback', ['report_id'], unique=False)
    op.create_index(op.f('ix_intelligence_feedback_source_name'), 'intelligence_feedback', ['source_name'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_intelligence_feedback_source_name'), table_name='intelligence_feedback')
    op.drop_index(op.f('ix_intelligence_feedback_report_id'), table_name='intelligence_feedback')
    op.drop_index(op.f('ix_intelligence_feedback_id'), table_name='intelligence_feedback')
    op.drop_table('intelligence_feedback')

