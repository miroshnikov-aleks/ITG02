from celery import shared_task
from .tasks import send_daily_report_task

@shared_task
def send_daily_report_scheduled():
    send_daily_report_task()