from django.db import models

class DailyReport(models.Model):
    date = models.DateField('Дата', unique=True)
    order_count = models.IntegerField('Количество заказов', default=0)
    total_revenue = models.DecimalField('Общая выручка', max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = 'Ежедневный отчёт'
        verbose_name_plural = 'Ежедневные отчёты'
        ordering = ['-date']

    def __str__(self):
        return f'Отчёт за {self.date}'
