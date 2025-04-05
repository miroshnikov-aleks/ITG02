from django.db import models
from django.conf import settings
from catalog.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('in_progress', 'В обработке'),
        ('in_delivery', 'В доставке'),
        ('completed', 'Выполнен'),
        ('canceled', 'Отменен'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    delivery_address = models.TextField('Адрес доставки')
    delivery_time = models.DateTimeField('Время доставки')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    comment = models.TextField('Комментарий', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ №{self.id}'

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField(
        'Цена',
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        unique_together = ['order', 'product']

    @property
    def total_price(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'