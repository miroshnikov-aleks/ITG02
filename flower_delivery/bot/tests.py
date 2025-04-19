from django.test import TestCase, TransactionTestCase
from unittest.mock import patch, AsyncMock, MagicMock
from django.utils import timezone
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from catalog.models import Product
from bot.telegram import async_send_telegram_notification, send_telegram_notification
import asyncio
from django.core.files.uploadedfile import SimpleUploadedFile

class BotTestCase(TransactionTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )

        test_image = SimpleUploadedFile(
            name='test_rose.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/jpeg'
        )

        self.product = Product.objects.create(
            name='Роза',
            price=100.00,
            description='Красная роза',
            available=True,
            image=test_image
        )

        self.order = Order.objects.create(
            user=self.user,
            delivery_address='Москва, ул. Пушкина, д. 10',
            delivery_time=timezone.now() + timezone.timedelta(hours=1),
            status='new'
        )

        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=self.product.price
        )

    @patch('bot.telegram.bot.send_message', new_callable=AsyncMock)
    @patch('bot.telegram.bot.send_photo', new_callable=AsyncMock)
    def test_async_send_telegram_notification(self, mock_send_photo, mock_send_message):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_send_telegram_notification(self.order))
        loop.close()

        mock_send_message.assert_called_once()
        mock_send_photo.assert_called_once()

    @patch('bot.telegram.async_send_telegram_notification', new_callable=AsyncMock)
    def test_send_telegram_notification(self, mock_async_send):
        send_telegram_notification(self.order)
        mock_async_send.assert_called_once_with(self.order)

    def tearDown(self):
        self.product.image.delete()
