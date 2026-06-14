from django.urls import path
from . import views # from period import views




urlpatterns = [

        path('services/fitness/', views.fitness_services, name='fitness-services'),
        path('services/kitchen/', views.kitchen_services, name='kitchen-services'),
        path('basketball/coaching/', views.basketball_coaching, name='basketball-coaching'),
]