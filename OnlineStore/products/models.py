from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # Додано правильний синтаксис для метода
        return self.name

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # Тепер у замовленні буде видно назву продукту
        return f"Order by {self.customer_name} - {self.product.name}"
