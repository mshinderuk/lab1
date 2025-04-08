from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product, Order


class ProductTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='UserPassword123!'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=100.00,
            stock_quantity=10,  # Заміна на нове поле
        )
        self.product_data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': 200.00,
            'stock_quantity': 20  # Заміна на нове поле
        }
        self.products_url = reverse('product-list')
        self.product_detail_url = reverse('product-detail', args=[self.product.id])

    def test_get_products_list(self):
        """
        Перевірка отримання списку продуктів (доступно всім)
        """
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_product_as_admin(self):
        """
        Перевірка створення продукту адміністратором
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.products_url, self.product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_create_product_as_regular_user_fails(self):
        """
        Перевірка, що звичайний користувач не може створити продукт
        """
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(self.products_url, self.product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)

    def test_update_product_as_admin(self):
        """
        Перевірка оновлення продукту адміністратором
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(self.product_detail_url, self.product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'New Product')

    def test_delete_product_as_admin(self):
        """
        Перевірка видалення продукту адміністратором
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_product_price_validation(self):
        """
        Перевірка валідації ціни продукту
        """
        self.client.force_authenticate(user=self.admin_user)
        data = self.product_data.copy()
        data['price'] = -100.00
        response = self.client.post(self.products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=100.00,
            stock_quantity=10  # Заміна на нове поле
        )
        self.order_data = {
            'product': self.product.id,
            'quantity': 2,
            'client_name': 'Test Client',
            'client_email': 'client@example.com'
        }
        self.orders_url = reverse('order-list')

    def test_create_order_authenticated_user(self):
        """
        Перевірка створення замовлення аутентифікованим користувачем
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.orders_url, self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().user, self.user)

    def test_create_order_unauthenticated_fails(self):
        """
        Перевірка, що неаутентифікований користувач не може створити замовлення
        """
        response = self.client.post(self.orders_url, self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 0)

    def test_order_quantity_validation(self):
        """
        Перевірка валідації кількості товару в замовленні
        """
        self.client.force_authenticate(user=self.user)
        data = self.order_data.copy()
        data['quantity'] = -1
        response = self.client.post(self.orders_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_order_stock_validation(self):
        """
        Перевірка валідації наявності достатньої кількості товару
        """
        self.client.force_authenticate(user=self.user)
        data = self.order_data.copy()
        data['quantity'] = 15  # Більше ніж є на складі (10)
        response = self.client.post(self.orders_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
