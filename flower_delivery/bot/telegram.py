import logging
import asyncio
import pytz
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from django.conf import settings
from django.utils import timezone
from asgiref.sync import sync_to_async
from orders.models import OrderItem
from analytics.models import DailyReport

logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# ====== Асинхронные функции для уведомлений ======
async def async_send_telegram_notification(order, is_new_order=True):
    """
    Асинхронная отправка уведомления в Telegram.
    """
    try:
        if is_new_order:
            message_text = await generate_new_order_message(order)
        else:
            message_text = await generate_status_change_message(order)

        photo_paths = await get_all_product_images(order)

        # Отправка текстового сообщения
        await bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=message_text,
            parse_mode=ParseMode.HTML
        )

        # Отправка изображений
        for photo_path in photo_paths:
            try:
                photo = FSInputFile(photo_path)
                await bot.send_photo(
                    chat_id=settings.TELEGRAM_CHAT_ID,
                    photo=photo,
                    caption=f"Изображение товара из заказа №{order.id}",
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке изображения: {str(e)}")

    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления в Telegram: {str(e)}", exc_info=True)
        raise
    finally:
        await bot.session.close()

@sync_to_async
def generate_new_order_message(order):
    items = OrderItem.objects.filter(order=order).select_related('product')
    moscow_tz = pytz.timezone('Europe/Moscow')
    created_at = timezone.localtime(order.created_at, moscow_tz)
    delivery_time = timezone.localtime(order.delivery_time, moscow_tz)

    message = [
        f"🌸 НОВЫЙ ЗАКАЗ ЦВЕТОВ 🌸",
        f"📦 Детали заказа:",
        f"🆔 Номер: {order.id}",
        f"📅 Дата: {created_at.strftime('%d.%m.%Y %H:%M')}",
        f"⏰ Доставка: {delivery_time.strftime('%d.%m.%Y %H:%M')}",
        f"📍 Адрес: {order.delivery_address}",
        f"💬 Комментарий: {order.comment or 'отсутствует'}",
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
        f"🌸 ИЗМЕНЕНИЕ СТАТУСА ЗАКАЗА 🌸",
        f"📦 Детали заказа:",
        f"🆔 Номер: {order.id}",
        f"📅 Дата: {created_at.strftime('%d.%m.%Y %H:%M')}",
        f"⏰ Доставка: {delivery_time.strftime('%d.%m.%Y %H:%M')}",
        f"📍 Адрес: {order.delivery_address}",
        f"💬 Комментарий: {order.comment or 'отсутствует'}",
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
    """
    Синхронная точка входа для Celery. Отправляет уведомление в Telegram.
    """
    try:
        # Создаем новый цикл событий, если его нет
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_send_telegram_notification(order, is_new_order))
        loop.close()
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления в Telegram: {str(e)}")

# ====== Ежедневный отчёт ======
async def send_daily_report():
    today = timezone.now().date()
    report = await sync_to_async(DailyReport.objects.filter(date=today).first)()

    if report:
        message_text = f"📊 Ежедневный отчёт за {today}:\n"
        message_text += f"📦 Количество заказов: {report.order_count}\n"
        message_text += f"💰 Общая выручка: {report.total_revenue} ₽"

        try:
            await bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=message_text,
                parse_mode=ParseMode.HTML
            )
            logger.info("✅ Ежедневный отчёт успешно отправлен в Telegram.")
        except Exception as e:
            logger.error(f"❌ Не удалось отправить ежедневный отчёт: {e}")
    else:
        logger.info("ℹ️ Нет данных для ежедневного отчёта за сегодня.")

    await bot.session.close()

def run_send_daily_report():
    """
    Точка входа для Celery задачи.
    """
    try:
        # Создаем новый цикл событий, если его нет
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_daily_report())
        loop.close()
    except Exception as e:
        logger.error(f"Ошибка при выполнении задачи send_daily_report: {str(e)}")
