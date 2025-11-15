"""add debate tables

Revision ID: 20251114_142906
Revises: 
Create Date: 2025-11-14 14:29:06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251114_142906'
down_revision = '015'  # 基于 Prompt 系统迁移
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 debate_config 表
    op.create_table(
        'debate_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_key', sa.String(length=100), nullable=False, comment='配置键'),
        sa.Column('config_value', sa.Text(), nullable=True, comment='配置值'),
        sa.Column('description', sa.Text(), nullable=True, comment='配置说明'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='辩论配置表'
    )
    op.create_index(op.f('ix_debate_config_id'), 'debate_config', ['id'], unique=False)
    op.create_index(op.f('ix_debate_config_config_key'), 'debate_config', ['config_key'], unique=True)
    
    # 创建 debate_history 表
    op.create_table(
        'debate_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('decision_id', sa.String(length=100), nullable=False, comment='关联的决策ID'),
        sa.Column('symbol', sa.String(length=20), nullable=False, comment='交易标的'),
        sa.Column('debate_rounds', sa.Integer(), nullable=True, comment='辩论轮次'),
        sa.Column('bull_arguments', sa.Text(), nullable=True, comment='多头论点（完整历史）'),
        sa.Column('bear_arguments', sa.Text(), nullable=True, comment='空头论点（完整历史）'),
        sa.Column('debate_full_history', sa.Text(), nullable=True, comment='完整辩论历史'),
        sa.Column('final_recommendation', sa.String(length=20), nullable=True, comment='最终推荐（BUY/SELL/HOLD）'),
        sa.Column('confidence', sa.Float(), nullable=True, comment='置信度（0-1）'),
        sa.Column('consensus_level', sa.Float(), nullable=True, comment='共识度（0-1）'),
        sa.Column('debate_duration_seconds', sa.Integer(), nullable=True, comment='辩论耗时（秒）'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='辩论历史记录表'
    )
    op.create_index(op.f('ix_debate_history_id'), 'debate_history', ['id'], unique=False)
    op.create_index(op.f('ix_debate_history_decision_id'), 'debate_history', ['decision_id'], unique=True)
    op.create_index(op.f('ix_debate_history_symbol'), 'debate_history', ['symbol'], unique=False)
    op.create_index('idx_debate_symbol_created', 'debate_history', ['symbol', 'created_at'], unique=False)
    op.create_index('idx_debate_recommendation', 'debate_history', ['final_recommendation'], unique=False)
    
    # 创建 debate_statistics 表
    op.create_table(
        'debate_statistics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False, comment='统计日期'),
        sa.Column('total_debates', sa.Integer(), nullable=True, comment='总辩论次数'),
        sa.Column('bull_wins', sa.Integer(), nullable=True, comment='多头胜利次数'),
        sa.Column('bear_wins', sa.Integer(), nullable=True, comment='空头胜利次数'),
        sa.Column('holds', sa.Integer(), nullable=True, comment='持有次数'),
        sa.Column('avg_consensus', sa.Float(), nullable=True, comment='平均共识度'),
        sa.Column('avg_confidence', sa.Float(), nullable=True, comment='平均置信度'),
        sa.Column('avg_duration', sa.Float(), nullable=True, comment='平均辩论时长（秒）'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True, comment='创建时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='辩论统计表'
    )
    op.create_index(op.f('ix_debate_statistics_id'), 'debate_statistics', ['id'], unique=False)
    op.create_index(op.f('ix_debate_statistics_date'), 'debate_statistics', ['date'], unique=True)
    
    # 插入默认配置
    op.execute("""
        INSERT INTO debate_config (config_key, config_value, description) VALUES
        ('debate_enabled', 'true', '是否启用辩论机制'),
        ('max_debate_rounds', '1', '最大辩论轮次'),
        ('min_position_size', '1000', '触发辩论的最小仓位（USD）'),
        ('min_permission_level', 'L3', '触发辩论的最低权限等级'),
        ('debate_timeout_seconds', '60', '辩论超时时间（秒）'),
        ('use_memory', 'true', '是否使用历史记忆'),
        ('daily_limit', '100', '每日最大辩论次数'),
        ('hourly_limit', '10', '每小时最大辩论次数')
    """)


def downgrade() -> None:
    # 删除表（按相反顺序）
    op.drop_index('idx_debate_recommendation', table_name='debate_history')
    op.drop_index('idx_debate_symbol_created', table_name='debate_history')
    op.drop_index(op.f('ix_debate_history_symbol'), table_name='debate_history')
    op.drop_index(op.f('ix_debate_history_decision_id'), table_name='debate_history')
    op.drop_index(op.f('ix_debate_history_id'), table_name='debate_history')
    op.drop_table('debate_history')
    
    op.drop_index(op.f('ix_debate_statistics_date'), table_name='debate_statistics')
    op.drop_index(op.f('ix_debate_statistics_id'), table_name='debate_statistics')
    op.drop_table('debate_statistics')
    
    op.drop_index(op.f('ix_debate_config_config_key'), table_name='debate_config')
    op.drop_index(op.f('ix_debate_config_id'), table_name='debate_config')
    op.drop_table('debate_config')

