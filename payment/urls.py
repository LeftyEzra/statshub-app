from django.urls import path
from . import views # from period import views




urlpatterns = [


        path('checkout', views.checkout, name='checkout'),
        path('order-confirmation/<uuid:order_id>/', views.order_confirmation, name='order-confirmation'),
        path('order details/<uuid:order_id>/', views.order_details, name='order-details'),
        path('payment-success/', views.payment_success, name='payment-success'),
        path('admin dashboard/', views.admin_dashboard, name='admin-dashboard'),



]