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
        'app.tasks.intelligence_learning',  # 情报学习和辩论任务
        'app.tasks.prompt_tasks',  # Prompt相关任务
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
    # Auto-generate debate report - every 4 hours
    'auto-generate-debate-report': {
        'task': 'app.tasks.intelligence_learning.auto_generate_debate_report',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours (0:00, 4:00, 8:00, 12:00, 16:00, 20:00)
        'options': {'expires': 3600},  # Expire after 1 hour
    },
}


if __name__ == '__main__':
    celery_app.start()

