"""add model versions

Revision ID: 008
Revises: 007
Create Date: 2025-11-05 12:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # 创建模型版本表
    op.create_table(
        'model_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version_name', sa.String(length=100), nullable=False),
        sa.Column('base_model', sa.String(length=100), nullable=True),
        sa.Column('training_platform', sa.String(length=50), nullable=True),
        sa.Column('training_job_id', sa.String(length=200), nullable=True),
        sa.Column('training_data_range', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('training_samples_count', sa.Integer(), nullable=True),
        sa.Column('hyperparameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('evaluation_metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='training'),
        sa.Column('deployed', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_versions_id'), 'model_versions', ['id'], unique=False)
    op.create_index(op.f('ix_model_versions_version_name'), 'model_versions', ['version_name'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_model_versions_version_name'), table_name='model_versions')
    op.drop_index(op.f('ix_model_versions_id'), table_name='model_versions')
    op.drop_table('model_versions')

