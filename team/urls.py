from django.urls import path
from . import views
#from .APIViews import CompetitionCreateView, CompetitionListView, CompetitionDetailView, CompetitionUpdateView, CompetitionDeleteView
#from .APIViews import TeamCreateView, TeamListView, TeamDetailView, TeamUpdateView, TeamDeleteView  
#from .APIViews import StaffCreateView, StaffDetailView, StaffDeleteView 
#from .APIViews import OpponentCreateView, OpponentListView, OpponentDetailView, OpponentUpdateView, OpponentDeleteView 
#from .APIViews import GameCreateView, GameListView, GameDetailView, GameUpdateView, GameDeleteView
#from .APIViews import PlayerCreateView, PlayerListView, PlayerDetailView, PlayerUpdateView, PlayerDeleteView
#from .APIViews import PlayerStatsLineCreateView, PlayerStatsLineListView, PlayerStatsLineDetailView, PlayerStatsLineUpdateView, PlayerStatsLineDeleteView        
#from .APIViews import , QuarterlyScoresListView, QuarterlyScoresDetailView, QuarterlyScoresUpdateView, QuarterlyScoresDeleteView

from .views import OpponentCreateView,  OpponentListView, OpponentDetailView, OpponentUpdateView
from .views import SeasonCreateView,  SeasonCompetitionListView, SeasonDetailView, SeasonUpdateView
from .views import CompetitionCreateView,  CompetitionUpdateView, CompetitionDeleteView
from .views import TeamCreateView,  TeamListView, TeamDetailView, TeamUpdateView
from .views import StaffCreateView,  StaffDetailView, StaffUpdateView, StaffDeleteView
from .views import PlayerCreateView,  PlayerDetailView, PlayerUpdateView#, PlayerDeleteView
from .views import GameCreateView, GameListView, GameScheduleView, GameDetailView, GameUpdateView
from .views import StandingCreateView, StandingListView

from .views import delete_opponent, delete_game, delete_player#, delete_season, team_roster
from .views import TeamDetailView

from .views import careerRecordCreate, careerRecordList, careerRecordUpdate, delete_record 


