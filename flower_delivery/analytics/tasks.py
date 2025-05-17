import logging
from celery import shared_task
from .models import DailyReport
from django.utils import timezone
from bot.telegram import trigger_daily_report

logger = logging.getLogger(__name__)

@shared_task
def send_daily_report_task():
    """
    Задача Celery для отправки ежедневного отчёта через Telegram.
    """
    logger.info("Запуск задачи ежедневного отчета...")
    try:
        today = timezone.now().date()
        report, created = DailyReport.objects.get_or_create(date=today)

        if created:
            report.order_count = 0
            report.total_revenue = 0.00
            report.save()

        trigger_daily_report()
    except Exception as e:
        logger.error(f"Ошибка в задаче ежедневного отчета: {e}", exc_info=True)

@shared_task
def test_task():
    """Тестовая задача для проверки работы Celery"""
    logger.info("Тестовая задача выполняется")
