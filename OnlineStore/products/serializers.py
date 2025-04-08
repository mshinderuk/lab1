from rest_framework import serializers
from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def validate_price(self, value):
        """
        Перевірка, щоб ціна була більше нуля
        """
        if value <= 0:
            raise serializers.ValidationError("Ціна повинна бути більше нуля")
        return value

    def validate_stock_quantity(self, value):
        """
        Перевірка, щоб кількість на складі була не від'ємною
        """
        if value < 0:
            raise serializers.ValidationError("Кількість на складі не може бути від'ємною")
        return value


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'product', 'product_name', 'quantity', 'customer_name', 'customer_email', 'created_at', 'user']
        read_only_fields = ['user']  # Це поле буде заповнюватись автоматично

    def validate_quantity(self, value):
        """
        Перевірка, щоб кількість була більше нуля
        """
        if value <= 0:
            raise serializers.ValidationError("Кількість повинна бути більше нуля")
        return value

    def validate(self, data):
        """
        Перевірка наявності достатньої кількості товару на складі
        """
        product = data.get('product')
        quantity = data.get('quantity')

        if product and quantity:
            if product.stock_quantity < quantity:
                raise serializers.ValidationError({
                    "quantity": f"На складі недостатньо товару. Доступно: {product.stock_quantity}"
                })

        return data