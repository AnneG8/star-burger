from django.db import models
from django.utils import timezone


class Location(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    lat = models.FloatField(
        'широта',
        blank=True,
    )
    lon = models.FloatField(
        'долгота',
        blank=True,
    )
    updated = models.DateTimeField(
        'дата обновления',
        default=timezone.now,
        db_index=True
    )

    class Meta:
        verbose_name = 'локация'
        verbose_name_plural = 'локации'
        unique_together = [
            ['lat', 'lon']
        ]

    def __str__(self):
        return f'({self.lat}, {self.lon})'

    def get_coordinates(self):
        return self.lat, self.lon
