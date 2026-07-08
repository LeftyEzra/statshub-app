from django.urls import path
from . import views

urlpatterns = [
    path('login-user', views.login_user, name='login-user'),
    path('logout-user', views.logout_user, name='logout-user'),
    path('register-user', views.register_user, name='register-user'),

    path('update-user/', views.update_user, name='update-user'),
    path('update-info/', views.update_info, name='update-info'),
    path('update-password/', views.update_password, name='update-password'),

    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.password_reset_sent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.reset_password, name='reset-password'),


]