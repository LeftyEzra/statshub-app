from django.urls import path
from . import views # from period import views
from .views import TeamStoreView
from .views import ProductCreateView



urlpatterns = [
    # 1. HOMEPAGE: Maps the root path to the TeamDetailView
    path('shop in style/', TeamStoreView.as_view(), name='grid-shop'),
    path('search product/', views.search_product, name='search-product'),
    path('add new product/', ProductCreateView.as_view(), name='add-product'),
    path('product/<slug:slug>/', views.product_detail, name='product-id'),
    path('update product/<slug:slug>/', views.product_update, name='update-product'),
    path('delete product/<slug:slug>/', views.delete_product, name='delete-product'),


    path('add new image', views.galleryCreate, name='add-product-image'),
    path('add product colors', views.colorCreate, name='add-product-colors'),
    path('add product sizes', views.sizeCreate, name='add-product-sizes'),




    
]