from django.db import models

class DailyReport(models.Model):
    date = models.DateField(unique=True, verbose_name="Дата")
    order_count = models.PositiveIntegerField(default=0, verbose_name="Количество заказов")
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Общая выручка")

    class Meta:
        verbose_name = "Ежедневный отчёт"
        verbose_name_plural = "Ежедневные отчёты"
        ordering = ['-date']

    def __str__(self):
        return f"Отчёт за {self.date}"
