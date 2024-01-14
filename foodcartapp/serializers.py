from rest_framework.serializers import ModelSerializer, ValidationError
import phonenumbers

from .models import Order, OrderItem, Restaurant
from .utils import fetch_coordinates


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )

    def validate_phonenumber(self, value):
        parsed_number = phonenumbers.parse(value, region='RU')
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError(f'Invalid phone number: {value}')
        return parsed_number

    class Meta:
        model = Order
        fields = [
            'id',
            'products',
            'firstname',
            'lastname',
            'phonenumber',
            'address'
        ]


class RestaurantSerializer(ModelSerializer):
    def validate_address(self, value):
        coordinates = fetch_coordinates(value)
        if not coordinates:
            raise ValidationError(f'Invalid address: {value}')
        return value

    class Meta:
        model = Restaurant
        fields = [
            'name',
            'address',
            'contact_phone'
        ]
