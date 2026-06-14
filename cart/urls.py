from django.urls import path
from . import views # from period import views



urlpatterns = [


    #Cart URLs
    
    path('cart-summary/', views.cart_summary, name='cart-summary'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('update/', views.update_cart, name='update-cart-item'),
    path('delete/', views.delete_cart, name='delete-cart-item'),
    #path('checkout/', views.checkout, name='checkout'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),

    
]