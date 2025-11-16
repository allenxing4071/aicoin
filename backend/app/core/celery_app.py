"""Celery application configuration"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    'aicoin',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.trading_loop',
        'app.tasks.data_collector',
        'app.tasks.metrics_calculator',
        'app.tasks.intelligence_learning'  # 新增：情报学习和辩论任务
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Trading decision loop - every 5-15 minutes (configurable)
    'trading-decision-loop': {
        'task': 'app.tasks.trading_loop.execute_trading_decision',
        'schedule': float(settings.DECISION_INTERVAL),  # seconds
        'options': {'expires': 60},
    },
    
    # Market data collection - every 1 minute
    'collect-market-data': {
        'task': 'app.tasks.data_collector.collect_market_data',
        'schedule': 60.0,  # 1 minute
        'options': {'expires': 30},
    },
    
    # Account snapshot - every 5 minutes
    'collect-account-snapshot': {
        'task': 'app.tasks.data_collector.collect_account_snapshot',
        'schedule': 300.0,  # 5 minutes
        'options': {'expires': 60},
    },
    
    # Performance metrics calculation - every 1 hour
    'calculate-performance-metrics': {
        'task': 'app.tasks.metrics_calculator.calculate_performance_metrics',
        'schedule': 3600.0,  # 1 hour
        'options': {'expires': 600},
    },
    
    # Auto-generate debate report - every 4 hours
    'auto-generate-debate-report': {
        'task': 'app.tasks.intelligence_learning.auto_generate_debate_report',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
        'options': {'expires': 3600},  # Expire after 1 hour
    },
}


if __name__ == '__main__':
    celery_app.start()

