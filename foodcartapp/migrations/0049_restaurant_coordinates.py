# Generated by Django 3.2.15 on 2024-01-15 22:53

from django.db import migrations, models
import django.db.models.deletion


def fill_restaurant_coordinates(apps, schema_editor):
    Restaurant = apps.get_model('foodcartapp', 'Restaurant')
    Location = apps.get_model('locations', 'Location')

    restaurants = Restaurant.objects.all()
    for restaurant in restaurants.iterator():
        location, created = Location.objects.get_or_create(
            lat=restaurant.lat,
            lon=restaurant.lon,
            defaults={
                'address': restaurant.address
            }
        )
        if created:
            location.save()
        else:
            restaurant.address = location.address

        restaurant.coordinates = location
        restaurant.save()


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
        ('foodcartapp', '0048_auto_20240115_0206'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='coordinates',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='locations.location', verbose_name='локация'),
        ),
        migrations.RunPython(fill_restaurant_coordinates),
        migrations.RemoveField(
            model_name='restaurant',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='lon',
        ),
    ]