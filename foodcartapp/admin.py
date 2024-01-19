from django.contrib import admin
from django.shortcuts import reverse, redirect, get_object_or_404

from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order
from .models import OrderItem
from .serializers import RestaurantSerializer
from .utils import fetch_coordinates
from locations.models import Location
import star_burger.settings as settings


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]

    def save_model(self, request, obj, form, change):
        serializer = RestaurantSerializer(data=request.POST)
        if serializer.is_valid(raise_exception=True):
            try:
                location = Location.objects.get(address=obj.address)
            except Location.DoesNotExist:
                lon, lat = fetch_coordinates(obj.address)
                location = Location.objects.create(
                    lat=lat,
                    lon=lon,
                    address=obj.address
                )
            obj.coordinates = location
            super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'address',
    ]
    list_display = [
        'registered_at',
        'status',
        'restaurant',
        'payment_method',
        'cost',
        'address',
        'firstname',
        'lastname',
    ]
    inlines = [
        OrderItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'cost',
                'payment_method',
                'status',
                'restaurant',
                'registered_at',
                'called_at',
                'delivered_at',
                'address',
                'firstname',
                'lastname',
                'phonenumber',
            ]
        }),
    )
    readonly_fields = [
        'cost',
        'registered_at',
    ]
    list_editable = [
        'status',
        'payment_method',
        'restaurant',
    ]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.price = instance.product.price
            instance.save()
        formset.save_m2m()
        super().save_formset(request, form, formset, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.fetch_with_cost()

    def cost(self, obj):
        return f'{obj.cost} руб.'
    cost.short_description = 'Стоимость'

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        if ("next" in request.GET and
            url_has_allowed_host_and_scheme(request.GET['next'],
                                            settings.ALLOWED_HOSTS)):
                return redirect(request.GET['next'])
        else:
            return res
