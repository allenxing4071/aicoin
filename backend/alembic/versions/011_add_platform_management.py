"""add platform management tables

Revision ID: 011
Revises: 010
Create Date: 2025-11-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===== 情报平台管理表 =====
    op.create_table(
        'intelligence_platforms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),  # 平台名称，如"百度智能云"
        sa.Column('provider', sa.String(), nullable=False),  # 提供商：baidu/tencent/volcano/aws
        sa.Column('platform_type', sa.String(), nullable=False),  # 类型：qwen_search/qwen_deep/free
        sa.Column('api_key', sa.String(), nullable=True),  # API密钥（加密存储）
        sa.Column('base_url', sa.String(), nullable=False),  # API基础URL
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),  # 是否启用
        sa.Column('config_json', postgresql.JSONB(), nullable=True),  # 额外配置（JSON）
        
        # 性能指标
        sa.Column('total_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('successful_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_response_time', sa.Float(), nullable=True),  # 平均响应时间（秒）
        sa.Column('total_cost', sa.Float(), nullable=False, server_default='0.0'),  # 累计成本
        
        # 时间戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_health_check', sa.DateTime(), nullable=True),
        sa.Column('health_status', sa.String(), nullable=True),  # healthy/unhealthy/unknown
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'platform_type', name='uix_provider_type')
    )
    op.create_index('ix_intelligence_platforms_enabled', 'intelligence_platforms', ['enabled'])
    op.create_index('ix_intelligence_platforms_provider', 'intelligence_platforms', ['provider'])
    
    # ===== 模型性能指标表 =====
    op.create_table(
        'model_performance_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),  # trained_70b/default_api
        sa.Column('metric_date', sa.Date(), nullable=False),  # 指标日期
        
        # 决策准确率指标
        sa.Column('total_decisions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('correct_decisions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('accuracy', sa.Float(), nullable=True),  # 决策准确率
        
        # 交易盈利指标
        sa.Column('total_trades', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('profitable_trades', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('profit_rate', sa.Float(), nullable=True),  # 盈利率
        sa.Column('total_pnl', sa.Float(), nullable=False, server_default='0.0'),  # 总盈亏
        sa.Column('avg_pnl_per_trade', sa.Float(), nullable=True),  # 平均每笔盈亏
        
        # 性能指标
        sa.Column('avg_response_time', sa.Float(), nullable=True),  # 平均响应时间（秒）
        sa.Column('avg_cost', sa.Float(), nullable=True),  # 平均成本
        
        # 风险指标
        sa.Column('max_loss', sa.Float(), nullable=True),  # 最大单次亏损
        sa.Column('win_loss_ratio', sa.Float(), nullable=True),  # 盈亏比
        
        # 时间戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_name', 'metric_date', name='uix_model_date')
    )
    op.create_index('ix_model_performance_model_name', 'model_performance_metrics', ['model_name'])
    op.create_index('ix_model_performance_metric_date', 'model_performance_metrics', ['metric_date'])
    
    # ===== 路由决策日志表 =====
    op.create_table(
        'routing_decisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('decision_id', sa.String(), nullable=False),  # 关联决策ID
        sa.Column('routing_strategy', sa.String(), nullable=False),  # 使用的路由策略
        sa.Column('model_used', sa.String(), nullable=False),  # 实际使用的模型
        sa.Column('models_called', postgresql.ARRAY(sa.String()), nullable=True),  # 调用的所有模型
        
        # 决策信息
        sa.Column('decision', sa.String(), nullable=True),  # BUY/SELL/HOLD
        sa.Column('confidence', sa.Float(), nullable=True),  # 置信度
        sa.Column('reasoning', sa.Text(), nullable=True),  # 推理过程
        
        # 路由信息
        sa.Column('why_this_strategy', sa.Text(), nullable=True),  # 为什么选择这个策略
        sa.Column('fallback_triggered', sa.Boolean(), nullable=False, server_default='false'),  # 是否触发降级
        sa.Column('routing_metadata', postgresql.JSONB(), nullable=True),  # 其他路由元数据
        
        # 性能数据
        sa.Column('response_time', sa.Float(), nullable=True),  # 响应时间（秒）
        sa.Column('cost', sa.Float(), nullable=True),  # 成本
        
        # 结果跟踪（后续更新）
        sa.Column('actual_result', sa.String(), nullable=True),  # 实际交易结果
        sa.Column('pnl', sa.Float(), nullable=True),  # 盈亏
        sa.Column('was_correct', sa.Boolean(), nullable=True),  # 决策是否正确
        
        # 时间戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('decision_id')
    )
    op.create_index('ix_routing_decisions_model_used', 'routing_decisions', ['model_used'])
    op.create_index('ix_routing_decisions_strategy', 'routing_decisions', ['routing_strategy'])
    op.create_index('ix_routing_decisions_created_at', 'routing_decisions', ['created_at'])


def downgrade() -> None:
    op.drop_table('routing_decisions')
    op.drop_table('model_performance_metrics')
    op.drop_table('intelligence_platforms')

