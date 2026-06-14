from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import mixins

from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.http import JsonResponse # Cart view
from django.contrib import messages
from django.db.models import Q



from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import  ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied 
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
import csv

from calendar import HTMLCalendar
from django .utils import timezone
from datetime import datetime
import datetime as dt

from .models import Product, GalleryImages, Colors, Sizes
from .forms import ProductForm, ProductImageForm, CustomerReviewForm, ProductColorForm, ProductSizesForm




def is_superuser(user):
    # Checks if the user is authenticated AND is a superuser.
    # If the user is not authenticated, they will be redirected to settings.LOGIN_URL.
    return user.is_authenticated and user.is_superuser # For the user_passes_test imported



# Define the Custom Mixin to handle 403 response
class SuperuserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        
        # Check if the user fails the test
        if not is_superuser(request.user):
            # If the test fails, explicitly raise the 403 exception.
            # This triggers Django to render error.html template.
            raise PermissionDenied 
            
        # If the test passes, continue to the original view dispatch method
        return super().dispatch(request, *args, **kwargs)

###############################################################################################
###############################################################################################
###############################################################################################
def search_product(request):
    # 's' matches  HTML <input name="s">
    query = request.GET.get('s', '').strip()

    if not query: # if nothing is searched and the user hit the search icon
        messages.warning(request, "Please enter a search term.")
        return render(request, 'grid-shop.html')

    
    searched_products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sports__icontains=query) |
            Q(category__icontains=query) |
            #Q(sizes__icontains=query) |   
            #Q(colors__icontains=query) |
            Q(brand_type__icontains=query) |
            Q(gender_type__icontains=query)
        ).order_by('name')
    #print(f"--- DEBUG ---")
    #print(f"Query typed: {query}")
    #print(f"Items found in DB: {searched_products.count()}")
    if searched_products.exists(): # if products searched exits in the database
        count = searched_products.count() #Count the number of the particuilar product
        print(count)
       
    else:
        messages.info(request, f'No results found for "{query}".')

    return render(request, 'grid-shop.html', {
        'searched': query,
        'searched_query': searched_products # Use 'products' to match your shop's variable name
    })


###############################################################################################
###############################################################################################
###############################################################################################


@user_passes_test(is_superuser, login_url='/')
def colorCreate(request):
    if request.method == "POST":
        form = ProductColorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, "Color Added Successfully ):)")
            return redirect('add-product-color')
            
        else:
            pass
    else: 
        form = ProductColorForm()

    return render(request, 'product-color-create.html', {"form" : form,}) 

@user_passes_test(is_superuser, login_url='/')
def sizeCreate(request):
    if request.method == "POST":
        form = ProductSizesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, "Size Added Successfully ):)")
            return redirect('add-product-sizes')
            
        else:
            pass
    else: 
        form = ProductSizesForm()

    return render(request, 'product-sizes-create.html', {"form" : form,})     




