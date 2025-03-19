from django.urls import path

from .views import admin_order_pdf, checkout, complete_order, payment_fail, payment_success, shipping
from .webhook import stripe_webhook

app_name = 'payment'

urlpatterns = [
    path('shipping/', shipping, name='shipping'),
    path('checkout/', checkout, name='checkout'),
    path('complete-order/', complete_order, name='complete-order'),
    path('payment-success/', payment_success, name='payment-success'),
    path('payment-fail/', payment_fail, name='payment-fail'),
    path('webhook-stripe/', stripe_webhook, name='webhook-stripe'),
    path('order/<int:order_id>/pdf/', admin_order_pdf, name='admin-order-pdf'),
]
