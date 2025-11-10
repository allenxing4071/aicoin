"""add ai cost management tables

Revision ID: 012
Revises: 011
Create Date: 2025-11-08 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    # 创建AI模型定价表
    op.create_table(
        'ai_model_pricing',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('model_name', sa.String(length=100), nullable=False, comment='模型名称'),
        sa.Column('provider', sa.String(length=50), nullable=False, comment='提供商'),
        sa.Column('display_name', sa.String(length=100), nullable=False, comment='显示名称'),
        sa.Column('model_type', sa.String(length=50), nullable=False, comment='模型类型'),
        sa.Column('input_price_per_million', sa.Float(), nullable=False, server_default='0.0', comment='输入token价格'),
        sa.Column('output_price_per_million', sa.Float(), nullable=False, server_default='0.0', comment='输出token价格'),
        sa.Column('total_calls', sa.Integer(), server_default='0', comment='总调用次数'),
        sa.Column('total_input_tokens', sa.Integer(), server_default='0', comment='总输入tokens'),
        sa.Column('total_output_tokens', sa.Integer(), server_default='0', comment='总输出tokens'),
        sa.Column('total_cost', sa.Float(), server_default='0.0', comment='总花费'),
        sa.Column('monthly_budget', sa.Float(), server_default='0.0', comment='月度预算'),
        sa.Column('current_month_cost', sa.Float(), server_default='0.0', comment='当月花费'),
        sa.Column('alert_threshold', sa.Float(), server_default='0.8', comment='告警阈值'),
        sa.Column('enabled', sa.Boolean(), server_default='true', comment='是否启用'),
        sa.Column('is_free', sa.Boolean(), server_default='false', comment='是否免费'),
        sa.Column('description', sa.Text(), comment='描述'),
        sa.Column('notes', sa.Text(), comment='备注'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), comment='更新时间'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), comment='最后使用时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='AI模型定价配置'
    )
    op.create_index('ix_ai_model_pricing_id', 'ai_model_pricing', ['id'])
    op.create_index('ix_ai_model_pricing_model_name', 'ai_model_pricing', ['model_name'], unique=True)
    
    # 创建AI模型使用日志表
    op.create_table(
        'ai_model_usage_log',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('model_name', sa.String(length=100), nullable=False, comment='模型名称'),
        sa.Column('request_id', sa.String(length=100), comment='请求ID'),
        sa.Column('input_tokens', sa.Integer(), nullable=False, comment='输入tokens'),
        sa.Column('output_tokens', sa.Integer(), nullable=False, comment='输出tokens'),
        sa.Column('cost', sa.Float(), nullable=False, comment='花费'),
        sa.Column('response_time', sa.Float(), comment='响应时间'),
        sa.Column('success', sa.Boolean(), server_default='true', comment='是否成功'),
        sa.Column('error_message', sa.Text(), comment='错误信息'),
        sa.Column('purpose', sa.String(length=100), comment='调用目的'),
        sa.Column('symbol', sa.String(length=20), comment='交易对'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), comment='创建时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='AI模型使用日志'
    )
    op.create_index('ix_ai_model_usage_log_id', 'ai_model_usage_log', ['id'])
    op.create_index('ix_ai_model_usage_log_model_name', 'ai_model_usage_log', ['model_name'])
    op.create_index('ix_ai_model_usage_log_request_id', 'ai_model_usage_log', ['request_id'])
    op.create_index('ix_ai_model_usage_log_created_at', 'ai_model_usage_log', ['created_at'])
    
    # 创建AI预算告警表
    op.create_table(
        'ai_budget_alerts',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('model_name', sa.String(length=100), nullable=False, comment='模型名称'),
        sa.Column('alert_type', sa.String(length=50), nullable=False, comment='告警类型'),
        sa.Column('alert_level', sa.String(length=20), nullable=False, comment='告警级别'),
        sa.Column('current_cost', sa.Float(), nullable=False, comment='当前花费'),
        sa.Column('budget_limit', sa.Float(), nullable=False, comment='预算限制'),
        sa.Column('usage_percentage', sa.Float(), nullable=False, comment='使用百分比'),
        sa.Column('message', sa.Text(), nullable=False, comment='告警消息'),
        sa.Column('is_resolved', sa.Boolean(), server_default='false', comment='是否已解决'),
        sa.Column('resolved_at', sa.DateTime(timezone=True), comment='解决时间'),
        sa.Column('resolved_by', sa.String(length=100), comment='解决人'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), comment='创建时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='AI预算告警记录'
    )
    op.create_index('ix_ai_budget_alerts_id', 'ai_budget_alerts', ['id'])
    op.create_index('ix_ai_budget_alerts_model_name', 'ai_budget_alerts', ['model_name'])
    op.create_index('ix_ai_budget_alerts_created_at', 'ai_budget_alerts', ['created_at'])
    
    # 插入初始模型定价数据
    op.execute("""
        INSERT INTO ai_model_pricing 
        (model_name, provider, display_name, model_type, input_price_per_million, output_price_per_million, is_free, description, enabled)
        VALUES 
        -- DeepSeek系列
        ('deepseek-chat', 'deepseek', 'DeepSeek Chat', 'decision', 1.0, 2.0, false, 'DeepSeek标准对话模型，用于AI交易决策', true),
        ('deepseek-reasoner', 'deepseek', 'DeepSeek Reasoner', 'decision', 4.0, 16.0, false, 'DeepSeek推理模型，深度思考能力', true),
        
        -- Qwen系列
        ('qwen-plus', 'qwen', 'Qwen-Plus', 'intelligence', 4.0, 12.0, false, '通义千问Plus，用于情报分析', true),
        ('qwen-turbo', 'qwen', 'Qwen-Turbo', 'intelligence', 2.0, 6.0, false, '通义千问Turbo，快速响应', true),
        ('qwen-max', 'qwen', 'Qwen-Max', 'intelligence', 40.0, 120.0, false, '通义千问Max，最强性能', true),
        
        -- OpenAI系列
        ('gpt-4o', 'openai', 'GPT-4o', 'analysis', 15.0, 60.0, false, 'OpenAI GPT-4o，多模态能力', true),
        ('gpt-4o-mini', 'openai', 'GPT-4o Mini', 'analysis', 1.05, 4.2, false, 'OpenAI GPT-4o Mini，性价比高', true),
        
        -- Claude系列
        ('claude-3.5-sonnet', 'anthropic', 'Claude 3.5 Sonnet', 'analysis', 21.0, 105.0, false, 'Anthropic Claude 3.5 Sonnet，强大推理', true),
        
        -- Groq (免费)
        ('groq-llama', 'groq', 'Groq Llama', 'intelligence', 0.0, 0.0, true, 'Groq免费模型，快速监控', true)
    """)


def downgrade():
    op.drop_index('ix_ai_budget_alerts_created_at', table_name='ai_budget_alerts')
    op.drop_index('ix_ai_budget_alerts_model_name', table_name='ai_budget_alerts')
    op.drop_index('ix_ai_budget_alerts_id', table_name='ai_budget_alerts')
    op.drop_table('ai_budget_alerts')
    
    op.drop_index('ix_ai_model_usage_log_created_at', table_name='ai_model_usage_log')
    op.drop_index('ix_ai_model_usage_log_request_id', table_name='ai_model_usage_log')
    op.drop_index('ix_ai_model_usage_log_model_name', table_name='ai_model_usage_log')
    op.drop_index('ix_ai_model_usage_log_id', table_name='ai_model_usage_log')
    op.drop_table('ai_model_usage_log')
    
    op.drop_index('ix_ai_model_pricing_model_name', table_name='ai_model_pricing')
    op.drop_index('ix_ai_model_pricing_id', table_name='ai_model_pricing')
    op.drop_table('ai_model_pricing')

