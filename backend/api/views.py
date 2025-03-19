from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from reviews.models import Review
from shop.models import Product

from .pagination import StandardResultsSetPagination
from .permissions import IsAdminOrReadOnly
from .serializers import ProductDetailSerializer, ProductSerializer, ReviewSerializer


class ProductListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('category').order_by('id')


class ProductDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductDetailSerializer
    lookup_field = 'pk'
    queryset = Product.objects.all()


class ReviewCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        product_id = self.request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        existing_review = Review.objects.filter(product=product, created_by=self.request.user).exists()

        if existing_review:
            raise ValidationError('You have already left a review for this product.')  # noqa: EM101, TRY003

        serializer.save(created_by=self.request.user, product=product)
