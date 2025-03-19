from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from .views import ProductDetailAPIView, ProductListAPIView, ReviewCreateAPIView

app_name = 'api'

schema_view = get_schema_view(
    openapi.Info(
        title='E-commerce API',
        description='E-commerce API Description',
        default_version='v1',
        terms_of_service='https://policies.google.com/',
        contact=openapi.Contact(email='admin@ecommerce.com'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
)

urlpatterns = [
    path('products/', ProductListAPIView.as_view()),
    path('products/<int:pk>/', ProductDetailAPIView.as_view()),
    path('reviews/create/', ReviewCreateAPIView.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
