from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
# Додаємо імпорти для Swagger документації
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
        responses={201: ProductSerializer()}
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
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
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        request_body=ProductSerializer,
        operation_description="Оновити існуючий продукт",
        responses={
            200: ProductSerializer(),
            400: "Некоректні дані",
            404: openapi.Response("Продукт не знайдено", examples={
                "application/json": {"error": "Product not found"}
            })
        }
    )
    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Видалити продукт",
        responses={
            204: "Продукт успішно видалено",
            404: openapi.Response("Продукт не знайдено", examples={
                "application/json": {"error": "Product not found"}
            })
        }
    )
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

class OrderListCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Отримати список усіх замовлень",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=OrderSerializer,
        operation_description="Створити нове замовлення",
        responses={201: OrderSerializer()}
    )
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Отримати деталі конкретного замовлення",
        responses={
            200: OrderSerializer(),
            404: openapi.Response("Замовлення не знайдено", examples={
                "application/json": {"error": "Order not found"}
            })
        }
    )
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        request_body=OrderSerializer,
        operation_description="Оновити існуюче замовлення",
        responses={
            200: OrderSerializer(),
            400: "Некоректні дані",
            404: openapi.Response("Замовлення не знайдено", examples={
                "application/json": {"error": "Order not found"}
            })
        }
    )
    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            serializer = OrderSerializer(order, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Видалити замовлення",
        responses={
            204: "Замовлення успішно видалено",
            404: openapi.Response("Замовлення не знайдено", examples={
                "application/json": {"error": "Order not found"}
            })
        }
    )
    def delete(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)