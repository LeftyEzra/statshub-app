from django import forms
from .models import ShippingAddress





#Update User Info
class ShippingForm(forms.ModelForm):
    class Meta:
        model   = ShippingAddress
        fields  = ('shipping_first_name', 'shipping_last_name',
                   'shipping_address1','shipping_address2', 
                   'shipping_city', 'shipping_state', 'shipping_zipcode',
                   'shipping_country', 'shipping_phone', 'shipping_email')
        exclude = ['user',]

