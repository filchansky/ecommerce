from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from cart.cart import Cart

from .forms import ShippingAddressForm
from .models import Order, OrderItem, ShippingAddress

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


@login_required(login_url='account:login')
def shipping(request):
    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
    except ShippingAddress.DoesNotExist:
        shipping_address = None

    form = ShippingAddressForm(instance=shipping_address)

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)

        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()

            return redirect('account:dashboard')

    return render(request, 'shipping/shipping.html', {'form': form})


@login_required(login_url='account:login')
def checkout(request):
    shipping_address, _ = ShippingAddress.objects.get_or_create(user=request.user)

    if shipping_address:
        context = {
            'title': 'Checkout',
            'shipping_address': shipping_address,
        }

        return render(request, 'payment/checkout.html', context)

    return render(request, 'payment/checkout.html')


@login_required(login_url='account:login')
def complete_order(request):
    if request.method == 'POST':
        payment_type = request.POST.get('stripe-payment')

        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        apartment_address = request.POST.get('apartment_address')
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        zip_code = request.POST.get('zip_code')

        cart = Cart(request)
        total_price = cart.get_total_price()

        if payment_type == 'stripe-payment':
            shipping_address, _ = ShippingAddress.objects.get_or_create(
                user=request.user,
                defaults={
                    'full_name': full_name,
                    'email': email,
                    'apartment_address': apartment_address,
                    'street_address': street_address,
                    'city': city,
                    'country': country,
                    'zip_code': zip_code,
                },
            )

            session_data = {
                'mode': 'payment',
                'success_url': request.build_absolute_uri(reverse('payment:payment-success')),
                'cancel_url': request.build_absolute_uri(reverse('payment:payment-fail')),
                'line_items': [],
            }

            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                total=total_price,
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['qty'],
                    user=request.user,
                )
                session_data['line_items'].append(
                    {
                        'price_data': {
                            'unit_amount': int(item['price'] * Decimal(100)),
                            'currency': 'usd',
                            'product_data': {
                                'name': item['product'],
                            },
                        },
                        'quantity': item['qty'],
                    },
                )

            session_data['client_reference_id'] = order.id
            session = stripe.checkout.Session.create(**session_data)

            return redirect(session.url, code=303)


def payment_success(request):
    for key in list(request.session.keys()):
        if key == 'session_key':
            del request.session[key]

    return render(request, 'payment/payment_success.html')


def payment_fail(request):
    return render(request, 'payment/payment_fail.html', {'title': 'Payment fail'})


def admin_order_pdf(request, order_id):
    try:
        order = Order.objects.select_related('user', 'shipping_address').get(id=order_id)
    except Order.DoesNotExist:
        raise Http404('Order not found')

    html = render_to_string('payment/order/pdf/pdf_invoice.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    css_path = static('payment/css/pdf_invoice.css').lstrip('/')
    stylesheets = [weasyprint.CSS(css_path)]
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)

    return response
