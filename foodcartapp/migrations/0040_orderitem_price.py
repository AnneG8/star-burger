# Generated by Django 3.2.15 on 2024-01-09 13:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_alter_order_phonenumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='стоимость заказа'),
            preserve_default=False,
        ),
    ]
