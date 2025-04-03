from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from catalog.models import Product
from bot.telegram import send_telegram_notification
from unittest.mock import patch

class OrderTestCase(TestCase):
    def setUp(self):
        # Создаем пользователя
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )

        # Создаем продукт
        self.product = Product.objects.create(
            name='Роза',
            price=100.00,
            description='Красная роза',
            available=True
        )

        # Создаем заказ
        self.order = Order.objects.create(
            user=self.user,
            delivery_address='Москва, ул. Пушкина, д. 10',
            delivery_time=timezone.now() + timezone.timedelta(hours=1),
            status='new'
        )

        # Добавляем товар в заказ
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=self.product.price
        )

    def test_order_creation(self):
        # Проверяем, что заказ создан корректно
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.status, 'new')
        self.assertEqual(self.order.items.count(), 1)
        self.assertEqual(self.order.total_price, 200.00)

    @patch('bot.telegram.async_send_telegram_notification')
    def test_send_telegram_notification(self, mock_send_notification):
        # Вызываем функцию отправки уведомления
        send_telegram_notification(self.order)

        # Проверяем, что функция была вызвана с правильными аргументами
        mock_send_notification.assert_called_once_with(self.order)

    def test_order_item_total_price(self):
        # Проверяем, что общая стоимость товара в заказе рассчитывается правильно
        self.assertEqual(self.order_item.total_price, 200.00)