SPORT_CATEGORY = (
    ('Basketball🏀', 'Basketball🏀'),('Boxing🥊', 'Boxing🥊'),
    ('Badmington🏸', 'Badmington🏸'),('Gym⛹', 'Gym⛹'),('Soccer⚽ ', 'Soccer⚽ '),('Football🏈⚽', 'Football🏈⚽'),
    ('Tracks & Fields🏃', 'Tracks & Fields🏃'), ('Rugby🏉', 'Rugby🏉'),('Volleyball🏐', 'Volleyball🏐'),
    ('Ping Pong🎾', 'Ping Pong🎾'),('Cricket', 'Cricket'),('Lawn Tennis🎾', 'Lawn Tennis🎾'),
)
class TeamStoreView(APIView):
    def get(self, request):
        # The base queryset
        products = Product.objects.all().order_by('name')
        product_sizes = Sizes.objects.all()
        product_colors = Colors.objects.all()
        print("SIZES")
        print(product_sizes)
        
        products_with_featured = Product.objects.filter(featured_player__isnull=False).order_by('name')

        # Filtering values from the URL
        sport_val = request.GET.get('sports')
        category_val = request.GET.get('category')
        selected_size = request.GET.get('sizes')
        selected_color = request.GET.get('colors')
        gender_val = request.GET.get('gender_type')
        

        # FILTRING APPLICATION
        if sport_val:
            products = products.filter(sports=sport_val)

        if category_val:
            products = products.filter(category=category_val)
        
        # Filters by the ID or Primary Key of the Size instance
        if selected_size:
            products = products.filter(sizes__pk=selected_size).distinct()

        if selected_color:
            products = products.filter(colors__pk=selected_color).distinct()    

        if gender_val:
            products = products.filter(gender_type=gender_val)

        # PAGINATE FILTERED RESULTS
        paginator = Paginator(products, 20) 
        page_number = request.GET.get('page')
        product_objs = paginator.get_page(page_number)

        
        context = {
            'products': product_objs,  
            'gender_list': [('Unisex', 'Unisex'), ('Male', 'Male'), ('Female', 'Female')],
            
            'sport_list' : SPORT_CATEGORY,
            'products_with_featured': products_with_featured, 
            'product_sizes': product_sizes,
            'product_colors': product_colors,
        }

        return render(request, 'grid-shop.html', context)



@method_decorator(user_passes_test(is_superuser, login_url='/'), name='dispatch')
class ProductCreateView(SuperuserRequiredMixin, APIView):
    def get(self, request,):
        form = ProductForm()
        return render(request, 'product-registration.html', {"form": form, })

    def post(self, request,):
        form = ProductForm(request.POST, request.FILES) 
        if form.is_valid():
            # SUCCESS PATH
            product = form.save()    
            messages.success(request, "Product Added Successfully :)")
            # Redirect to GET endpoint to clear the form data
            return redirect('add-product')
        else:
            # FAILURE PATH
            messages.error(request, "There were errors in the form. Please correct them and try again.")
            
            # 🚀 FIX: Only return the form object, not the non-existent 'team' object
            return render(request, 'product-registration.html', {"form": form,})

# Product view page


# Function Base View For Product Details
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_sizes = product.sizes
    print("SIZES")
    print(product_sizes)

    
    if request.method == "POST":
        form = CustomerReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.save()
            messages.success(request, "Review Added Successfully :)")
            return redirect('product-id', slug=product.slug)
    else:
        form = CustomerReviewForm()

    context = {
        "product_details": product,
        "reviews": product.reviews.all(),
        "stars": range(1, 6),
        "form": form,
        "product_images": GalleryImages.objects.filter(product=product),
    }
    return render(request, "product-page.html", context)


  
@user_passes_test(is_superuser, login_url='/')
def product_update(request, slug): 
   
    update_product = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=update_product)
        if form.is_valid():
            form.save() 
            messages.success(request, "Product Updated Successfully! :)")
            return redirect('product-id', slug=update_product.slug)
    else: 
        # 3. Initialize the form with the existing data
        form = ProductForm(instance=update_product)

    return render(request, 'product-update.html', {
        "form": form, 
       
        "update_product": update_product
    })


# Delete
@user_passes_test(is_superuser, login_url='/')
def delete_product(request, slug): 
    
    delete_product = get_object_or_404(Product, slug=slug)
    delete_product.delete()
    return redirect('grid-shop')

#######################################################################################
###########################################Customer Rieviews ##########################
########################################################################################


#######################################################################################
######################################################################################
########################################################################################
@user_passes_test(is_superuser, login_url='/')
def galleryCreate(request):
    if request.method == "POST":
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, "Image Added Successfully ):)")
            return redirect('add-product-image')
            
        else:
            pass
    else: 
        form = ProductImageForm()

    return render(request, 'gallery-product-create.html', {"form" : form,}) 

  


