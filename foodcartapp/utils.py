from django.conf import settings

from geopy import distance as dist
import requests


def fetch_coordinates(address, apikey=settings.YANDEX_GEOCODER_KEY):
    try:
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']
        if not found_places:
            return None
    except (requests.exceptions.HTTPError, KeyError):
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distance(from_, to_):
    distance = dist.distance(from_, to_).km
    return round(distance)
