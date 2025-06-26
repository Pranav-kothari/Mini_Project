from django import forms
from .models import Product
from .models import Address

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'image']  # Jo bhi fields hain model me

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'full_name', 'phone_number', 'address_line_1', 'address_line_2',
            'city', 'state', 'pincode', 'country', 'is_default'
        ]
        widgets = {
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }