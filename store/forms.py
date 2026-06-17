from django import forms
from .models import Product, GalleryImages, CustomerReview, Colors, Sizes
from django.forms import inlineformset_factory



# Product Form
class ProductSizesForm(forms.ModelForm):
    class Meta:
        model = Sizes
        fields = '__all__'

# Product Color Form
class ProductColorForm(forms.ModelForm):
    class Meta:
        model = Colors
        fields = '__all__'


# Product Form
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # 🚀 CRITICAL: Use the exact model names: 'sizes' and 'colors'
        fields = ['name', 'price', 'category', 'sports', 'sizes', 'colors', 'brand_type', 'description', 'is_sales', 'sales_price', 'pieces', 'featured_player', 'image']
        
        widgets = {
            # This converts the ugly box into an easy, clean checkbox list or multi-select grid
            'sizes': forms.CheckboxSelectMultiple(),
            'colors': forms.CheckboxSelectMultiple(),
        }
        

# Order Form
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImages
        fields = '__all__'


# Order Form
class CustomerReviewForm(forms.ModelForm):
    class Meta:
        model = CustomerReview
        fields = ['customer_name', 'customer_image', 'review_message', 'rating']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'customer_image': forms.FileInput(attrs={'class': 'form-control'}),
            'review_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your review...'}),
            'rating': forms.Select(attrs={'class': 'form-select'}, choices=[(5,'★★★★★'),(4,'★★★★☆'),(3,'★★★☆☆'),(2,'★★☆☆☆'),(1,'★☆☆☆☆')]),
        }


        



