from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from shop.models import Product

User = get_user_model()


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=(MinValueValidator(1), MaxValueValidator(5)))
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.created_by} on Product: {self.product}'
