from django.urls import path
from . import views
from .views import CompetitionsCreateView#, CompetitionListView, CompetitionDetailView, CompetitionUpdateView, CompetitionDeleteView

#from .views import TeamListAPI

urlpatterns = [
    path('data/', views.getData, name='api-data'),
    #path('competition-create/',CompetitionsCreateView.as_view(), name='competition_create'),

    
    #path('teamList/',TeamListAPI.as_view(), name='team-data'),
    #path('register_user', views.register_user, name='register-user'),


]