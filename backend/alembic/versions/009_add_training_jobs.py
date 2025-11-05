"""add training jobs

Revision ID: 009
Revises: 008
Create Date: 2025-11-05 12:03:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    # 创建训练任务表
    op.create_table(
        'training_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(length=200), nullable=False),
        sa.Column('model_version_id', sa.Integer(), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('instance_type', sa.String(length=100), nullable=True),
        sa.Column('training_type', sa.String(length=50), nullable=True),
        sa.Column('dataset_path', sa.String(length=500), nullable=True),
        sa.Column('dataset_size', sa.Integer(), nullable=True),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('progress_percentage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('current_epoch', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_epochs', sa.Integer(), nullable=True),
        sa.Column('logs_path', sa.String(length=500), nullable=True),
        sa.Column('checkpoint_path', sa.String(length=500), nullable=True),
        sa.Column('final_metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('estimated_cost', sa.Integer(), nullable=True),
        sa.Column('actual_cost', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_jobs_id'), 'training_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_training_jobs_job_id'), 'training_jobs', ['job_id'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_training_jobs_job_id'), table_name='training_jobs')
    op.drop_index(op.f('ix_training_jobs_id'), table_name='training_jobs')
    op.drop_table('training_jobs')

