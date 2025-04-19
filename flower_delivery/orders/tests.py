from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from catalog.models import Product
from bot.telegram import send_telegram_notification
from unittest.mock import patch

class OrderTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )

        self.product = Product.objects.create(
            name='Роза',
            price=100.00,
            description='Красная роза',
            available=True
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

    def test_order_creation(self):
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.status, 'new')
        self.assertEqual(self.order.items.count(), 1)
        self.assertEqual(self.order.total_price, 200.00)

    @patch('bot.telegram.async_send_telegram_notification')
    def test_send_telegram_notification(self, mock_send_notification):
        send_telegram_notification(self.order)
        mock_send_notification.assert_called_once_with(self.order)

    def test_order_item_total_price(self):
        self.assertEqual(self.order_item.total_price, 200.00)

    def test_reorder(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(f'/orders/reorder/{self.order.id}/', {
            'delivery_address': 'Новый адрес',
            'delivery_time': (timezone.now() + timezone.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M'),
            'comment': 'Новый комментарий',
            f'quantity_{self.product.id}': 2
        })
        self.assertEqual(response.status_code, 302)
        new_order = Order.objects.latest('id')
        self.assertEqual(new_order.delivery_address, 'Новый адрес')
        self.assertEqual(new_order.items.count(), 1)
        self.assertEqual(new_order.items.first().product, self.product)
        self.assertEqual(new_order.items.first().quantity, 2)

    @patch('bot.telegram.async_send_telegram_notification')
    def test_update_order_status(self, mock_send_notification):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(f'/orders/update_status/{self.order.id}/', {
            'status': 'in_progress'
        })
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_progress')
        mock_send_notification.assert_called_once_with(self.order)
