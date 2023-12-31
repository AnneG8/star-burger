from rest_framework.serializers import ModelSerializer, ValidationError
import phonenumbers

from .models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False)

    def validate_phonenumber(self, value):
        parsed_number = phonenumbers.parse(value, region='RU')
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError(f'Invalid phone number: {value}')
        return parsed_number

    class Meta:
        model = Order
        fields = [
            'products',
            'firstname',
            'lastname',
            'phonenumber',
            'address'
        ]
