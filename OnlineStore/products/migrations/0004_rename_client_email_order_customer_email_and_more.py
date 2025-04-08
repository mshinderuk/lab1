# Generated by Django 5.1.7 on 2025-04-08 18:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_remove_order_customer_email_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='client_email',
            new_name='customer_email',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='client_name',
            new_name='customer_name',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='stock',
            new_name='stock_quantity',
        ),
    ]
