from django.db import models
from django.db.models import Sum, F, DecimalField
from django.core.validators import MinValueValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def fetch_with_cost(self):
        return self.annotate(
            cost=Sum(F('order_items__price')) * F('order_items__quantity')
        )


class Order(models.Model):
    ACCEPTED = 'accepted'
    IN_PROCESS = 'in process'
    IN_DELIVERY = 'in delivery'
    RECEIVED = 'received'
    ONLINE = 'online'
    CARD = 'by card'
    CASH = 'cash'

    STATUSES = [
        (ACCEPTED, 'Принят'),
        (IN_PROCESS, 'Собирается'),
        (IN_DELIVERY, 'В пути'),
        (RECEIVED, 'Получен')
    ]
    PAYMENT_METHODS= [
        (ONLINE, 'Картой онлайн'),
        (CARD, 'Картой при получении'),
        (CASH, 'Наличными при получении')
    ]
    products = models.ManyToManyField(
        Product,
        through='OrderItem',
        related_name='orders',
        verbose_name='продукты',
    )
    registrated_at = models.DateTimeField(
        'зарегистрирован',
        default=timezone.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        'обзвонен',
        null=True,
        blank=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        'доставлен',
        null=True,
        blank=True,
        db_index=True
    )
    payment_method = models.CharField(
        'способ оплаты',
        max_length=7,
        choices=PAYMENT_METHODS,
        default=CASH,
        db_index=True
    )
    firstname = models.CharField(
        'имя',
        max_length=50
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50,
        blank=True,
    )
    phonenumber = PhoneNumberField(
        'номер телефона'
    )
    address = models.TextField(
        'адрес доставки'
    )
    status = models.CharField(
        'статус',
        max_length=11,
        choices=STATUSES,
        default=ACCEPTED,
        db_index=True
    )
    comment = models.TextField(
        'комментарий',
        blank=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"Заказ №{self.id} по адресу {self.address}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='продукт',
    )
    price = models.DecimalField(
        'стоимость заказа',
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveIntegerField(
        'количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'
        unique_together = [
            ['order', 'product']
        ]

    def __str__(self):
        return f"{self.order}: {self.product} - {self.quantity} штук"
