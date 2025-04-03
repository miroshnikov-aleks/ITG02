from django.test import TestCase
from django.urls import reverse
from .models import Product

class CatalogViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем тестовые продукты
        cls.available_product1 = Product.objects.create(
            name="Розы красные",
            price=1500.00,
            description="Красные розы 50 см",
            available=True
        )
        
        cls.available_product2 = Product.objects.create(
            name="Тюльпаны белые",
            price=800.00,
            description="Белые тюльпаны",
            available=True
        )
        
        cls.unavailable_product = Product.objects.create(
            name="Орхидеи фиолетовые",
            price=2500.00,
            description="Нет в наличии",
            available=False
        )

    def test_product_list_status_code(self):
        response = self.client.get(reverse('catalog:product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_template_used(self):
        response = self.client.get(reverse('catalog:product_list'))
        self.assertTemplateUsed(response, 'catalog/product_list.html')

    def test_product_list_context(self):
        response = self.client.get(reverse('catalog:product_list'))
        # Исправлено название метода и учтена локализация
        self.assertQuerySetEqual(
            response.context['products'],
            [self.available_product1, self.available_product2],
            ordered=False
        )
        
    def test_product_list_content(self):
        response = self.client.get(reverse('catalog:product_list'))
        # Исправлено ожидание формата цены с учетом локализации
        self.assertContains(response, self.available_product1.name)
        self.assertContains(response, self.available_product2.name)
        self.assertContains(response, "1500,00 ₽")  # Запятая вместо точки
        self.assertContains(response, "800,00 ₽")    # Запятая вместо точки
        
        # Проверка отсутствия недоступного товара
        self.assertNotContains(response, self.unavailable_product.name)
        
    def test_empty_product_list(self):
        Product.objects.all().delete()
        response = self.client.get(reverse('catalog:product_list'))
        self.assertContains(response, "Товары временно отсутствуют")