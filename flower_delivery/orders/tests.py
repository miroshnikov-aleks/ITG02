from django.test import TransactionTestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from catalog.models import Product
from analytics.models import DailyReport
from decimal import Decimal
from django.utils import timezone
import pytz
from unittest.mock import patch

class OrderCreateViewTest(TransactionTestCase):
    def setUp(self):
        # Мокаем текущее время для попадания в рабочий интервал
        self.moscow_tz = pytz.timezone('Europe/Moscow')
        self.fixed_time = self.moscow_tz.localize(
            timezone.datetime(2024, 1, 1, 12, 0)  # 12:00 по Москве
        )
        self.time_patcher = patch('django.utils.timezone.now')
        self.mock_now = self.time_patcher.start()
        self.mock_now.return_value = self.fixed_time

        # Создаем пользователя
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123',
            is_staff=False
        )
        self.client = Client()  # Теперь Client импортирован
        self.client.login(email='testuser@example.com', password='testpass123')

        # Создаем товар
        self.product = Product.objects.create(
            name='Аллегрия',
            price=300.00,
            description='Оранжевые розы',
            available=True
        )

    def tearDown(self):
        self.time_patcher.stop()

    def test_order_create_view(self):
        # Устанавливаем время доставки на 1 час вперед
        delivery_time = self.fixed_time + timezone.timedelta(hours=1)

        # Данные для заказа
        order_data = {
            'delivery_address': 'Москва, ул. Пушкина, д. 10',
            'delivery_time': delivery_time.strftime('%Y-%m-%dT%H:%M'),
            'comment': 'Позвонить перед доставкой',
            f'quantity_{self.product.id}': 2,
        }

        # Отправляем POST-запрос
        response = self.client.post(reverse('orders:order_create'), data=order_data)

        # Проверяем редирект
        self.assertEqual(response.status_code, 302)

        # Проверяем создание заказа
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)

        # Проверяем элементы заказа
        order_item = OrderItem.objects.get(order=order)
        self.assertEqual(order_item.quantity, 2)

        # Проверяем обновление аналитики
        report = DailyReport.objects.get(date=self.fixed_time.date())
        self.assertEqual(report.order_count, 1)
        self.assertEqual(report.total_revenue, Decimal('600.00'))
