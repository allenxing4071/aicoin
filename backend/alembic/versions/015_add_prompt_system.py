"""add prompt template system with quantitative analysis

Revision ID: 015
Revises: 014
Create Date: 2025-11-15 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade():
    # ===== 1. Prompt模板表 =====
    op.create_table(
        'prompt_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='模板名称（如：default, l0_conservative）'),
        sa.Column('category', sa.String(length=50), nullable=False, comment='类别（decision/debate/intelligence）'),
        sa.Column('permission_level', sa.String(length=10), nullable=True, comment='权限等级（L0-L5，NULL表示通用）'),
        sa.Column('content', sa.Text(), nullable=False, comment='Prompt内容'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1', comment='版本号'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否为当前激活版本'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='创建人ID'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        comment='🎯 Prompt模板 - 存储AI决策的思维规则，支持版本管理和权限等级'
    )
    op.create_index('idx_prompt_category_level', 'prompt_templates', ['category', 'permission_level'], unique=False)
    op.create_index('idx_prompt_active', 'prompt_templates', ['is_active'], unique=False)
    op.create_index(op.f('ix_prompt_templates_id'), 'prompt_templates', ['id'], unique=False)
    
    # ===== 2. Prompt版本历史表 =====
    op.create_table(
        'prompt_template_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, comment='版本号'),
        sa.Column('content', sa.Text(), nullable=False, comment='Prompt内容'),
        sa.Column('change_summary', sa.Text(), nullable=True, comment='变更说明'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='创建人ID'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['prompt_templates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='📚 Prompt版本历史 - 记录所有历史版本，支持回滚'
    )
    op.create_index('idx_version_template', 'prompt_template_versions', ['template_id', 'version'], unique=False)
    op.create_index(op.f('ix_prompt_template_versions_id'), 'prompt_template_versions', ['id'], unique=False)
    
    # ===== 3. Prompt性能追踪表 =====
    op.create_table(
        'prompt_performance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        # 基础统计
        sa.Column('total_decisions', sa.Integer(), server_default='0', comment='总决策次数'),
        sa.Column('winning_decisions', sa.Integer(), server_default='0', comment='盈利决策次数'),
        sa.Column('losing_decisions', sa.Integer(), server_default='0', comment='亏损决策次数'),
        sa.Column('win_rate', sa.Numeric(precision=5, scale=2), nullable=True, comment='胜率（0-1）'),
        sa.Column('total_pnl', sa.Numeric(precision=20, scale=8), server_default='0', comment='总盈亏（USD）'),
        sa.Column('avg_pnl', sa.Numeric(precision=20, scale=8), nullable=True, comment='平均盈亏（USD）'),
        # 风险指标（量化师关键指标）
        sa.Column('sharpe_ratio', sa.Numeric(precision=5, scale=2), nullable=True, comment='夏普比率'),
        sa.Column('sortino_ratio', sa.Numeric(precision=5, scale=2), nullable=True, comment='索提诺比率'),
        sa.Column('max_drawdown', sa.Numeric(precision=5, scale=2), nullable=True, comment='最大回撤（0-1）'),
        sa.Column('calmar_ratio', sa.Numeric(precision=5, scale=2), nullable=True, comment='卡玛比率'),
        sa.Column('var_95', sa.Numeric(precision=10, scale=2), nullable=True, comment='95% VaR（风险价值）'),
        sa.Column('cvar_95', sa.Numeric(precision=10, scale=2), nullable=True, comment='95% CVaR（条件风险价值）'),
        # 市场环境分类
        sa.Column('market_regime', sa.String(length=50), nullable=True, comment='市场状态（high_volatility/low_volatility/normal）'),
        # 元数据
        sa.Column('sample_count', sa.Integer(), server_default='0', comment='样本数量'),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['template_id'], ['prompt_templates.id'], ),
        sa.PrimaryKeyConstraint('id'),
        comment='📊 Prompt性能追踪 - 记录每个Prompt的交易表现和风险指标'
    )
    op.create_index('idx_performance_template', 'prompt_performance', ['template_id'], unique=False)
    op.create_index('idx_performance_regime', 'prompt_performance', ['template_id', 'market_regime'], unique=False)
    op.create_index('idx_performance_sharpe', 'prompt_performance', ['sharpe_ratio'], unique=False)
    op.create_index(op.f('ix_prompt_performance_id'), 'prompt_performance', ['id'], unique=False)
    
    # ===== 4. Prompt A/B测试表 =====
    op.create_table(
        'prompt_ab_tests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_name', sa.String(length=200), nullable=False, comment='测试名称'),
        # 测试配置
        sa.Column('prompt_a_id', sa.Integer(), nullable=False, comment='对照组Prompt ID'),
        sa.Column('prompt_b_id', sa.Integer(), nullable=False, comment='实验组Prompt ID'),
        sa.Column('traffic_split', sa.Numeric(precision=3, scale=2), server_default='0.5', comment='流量分配比例（0-1）'),
        # 测试状态
        sa.Column('status', sa.String(length=20), server_default='RUNNING', comment='状态（RUNNING/COMPLETED/STOPPED）'),
        sa.Column('start_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_days', sa.Integer(), server_default='7', comment='测试持续天数'),
        # A组统计
        sa.Column('a_total_decisions', sa.Integer(), server_default='0'),
        sa.Column('a_winning_decisions', sa.Integer(), server_default='0'),
        sa.Column('a_win_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('a_total_pnl', sa.Numeric(precision=20, scale=8), server_default='0'),
        sa.Column('a_sharpe_ratio', sa.Numeric(precision=5, scale=2), nullable=True),
        # B组统计
        sa.Column('b_total_decisions', sa.Integer(), server_default='0'),
        sa.Column('b_winning_decisions', sa.Integer(), server_default='0'),
        sa.Column('b_win_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('b_total_pnl', sa.Numeric(precision=20, scale=8), server_default='0'),
        sa.Column('b_sharpe_ratio', sa.Numeric(precision=5, scale=2), nullable=True),
        # 统计显著性检验
        sa.Column('p_value', sa.Numeric(precision=10, scale=8), nullable=True, comment='p值（卡方检验）'),
        sa.Column('is_significant', sa.Boolean(), server_default='false', comment='是否统计显著（p<0.05）'),
        sa.Column('winner', sa.String(length=1), nullable=True, comment='获胜者（A/B/DRAW）'),
        # 结论
        sa.Column('conclusion', sa.Text(), nullable=True, comment='测试结论'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], ),
        sa.ForeignKeyConstraint(['prompt_a_id'], ['prompt_templates.id'], ),
        sa.ForeignKeyConstraint(['prompt_b_id'], ['prompt_templates.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('test_name'),
        comment='🧪 Prompt A/B测试 - 科学验证Prompt优化效果，确保统计显著性'
    )
    op.create_index('idx_ab_test_status', 'prompt_ab_tests', ['status'], unique=False)
    op.create_index('idx_ab_test_prompts', 'prompt_ab_tests', ['prompt_a_id', 'prompt_b_id'], unique=False)
    op.create_index(op.f('ix_prompt_ab_tests_id'), 'prompt_ab_tests', ['id'], unique=False)


def downgrade():
    # 删除表（逆序）
    op.drop_index(op.f('ix_prompt_ab_tests_id'), table_name='prompt_ab_tests')
    op.drop_index('idx_ab_test_prompts', table_name='prompt_ab_tests')
    op.drop_index('idx_ab_test_status', table_name='prompt_ab_tests')
    op.drop_table('prompt_ab_tests')
    
    op.drop_index(op.f('ix_prompt_performance_id'), table_name='prompt_performance')
    op.drop_index('idx_performance_sharpe', table_name='prompt_performance')
    op.drop_index('idx_performance_regime', table_name='prompt_performance')
    op.drop_index('idx_performance_template', table_name='prompt_performance')
    op.drop_table('prompt_performance')
    
    op.drop_index(op.f('ix_prompt_template_versions_id'), table_name='prompt_template_versions')
    op.drop_index('idx_version_template', table_name='prompt_template_versions')
    op.drop_table('prompt_template_versions')
    
    op.drop_index(op.f('ix_prompt_templates_id'), table_name='prompt_templates')
    op.drop_index('idx_prompt_active', table_name='prompt_templates')
    op.drop_index('idx_prompt_category_level', table_name='prompt_templates')
    op.drop_table('prompt_templates')

