from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Product
from reviews.models import Review
from reviews.forms import ReviewForm  # Импортируем форму

class ReviewTestCase(TestCase):
    def setUp(self):
        # Создаем пользователя
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        # Создаем товар
        self.product = Product.objects.create(
            name='Аллегрия',
            price=300.00,
            description='Оранжевые розы',
            available=True
        )

    def test_review_creation(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Отличный букет!'
        )
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.rating, 5)

    def test_review_list_view(self):
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Хороший букет'
        )
        # Логин через email
        self.client.login(email='testuser@example.com', password='testpass')
        response = self.client.get(reverse('reviews:review_list', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Хороший букет')

    def test_review_create_view_get(self):
        self.client.login(email='testuser@example.com', password='testpass')
        response = self.client.get(reverse('reviews:review_create', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        # Проверяем наличие формы в контексте
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ReviewForm)

    def test_review_create_view_post_valid(self):
        self.client.login(email='testuser@example.com', password='testpass')
        data = {
            'rating': 4,
            'comment': 'Красивые цветы'
        }
        response = self.client.post(
            reverse('reviews:review_create', args=[self.product.pk]),
            data=data
        )
        self.assertRedirects(response, reverse('catalog:product_detail', args=[self.product.pk]))
        self.assertTrue(Review.objects.filter(comment='Красивые цветы').exists())

    def test_review_create_view_post_invalid(self):
        self.client.login(email='testuser@example.com', password='testpass')
        # Отправляем пустую форму
        response = self.client.post(
            reverse('reviews:review_create', args=[self.product.pk]),
            data={}
        )
        self.assertEqual(response.status_code, 200)
        # Проверяем наличие формы с ошибками
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'rating', 'Обязательное поле.')
        self.assertFormError(form, 'comment', 'Обязательное поле.')

    def test_review_create_view_unauthenticated(self):
        response = self.client.post(
            reverse('reviews:review_create', args=[self.product.pk]),
            data={'rating': 5, 'comment': 'Текст'}
        )
        # Проверяем редирект на страницу логина
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={reverse('reviews:review_create', args=[self.product.pk])}"
        )