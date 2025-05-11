from django.test import TestCase
from django.urls import reverse
from .models import Product

class CatalogViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем доступные розы из каталога
        cls.available_rose1 = Product.objects.create(
            name="Аллегрия",
            price=300.00,
            description="Оранжевые с крупными для роз - спрей цветками в диаметре 5-7 см, бутоны вытянуты.",
            available=True
        )

        cls.available_rose2 = Product.objects.create(
            name="Аллилуйя",
            price=300.00,
            description="Очень длинный бутон распускается в элегантный махровый цветок, тёмно-красный, бархатистый с серебристой оборотной стороной лепестков.",
            available=True
        )

        # Создаем недоступную розу
        cls.unavailable_rose = Product.objects.create(
            name="Потрясающая Грейс",
            price=350.00,
            description="Цветы светло-розовые, густо-набитые, глубокой чашевидной формы, с сильным ароматом.",
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
        self.assertQuerySetEqual(
            response.context['products'],
            [self.available_rose1, self.available_rose2],
            ordered=False
        )

    def test_product_list_content(self):
        response = self.client.get(reverse('catalog:product_list'))
        self.assertContains(response, self.available_rose1.name)
        self.assertContains(response, self.available_rose2.name)
        self.assertContains(response, "300,00 ₽")
        self.assertNotContains(response, self.unavailable_rose.name)

    def test_empty_product_list(self):
        Product.objects.all().delete()
        response = self.client.get(reverse('catalog:product_list'))
        self.assertContains(response, "Товары временно отсутствуют")

    def test_product_detail_view(self):
        # Тестируем представление детализации продукта
        response = self.client.get(reverse('catalog:product_detail', args=[self.available_rose1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.available_rose1.name)
        self.assertContains(response, self.available_rose1.description)
        self.assertContains(response, "300,00 ₽")

    def test_product_detail_template_used(self):
        response = self.client.get(reverse('catalog:product_detail', args=[self.available_rose1.id]))
        self.assertTemplateUsed(response, 'catalog/product_detail.html')

    def test_unavailable_product_not_in_list(self):
        response = self.client.get(reverse('catalog:product_list'))
        self.assertNotContains(response, self.unavailable_rose.name)
