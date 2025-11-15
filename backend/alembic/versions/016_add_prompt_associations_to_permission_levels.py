"""add prompt associations to permission levels

Revision ID: 016
Revises: 015
Create Date: 2025-11-15 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '016'
down_revision = '20251114_142906'  # 基于辩论系统迁移
branch_labels = None
depends_on = None


def upgrade():
    # 添加 Prompt 关联字段到 permission_level_configs 表
    op.add_column('permission_level_configs', 
        sa.Column('decision_prompt_id', sa.Integer(), nullable=True, comment='决策 Prompt 模板 ID'))
    op.add_column('permission_level_configs', 
        sa.Column('debate_prompt_id', sa.Integer(), nullable=True, comment='辩论 Prompt 模板 ID'))
    op.add_column('permission_level_configs', 
        sa.Column('intelligence_prompt_id', sa.Integer(), nullable=True, comment='情报 Prompt 模板 ID'))
    
    # 添加外键约束（可选，如果需要强制引用完整性）
    # op.create_foreign_key(
    #     'fk_permission_decision_prompt',
    #     'permission_level_configs', 'prompt_templates',
    #     ['decision_prompt_id'], ['id'],
    #     ondelete='SET NULL'
    # )
    # op.create_foreign_key(
    #     'fk_permission_debate_prompt',
    #     'permission_level_configs', 'prompt_templates',
    #     ['debate_prompt_id'], ['id'],
    #     ondelete='SET NULL'
    # )
    # op.create_foreign_key(
    #     'fk_permission_intelligence_prompt',
    #     'permission_level_configs', 'prompt_templates',
    #     ['intelligence_prompt_id'], ['id'],
    #     ondelete='SET NULL'
    # )


def downgrade():
    # 删除外键约束（如果添加了）
    # op.drop_constraint('fk_permission_intelligence_prompt', 'permission_level_configs', type_='foreignkey')
    # op.drop_constraint('fk_permission_debate_prompt', 'permission_level_configs', type_='foreignkey')
    # op.drop_constraint('fk_permission_decision_prompt', 'permission_level_configs', type_='foreignkey')
    
    # 删除列
    op.drop_column('permission_level_configs', 'intelligence_prompt_id')
    op.drop_column('permission_level_configs', 'debate_prompt_id')
    op.drop_column('permission_level_configs', 'decision_prompt_id')

