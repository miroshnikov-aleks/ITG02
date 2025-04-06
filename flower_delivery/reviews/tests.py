from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Product
from .models import Review

class ReviewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.product = Product.objects.create(
            name='Роза',
            price=100.00,
            description='Красная роза',
            available=True
        )
        self.review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Отличный букет!'
        )

    def test_review_creation(self):
        self.assertEqual(self.review.product, self.product)
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, 'Отличный букет!')

    def test_review_list_view(self):
        response = self.client.get(reverse('reviews:review_list', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Отличный букет!')

    def test_review_create_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('reviews:review_create', args=[self.product.pk]), {
            'rating': 4,
            'comment': 'Хороший букет!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(comment='Хороший букет!').exists())
