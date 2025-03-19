import random
import string

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=250, db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    slug = models.SlugField(max_length=250, unique=True, editable=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        unique_together = ['parent', 'slug']

    def __str__(self):
        full_path = [self.name]
        k = self.parent

        while k is not None:
            full_path.append(k.name)
            k = k.parent

        return ' > '.join(full_path[::-1])

    @staticmethod
    def _rand_slug():
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(3))  # noqa: S311

    def save(self, *args, **kwargs):  # noqa: DJ012
        if not self.slug:
            self.slug = slugify(self._rand_slug() + '-pickBetter' + self.name)
        super(Category, self).save(*args, **kwargs)  # noqa: UP008

    def get_absolute_url(self):  # noqa: DJ012
        return reverse('shop:category-list', args=[str(self.slug)])


class Product(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/products/%Y/%m/%d', default='images/products/default.jpg')
    price = models.DecimalField(max_digits=7, decimal_places=2, default=99.99)
    discount = models.IntegerField(default=0, validators=(MinValueValidator(0), MaxValueValidator(100)))
    brand = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=250, unique=True, editable=True, null=False)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:product-detail', args=[str(self.slug)])

    def get_discount_price(self):
        discount_price = self.price - (self.price * self.discount / 100)
        return round(discount_price, 2)

    @property
    def get_full_image_url(self):
        return self.image.url if self.image else ''


class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(available=True)


class ProductProxy(Product):
    objects = ProductManager()

    class Meta:
        proxy = True
