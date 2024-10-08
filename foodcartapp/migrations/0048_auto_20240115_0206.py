# Generated by Django 3.2.15 on 2024-01-14 23:06

from django.db import migrations

from foodcartapp.utils import fetch_coordinates


def fill_restaurant_lat_and_lon(apps, schema_editor):
    Restaurant = apps.get_model('foodcartapp', 'Restaurant')
    restaurants = Restaurant.objects.all()
    for restaurant in restaurants.iterator():
        restaurant.lon, restaurant.lat = fetch_coordinates(restaurant.address)
        restaurant.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20240115_0204'),
    ]

    operations = [
        migrations.RunPython(fill_restaurant_lat_and_lon),
    ]
