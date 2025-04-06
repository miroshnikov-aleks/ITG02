from django.db import models
from django.urls import reverse

class Product(models.Model):
    name = models.CharField('Название', max_length=255)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='products/')
    available = models.BooleanField('Доступен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.pk])
