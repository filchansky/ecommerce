from django import forms

from .models import ShippingAddress


class ShippingAddressForm(forms.ModelForm):

    class Meta:
        model = ShippingAddress
        fields = ('full_name', 'email', 'apartment_address', 'street_address', 'city', 'country', 'zip_code')
        exclude = ('user',)
