from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
# Додаємо імпорти для Swagger документації
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Імпортуємо кастомні перевірки
from accounts.permissions import IsAdmin, IsOwnerOrReadOnly


class ProductListCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Отримати список усіх продуктів",
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=ProductSerializer,
        operation_description="Створити новий продукт",
        responses={
            201: ProductSerializer(),
            400: "Некоректні дані",
            401: "Необхідна аутентифікація",
            403: "Недостатньо прав"
        }
    )
    def post(self, request):
        # Перевіряємо, чи користувач автентифікований і чи має права адміністратора
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({"detail": "Недостатньо прав"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [IsAdmin]  # Використання кастомної перевірки для всіх методів цього класу

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_description="Отримати деталі конкретного продукту",
        responses={
            200: ProductSerializer(),
            404: openapi.Response("Продукт не знайдено", examples={
                "application/json": {"error": "Product not found"}
            })
        }
    )
    def get(self, request, pk):
        # Для метода GET не потрібна автентифікація, тому видаляємо permission_classes для цього методу
        self.permission_classes = []
        self.check_permissions(request)

        product = self.get_object(pk)
        if product is None:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=ProductSerializer,
        operation_description="Оновити існуючий продукт",
        responses={
            200: ProductSerializer(),
            400: "Некоректні дані",
            401: "Необхідна аутентифікація",
            403: "Недостатньо прав",
            404: openapi.Response("Продукт не знайдено", examples={
                "application/json": {"error": "Product not found"}
            })
        }
    )
    def put(self, request, pk):
        # Відновлюємо перевірку прав для методу PUT
        self.permission_classes = [IsAdmin]
        self.check_permissions(request)

        product = self.get_object(pk)
        if product is None:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Видалити продукт",
        responses={
            204: "Продукт успішно видалено",
            401: "Необхідна аутентифікація",
            403: "Недостатньо прав",
            404: openapi.Response("Продукт не знайдено", examples={
                "application/json": {"error": "Product not found"}
            })
        }
    )
    def delete(self, request, pk):
        # Перевірка прав для методу DELETE
        self.permission_classes = [IsAdmin]
        self.check_permissions(request)

        product = self.get_object(pk)
        if product is None:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Тільки автентифіковані користувачі можуть працювати з замовленнями

    @swagger_auto_schema(
        operation_description="Отримати список усіх замовлень",
        responses={
            200: OrderSerializer(many=True),
            401: "Необхідна аутентифікація"
        }
    )
    def get(self, request):
        # Звичайні користувачі бачать тільки свої замовлення, адміністратори - всі
        if request.user.is_staff:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=OrderSerializer,
        operation_description="Створити нове замовлення",
        responses={
            201: OrderSerializer(),
            400: "Некоректні дані",
            401: "Необхідна аутентифікація"
        }
    )
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Автоматично призначаємо замовлення поточному користувачу
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]  # Додаємо кастомну перевірку власності

    def get_object(self, pk, user):
        try:
            order = Order.objects.get(pk=pk)
            # Перевіряємо, чи має користувач доступ до цього замовлення
            if not user.is_staff and hasattr(order, 'user') and order.user != user:
                return None
            return order
        except Order.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_description="Отримати деталі конкретного замовлення",
        responses={
            200: OrderSerializer(),
            401: "Необхідна аутентифікація",
            403: "Недостатньо прав",
            404: openapi.Response("Замовлення не знайдено", examples={
                "application/json": {"error": "Order not found"}
            })
        }
    )
    def get(self, request, pk):
        order = self.get_object(pk, request.user)
        if order is None:
            return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=OrderSerializer,
        operation_description="Оновити існуюче замовлення",
        responses={
            200: OrderSerializer(),
            400: "Некоректні дані",
            401: "Необхідна аутентифікація",
            403: "Недостатньо прав",
            404: openapi.Response("Замовлення не знайдено", examples={
                "application/json": {"error": "Order not found"}
            })
        }
    )
    def put(self, request, pk):
        order = self.get_object(pk, request.user)
        if order is None:
            return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Видалити замовлення",
        responses={
            204: "Замовлення успішно видалено",
            401: "Необхідна аутентифікація",
            403: "Недостатньо прав",
            404: openapi.Response("Замовлення не знайдено", examples={
                "application/json": {"error": "Order not found"}
            })
        }
    )
    def delete(self, request, pk):
        order = self.get_object(pk, request.user)
        if order is None:
            return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)