urlpatterns = [

   

    # 1. HOMEPAGE: Maps the root path to the TeamDetailView
    path('about', views.about, name='about'),
    path('help-and-support/', views.help_and_support, name='help-and-suppport'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    

    path('search/', views.search, name='search-result'),
    path('', TeamDetailView.as_view(), name='home'),

    # Season Urls
    path('season create/',SeasonCreateView.as_view(), name='season-create'),
    path('seasoncompetition_list/',SeasonCompetitionListView.as_view(), name='season-competition-list'),
    path('season_id/<slug:slug>/',SeasonDetailView.as_view(), name='season-id'),
    path('season update/<slug:slug>/',SeasonUpdateView.as_view(), name='update-season'),
    
    path('season delete/<slug:slug>/',views.delete_season, name='delete-season'),

    # Competition Urls
    path('competition create/',CompetitionCreateView.as_view(), name='competition-create'),
    #path('competitions_list/',CompetitionListView.as_view(), name='competitions-list'),

    path('competition update/<slug:slug>/',CompetitionUpdateView.as_view(), name='competition-update'),
    path('competition delete/<slug:slug>/',CompetitionDeleteView.as_view(), name='competition-delete'),


    # Teams urls
    # CBV Path for Team creation, listing, update and delete.
    path('team create/', TeamCreateView.as_view(), name='team-create'),
    path('competition/<slug:competition_slug>/team_list/', TeamListView.as_view(), name='team-list'),
    path('competition/<slug:competition_slug>/<slug:team_slug>/roster/', views.team_roster, name='team-roster'),
    path('competition/<slug:competition_slug>/team/', TeamDetailView.as_view(), name='team-id'),
    path('competition/<slug:competition_slug>/last-5-games-charts/', views.team_shot_chart, name='team-charts'),
  
    path('competition/<slug:competition_slug>/update/', TeamUpdateView.as_view(), name='update-team'),

  




    #Players Urls
    path('player create/',PlayerCreateView.as_view(), name='create-player'),
    path('competition/<slug:competition_slug>/player/<slug:slug>/', PlayerDetailView.as_view(), name='players-id'),
    path('player update/<slug:competition_slug>/player/<slug:slug>/', PlayerUpdateView.as_view(), name='update-player'),
    #path('delete player/<slug:slug>/player/<int:pk>', PlayerDeleteView.as_view(), name='delete-player'),
    path('delete player/<slug:competition_slug>/delete player/<slug:slug>/', views.delete_player, name='delete-player'),
    path('dashboard/<slug:player_slug>/statistical-analysis/', views.player_stats_charts, name='player-dashboard'),

    path('ceate-chart/', views.chartCreate, name='create-chart'),
    path('charts/<slug:player_slug>/last-5-games/', views.player_shot_chart, name='shot-charts'),
    path('edit-chart/<slug:player_slug>/', views.update_chart, name='update-chart'),
    path('delete-chart/<slug:player_slug>/', views.delete_chart, name='delete-chart'),
    
    # Career Records
    path('competition/<slug:slug>/record/create/', views.careerRecordCreate, name='create-records'),
    path('competition/<slug:slug>/record list/', views.careerRecordList, name='record-list'),
    path('competition/<slug:slug>/update record/<int:pk>/', views.careerRecordUpdate, name='update-record'),
    path('delete/record/<slug:slug>/delete/record/<int:pk>/', views.delete_record, name='delete-record'),
    #Staff Urls
    path('staff_create/',StaffCreateView.as_view(), name='create-staff'),
    path('competition/<slug:competition_slug>/staff/<slug:slug>/', StaffDetailView.as_view(), name='staff-id'),
    path('staff update/<slug:competition_slug>/staff/<slug:slug>/', StaffUpdateView.as_view(), name='update-staff'),
    path('delete staff/<slug:competition_slug>/', StaffDeleteView.as_view(), name='delete-staff'),


    #Staff Urls
    path('opponent create/',OpponentCreateView.as_view(), name='create-opponent'),
    path('opponent list/', OpponentListView.as_view(), name='opponent-list'),
    path('opponent detail/<slug:slug>/', OpponentDetailView.as_view(), name='opponent-id'),
    path('opponent update/<slug:slug>/', OpponentUpdateView.as_view(), name='update-opponent'),
    path('delete opponent/<slug:slug>/', views.delete_opponent, name='delete-opponent'),


    
    # Teams urls
    # CBV Path for Game creation, listing, update and delete.
    #path('game/create/', GameCreateView.as_view(), name='create-game'),
    path('competition/<slug:competition_slug>/game/create/', GameCreateView.as_view(), name='create-game'), 
    path('competition/<slug:competition_slug>/game/list/', GameListView.as_view(), name='game-list'),
    path('competition/<slug:competition_slug>/game/schedule/', GameScheduleView.as_view(), name='game-schedule'),
    path('competition/<slug:competition_slug>/game/<slug:game_slug>/', GameDetailView.as_view(), name='game-overview'),
    path('competition/<slug:competition_slug>/update game/<slug:game_slug>/', GameUpdateView.as_view(), name='update-game'),
    path('delete game/<slug:competition_slug>/delete game/<slug:game_slug>/', views.delete_game, name='delete-game'),

    #Game Stats To Pdf url
    path('game stats/<slug:slug>', views.game_stats_pdf, name='game-stats-pdf'),

    # Standing Url
    path('standing-create/<slug:slug>/standing/create/', StandingCreateView.as_view(), name='create-standing'), 
    path('competition/<slug:slug>/standings/', StandingListView.as_view(), name='view-standing'),
    #path('update/<slug:slug>/update standing/<int:pk>', StandingUpdateView, name='update-standing'),


    # News
    # News
    # BEFORE: path('competition/<competition_id:pk>/news create/', ... )
    path('competition/<slug:competition_slug>/news create/', views.NewsCreate, name='create-news'),
    path('competition/<slug:competition_slug>/news list/', views.NewsList, name='news-list'),
    path('competition/<slug:competition_slug>/update news/<int:pk>/', views.NewsUpdate, name='update-news'),
    path('delete record/<slug:competition_slug>/delete news/<int:pk>/', views.delete_news, name='delete-news'),
    
    # Awards 
    path('competition /award create/', views.AwardCreate, name='create-award'),
    path('competition/award list/', views.AwardList, name='award-list'),
    path('competition/update award/<int:pk>/', views.AwardUpdate, name='update-award'),

    # Contact
    path('create contact/', views.contactCreate, name='create-contact'),
    path('contact/', views.contact, name='contact'),
    path('list contact/', views.contactList, name='contact-list'),
    path('delete contact/<int:pk>/', views.delete_contact, name='delete-contact'),
    
    # Suscriber
    path('subscribe/', views.NewsletterSubscriberCreate, name='subscribe-newsletter'),
    path('list subscribers/', views.subscriberList, name='subscriber-list'),
    path('delete-subscriber/<slug:slug>/', views.delete_subscriber, name='delete-subscriber'),

    # Suscriber
    path('create image/', views.galleryCreate, name='create-image'),
    path('all-images/', views.galleryList, name='gallery'),
    path('edit image/<int:pk>/', views.update_image, name='update-image'),
    path('delete image/<int:pk>/', views.delete_image, name='delete-image'),




    
]

