from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'password2': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='ExistingPassword123!'
        )

    def test_register_success(self):
        """
        Перевірка успішної реєстрації користувача
        """
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username='testuser').email, 'test@example.com')

    def test_register_passwords_dont_match(self):
        """
        Перевірка валідації паролів при реєстрації
        """
        data = self.user_data.copy()
        data['password2'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_register_email_already_exists(self):
        """
        Перевірка валідації унікальності email
        """
        data = self.user_data.copy()
        data['email'] = 'existing@example.com'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_login_success(self):
        """
        Перевірка успішного входу
        """
        login_data = {
            'username': 'existinguser',
            'password': 'ExistingPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """
        Перевірка входу з неправильними обліковими даними
        """
        login_data = {
            'username': 'existinguser',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)