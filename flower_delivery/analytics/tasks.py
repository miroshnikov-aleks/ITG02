import logging
from celery import shared_task
from asgiref.sync import async_to_sync
from bot.telegram import run_send_daily_report
from analytics.models import DailyReport
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task
def send_daily_report_task():
    """
    Задача Celery для отправки ежедневного отчёта через Telegram.
    """
    logger.info("Задача send_daily_report_task выполняется")
    try:
        run_send_daily_report()
    except Exception as e:
        logger.error(f"Ошибка при отправке ежедневного отчёта: {e}", exc_info=True)

@shared_task
def test_task():
    """
    Тестовая задача для проверки работы Celery.
    """
    logger.info("Тестовая задача выполняется")
    print("Test task executed")
