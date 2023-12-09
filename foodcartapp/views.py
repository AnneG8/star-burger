import json
import os

import phonenumbers
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from jsonschema import validate, ValidationError

from .models import Product, Order, OrderItem


current_dir = os.path.dirname(__file__)
filepath = os.path.join(current_dir, 'schemas', 'order_schema.json')
with open(filepath, 'r') as schema_file:
    order_schema = json.load(schema_file)


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_params = request.data
    is_valid_order, err = check_order_params(order_params)
    if not is_valid_order:
        return Response({'error': err}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        firstname=order_params.get('firstname'),
        lastname=order_params.get('lastname'),
        phonenumber=order_params.get('phonenumber'),
        address=order_params.get('address')
    )
    product_list = order_params.get('products')

    for product_item in product_list:
        product_id = product_item.get('product')
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist as err:
            return Response(
                {'error': str(err)},
                status=status.HTTP_400_BAD_REQUEST
            )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=product_item.get('quantity')
        )
    return Response(order_params)


def check_phonenumber(phonenumber):
    err = f'Invalid phone number: {phonenumber}'
    try:
        parsed_number = phonenumbers.parse(phonenumber, region='RU')
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError(err)
    except phonenumbers.NumberParseException as e:
        raise ValidationError(err + str(e))


def check_order_params(order):
    try:
        validate(instance=order, schema=order_schema)
        check_phonenumber(order['phonenumber'])
    except ValidationError as err:
        return (False, str(err).replace("\n", " "))
    return (True, '')


