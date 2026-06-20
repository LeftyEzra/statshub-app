from django.urls import path
from . import views
from .views import CompetitionsCreateView#, CompetitionListView, CompetitionDetailView, CompetitionUpdateView, CompetitionDeleteView


#from .APIViews import CompetitionCreateView, CompetitionListView, CompetitionDetailView, CompetitionUpdateView, CompetitionDeleteView
#from .APIViews import TeamCreateView, TeamListView, TeamDetailView, TeamUpdateView, TeamDeleteView  
#from .APIViews import StaffCreateView, StaffDetailView, StaffDeleteView 
#from .APIViews import OpponentCreateView, OpponentListView, OpponentDetailView, OpponentUpdateView, OpponentDeleteView 
#from .APIViews import GameCreateView, GameListView, GameDetailView, GameUpdateView, GameDeleteView
#from .APIViews import PlayerCreateView, PlayerListView, PlayerDetailView, PlayerUpdateView, PlayerDeleteView
#from .APIViews import PlayerStatsLineCreateView, PlayerStatsLineListView, PlayerStatsLineDetailView, PlayerStatsLineUpdateView, PlayerStatsLineDeleteView        
#from .APIViews import , QuarterlyScoresListView, QuarterlyScoresDetailView, QuarterlyScoresUpdateView, QuarterlyScoresDeleteView

#from .views import TeamListAPI

urlpatterns = [
    path('data/', views.getData, name='api-data'),
    #path('competition-create/',CompetitionsCreateView.as_view(), name='competition_create'),

    
    #path('teamList/',TeamListAPI.as_view(), name='team-data'),
    #path('register_user', views.register_user, name='register-user'),


]