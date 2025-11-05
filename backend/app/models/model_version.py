"""Model Version Model - DeepSeek模型版本管理"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class ModelVersion(Base):
    """
    模型版本表
    
    用于管理DeepSeek模型的不同训练版本
    """
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version_name = Column(String(100), nullable=False, unique=True, index=True)
    base_model = Column(String(100))  # deepseek-chat, deepseek-67b等
    
    # 训练信息
    training_platform = Column(String(50))  # baidu_xinhai/ali_pai/aws_sagemaker
    training_job_id = Column(String(200))  # 云平台的任务ID
    training_data_range = Column(JSON)  # {"start_date": "...", "end_date": "..."}
    training_samples_count = Column(Integer)
    
    # 超参数
    hyperparameters = Column(JSON)  # {"lora_rank": 8, "learning_rate": 1e-4, ...}
    
    # 评估指标
    evaluation_metrics = Column(JSON)  # {"accuracy": 0.85, "win_rate": 0.65, ...}
    
    # 状态
    status = Column(String(50), default="training")  # training/completed/failed/deployed
    deployed = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<ModelVersion(name={self.version_name}, status={self.status})>"


class TrainingJob(Base):
    """
    训练任务表
    
    记录每次模型训练任务的详细信息
    """
    __tablename__ = "training_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(200), nullable=False, unique=True, index=True)
    model_version_id = Column(Integer, nullable=True)  # 外键到model_versions
    
    # 训练配置
    platform = Column(String(50), nullable=False)
    instance_type = Column(String(100))  # A100x4, H100x8等
    training_type = Column(String(50))  # lora/qlora/full_param
    
    # 数据集信息
    dataset_path = Column(String(500))
    dataset_size = Column(Integer)
    
    # 训练参数
    config = Column(JSON)  # 完整的训练配置
    
    # 进度
    status = Column(String(50), default="pending")  # pending/running/completed/failed
    progress_percentage = Column(Integer, default=0)
    current_epoch = Column(Integer, default=0)
    total_epochs = Column(Integer)
    
    # 日志和结果
    logs_path = Column(String(500))
    checkpoint_path = Column(String(500))
    final_metrics = Column(JSON)
    
    # 成本
    estimated_cost = Column(Integer)  # 预估成本（美元）
    actual_cost = Column(Integer)  # 实际成本
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<TrainingJob(job_id={self.job_id}, status={self.status})>"

