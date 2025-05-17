import logging
import asyncio
from typing import List, Optional
import pytz
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from django.conf import settings
from django.utils import timezone
from asgiref.sync import sync_to_async

# Models
from orders.models import Order, OrderItem
from analytics.models import DailyReport

logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# ====== Утилиты ======
@sync_to_async
def _get_order_details(order: Order) -> tuple:
    """Получение деталей заказа из БД"""
    items = list(OrderItem.objects.filter(order=order).select_related('product'))
    return (
        timezone.localtime(order.created_at, MOSCOW_TZ),
        timezone.localtime(order.delivery_time, MOSCOW_TZ),
        items
    )

@sync_to_async
def _get_product_images(order: Order) -> List[str]:
    """Получение путей к изображениям товаров"""
    return [
        item.product.image.path
        for item in OrderItem.objects.filter(order=order).select_related('product')
        if item.product.image
    ]

# ====== Форматирование сообщений ======
async def _format_order_header(order: Order, is_new: bool) -> str:
    created_at, delivery_time, _ = await _get_order_details(order)
    if is_new:
        return (
            "🌸 *НОВЫЙ ЗАКАЗ ЦВЕТОВ* 🌸\n"
            "📦 *Детали заказа:*\n"
            f"🆔 *Номер:* {order.id}\n"
            f"📅 *Дата:* {created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"⏰ *Доставка:* {delivery_time.strftime('%d.%m.%Y %H:%M')}\n"
            f"📍 *Адрес:* {order.delivery_address}\n"
            f"💬 *Комментарий:* {order.comment or 'отсутствует'}\n"
        )
    else:
        return (
            "🌸 *ИЗМЕНЕНИЕ СТАТУСА ЗАКАЗА* 🌸\n"
            "📦 *Детали заказа:*\n"
            f"🆔 *Номер:* {order.id}\n"
            f"📅 *Дата:* {created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"⏰ *Доставка:* {delivery_time.strftime('%d.%m.%Y %H:%M')}\n"
            f"📍 *Адрес:* {order.delivery_address}\n"
            f"💬 *Комментарий:* {order.comment or 'отсутствует'}\n"
        )

async def _format_order_items(order: Order) -> str:
    _, _, items = await _get_order_details(order)
    items_text = "\n".join(
        f"➖ {item.product.name} ({item.quantity} шт.) - {item.price:.2f}₽"
        for item in items
    )
    return f"*Состав заказа:*\n{items_text}\n"

async def _format_order_footer(order: Order) -> str:
    # Используем sync_to_async для доступа к свойству total_price
    total_price = await sync_to_async(lambda: order.total_price)()
    if order.status == 'new':
        return (
            f"💰 *ИТОГО:* {total_price:.2f}₽\n"
            f"📦 *Статус заказа:* {order.get_status_display()}\n"
        )
    else:
        return (
            f"💰 *ИТОГО:* {total_price:.2f}₽\n"
            f"📦 *Новый статус заказа:* {order.get_status_display()}\n"
        )

# ====== Основные функции ======
async def _send_telegram_message(text: str) -> None:
    """Отправка текстового сообщения"""
    try:
        await bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=text,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {str(e)}", exc_info=True)

async def _send_telegram_photo(image_path: str, caption: str = "") -> None:
    """Отправка изображения"""
    try:
        photo = FSInputFile(image_path)
        await bot.send_photo(
            chat_id=settings.TELEGRAM_CHAT_ID,
            photo=photo,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Ошибка отправки изображения: {str(e)}", exc_info=True)

# ====== Публичные методы ======
async def handle_order_notification(order: Order, is_new: bool = True) -> None:
    """Обработка уведомления о заказе"""
    try:
        header = await _format_order_header(order, is_new)
        items = await _format_order_items(order)
        footer = await _format_order_footer(order)
        message = header + items + footer

        await _send_telegram_message(message)

        image_paths = await _get_product_images(order)
        for path in image_paths:
            await _send_telegram_photo(path, f"📸 Товар из заказа №{order.id}")

    except Exception as e:
        logger.error(f"Ошибка обработки заказа {order.id}: {str(e)}", exc_info=True)
    finally:
        await bot.session.close()

async def send_daily_report() -> None:
    """Отправка ежедневного отчета"""
    try:
        today = timezone.now().date()
        report = await sync_to_async(DailyReport.objects.filter(date=today).first)()

        if not report:
            logger.warning("Отчет за сегодня не найден")
            return

        message = (
            "📊 *Ежедневный отчет*\n"
            f"📅 {report.date.strftime('%d %B %Y')}\n"
            f"📦 Заказов: {report.order_count}\n"
            f"💰 Выручка: {report.total_revenue:.2f}₽\n"
        )

        if report.order_count > 0:
            avg = report.total_revenue / report.order_count
            message += f"🏆 Средний чек: {avg:.2f}₽"

        await _send_telegram_message(message)
        logger.info("Ежедневный отчет успешно отправлен")

    except Exception as e:
        logger.error(f"Ошибка отправки ежедневного отчета: {str(e)}", exc_info=True)
    finally:
        await bot.session.close()

# ====== Синхронные обертки для Celery ======
def send_order_notification(order_pk: int, is_new: bool = True) -> None:
    """Синхронная обертка для уведомлений"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        order = Order.objects.get(pk=order_pk)
        loop.run_until_complete(handle_order_notification(order, is_new))
    except Order.DoesNotExist:
        logger.error(f"Заказ с pk={order_pk} не найден")
    except Exception as e:
        logger.error(f"Ошибка в задаче отправки уведомления: {str(e)}", exc_info=True)
    finally:
        loop.close()

def trigger_daily_report() -> None:
    """Синхронная обертка для ежедневного отчета"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_daily_report())
    except Exception as e:
        logger.error(f"Ошибка в задаче ежедневного отчета: {str(e)}", exc_info=True)
    finally:
        loop.close()
