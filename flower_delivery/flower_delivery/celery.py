import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')

app = Celery('flower_delivery')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-daily-report': {
        'task': 'analytics.tasks.send_daily_report_task',
        'schedule': crontab(hour=0, minute=50),  # Каждый день в 18:00
    },
}

app.conf.task_routes = {
    'analytics.tasks.send_daily_report_task': {'queue': 'analytics'},
}

app.conf.worker_prefetch_multiplier = 1
app.conf.worker_max_tasks_per_child = 1

# Настройка для Windows
app.conf.broker_pool_limit = 1
app.conf.worker_pool = 'solo'
