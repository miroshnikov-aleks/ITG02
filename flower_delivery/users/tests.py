from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.forms import CustomUserCreationForm, CustomAuthenticationForm

class UserTestCase(TestCase):
    def setUp(self):
        # Создаем уникальные данные для тестов
        self.registration_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }

    def test_user_registration(self):
        # Проверяем регистрацию нового пользователя
        response = self.client.post(reverse('users:register'), data=self.registration_data)
        self.assertEqual(response.status_code, 302)  # Ожидаем редирект после успешной регистрации
        self.assertTrue(get_user_model().objects.filter(email=self.registration_data['email']).exists())

    def test_user_login(self):
        # Сначала регистрируем пользователя
        self.client.post(reverse('users:register'), data=self.registration_data)

        # Проверяем вход пользователя
        login_data = {
            'username': self.registration_data['email'],
            'password': self.registration_data['password1']
        }
        response = self.client.post(reverse('users:login'), data=login_data)
        self.assertEqual(response.status_code, 302)  # Ожидаем редирект после успешного входа

    def test_user_logout(self):
        # Сначала регистрируем и логиним пользователя
        self.client.post(reverse('users:register'), data=self.registration_data)
        login_data = {
            'username': self.registration_data['email'],
            'password': self.registration_data['password1']
        }
        self.client.post(reverse('users:login'), data=login_data)

        # Проверяем выход пользователя
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)  # Ожидаем редирект после успешного выхода

    def test_registration_form_validity(self):
        # Проверяем валидацию формы регистрации с уникальными данными
        form = CustomUserCreationForm(data={
            'username': 'anotheruser',
            'email': 'anotheruser@example.com',
            'password1': 'anotherpass123',
            'password2': 'anotherpass123'
        })
        self.assertTrue(form.is_valid(), form.errors)  # Добавляем вывод ошибок валидации

    def test_login_form_validity(self):
        # Сначала создаем пользователя
        user = get_user_model().objects.create_user(
            username='anotheruser',
            email='anotheruser@example.com',
            password='anotherpass123'
        )

        # Проверяем валидацию формы входа
        login_data = {
            'username': 'anotheruser@example.com',
            'password': 'anotherpass123'
        }
        form = CustomAuthenticationForm(data=login_data)
        self.assertTrue(form.is_valid(), form.errors)  # Добавляем вывод ошибок валидации
