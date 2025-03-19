from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from shop.models import Product

User = get_user_model()


class ShippingAddress(models.Model):
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=254)
    apartment_address = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100, default='', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Shipping Address'
        verbose_name_plural = 'Shipping Addresses'
        ordering = ['-id']

    def __str__(self):
        return 'Shipping Address: ' + self.full_name

    def get_absolute_url(self):
        return '/payment/shipping'

    @classmethod
    def create_default_shipping_address(cls, user):
        default_shipping_address = {
            'user': user,
            'full_name': 'Noname',
            'email': 'email@example.com',
            'street_address': 'fill address',
            'apartment_address': 'fill address',
            'country': '',
        }
        shipping_address = cls(**default_shipping_address)
        shipping_address.save()

        return shipping_address


class Order(models.Model):
    total = models.DecimalField(max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    paid = models.BooleanField(default=False)
    discount = models.IntegerField(default=0, validators=(MinValueValidator(0), MaxValueValidator(100)))

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]
        constraints = [models.CheckConstraint(check=models.Q(total__gte=0), name='total_gte_0')]

    def __str__(self):
        return 'Order: ' + str(self.id)

    def get_absolute_url(self):
        return reverse('payment:order-detail', kwargs={'pk': self.pk})

    def get_total_cost_before_discount(self):
        return sum(item.get_cost() for item in self.items.all())

    @property
    def get_discount(self):
        if total_cost := self.get_total_cost_before_discount() and self.discount:
            return total_cost * (self.discount / Decimal(100))

        return Decimal(0)

    def get_total_cost(self):
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'OrderItem'
        verbose_name_plural = 'OrderItems'
        ordering = ['-id']
        constraints = [models.CheckConstraint(check=models.Q(quantity__gt=0), name='quantity__gte_0')]

    def __str__(self):
        return 'OrderItem ' + str(self.id)

    def get_cost(self):
        return self.price * self.quantity

    @classmethod
    def get_total_quantity_for_product(cls, product):
        return (
            cls.objects.filter(product=product).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
        )

    @staticmethod
    def get_average_price():
        return OrderItem.objects.aggregate(average_price=models.Avg('price'))['average_price']
