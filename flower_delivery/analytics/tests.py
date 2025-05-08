from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from analytics.models import DailyReport
from django.utils import timezone
from django.utils.formats import date_format, number_format

class AnalyticsTests(TestCase):
    def setUp(self):
        # Создаем пользователя с правами staff для тестирования доступа к отчетам
        User = get_user_model()
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staffuser@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client = Client()

        # Создаем несколько записей DailyReport для тестирования
        today = timezone.now().date()
        self.report1 = DailyReport.objects.create(
            date=today,
            order_count=5,
            total_revenue=10000.00
        )
        self.report2 = DailyReport.objects.create(
            date=today - timezone.timedelta(days=1),
            order_count=3,
            total_revenue=7500.00
        )

    def test_daily_report_creation(self):
        """Тест создания записи DailyReport."""
        report = DailyReport.objects.get(date=self.report1.date)
        self.assertEqual(report.order_count, 5)
        self.assertEqual(report.total_revenue, 10000.00)

    def test_daily_report_ordering(self):
        """Тест порядка сортировки отчетов (по убыванию даты)."""
        reports = DailyReport.objects.all()
        self.assertEqual(reports[0], self.report1)  # Самый новый отчет должен быть первым
        self.assertEqual(reports[1], self.report2)

    def test_daily_report_list_view(self):
        """Тест представления daily_report_list."""
        # Логинимся как staff пользователь
        self.client.login(email='staffuser@example.com', password='testpass123')

        # Делаем запрос к представлению
        url = reverse('analytics:daily_report_list')
        response = self.client.get(url)

        # Проверяем статус ответа
        self.assertEqual(response.status_code, 200)

        # Проверяем, что контекст содержит все отчеты
        self.assertQuerySetEqual(
            response.context['reports'],
            DailyReport.objects.all(),
            ordered=False
        )

        # Проверяем, что отчеты отображаются в HTML
        formatted_date1 = date_format(self.report1.date, "d E Y")
        formatted_date2 = date_format(self.report2.date, "d E Y")
        formatted_revenue1 = number_format(self.report1.total_revenue, use_l10n=True, decimal_pos=2)
        formatted_revenue2 = number_format(self.report2.total_revenue, use_l10n=True, decimal_pos=2)

        self.assertContains(response, formatted_date1)
        self.assertContains(response, f"{self.report1.order_count}")
        self.assertContains(response, f"{formatted_revenue1} ₽")
        self.assertContains(response, formatted_date2)
        self.assertContains(response, f"{self.report2.order_count}")
        self.assertContains(response, f"{formatted_revenue2} ₽")

    def test_daily_report_list_view_access_denied(self):
        """Тест запрета доступа к daily_report_list для не-staff пользователей."""
        # Создаем обычного пользователя
        User = get_user_model()
        regular_user = User.objects.create_user(
            username='regularuser',
            email='regularuser@example.com',
            password='testpass123'
        )
        self.client.login(email='regularuser@example.com', password='testpass123')

        # Делаем запрос к представлению
        url = reverse('analytics:daily_report_list')
        response = self.client.get(url)

        # Проверяем, что доступ запрещен
        self.assertEqual(response.status_code, 302)  # Ожидается редирект
        self.assertRedirects(response, '/admin/login/?next=/analytics/reports/')
