import logging
import asyncio
import pytz
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InputFile
from aiogram.utils.markdown import hbold, hitalic
from django.conf import settings
from django.utils import timezone
from asgiref.sync import sync_to_async, async_to_sync
from orders.models import OrderItem

logger = logging.getLogger(__name__)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

async def async_send_telegram_notification(order):
    try:
        message_text = await generate_order_message(order)
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

@sync_to_async
def generate_order_message(order):
    items = OrderItem.objects.filter(order=order).select_related('product')

    moscow_tz = pytz.timezone('Europe/Moscow')
    created_at = timezone.localtime(order.created_at, moscow_tz)
    delivery_time = timezone.localtime(order.delivery_time, moscow_tz)

    message = [
        f"🌸 {hbold('НОВЫЙ ЗАКАЗ ЦВЕТОВ')} 🌸\n",
        f"📦 {hbold('Детали заказа:')}",
        f"🆔 Номер: {order.id}",
        f"📅 Дата: {created_at.strftime('%d.%m.%Y %H:%M')}",
        f"⏰ Доставка: {delivery_time.strftime('%d.%m.%Y %H:%M')}",
        f"📍 Адрес: {hitalic(order.delivery_address)}",
        f"💬 Комментарий: {hitalic(order.comment or 'отсутствует')}\n",
        f"{hbold('Состав заказа:')}"
    ]

    for item in items:
        message.append(f"➖ {item.product.name} ({item.quantity} шт.) - {item.price}₽")

    message.append(f"\n💰 {hbold('ИТОГО:')} {order.total_price}₽")
    return '\n'.join(message)

@sync_to_async
def get_all_product_images(order):
    items = OrderItem.objects.filter(order=order).select_related('product')
    return [item.product.image.path for item in items if item.product.image]

def send_telegram_notification(order):
    try:
        async_to_sync(async_send_telegram_notification)(order)
    except Exception as e:
        logger.error(f"Notification error: {str(e)}")