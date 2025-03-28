from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Order, ShippingAddress


@shared_task()
def send_order_confirmation(order_id):
    order = Order.objects.get(id=order_id)
    subject = f'Order {order_id} payment confirmation'
    recipient_data = ShippingAddress.objects.get(user=order.user)
    recipient_email = recipient_data.email
    message = f'Your order and payment have been confirmed. Your order number is {order.id}.'

    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient_email],
    )
