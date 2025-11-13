"""
AI模型定价和余额管理模型
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AIModelPricing(Base):
    """AI模型定价配置表"""
    __tablename__ = "ai_model_pricing"
    __table_args__ = {'comment': '💵 AI模型定价配置，记录各个模型的费用标准'}
    
    id = Column(Integer, primary_key=True, index=True, comment="💵 主键ID")
    
    # 模型基本信息
    model_name = Column(String(100), unique=True, nullable=False, index=True, comment="💵 模型名称，如deepseek-chat")
    provider = Column(String(50), nullable=False, comment="💵 提供商，如deepseek、qwen、openai")
    display_name = Column(String(100), nullable=False, comment="💵 显示名称，如DeepSeek Chat")
    model_type = Column(String(50), nullable=False, comment="💵 模型类型：decision(决策)、intelligence(情报)、analysis(分析)")
    
    # 定价信息（单位：人民币/百万tokens）
    input_price_per_million = Column(Float, nullable=False, default=0.0, comment="💵 输入token价格（元/百万tokens）")
    output_price_per_million = Column(Float, nullable=False, default=0.0, comment="💵 输出token价格（元/百万tokens）")
    
    # 使用统计
    total_calls = Column(Integer, default=0, comment="💵 总调用次数")
    total_input_tokens = Column(Integer, default=0, comment="💵 总输入tokens")
    total_output_tokens = Column(Integer, default=0, comment="💵 总输出tokens")
    total_cost = Column(Float, default=0.0, comment="💵 总花费（元）")
    
    # 余额和限制
    monthly_budget = Column(Float, default=0.0, comment="💵 月度预算（元），0表示无限制")
    current_month_cost = Column(Float, default=0.0, comment="💵 当月已花费（元）")
    alert_threshold = Column(Float, default=0.8, comment="💵 告警阈值（0-1），超过预算的百分比时告警")
    
    # 状态
    enabled = Column(Boolean, default=True, comment="💵 是否启用")
    is_free = Column(Boolean, default=False, comment="💵 是否免费模型")
    
    # 备注
    description = Column(Text, comment="💵 模型描述")
    notes = Column(Text, comment="💵 备注信息")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="💵 创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="💵 更新时间")
    last_used_at = Column(DateTime(timezone=True), comment="💵 最后使用时间")
    
    def __repr__(self):
        return f"<AIModelPricing(model={self.model_name}, cost={self.total_cost:.2f}元)>"
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """计算单次调用成本"""
        input_cost = (input_tokens / 1_000_000) * self.input_price_per_million
        output_cost = (output_tokens / 1_000_000) * self.output_price_per_million
        return input_cost + output_cost
    
    def is_budget_exceeded(self) -> bool:
        """检查是否超出预算"""
        if self.monthly_budget <= 0:
            return False
        return self.current_month_cost >= self.monthly_budget
    
    def should_alert(self) -> bool:
        """检查是否应该告警"""
        if self.monthly_budget <= 0:
            return False
        return self.current_month_cost >= (self.monthly_budget * self.alert_threshold)
    
    def remaining_budget(self) -> float:
        """剩余预算"""
        if self.monthly_budget <= 0:
            return float('inf')
        return max(0, self.monthly_budget - self.current_month_cost)


class AIModelUsageLog(Base):
    """AI模型使用日志表"""
    __tablename__ = "ai_model_usage_log"
    __table_args__ = {'comment': '💵 AI模型使用日志，记录每次调用的详细信息'}
    
    id = Column(Integer, primary_key=True, index=True, comment="💵 主键ID")
    
    # 关联信息
    model_name = Column(String(100), nullable=False, index=True, comment="💵 模型名称")
    decision_id = Column(String(100), index=True, comment="💵 决策ID，用于追踪")  # 对应实际表的decision_id
    user_id = Column(Integer, comment="💵 用户ID")  # 对应实际表的user_id
    
    # 使用信息（使用实际表的字段名）
    prompt_tokens = Column(Integer, nullable=False, default=0, comment="💵 输入tokens数量")  # 实际表字段名
    completion_tokens = Column(Integer, nullable=False, default=0, comment="💵 输出tokens数量")  # 实际表字段名
    cost = Column(Float, nullable=False, comment="💵 本次花费（元）")
    
    # 性能信息
    response_time = Column(Float, comment="💵 响应时间（秒）")
    success = Column(Boolean, default=True, comment="💵 是否成功")
    error_message = Column(Text, comment="💵 错误信息")
    
    # 上下文信息
    purpose = Column(String(100), comment="💵 调用目的：decision、intelligence、analysis等")
    
    # 时间戳（使用实际表的字段名）
    timestamp = Column(DateTime, server_default=func.now(), index=True, comment="💵 创建时间")  # 实际表字段名
    
    # 添加属性别名以保持代码兼容性
    @property
    def input_tokens(self):
        return self.prompt_tokens
    
    @input_tokens.setter  
    def input_tokens(self, value):
        self.prompt_tokens = value
    
    @property
    def output_tokens(self):
        return self.completion_tokens
    
    @output_tokens.setter
    def output_tokens(self, value):
        self.completion_tokens = value
    
    @property
    def created_at(self):
        return self.timestamp
    
    @created_at.setter
    def created_at(self, value):
        self.timestamp = value
    
    def __repr__(self):
        return f"<AIModelUsageLog(model={self.model_name}, cost={self.cost:.4f}元)>"


class AIBudgetAlert(Base):
    """AI预算告警记录表"""
    __tablename__ = "ai_budget_alerts"
    __table_args__ = {'comment': '💵 AI预算告警记录'}
    
    id = Column(Integer, primary_key=True, index=True, comment="💵 主键ID")
    
    # 告警信息
    model_name = Column(String(100), nullable=False, index=True, comment="💵 模型名称")
    alert_type = Column(String(50), nullable=False, comment="💵 告警类型：threshold、exceeded、daily_limit")
    alert_level = Column(String(20), nullable=False, comment="💵 告警级别：warning、critical")
    
    # 详细信息
    current_cost = Column(Float, nullable=False, comment="💵 当前花费")
    budget_limit = Column(Float, nullable=False, comment="💵 预算限制")
    usage_percentage = Column(Float, nullable=False, comment="💵 使用百分比")
    
    message = Column(Text, nullable=False, comment="💵 告警消息")
    
    # 处理状态
    is_resolved = Column(Boolean, default=False, comment="💵 是否已解决")
    resolved_at = Column(DateTime(timezone=True), comment="💵 解决时间")
    resolved_by = Column(String(100), comment="💵 解决人")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, comment="💵 创建时间")
    
    def __repr__(self):
        return f"<AIBudgetAlert(model={self.model_name}, type={self.alert_type})>"

