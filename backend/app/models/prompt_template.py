"""
Prompt模板系统数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, JSON, DateTime, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PromptTemplate(Base):
    """Prompt模板表"""
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="模板名称（如：default, l0_conservative）")
    category = Column(String(50), nullable=False, comment="类别（decision/debate/intelligence）")
    permission_level = Column(String(10), nullable=True, comment="权限等级（L0-L5，NULL表示通用）")
    content = Column(Text, nullable=False, comment="Prompt内容")
    version = Column(Integer, default=1, nullable=False, comment="版本号")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否为当前激活版本")
    created_by = Column(Integer, ForeignKey("admin_users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    versions = relationship("PromptTemplateVersion", back_populates="template", cascade="all, delete-orphan")
    performance_records = relationship("PromptPerformance", back_populates="template", cascade="all, delete-orphan")
    ab_tests = relationship("PromptABTest", foreign_keys="[PromptABTest.prompt_a_id, PromptABTest.prompt_b_id]")
    
    # 索引
    __table_args__ = (
        Index('idx_prompt_category_level', 'category', 'permission_level'),
        Index('idx_prompt_active', 'is_active'),
        {'comment': '🎯 Prompt模板 - 存储AI决策的思维规则，支持版本管理和权限等级'}
    )
    
    def __repr__(self):
        return f"<PromptTemplate(id={self.id}, name={self.name}, category={self.category}, level={self.permission_level}, v{self.version})>"


class PromptTemplateVersion(Base):
    """Prompt模板版本历史表"""
    __tablename__ = "prompt_template_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("prompt_templates.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False, comment="版本号")
    content = Column(Text, nullable=False, comment="Prompt内容")
    change_summary = Column(Text, comment="变更说明")
    created_by = Column(Integer, ForeignKey("admin_users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    template = relationship("PromptTemplate", back_populates="versions")
    
    # 索引
    __table_args__ = (
        Index('idx_version_template', 'template_id', 'version'),
        {'comment': '📚 Prompt版本历史 - 记录所有历史版本，支持回滚'}
    )
    
    def __repr__(self):
        return f"<PromptTemplateVersion(id={self.id}, template_id={self.template_id}, v{self.version})>"


class PromptPerformance(Base):
    """Prompt性能追踪表"""
    __tablename__ = "prompt_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=False)
    
    # 基础统计
    total_decisions = Column(Integer, default=0, comment="总决策次数")
    winning_decisions = Column(Integer, default=0, comment="盈利决策次数")
    losing_decisions = Column(Integer, default=0, comment="亏损决策次数")
    win_rate = Column(Numeric(5, 2), comment="胜率（0-1）")
    total_pnl = Column(Numeric(20, 8), default=0, comment="总盈亏（USD）")
    avg_pnl = Column(Numeric(20, 8), comment="平均盈亏（USD）")
    
    # 风险指标（量化师关键指标）
    sharpe_ratio = Column(Numeric(5, 2), comment="夏普比率")
    sortino_ratio = Column(Numeric(5, 2), comment="索提诺比率")
    max_drawdown = Column(Numeric(5, 2), comment="最大回撤（0-1）")
    calmar_ratio = Column(Numeric(5, 2), comment="卡玛比率")
    var_95 = Column(Numeric(10, 2), comment="95% VaR（风险价值）")
    cvar_95 = Column(Numeric(10, 2), comment="95% CVaR（条件风险价值）")
    
    # 市场环境分类
    market_regime = Column(String(50), comment="市场状态（high_volatility/low_volatility/normal）")
    
    # 元数据
    sample_count = Column(Integer, default=0, comment="样本数量")
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    template = relationship("PromptTemplate", back_populates="performance_records")
    
    # 索引
    __table_args__ = (
        Index('idx_performance_template', 'template_id'),
        Index('idx_performance_regime', 'template_id', 'market_regime'),
        Index('idx_performance_sharpe', 'sharpe_ratio'),
        {'comment': '📊 Prompt性能追踪 - 记录每个Prompt的交易表现和风险指标'}
    )
    
    def __repr__(self):
        return f"<PromptPerformance(id={self.id}, template_id={self.template_id}, win_rate={self.win_rate}, sharpe={self.sharpe_ratio})>"


class PromptABTest(Base):
    """Prompt A/B测试表"""
    __tablename__ = "prompt_ab_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String(200), nullable=False, unique=True, comment="测试名称")
    
    # 测试配置
    prompt_a_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=False, comment="对照组Prompt ID")
    prompt_b_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=False, comment="实验组Prompt ID")
    traffic_split = Column(Numeric(3, 2), default=0.5, comment="流量分配比例（0-1）")
    
    # 测试状态
    status = Column(String(20), default='RUNNING', comment="状态（RUNNING/COMPLETED/STOPPED）")
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_days = Column(Integer, default=7, comment="测试持续天数")
    
    # A组统计
    a_total_decisions = Column(Integer, default=0)
    a_winning_decisions = Column(Integer, default=0)
    a_win_rate = Column(Numeric(5, 2))
    a_total_pnl = Column(Numeric(20, 8), default=0)
    a_sharpe_ratio = Column(Numeric(5, 2))
    
    # B组统计
    b_total_decisions = Column(Integer, default=0)
    b_winning_decisions = Column(Integer, default=0)
    b_win_rate = Column(Numeric(5, 2))
    b_total_pnl = Column(Numeric(20, 8), default=0)
    b_sharpe_ratio = Column(Numeric(5, 2))
    
    # 统计显著性检验
    p_value = Column(Numeric(10, 8), comment="p值（卡方检验）")
    is_significant = Column(Boolean, default=False, comment="是否统计显著（p<0.05）")
    winner = Column(String(1), comment="获胜者（A/B/DRAW）")
    
    # 结论
    conclusion = Column(Text, comment="测试结论")
    created_by = Column(Integer, ForeignKey("admin_users.id"))
    
    # 索引
    __table_args__ = (
        Index('idx_ab_test_status', 'status'),
        Index('idx_ab_test_prompts', 'prompt_a_id', 'prompt_b_id'),
        {'comment': '🧪 Prompt A/B测试 - 科学验证Prompt优化效果，确保统计显著性'}
    )
    
    def __repr__(self):
        return f"<PromptABTest(id={self.id}, name={self.test_name}, status={self.status}, winner={self.winner})>"

