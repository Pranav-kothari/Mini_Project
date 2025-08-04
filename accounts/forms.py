from django import forms
from .models import Product
from .models import Address
from django.contrib.auth.models import User
from django import forms
from .models import WishlistRequest
from .models import ProductReview


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

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control' 

class WishlistRequestForm(forms.ModelForm):
    class Meta:
        model = WishlistRequest
        fields = ['product_name', 'description', 'category', 'subcategory']

class ProductReviewForm(forms.ModelForm):
    
    reviewer_name = forms.CharField(max_length=100, required=False, initial='', label="Your Name")

    title = forms.CharField(max_length=255, required=True, label="Review Title")
    review_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), label="Your Review")


    class Meta:
        model = ProductReview
        fields = ['rating', 'review_text'] # These are the form fields you expect from HTML

        
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'review_text': forms.Textarea(attrs={'rows': 4}), # Apply the widget to 'review_text'
        }

    # Custom clean method to handle data before saving to the model
    def clean(self):
        cleaned_data = super().clean()
        
        # Access the 'review_text' from the cleaned data of the form
        review_text = cleaned_data.get('review_text')
        
       
        if review_text:
            self.instance.comment = review_text
        

        return cleaned_data
