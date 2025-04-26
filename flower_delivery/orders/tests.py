from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from catalog.models import Product
from analytics.models import DailyReport
from decimal import Decimal
from django.utils import timezone
import pytz

class OrderCreateViewTest(TestCase):
    def setUp(self):
        # Создаем пользователя
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(email='testuser@example.com', password='testpass123')

        # Создаем товар (роза "Аллегрия")
        self.product = Product.objects.create(
            name='Аллегрия',
            price=300.00,
            description='Оранжевые с крупными для роз - спрей цветками в диаметре 5-7 см, бутоны вытянуты.',
            available=True
        )

    def test_order_create_view(self):
        # Устанавливаем текущее время доставки с учетом часового пояса
        moscow_tz = pytz.timezone('Europe/Moscow')
        delivery_time = timezone.now() + timezone.timedelta(hours=1)
        delivery_time = timezone.localtime(delivery_time, moscow_tz)

        # Данные для создания заказа
        order_data = {
            'delivery_address': 'Москва, ул. Пушкина, д. 10',
            'delivery_time': delivery_time.strftime('%Y-%m-%dT%H:%M'),
            'comment': 'Пожалуйста, позвоните перед доставкой',
            f'quantity_{self.product.id}': 2,
        }

        # Отправляем POST-запрос для создания заказа
        response = self.client.post(reverse('orders:order_create'), data=order_data)

        # Проверяем, что заказ был успешно создан
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

        # Получаем созданный заказ
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.delivery_address, order_data['delivery_address'])
        self.assertEqual(timezone.localtime(order.delivery_time, moscow_tz).strftime('%Y-%m-%dT%H:%M'), order_data['delivery_time'])
        self.assertEqual(order.comment, order_data['comment'])

        # Проверяем, что товар был добавлен в заказ
        order_item = OrderItem.objects.get(order=order, product=self.product)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, self.product.price)

        # Проверяем, что ежедневный отчет был обновлен
        today = timezone.now().date()
        report = DailyReport.objects.get(date=today)
        self.assertEqual(report.order_count, 1)
        self.assertEqual(report.total_revenue, Decimal('600.00'))
