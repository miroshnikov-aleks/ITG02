import logging
import asyncio
import pytz
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InputFile
from django.conf import settings
from django.utils import timezone
from asgiref.sync import sync_to_async, async_to_sync
from orders.models import OrderItem
from analytics.models import DailyReport

logger = logging.getLogger(__name__)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

async def async_send_telegram_notification(order, is_new_order=True):
    try:
        if is_new_order:
            message_text = await generate_new_order_message(order)
        else:
            message_text = await generate_status_change_message(order)

        photo_paths = await get_all_product_images(order)

        await bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=message_text,
            parse_mode=ParseMode.HTML
        )

        for photo_path in photo_paths:
            photo = FSInputFile(photo_path) if not photo_path.startswith('http') else InputFile.from_url(photo_path)
            await bot.send_photo(
                chat_id=settings.TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"Изображение товара из заказа №{order.id}",
                parse_mode=ParseMode.HTML
            )

    except Exception as e:
        logger.error(f"Telegram notification error: {str(e)}", exc_info=True)
        raise
    finally:
        await bot.session.close()

async def send_daily_report():
    today = timezone.now().date()
    report = DailyReport.objects.filter(date=today).first()
    if report:
        message_text = f"📊 Ежедневный отчёт за {today}:\n"
        message_text += f"📦 Количество заказов: {report.order_count}\n"
        message_text += f"💰 Общая выручка: {report.total_revenue} ₽"
        await bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=message_text,
            parse_mode=ParseMode.HTML
        )

@sync_to_async
def generate_new_order_message(order):
    items = OrderItem.objects.filter(order=order).select_related('product')

    moscow_tz = pytz.timezone('Europe/Moscow')
    created_at = timezone.localtime(order.created_at, moscow_tz)
    delivery_time = timezone.localtime(order.delivery_time, moscow_tz)

    message = [
        f"🌸 НОВЫЙ ЗАКАЗ ЦВЕТОВ 🌸\n",
        f"📦 Детали заказа:",
        f"🆔 Номер: {order.id}",
        f"📅 Дата: {created_at.strftime('%d.%m.%Y %H:%M')}",
        f"⏰ Доставка: {delivery_time.strftime('%d.%m.%Y %H:%M')}",
        f"📍 Адрес: {order.delivery_address}",
        f"💬 Комментарий: {order.comment or 'отсутствует'}\n",
        f"Состав заказа:"
    ]

    for item in items:
        message.append(f"➖ {item.product.name} ({item.quantity} шт.) - {item.price}₽")

    message.append(f"\n💰 ИТОГО: {order.total_price}₽")
    message.append(f"\n📦 Статус заказа: {order.get_status_display()}")
    return '\n'.join(message)

@sync_to_async
def generate_status_change_message(order):
    items = OrderItem.objects.filter(order=order).select_related('product')

    moscow_tz = pytz.timezone('Europe/Moscow')
    created_at = timezone.localtime(order.created_at, moscow_tz)
    delivery_time = timezone.localtime(order.delivery_time, moscow_tz)

    message = [
        f"🌸 ИЗМЕНЕНИЕ СТАТУСА ЗАКАЗА 🌸\n",
        f"📦 Детали заказа:",
        f"🆔 Номер: {order.id}",
        f"📅 Дата: {created_at.strftime('%d.%m.%Y %H:%M')}",
        f"⏰ Доставка: {delivery_time.strftime('%d.%m.%Y %H:%M')}",
        f"📍 Адрес: {order.delivery_address}",
        f"💬 Комментарий: {order.comment or 'отсутствует'}\n",
        f"Состав заказа:"
    ]

    for item in items:
        message.append(f"➖ {item.product.name} ({item.quantity} шт.) - {item.price}₽")

    message.append(f"\n💰 ИТОГО: {order.total_price}₽")
    message.append(f"\n📦 Новый статус заказа: {order.get_status_display()}")
    return '\n'.join(message)

@sync_to_async
def get_all_product_images(order):
    items = OrderItem.objects.filter(order=order).select_related('product')
    return [item.product.image.path for item in items if item.product.image]

def send_telegram_notification(order, is_new_order=True):
    try:
        async_to_sync(async_send_telegram_notification)(order, is_new_order)
    except Exception as e:
        logger.error(f"Notification error: {str(e)}")
