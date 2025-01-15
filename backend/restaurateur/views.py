from functools import reduce

from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy

from foodcartapp.models import Product, Restaurant, Order
from foodcartapp.utils import fetch_coordinates, get_distance


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    active_orders = Order.objects.exclude(status=Order.RECEIVED)\
                                 .fetch_with_cost()\
                                 .prefetch_related('products')
    for order in active_orders:
        products = [product for product in order.products.all()]
        order_restaurants = get_available_restaurants(products)
        order_coordinates = fetch_coordinates(order.address)
        if order_coordinates:
            for restaurant in order_restaurants:
                restaurant.distance = get_distance(
                    restaurant.coordinates.get_coordinates(),
                    order_coordinates
                )
            order.restaurants = order_restaurants
    return render(request, template_name='order_items.html', context={
        'order_items': active_orders
    })


def get_available_restaurants(products):
    products_ids = [product.id for product in products]
    products = Product.objects.filter(id__in=products_ids)\
                              .prefetch_related('menu_items')
    availability = []
    for product in products:
        available_restaurants = set()
        for item in product.menu_items.all():
            if item.availability:
                available_restaurants.add(item.restaurant)
        availability.append(available_restaurants)
    return reduce(set.intersection, availability)
