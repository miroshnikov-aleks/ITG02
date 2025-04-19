from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import DailyReport

class AnalyticsViewsTestCase(TestCase):
    def setUp(self):
        # Создаем тестового пользователя с правами staff
        self.user = User.objects.create_user(username='testuser', password='testpass', is_staff=True)
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

        # Создаем тестовые данные для DailyReport
        self.report1 = DailyReport.objects.create(date='2023-10-01', order_count=5, total_revenue=1500.00)
        self.report2 = DailyReport.objects.create(date='2023-10-02', order_count=3, total_revenue=900.00)

    def test_daily_report_list_view(self):
        # Получаем URL для представления daily_report_list
        url = reverse('analytics:daily_report_list')

        # Выполняем GET-запрос к представлению
        response = self.client.get(url)

        # Проверяем, что статус кода равен 200
        self.assertEqual(response.status_code, 200)

        # Проверяем, что контекст содержит ожидаемые данные
        self.assertIn('reports', response.context)
        self.assertEqual(list(response.context['reports']), [self.report2, self.report1])

        # Проверяем, что используется правильный шаблон
        self.assertTemplateUsed(response, 'analytics/daily_report_list.html')
