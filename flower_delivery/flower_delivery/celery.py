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
        'schedule': crontab(hour=18, minute=0),  # Запуск в 18:00 каждый день
    },
}