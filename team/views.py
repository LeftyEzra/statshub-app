from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import mixins


from team.models import Season, Competition, Team, TeamStaff, Game, Player, PlayerStatLine, QuarterlyScores, Opponent, CareerRecords, Standing, TeamNews, GalleryImages, Awards
from team.models import Contact, NewsletterSubscriber, ShotCharts
from store.models import Product
from .forms import SeasonForm, OpponentForm, CompetitionForm, TeamForm, TeamStaffForm, PlayerForm, GameForm, QuarterlyScoresForm, PlayerStatLineForm, StandingForm, TeamNewsForm
from .forms import SponsorForm, CareerRecordsForm, AwardsForm, ContactForm, NewsletterSubscriberForm, GalleryImagesForm, ShotChartForm

from datetime import datetime, timedelta # Module to represent the difference between two dates
from django.utils.timezone import now
from django.contrib import messages
from django .utils import timezone
from calendar import HTMLCalendar
from datetime import date
from datetime import datetime
import datetime as dt


from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import  ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied 
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
import csv


from django.forms import modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q


from django.db.models import Sum, F, Value, IntegerField,ExpressionWrapper, FloatField
from django.db.models.functions import Cast # Casting string to integer
from datetime import datetime, timedelta # Module to represent the fifference between two dates
from django.utils.timezone import now
from django .utils import timezone
from calendar import HTMLCalendar
import plotly.graph_objects as go
from operator import itemgetter
from datetime import date
import pandas as pd
import plotly  # This is needed for PlotlyJSONEncoder
import json


# NEW IMPORTS REQUIRED FOR HTML EMAIL:
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import logging
logger = logging.getLogger(__name__)


#To geneate pdf
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, landscape
from django.http import FileResponse
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io


from django.core.files.storage import default_storage



from store.models import Product



####################################################################################
####################################################################################
# Registration forms for testing purposes
####################################################################################
####################################################################################    

#PlayerFormSet = inlineformset_factory(Team, Player, form=PlayerForm, extra=1, can_delete=False, max_num=15)

def is_superuser(user):
    # Checks if the user is authenticated AND is a superuser.
    # If the user is not authenticated, they will be redirected to settings.LOGIN_URL.
    return user.is_authenticated and user.is_superuser # For the user_passes_test imported

"""
def is_superuser(user):
    # Check if the user fails the test
    if not user.is_authenticated and user.is_superuser:
        # If the test fails, explicitly raise the 403 exception.
        # This triggers Django to render error.html template.
        raise PermissionDenied 
    # Checks if the user is authenticated AND is a superuser.
    # If the user is not authenticated, they will be redirected to settings.LOGIN_URL.
    return user.is_authenticated and user.is_superuser # For the user_passes_test imported
"""


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




# View to handle all registrations forms
@user_passes_test(is_superuser)
def registration_page(request):
    return render(request, 'registrations.html', {})

####################################################################################
####################################################################################
# Season Create View
####################################################################################
####################################################################################
# Using the generic view of django

class SeasonCreateView(SuperuserRequiredMixin, CreateView):
    model = Season
    form_class = SeasonForm
    template_name = 'season_registration.html'
    success_url = '/season_competition_list/'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            season_form = self.get_form()
            if season_form.is_valid():
                messages.success(request, "Season Added Successfully :)")
                return self.form_valid(season_form)

            else:
                return self.form_invalid(season_form)
        return super().post(request, *args, **kwargs)


#Season List View

class SeasonCompetitionListView(APIView):
    def get(self, request):
        competitions = Competition.objects.all().order_by('name')
        seasons = Season.objects.all().order_by('year')
        
        return render(request, 'season_competition_list.html', {
            'competitions': competitions,
            'seasons': seasons,
            
        })


# Class Base View For Team Details
class SeasonDetailView(View):
    def get(self, request, slug):
        season_details = get_object_or_404(Season, slug=slug)
        
        context = {
                'season_details': {
                'pk': season_details.slug,  # Include the primary key
                'year': season_details.year,
                'name': season_details.name,
                'is_current_season': season_details.is_current_season,
                },
            }

        return render(request, 'season_details.html', context)


# Class Base View For Update
@method_decorator(user_passes_test(is_superuser, login_url='/'), name='dispatch')
class SeasonUpdateView(View):
    # Handle GET and POST requests to UPDATE team details
    def get(self, request, slug):
        season_update = get_object_or_404(Season, slug=slug)
        form = SeasonForm(request.POST or None, instance=season_update)
        return render(request, 'season_update.html', {'form': form, 'season_updates': season_update})

    def post(self, request, slug):
        season_updates = get_object_or_404(Season, slug=slug)
        form = SeasonForm(request.POST, request.FILES, instance=season_updates)
        

        if form.is_valid():
            form.save()
            messages.success(request, (" Season Updated Sucessfully ):")) # Return a valid update message.
            return redirect('season-competition-list',)
        return render(request, 'season_update.html', {'form': form, 'season_updates': season_updates})    


# Function Base View For Deleting 
# DELETE SEASON

@user_passes_test(is_superuser, login_url='/')
def delete_season(request, slug):
    season = get_object_or_404(Season, slug=slug)
    season.delete()
    # Return an error message.
    messages.success(request, (" Season deleted successfully ):"))
    return redirect('season-competition-list',)        


####################################################################################
####################################################################################
# Competition
####################################################################################
####################################################################################
# Using the generic view of django
# Class Base View Creating Competition
# Class Base View For Update
@method_decorator(user_passes_test(is_superuser, login_url='/'), name='dispatch')
class CompetitionCreateView(View):
    def get(self, request):
        form = CompetitionForm()
        return render(request, 'competition_registration.html', {"form": form,})

    def post(self, request):
        form = CompetitionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Competition Added Successfully :)")
            
            # This safely looks up your path name 'competition-create' dynamically
            return HttpResponseRedirect(reverse('competition-create'))
            
        else:
            messages.error(request, "There were errors in the form. Please correct them and try again.")
        
        return render(request, 'competition_registration.html', {"form": form})


#Season List View
class CompetitionListView(APIView):
    def get(self, request):
        pass
   


# Class Base View For Team Details
class CompetitionDetailView(APIView):
    def get(self, request, slug):
        pass
        #season_details = get_object_or_404(Season, pk=pk)
        #competition = get_object_or_404(Competition, pk=competition_id)

        """context = {
                'season_details': {
                'pk': season_details.pk,  # Include the primary key
                'year': season_details.year,
                'name': season_details.name,
                'is_current_season': season_details.is_current_season,
                },
            }

        return render(request, 'season_details.html', context)"""


# Class Base View For Update
class CompetitionUpdateView(SuperuserRequiredMixin, View):
    # Handle GET and POST requests to UPDATE team details
    def get(self, request, slug):
        competition_update = get_object_or_404(Competition, slug=slug)
        form = CompetitionForm(request.POST or None, instance=competition_update)
        return render(request, 'competition_update.html', {'form': form, 'competition_updates': competition_update})

    def post(self, request, slug):
        competition_updates = get_object_or_404(Competition, slug=slug)
        form = CompetitionForm(request.POST, request.FILES, instance=competition_updates)

        if form.is_valid():
            form.save()

            # Return a valid update message.
            messages.success(request, (" Competition Updated Sucessfully ):"))
            return redirect('season-competition-list',)
        return render(request, 'competition_update.html', {'form': form, 'competition_updates': competition_updates})    


# Function Base View For Deleting 
# DELETE COMPETITION
class CompetitionDeleteView(SuperuserRequiredMixin, APIView):
    def delete(self, request, slug):
        competition = get_object_or_404(Competition, slug=slug)
        competition.delete()
        return redirect('season-competition-list') 
              

####################################################################################
####################################################################################
####################################################################################
# About View
def about(request):
    return render(request, 'about-us.html', {})  

### Support and Help
def help_and_support(request):
    return render(request, 'support.html', {})

### Privacy Policy
def privacy_policy(request):
    return render(request, 'privacy-policy.html', {})    
    
              
####################################################################################
# Team View
####################################################################################
####################################################################################

# Class Base View Creating Team

class TeamCreateView(SuperuserRequiredMixin, View):
    def get(self, request):
        form = TeamForm()
        return render(request, 'team_registration.html', {"form": form, })

    def post(self, request):
        form = TeamForm(request.POST, request.FILES) 
        
        if form.is_valid():
            # SUCCESS PATH
            team = form.save()    
            messages.success(request, "Team Added Successfully :)")
            # Redirect to GET endpoint to clear the form data
            return HttpResponseRedirect('/team_create?')
        else:
            # FAILURE PATH
            messages.error(request, "There were errors in the form. Please correct them and try again.")
            
            # 🚀 FIX: Only return the form object, not the non-existent 'team' object
            return render(request, 'team_registration.html', {"form": form})
#  Class Base View For Opponent List
class TeamListView(View):
    def get(self, request, competition_slug, ): 
        
        competition = get_object_or_404(Competition, slug=competition_slug)
       
        #games = get_object_or_404(Game, pk=game_id, competition=competition).distinct().order_by('date')
        team = competition.team
        
        
        return render(request, 'team_list.html', {'team':team})   








# Function to convert date of birth of players to number
def calculate_age(birthdate):
    if birthdate is None:
        return None
        
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

"""
class TeamDetailView(APIView):
    def get(self, request, competition_id=None, team_id=None): 
        
        # HANDLE SPECIFIC TEAM/COMPETITION (Dynamic URL)
        if competition_id and team_id: 
            try:
                competition = get_object_or_404(Competition, pk=competition_id)
                team_details = get_object_or_404(Team, pk=team_id) 
            except Http404:
                # Error rendering uses the designated home.html template
                return render(request, 'home.html', {'error':'Competition and Team not found.'})

        # HANDLE HOMEPAGE (Default Content )
        else:
            # Find the current competition
            competition = Competition.objects.filter(is_current_competition=True).first()
            if not competition:
                return render(request, 'home.html', {'error': 'No current competition set.'})

            # Get the single team object associated with the current competition.
            team_details = competition.team_competition.all().first()
            if not team_details:
                return render(request, 'home.html', {'error': 'No team found for current competition.'})

        # --- CODE RUNNING FOR BOTH CASES (Data Aggregation) ---
        
        team = team_details
        opponents = competition.opponents.all().order_by('name')
        games = competition.competition.all().order_by('date') 
        staff = TeamStaff.objects.filter(team=team) 
        players = team.players.all()
        news =  TeamNews.objects.filter( competition=competition,)
        t_images = GalleryImages.objects.filter(team=team)
        #SEt up pagination
        p = Paginator(GalleryImages.objects.all(), 6) # Pass the queryset, not the method
        page = request.GET.get('page')
        team_images = p.get_page(page)
        nums = "a" * team_images.paginator.num_pages
       
        
        
        # Fetch standings and the related game type
        tournament_standing = Standing.objects.filter( competition=competition,).select_related('team', 'opponent',)

        all_games = competition.competition.all().prefetch_related('quarterly_scores')
        #  Returns only the stats for the games in this competition.
        all_game_stats = PlayerStatLine.objects.filter(game_schedule__in=all_games)
     
       
        #######################################################################################################
        ######################################################################################################
        #######################################################################################################
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
        # All Game Statistics
        all_game_stats_df = pd.DataFrame(
                        all_game_stats.values('player_name__id', 'game_schedule__date', 'player_name__player_image','player_name__player_name', 'team__name', 'points', 'assists', 'blocks',
                                              'steals','offensive_rebs', 'defensive_rebs', 'game_schedule__game_type', 'game_schedule__team_scores',
                                              'game_schedule__opponent_scores', 'point_3_attempts', 'point_3_made',
                                              'field_goal_attempts', 'field_goal_made', 'ft_attempts', 'ft_made','turnovers'))

        all_game_stats_df = all_game_stats_df.rename(columns={'player_name__id':'player_id', })  
          
                                                                          
        all_game_stats_df['total_rebounds'] = all_game_stats_df['offensive_rebs'] + all_game_stats_df['defensive_rebs']  
   
        # Calculation the efficiency of the games
        all_game_stats_df["efficiency"] = (
                                    all_game_stats_df["points"]
                                    + all_game_stats_df["total_rebounds"]
                                    + all_game_stats_df["assists"]
                                    + all_game_stats_df["steals"]
                                    + all_game_stats_df["blocks"]
                                    - (
                                        (all_game_stats_df["field_goal_attempts"] - all_game_stats_df["field_goal_made"])
                                        + (all_game_stats_df["ft_attempts"] - all_game_stats_df["ft_made"])
                                        + all_game_stats_df["turnovers"]
                                    )
                                )
          
        # Players Defense Calculation
        all_game_stats_df['def'] = all_game_stats_df['steals'] * 2 + all_game_stats_df['blocks'] * 2 + all_game_stats_df['defensive_rebs'] * 0.5 
        # Getting the regular season and playoffs games
        regular_season = all_game_stats_df[all_game_stats_df['game_schedule__game_type'].isin(["regular"])]
        regular_season= regular_season[~regular_season['game_schedule__team_scores'].isin([0])]

        # Function to get per game stats leaders
        def stats_leaders_per_game(stat):
            leaders_per_game = (
                regular_season.groupby(
                    ["player_id","player_name__player_name",'player_name__player_image',]
                )[['points', 'total_rebounds','assists', 'blocks', 'steals', 'efficiency', 'def',]].mean().sort_values(stat, ascending=False).reset_index()
            )
            return leaders_per_game
        
        
        # These lines is to call the function
        pts_per_game = stats_leaders_per_game('points').head(3)
        reb_per_game = stats_leaders_per_game('total_rebounds').head(3)
        ast_per_game = stats_leaders_per_game('assists').head(3) 
        blk_per_game = stats_leaders_per_game('blocks').head(3)
        stl_per_game = stats_leaders_per_game('steals').head(3)
        eff_per_game = stats_leaders_per_game('efficiency').head(3)
        def_per_game = stats_leaders_per_game('def').head(3)
        #######################################################################################################
        ######################################################################################################
        #######################################################################################################
        mean_opp_points = regular_season.groupby(['game_schedule__date'])['game_schedule__opponent_scores'].mean().mean().round(1)
        mean_points = regular_season.groupby(['game_schedule__date'])['points'].sum().mean().round(1)
        mean_rebounds = regular_season.groupby(['game_schedule__date'])['total_rebounds'].sum().mean().round(1)
        mean_assists = regular_season.groupby(['game_schedule__date'])['assists'].sum().mean().round(1)                      
        #######################################################################################################
        ######################################################################################################
        #######################################################################################################
        # 1. Calculate Percents
        team_fg_pct = ((regular_season['field_goal_made'].sum() / regular_season['field_goal_attempts'].sum()) * 100).round(1)
        team_3p_pct = ((regular_season['point_3_made'].sum() / regular_season['point_3_attempts'].sum()) * 100).round(1)
        team_ft_pct = ((regular_season['ft_made'].sum() / regular_season['ft_attempts'].sum()) * 100).round(1)
        # views.py
        

        print(team_fg_pct)
        print(team_3p_pct)
        print(team_ft_pct)
        # 2. Logic for League Ranking (Example)
        # league_avg_3p = 35.0
        # rank = "1st" if team_3p_pct > 40 else "Top 10"
        
     
        #######################################################################################################
        ######################################################################################################
        #######################################################################################################


        # 2. Convert to DataFrame
        standing_df = pd.DataFrame(
            tournament_standing.values( 'competition__name', 'game_type',
                'team__name', 'team__team_logo', 
                'opponent__name', 'opponent__logo',
                'w', 'l', 'home_record', 'away_record', 
                'ppg', 'opp_ppg', 'strk', 'last_5', 
            )
        ).sort_values('w', ascending=False).reset_index(drop=True)


        standing_df['team__name'] = standing_df['team__name'].fillna(standing_df['opponent__name'])
        standing_df['opponent__name'] = standing_df['opponent__name'].fillna(standing_df['team__name'])
        standing_df['team__team_logo'] = standing_df['team__team_logo'].fillna(standing_df['opponent__logo'])                             
        standing_df['opponent__logo'] = standing_df['opponent__logo'].fillna(standing_df['team__team_logo'])
        #######################################################################################################
        ######################################################################################################
        #######################################################################################################
        
        # Calculate age for the filtered players
        for player in players:
            player.age = calculate_age(player.date_of_birth) 

        # 4. Prepare Context
        context = {
            'team_detail': {
                'pk': team.pk, 
                'team_logo': team.team_logo.url if team.team_logo else None,
                'name': team.name,
                
            },
            'competition': competition,
            'players': players,
            'opponents': opponents,
            'staff': staff,
            'games': games,
            'team': team,
            'news': news,
            'standing_df': standing_df.to_dict('records'),
            #Top Leaders
            'pts_per_game': pts_per_game.to_dict('records'),
            'reb_per_game': reb_per_game.to_dict('records'),
            'ast_per_game': ast_per_game.to_dict('records'),
            'blk_per_game': blk_per_game.to_dict('records'),
            'stl_per_game': stl_per_game.to_dict('records'),
            'eff_per_game': eff_per_game.to_dict('records'),
            'def_per_game': def_per_game.to_dict('records'),
            # Team Average Stats
            'mean_points': mean_points,
            'mean_rebounds': mean_rebounds,
            'mean_assists': mean_assists,
            'mean_opp_points': mean_opp_points,
            # Pecent Section
            'team_fg_pct': team_fg_pct,
            'team_ft_pct': team_ft_pct,
            'team_3p_pct': team_3p_pct,
            # News Section
            'hot_news': TeamNews.objects.filter(competition=competition, category='Hot').order_by('-published_date')[:1],
            'team_news': TeamNews.objects.filter(competition=competition, category='Team').order_by('-published_date')[:2],
            'league_news': TeamNews.objects.filter(competition=competition, category='League')[:1],
            'spotlight_news': TeamNews.objects.filter(competition=competition, category='Spotlight').order_by('-published_date')[:4],
            'sidebar_news': TeamNews.objects.filter(competition=competition).order_by('-published_date')[:5],
            'base_news': TeamNews.objects.filter(competition=competition, category='Base').order_by('-published_date'),
            # Regular Season Games
            'regular_season_games_df': Game.objects.filter(competition=competition, game_type='regular').order_by('date'),
            'international_games': Game.objects.exclude(competition=competition).order_by('date'),
            # Gallery Images
            'team_images': team_images,
            
            'nums': nums,
            'awards' : Awards.objects.all().order_by('date'),
        
            # All products
            'products' : Product.objects.all().order_by('name')
        }
        # Renders the detailed data using the home.html template
        return render(request, 'home.html', context)
"""

class TeamDetailView(APIView):
    def get(self, request, competition_slug=None, team_slug=None): 
        
        # HANDLE SPECIFIC TEAM/COMPETITION (Dynamic URL)
        if competition_slug and team_slug: 
            try:
                competition = get_object_or_404(Competition, slug=competition_slug)
                team_details = get_object_or_404(Team, slug=team_slug) 
            except Http404:
                # Error rendering uses the designated home.html template
                return render(request, 'home.html', {'error':'Competition and Team not found.'})

        # HANDLE HOMEPAGE (Default Content )
        else:
            # Find the current competition
            competition = Competition.objects.filter(is_current_competition=True).first()
            if not competition:
                return render(request, 'home.html', {'error': 'No current competition set.'})

            # Get the single team object associated with the current competition.
            team_details = competition.team_competition.all().first()
            if not team_details:
                return render(request, 'home.html', {'error': 'No team found for current competition.'})

        # --- CODE RUNNING FOR BOTH CASES (Data Aggregation) ---
        
        team = team_details
        opponents = competition.opponents.all().order_by('name')
        games = Game.objects.filter(competition=competition).order_by('date')
        #games = competition.competition.all().order_by('date') 
        staff = TeamStaff.objects.filter(team=team) 
        players = team.players.all()
        news = TeamNews.objects.filter(competition=competition)
        t_images = GalleryImages.objects.filter(team=team)
        
        # Set up pagination
        p = Paginator(GalleryImages.objects.all(), 6) 
        page = request.GET.get('page')
        team_images = p.get_page(page)
        nums = "a" * team_images.paginator.num_pages
       
        # Fetch standings and the related game type
        tournament_standing = Standing.objects.filter(competition=competition).select_related('team', 'opponent')
        # Query the Game model directly and keep your prefetch_related intact!
        all_games = Game.objects.filter(competition=competition).prefetch_related('quarterly_scores')
        
        # Returns only the stats for the games in this competition.
        all_game_stats = PlayerStatLine.objects.filter(game_schedule__in=all_games)
     
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)

        # 🚀 SECURITY DEFENSE: Check if any database records exist for game statistics
        if all_game_stats.exists():
            # All Game Statistics
            all_game_stats_df = pd.DataFrame(
                all_game_stats.values(
                    'player_name__id', 'slug', 'game_schedule__date', 'player_name__player_image', 'player_name__player_name', 
                    'team__name', 'points', 'assists', 'blocks', 'steals', 'offensive_rebs', 'defensive_rebs', 
                    'game_schedule__game_type', 'game_schedule__team_scores', 'game_schedule__opponent_scores', 
                    'point_3_attempts', 'point_3_made', 'field_goal_attempts', 'field_goal_made', 
                    'ft_attempts', 'ft_made', 'turnovers'
                )
            )

            all_game_stats_df = all_game_stats_df.rename(columns={'player_name__id': 'player_id'})  
                                                                                          
            all_game_stats_df['total_rebounds'] = all_game_stats_df['offensive_rebs'] + all_game_stats_df['defensive_rebs']  
       
            # Calculation the efficiency of the games
            all_game_stats_df["efficiency"] = (
                all_game_stats_df["points"]
                + all_game_stats_df["total_rebounds"]
                + all_game_stats_df["assists"]
                + all_game_stats_df["steals"]
                + all_game_stats_df["blocks"]
                - (
                    (all_game_stats_df["field_goal_attempts"] - all_game_stats_df["field_goal_made"])
                    + (all_game_stats_df["ft_attempts"] - all_game_stats_df["ft_made"])
                    + all_game_stats_df["turnovers"]
                )
            )
              
            # Players Defense Calculation
            all_game_stats_df['def'] = all_game_stats_df['steals'] * 2 + all_game_stats_df['blocks'] * 2 + all_game_stats_df['defensive_rebs'] * 0.5 
            
            # Getting the regular season and playoffs games
            regular_season = all_game_stats_df[all_game_stats_df['game_schedule__game_type'].isin(["regular"])]
            regular_season = regular_season[~regular_season['game_schedule__team_scores'].isin([0])]

            # Function to get per game stats leaders
            def stats_leaders_per_game(stat):
                if regular_season.empty:
                    return pd.DataFrame(columns=["player_id", "player_name__player_name", "player_name__player_image", stat])
                leaders_per_game = (
                    regular_season.groupby(
                        ["player_id", "player_name__player_name", 'player_name__player_image']
                    )[['points', 'total_rebounds', 'assists', 'blocks', 'steals', 'efficiency', 'def']].mean().sort_values(stat, ascending=False).reset_index()
                )
                return leaders_per_game
            
            # These lines call the function
            pts_per_game = stats_leaders_per_game('points').head(3).to_dict('records')
            reb_per_game = stats_leaders_per_game('total_rebounds').head(3).to_dict('records')
            ast_per_game = stats_leaders_per_game('assists').head(3).to_dict('records') 
            blk_per_game = stats_leaders_per_game('blocks').head(3).to_dict('records')
            stl_per_game = stats_leaders_per_game('steals').head(3).to_dict('records')
            eff_per_game = stats_leaders_per_game('efficiency').head(3).to_dict('records')
            def_per_game = stats_leaders_per_game('def').head(3).to_dict('records')

            # Handle averages with empty group logic safeguards
            if not regular_season.empty:
                mean_opp_points = regular_season.groupby(['game_schedule__date'])['game_schedule__opponent_scores'].mean().mean().round(1)
                mean_points = regular_season.groupby(['game_schedule__date'])['points'].sum().mean().round(1)
                mean_rebounds = regular_season.groupby(['game_schedule__date'])['total_rebounds'].sum().mean().round(1)
                mean_assists = regular_season.groupby(['game_schedule__date'])['assists'].sum().mean().round(1)                               
                
                # Percent Calculations
                fg_attempts_sum = regular_season['field_goal_attempts'].sum()
                team_fg_pct = ((regular_season['field_goal_made'].sum() / fg_attempts_sum) * 100).round(1) if fg_attempts_sum > 0 else 0.0
                
                fg_3p_attempts_sum = regular_season['point_3_attempts'].sum()
                team_3p_pct = ((regular_season['point_3_made'].sum() / fg_3p_attempts_sum) * 100).round(1) if fg_3p_attempts_sum > 0 else 0.0
                
                ft_attempts_sum = regular_season['ft_attempts'].sum()
                team_ft_pct = ((regular_season['ft_made'].sum() / ft_attempts_sum) * 100).round(1) if ft_attempts_sum > 0 else 0.0
            else:
                mean_opp_points = mean_points = mean_rebounds = mean_assists = 0.0
                team_fg_pct = team_3p_pct = team_ft_pct = 0.0
        else:
            # Fallback arrays if game_stats are zero records
            pts_per_game = reb_per_game = ast_per_game = blk_per_game = stl_per_game = eff_per_game = def_per_game = []
            mean_opp_points = mean_points = mean_rebounds = mean_assists = 0.0
            team_fg_pct = team_3p_pct = team_ft_pct = 0.0

        # 🚀 SECURITY DEFENSE: Check if standings rows exist before passing to Pandas
        if tournament_standing.exists():
            standing_df = pd.DataFrame(
                tournament_standing.values(
                    'competition__name', 'game_type', 'team__name', 'team__team_logo', 
                    'opponent__name', 'opponent__logo', 'w', 'l', 'home_record', 'away_record', 
                    'ppg', 'opp_ppg', 'strk', 'last_5'
                )
            ).sort_values('w', ascending=False).reset_index(drop=True)

            standing_df['team__name'] = standing_df['team__name'].fillna(standing_df['opponent__name'])
            standing_df['opponent__name'] = standing_df['opponent__name'].fillna(standing_df['team__name'])
            standing_df['team__team_logo'] = standing_df['team__team_logo'].fillna(standing_df['opponent__logo'])                                             
            standing_df['opponent__logo'] = standing_df['opponent__logo'].fillna(standing_df['team__team_logo'])
            standing_records = standing_df.to_dict('records')
        else:
            standing_records = []

        # Calculate age for the filtered players
        for player in players:
            player.age = calculate_age(player.date_of_birth) 

        # 4. Prepare Context
        context = {
            'team_detail': {
                'pk': team.slug, 
                'team_logo': team.team_logo.url if team.team_logo else None,
                'name': team.name,
            },
            'competition': competition,
            'players': players,
            'opponents': opponents,
            'staff': staff,
            'games': games,
            'team': team,
            'news': news,
            'standing_df': standing_records,
            
            # Top Leaders
            'pts_per_game': pts_per_game,
            'reb_per_game': reb_per_game,
            'ast_per_game': ast_per_game,
            'blk_per_game': blk_per_game,
            'stl_per_game': stl_per_game,
            'eff_per_game': eff_per_game,
            'def_per_game': def_per_game,
            
            # Team Average Stats
            'mean_points': mean_points,
            'mean_rebounds': mean_rebounds,
            'mean_assists': mean_assists,
            'mean_opp_points': mean_opp_points,
            
            # Percent Section
            'team_fg_pct': team_fg_pct,
            'team_ft_pct': team_ft_pct,
            'team_3p_pct': team_3p_pct,
            
            # News Section
            'hot_news': TeamNews.objects.filter(competition=competition, category='Hot').order_by('-published_date')[:1],
            'team_news': TeamNews.objects.filter(competition=competition, category='Team').order_by('-published_date')[:2],
            'league_news': TeamNews.objects.filter(competition=competition, category='League')[:1],
            'spotlight_news': TeamNews.objects.filter(competition=competition, category='Spotlight').order_by('-published_date')[:4],
            'sidebar_news': TeamNews.objects.filter(competition=competition).order_by('-published_date')[:5],
            'base_news': TeamNews.objects.filter(competition=competition, category='Base').order_by('-published_date'),
            
            # Regular Season Games
            'regular_season_games_df': Game.objects.filter(competition=competition, game_type='regular').order_by('date'),
            'international_games': Game.objects.exclude(competition=competition).order_by('date'),
            
            # Gallery Images
            'team_images': team_images,
            'nums': nums,
            'awards': Awards.objects.all().order_by('date'),
            'products': Product.objects.all().order_by('name')
        }
        
        return render(request, 'home.html', context)


###########################################################################
##########################################################################
##########################################################################
def team_shot_chart(request, competition_slug): 
    competition  = get_object_or_404(Competition, slug=competition_slug) 
    team = competition.team
    team_details = team
    
    players = team_details.players.all()  # Using the foreign key Team related_name 'players'
    # Get the player's statistics
    all_games = Game.objects.filter(competition=competition).prefetch_related('quarterly_scores')
    ##  Returns only the stats for the games in this competition.
    all_game_stats = PlayerStatLine.objects.filter(game_schedule__in=all_games)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    if all_game_stats.exists():
        player_stats_df = pd.DataFrame(
                    all_game_stats.values('player_name__id', 'slug', 'player_name__jersey_number','player_name__player_name', 
                                'player_name__player_image','points', 'assists', 
                                'field_goal_attempts', 'field_goal_made', 'ft_attempts', 'ft_made',
                                'point_3_attempts', 'point_3_made',
                                'turnovers', 'minutes',  'blocks', 'steals', 'personal_fouls',
                                'offensive_rebs', 'defensive_rebs',
                                'team__name', 'game_schedule__opponent__name', 'game_schedule__opponent__abbreviation',
                                'game_schedule__date', 'game_schedule__team_win_loss',
                                'game_schedule__indicator', 'game_schedule__competition__name', 'game_schedule__game_type',
                                'game_schedule__competition__year__year','game_schedule__team_scores', 'game_schedule__opponent_scores'))
        # Create the mapping dictionary
        column_mapping = {
            'player_name__id': 'player_id','player_name__jersey_number': 'jersey_number','player_name__player_name': 'player_name','player_name__player_image': 'player_image',
            'field_goal_attempts': 'fga','field_goal_made': 'fgm','point_3_attempts': 'p3a','point_3_made': 'p3m',
            'ft_attempts': 'fta','ft_made': 'ftm','offensive_rebs': 'oreb','defensive_rebs': 'dreb','personal_fouls': 'pf',
            'team__name': 'team_name','game_schedule__opponent__name': 'opponent_name','game_schedule__opponent__abbreviation': 'opponent_abbr',
            'game_schedule__date': 'game_date','game_schedule__team_win_loss': 'result','game_schedule__indicator': 'location', # e.g., @ or vs
            'game_schedule__competition__name': 'competition','game_schedule__game_type': 'game_type','game_schedule__competition__year__year': 'season',
            'game_schedule__team_scores': 'team_score','game_schedule__opponent_scores': 'opponent_score'
        }

        # Apply the rename
        player_stats_df.rename(columns=column_mapping, inplace=True)
        
        player_stats_df['rebs'] = player_stats_df['oreb'] + player_stats_df['dreb']
        player_stats_df['game_date'] = (pd.to_datetime(player_stats_df['game_date']))
    
        # This lambda is to abbreviate the League Name with the first letter of each words  (e.g., "Programming Languages" becomes "PL")
        player_stats_df['competition'] = player_stats_df['competition'].apply(
                                                    lambda x: "".join([word[0].upper() for word in str(x).split()]))
            
        # Calculation the efficiency of the games
        player_stats_df["efficiency"] = (
                                    player_stats_df["points"]
                                    + player_stats_df["rebs"]
                                    + player_stats_df["assists"]
                                    + player_stats_df["steals"]
                                    + player_stats_df["blocks"]
                                    - (
                                        (player_stats_df["fga"] - player_stats_df["fgm"])
                                        + (player_stats_df["fta"] - player_stats_df["ftm"])
                                        + player_stats_df["turnovers"]
                                    )
                                )         
        # Players Defence Calculation
        player_stats_df['def'] = player_stats_df['steals'] * 2 + player_stats_df['blocks'] * 2 + player_stats_df['dreb'] * 0.5 
        
        # Players Defence Calculation
        team_stats_df = player_stats_df.sort_values(by='game_date', ascending=False)
    
        last_5_df = team_stats_df[team_stats_df['game_type'].isin(["regular"])].copy()
        last_5_df = last_5_df[~last_5_df['team_score'].isin([0])]
        last_5_df['game_date'] = last_5_df['game_date'].dt.date
        last_5_df['game_date'] = last_5_df['game_date'].astype("string")
        last_5_df = last_5_df.groupby(['game_date'])[['points', 'oreb',
                                'dreb', 'rebs',
                                'fgm', 'fga','fta', 'ftm',
                                'p3a', 'p3m']].sum().reset_index()
        last_5_games_df = last_5_df.tail()
        #print(last_5_games_df)
    
        last_5_games_list = last_5_games_df.to_dict('records')
        last_5_games_json = json.dumps(last_5_games_list)
        
        context = {
            'team_details': team_details,
            'competition': competition,
            'charts': ShotCharts.objects.filter(team=team_details),
            'last_5_games_json': last_5_games_json,
            'last_5_games': last_5_games_list,
        }

        return render(request, 'team-charts.html', context)
    else:
        last_5_games_list = last_5_games_json = []
        last_5_games = []
        charts = [] 

        context = {
        'team_details': team_details,
        'competition': competition,
        
    }   

    return render(request, 'team-charts.html', context)

############################################################################
##############################################################################
##############################################################################
# FUNCTION VIEW TEAM ROSTER

def team_roster(request, competition_slug, team_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    team = Team.objects.filter(slug=team_slug, competitions=competition).first()
    #Stop right here if the team isn't found in this competition
    if team is None:
        from django.http import Http404
        raise Http404(f"Team '{team_slug}' does not exist in this competition.")
        
    team_details = team   
    players = team_details.players.all()  # Using the foreign key Team related_name 'players'
    
    # Get the player's statistics
    staff = TeamStaff.objects.filter(team=team_details)
    tournament_stats = PlayerStatLine.objects.filter(player_name__in=players)
    print('Tournament stats')
    print(players)

    # Calculate age for the filtered players
    for player in players:
        player.age = calculate_age(player.date_of_birth) 

    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)

    # Trying to get othr players mean values
    if tournament_stats.exists():
        players_df = pd.DataFrame(
                        tournament_stats.values('player_name__id', 'slug', 'player_name__jersey_number','player_name__player_name', 'player_name__jersey_number', 'player_name__active_status', 'player_name__experience',
                                'player_name__player_image', 'player_name__position', 'player_name__height_cm', 'player_name__weight_kg', 'player_name__country', 'player_name__date_of_birth',
                                'points', 'assists', 'player_name__position', 'game_schedule__game_type', 'game_schedule__team_win_loss',
                                    'offensive_rebs', 'defensive_rebs', 'game_schedule__competition__year__year'))
        players_df = players_df[players_df['game_schedule__game_type'].isin(["regular"])]
        players_df = players_df.rename(columns={'player_name__id':'player_id', })          
        players_df['total_rebounds'] = players_df['offensive_rebs'] + players_df['defensive_rebs']
        
        players_mean_stats = (players_df.groupby(
                                ["player_id","player_name__player_name",'player_name__jersey_number','player_name__player_image', 'player_name__position', 'game_schedule__game_type', 'game_schedule__competition__year__year',
                                'player_name__active_status', 'player_name__experience','player_name__height_cm', 'player_name__weight_kg', 'player_name__country', 'player_name__date_of_birth', ]
                            )[['points', 'total_rebounds','assists',]].mean().round(1).sort_values('points',ascending=False).reset_index())

        """
        # Convert to list of dicts
        stats_list = players_mean_stats.to_dict('records')

        # Add the proper full URL to each record
        for player in stats_list:
            image_path = player.get('player_name__player_image')
            # This automatically uses your Cloudinary backend to generate the URL
            player['final_image_url'] = default_storage.url(image_path) if image_path else None


        {% for player in players_mean_stats %}
        <a href="{% url 'players-id' competition.slug player.player_name__slug %}">
            {% if player.final_image_url %}
                <img src="{{ player.final_image_url }}" alt="{{ player.player_name__player_name }}" class="player-photo">
            {% else %}
                <img src="https://res.cloudinary.com/dgznffguu/image/upload/v1/uploads/Team_Logos/python.PNG" alt="Default" class="player-photo">
            {% endif %}
        </a>
    {% endfor %}    

        """
        
        return render(request, 'roster.html', {'competition':competition, #'tournament_stats':tournament_stats,
                                                    'team_details': team_details, 
                                                    'players': players, 
                                                    'staffs': staff,
                                                    'players_mean_stats': players_mean_stats.to_dict('records'),
                                                    })
    else:
       
        
        return render(request, 'roster.html', {'competition':competition, #'tournament_stats':tournament_stats,
                                                    'team_details': team_details, 
                                                    'players': players, 
                                                    'staffs': staff,
                                                    
                                          
                                                    })                                               


# Class Base View For Update

class TeamUpdateView(SuperuserRequiredMixin, APIView):
    # Handle GET and POST requests to UPDATE team details
    def get(self, request, competition_slug, ): 
        competition = get_object_or_404(Competition, slug=competition_slug)
        team = competition.team
        update_team = team
        form = TeamForm(request.POST or None, instance=update_team)
        return render(request, 'team_update.html', {'form': form, 'update_team': update_team})

    def post(self, request, competition_slug,):
        competition = get_object_or_404(Competition, slug=competition_slug)
        update_team = competition.team
        form = TeamForm(request.POST, request.FILES, instance=update_team)

        if form.is_valid():
            form.save()
            # Return a valid update message.
            messages.success(request, (" Team Updated Sucessfully ):"))
            return redirect('team-id', competition_slug=competition_slug)#Error Here.......
        return render(request, 'team_update.html', {'form': form, 'update_team': update_team})            


####################################################################################
####################################################################################
# Players View
####################################################################################
####################################################################################


# Class Base View Creating Opponents

class PlayerCreateView(SuperuserRequiredMixin, View):
    def get(self, request):
        form = PlayerForm()
        return render(request, 'players-registration.html', {"form": form,})

    def post(self, request):
        form = PlayerForm(request.POST, request.FILES)
        
        if form.is_valid():
            player = form.save()
            
            messages.success(request, f"Player '{player.player_name}' Added Successfully :)")
            return HttpResponseRedirect('/player create?')
        else:
            messages.error(request, "There were errors in the form. Please correct them and try again.")
            print("Player Form Errors:", form.errors)  # Debug: Print team form errors
            
        return render(request, 'players-registration.html', {"form": form})


#  Class Base View For Opponent List
class PlayerListView(APIView):
    def get(self, request, slug):
        teams_details = get_object_or_404(Team, slug=slug)
        players = teams_details.players.all() 
        return render(request, 'roster.html', {'players':players})        




class PlayerDetailView(APIView):
    def get(self, request, slug, competition_slug=None):
        if competition_slug:
            competition = get_object_or_404(Competition, slug=competition_slug)
            if competition.is_current_competition:
                team = competition.team
                print(f"Team: {team}.upper()")
                player_details = get_object_or_404(Player, slug=slug, team=team)
                
                other_players = Player.objects.exclude(slug=slug).order_by('player_name')
                player_details.age = calculate_age(player_details.date_of_birth)  # Calculate the player's age
                career_records = player_details.career_records.first()

                # Get the player's statistics
                tournament_stats = PlayerStatLine.objects.filter(player_name=player_details).order_by('-game_schedule')
                other_players_stats = PlayerStatLine.objects.filter(player_name__in=other_players)

                player_merchandise = Product.objects.filter(featured_player=player_details)
                # Show 2 products per page
                paginator = Paginator(player_merchandise, 2) 
                page_number = request.GET.get('page')
                player_merchandise_obj = paginator.get_page(page_number)
                ###############################################################################################
                ###################################Conversion To Pandas DataFrame #####################################
                ###############################################################################################
                pd.set_option("display.max_columns", None)
                pd.set_option("display.max_rows", None)
                if tournament_stats.exists():
                    player_stats_df = pd.DataFrame(
                                tournament_stats.values('player_name__id', 'player_name__slug', 'game_schedule__id','player_name__jersey_number','player_name__player_name', 
                                            'player_name__player_image','points', 'assists', 
                                            'field_goal_attempts', 'field_goal_made', 'ft_attempts', 'ft_made',
                                            'point_3_attempts', 'point_3_made',
                                            'turnovers', 'minutes',  'blocks', 'steals', 'personal_fouls',
                                            'offensive_rebs', 'defensive_rebs',
                                            'team__name', 'team__team_logo', 'game_schedule__opponent__name', 'game_schedule__opponent__abbreviation', 'game_schedule__opponent__logo',
                                            'game_schedule__date', 'game_schedule__time', 'game_schedule__team_win_loss',
                                            'game_schedule__indicator', 'game_schedule__competition__name', 'game_schedule__game_type',
                                            'game_schedule__competition__year__year','game_schedule__team_scores', 'game_schedule__opponent_scores'))

                    player_stats_df = player_stats_df.rename(columns={'player_name__id':'player_id', 'game_schedule__id':'game_id' }) 
                    player_stats_df['total_rebounds'] = player_stats_df['offensive_rebs'] + player_stats_df['defensive_rebs']
                    player_stats_df['fg_percent'] = (((player_stats_df['field_goal_made'] / player_stats_df['field_goal_attempts']) * 100).round(1)).fillna(0)
                    player_stats_df['point_3_percent'] = (((player_stats_df['point_3_made'] / player_stats_df['point_3_attempts']) * 100).round(1)).fillna(0)
                    player_stats_df['ft_percent'] = (((player_stats_df['ft_made'] / player_stats_df['ft_attempts']) * 100).round(1)).fillna(0)
                    player_stats_df['game_schedule__date'] = pd.to_datetime(player_stats_df['game_schedule__date'])#.dt.strftime('%d/%m/%Y')
                    player_stats_df['minutes'] = player_stats_df['minutes'].astype("float")
                    
                    
        
        
                    # This lambda is to abbreviate the League Name with the first letter of each words  (e.g., "Programming Languages" becomes "PL")
                    player_stats_df['game_schedule__competition__name'] = player_stats_df['game_schedule__competition__name'].apply(
                                                                lambda x: "".join([word[0].upper() for word in str(x).split()])
                                                            )
            
                    # Calculation the efficiency of the games
                    player_stats_df["efficiency"] = (
                                                player_stats_df["points"]
                                                + player_stats_df["total_rebounds"]
                                                + player_stats_df["assists"]
                                                + player_stats_df["steals"]
                                                + player_stats_df["blocks"]
                                                - (
                                                    (player_stats_df["field_goal_attempts"] - player_stats_df["field_goal_made"])
                                                    + (player_stats_df["ft_attempts"] - player_stats_df["ft_made"])
                                                    + player_stats_df["turnovers"]
                                                )
                                            )
                                
                    # Players Defence Calculation
                    player_stats_df['def'] = player_stats_df['steals'] * 2 + player_stats_df['blocks'] * 2 + player_stats_df['defensive_rebs'] * 0.5 
                    player_stats_df = player_stats_df.sort_values(by='game_schedule__date', ascending=False) 

                    game_schedules = player_stats_df[player_stats_df['game_schedule__game_type'].isin(["regular"])].copy()
                    game_schedules =  game_schedules.sort_values('game_schedule__date',ascending=False)
                    # If using a DataFrame
                    game_schedules['game_id'] = game_schedules['game_id'].astype(int)
                    print(game_schedules[['player_id', 'game_id']])

                    # 1. Calculate Percents
                    player_shooting_pct = game_schedules[~game_schedules['game_schedule__team_scores'].isin([0])]
                    player_fg_pct = ((player_shooting_pct['field_goal_made'].sum() / player_shooting_pct['field_goal_attempts'].sum()) * 100).round(1)
                    player_3p_pct = ((player_shooting_pct['point_3_made'].sum() / player_shooting_pct['point_3_attempts'].sum()) * 100).round(1)
                    player_ft_pct = ((player_shooting_pct['ft_made'].sum() / player_shooting_pct['ft_attempts'].sum()) * 100).round(1)
                    print(player_fg_pct)
                    print(player_3p_pct)
                    print(player_ft_pct)
                    
                    ###################################################################################################
                    ##################################################################################################
                    ###################################################################################################
                    # Regular season Mean Games
                    regular_season_games_played_df = player_stats_df[player_stats_df['game_schedule__game_type'].isin(["regular"])].copy()
                    regular_season_games_played_df = regular_season_games_played_df[~regular_season_games_played_df['game_schedule__team_scores'].isin([0])]
                    # Number Of Games Played and Win or Loss
                    regular_season_wins = len(regular_season_games_played_df[regular_season_games_played_df['game_schedule__team_win_loss'] == 'Win' ])
                    regular_season_losses = len(regular_season_games_played_df[regular_season_games_played_df['game_schedule__team_win_loss'] == 'Loss' ])
                    regular_season_games_played_df['game_schedule__team_win_loss'] = regular_season_games_played_df['game_schedule__team_win_loss'].replace({'Win':'W', 'Loss':'L'})
                    regular_season_games_played = regular_season_wins + regular_season_losses



                    point_trend = regular_season_games_played_df[[ 'game_schedule__date', 'points']].copy()
                    point_trend['game_schedule__date'] = point_trend['game_schedule__date'].dt.date
                    point_trend['game_schedule__date'] = point_trend['game_schedule__date'].astype("string")
                    point_trend = point_trend.groupby('game_schedule__date')['points'].sum().astype(float)
                    #point_trend['game_schedule__date'] = point_trend['game_schedule__date'].astype("string")
                    print("POINT TREND")
                    #print(point_trend.index)
                    #print(point_trend.values)

                    # Calculate averages of the tournament and then to a rounded value or float
                    mean_points = regular_season_games_played_df['points'].mean().astype(float).round(1)
                    mean_rebounds = regular_season_games_played_df['total_rebounds'].mean().astype(float).round(1)
                    mean_assists = regular_season_games_played_df['assists'].mean().astype(float).round(1)
                    ###################################################################################################
                    regular_season_mean_total = (regular_season_games_played_df.groupby(
                                            ["player_id", 'player_name__slug', "player_name__player_name", 'team__name','game_schedule__competition__name', 'game_schedule__competition__year__year']
                                            )[['minutes','points', 'total_rebounds','assists', 'field_goal_attempts', 'field_goal_made', 'fg_percent',
                                            'point_3_attempts', 'point_3_made', 'point_3_percent', 'ft_attempts', 'ft_made', 'ft_percent',
                                            'offensive_rebs', 'defensive_rebs', 'blocks', 'steals', 'personal_fouls', 'turnovers', 'efficiency', 'def'
                                            ]].mean().round(1).sort_values('points',ascending=False).reset_index())
                
                    # Last  games
                    last_5_games = regular_season_games_played_df.head(5)
                    
                    last_5_games_mean = (last_5_games.groupby(
                                            ["player_id", 'player_name__slug', "player_name__player_name", 'team__name','game_schedule__competition__name', 'game_schedule__competition__year__year']
                                            )[['minutes', 'points', 'total_rebounds','assists', 'field_goal_attempts', 'field_goal_made', 'fg_percent',
                                            'point_3_attempts', 'point_3_made', 'point_3_percent', 'ft_attempts', 'ft_made', 'ft_percent',
                                            'offensive_rebs', 'defensive_rebs', 'blocks', 'steals', 'personal_fouls', 'turnovers', 'efficiency', 'def'
                                            ]].mean().round(1).sort_values('points',ascending=False).reset_index())
                    
                    #Last Game 
                    last_game_played = player_stats_df[~player_stats_df['points'].isin([0])]
                    last_game = last_game_played.iloc[0]
                    
                    
                
                    ###################################################################################################
                    ###################################################################################################
                    ###################################################################################################
                    ###################################################################################################
                    playoffs_games_played_df = player_stats_df[player_stats_df['game_schedule__game_type'].isin(["playoff"])].copy()
                    playoffs_games_played_df = playoffs_games_played_df[~playoffs_games_played_df['game_schedule__team_scores'].isin([0])]

                    wins = len(playoffs_games_played_df[playoffs_games_played_df['game_schedule__team_win_loss'] == 'Win' ])
                    losses = len(playoffs_games_played_df[playoffs_games_played_df['game_schedule__team_win_loss'] == 'Loss' ])
                    playoffs_games_played_df['game_schedule__team_win_loss'] = playoffs_games_played_df['game_schedule__team_win_loss'].replace({'Win':'W', 'Loss':'L'})
                    playoffs_games_played = wins + losses
                

                    playoffs_mean_total = (playoffs_games_played_df.groupby(
                                            ["player_id",'player_name__slug', "player_name__player_name", 'team__name','game_schedule__competition__name', 'game_schedule__competition__year__year']
                                            )[['points', 'total_rebounds','assists', 'field_goal_attempts', 'field_goal_made', 'fg_percent',
                                            'point_3_attempts', 'point_3_made', 'point_3_percent', 'ft_attempts', 'ft_made', 'ft_percent',
                                            'offensive_rebs', 'defensive_rebs', 'blocks', 'steals', 'personal_fouls', 'turnovers', 'efficiency', 'def'
                                            ]].mean().round(1).sort_values('points',ascending=False).reset_index())

                    
                    ###################################################################################################
                    ###################################################################################################  
                    ###################################################################################################
                    international_games = player_stats_df[player_stats_df['game_schedule__game_type'].isin(["international"])].copy()
                    international_games = international_games[~international_games['game_schedule__team_scores'].isin([0])]

                    #wins = (international_games['game_schedule__team_win_loss'] == 'Win').count()
                    #losses = (international_games['game_schedule__team_win_loss'] == 'Loss' ).count()  
                    wins = len(international_games[international_games['game_schedule__team_win_loss'] == 'Win' ])
                    losses = len(international_games[international_games['game_schedule__team_win_loss'] == 'Loss' ])
                    international_games['game_schedule__team_win_loss'] = international_games['game_schedule__team_win_loss'].replace({'Win':'W', 'Loss':'L'})
                    international_games_played = wins + losses
                    
                    #print('Number of International games played are: ', international_games_played)
                    international_games_mean_total = (international_games.groupby(
                                            ["player_id", 'player_name__slug', "player_name__player_name", 'team__name','game_schedule__competition__name', 'game_schedule__competition__year__year']
                                            )[['points', 'total_rebounds','assists', 'field_goal_attempts', 'field_goal_made', 'fg_percent',
                                            'point_3_attempts', 'point_3_made', 'point_3_percent', 'ft_attempts', 'ft_made', 'ft_percent',
                                            'offensive_rebs', 'defensive_rebs', 'blocks', 'steals', 'personal_fouls', 'turnovers', 'efficiency', 'def'
                                            ]].mean().round(1).sort_values('points',ascending=False).reset_index())
                    
                    ###################################################################################################
                    ##################################################################################################
                    ###################################################################################################
                    # Trying to get othr players mean values
                    other_players_df = pd.DataFrame(
                                    other_players_stats.values('player_name__id', 'player_name__slug', 'player_name__jersey_number','player_name__player_name', 'player_name__jersey_number',
                                            'player_name__player_image','points', 'assists', 'player_name__position', 'game_schedule__game_type', 'game_schedule__team_scores',
                                            'offensive_rebs', 'defensive_rebs',))
                    other_players_df = other_players_df[other_players_df['game_schedule__game_type'].isin(["regular"])]
                    other_players_df = other_players_df[~other_players_df['game_schedule__team_scores'].isin([0])]
                    other_players_df = other_players_df.rename(columns={'player_name__id':'player_id', })          
                    other_players_df['total_rebounds'] = other_players_df['offensive_rebs'] + other_players_df['defensive_rebs']

                
                    
                    others_players_mean_stats = (other_players_df.groupby(
                                            ["player_id","player_name__player_name",'player_name__jersey_number','player_name__player_image', 'player_name__position', 'game_schedule__game_type',]
                                        )[['points', 'total_rebounds','assists',]].mean().sort_values('points',ascending=False).reset_index())
                                    
                    ###################################################################################################
                    ###################################################################################################
                    ###################################################################################################
                    
                    regular_season = player_stats_df[player_stats_df['game_schedule__game_type'].isin(["regular"])]
                    playoffs = player_stats_df[player_stats_df['game_schedule__game_type'].isin(["playoff"])]
                    international_games = player_stats_df[player_stats_df['game_schedule__game_type'].isin(["international"])]
                    # Try .count()
                    # df = df[~df['Count'].isin([1])]
                    ###############################################################################################
                    ###############################################################################################
                    ###############################################################################################
                
                    ###############################################################################################
                    ###############################################################################################
                    ###############################################################################################
                
                    # Pass them to the context
                    context = {
                        'team': team,
                        'player_details': player_details,
                        'others_players_mean_stats': others_players_mean_stats.to_dict('records'),
                        'career_records': career_records,
                        'regular_season_games_played': regular_season_games_played,
                        'playoffs_games_played': playoffs_games_played,
                        'regular_season_wins': regular_season_wins,
                        'regular_season_losses': regular_season_losses,
                        'game_schedules': game_schedules.to_dict('records'),
                        
                        
                        'last_5_games': last_5_games.to_dict('records'),
                        'last_game': last_game.to_dict(),
                        'playoffs':  playoffs.to_dict('records'),
                        'international_games_mean_total':  international_games_mean_total.to_dict('records'),
                        # Charts Data
                        # For Inline JScript
                        #'point_trend_labels': json.dumps(point_trend.index.tolist()),
                        'point_trend_labels': json.dumps([str(d) for d in point_trend.index]), # external .js
                        'point_trend_data': json.dumps(point_trend.values.tolist()),
                        
                        #Players Averages
                        'mean_points': mean_points,
                        'mean_rebounds': mean_rebounds,
                        'mean_assists': mean_assists,
                        'regular_season_mean_total': regular_season_mean_total.to_dict('records'),
                        'last_5_games_mean': last_5_games_mean.to_dict('records'),
                        'playoffs_mean_total': playoffs_mean_total.to_dict('records'),
                        # For SVG basketball court
                        'player_fg_pct': player_fg_pct,
                        'player_3p_pct': player_3p_pct,
                        'player_ft_pct': player_ft_pct,
                        
                        # Players Image
                        'player_images': GalleryImages.objects.filter(player_pictures=player_details),
                        # Player Product
                        'player_merchandise': player_merchandise_obj,
                    }

                    return render(request, 'player-page.html', context)
                else:
                    
                    context = {
                        'player_details': player_details,
                        # Players Image
                        'player_images': GalleryImages.objects.filter(player_pictures=player_details),
                        # Player Product
                        'player_merchandise': player_merchandise_obj,
                        'team': team,
                    }

                    return render(request, 'player-page.html', context)

        # Fallback if IDs are missing or invalid
        return render(request, 'player-page.html', {
            'error': 'Invalid competition or team ID.'
        })

# For Chart.js
"""
def player_stats_charts(request,  player_slug):
    player_details = get_object_or_404(Player, slug=player_slug,)
    other_players = Player.objects.exclude(slug=player_slug).order_by('player_name')
    competition = player_details.team.competitions
    

    # Get the player's statistics
    tournament_stats = PlayerStatLine.objects.filter(player_name=player_details)
    other_players_stats = PlayerStatLine.objects.filter(player_name__in=other_players)

    

    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
                
    player_stats_df = pd.DataFrame(
                tournament_stats.values('player_name__id', 'player_name__slug', 'player_name__jersey_number','player_name__player_name', 
                            'player_name__player_image','points', 'assists', 
                            'field_goal_attempts', 'field_goal_made', 'ft_attempts', 'ft_made',
                            'point_3_attempts', 'point_3_made',
                            'turnovers', 'minutes',  'blocks', 'steals', 'personal_fouls',
                            'offensive_rebs', 'defensive_rebs',
                            'team__name', 'game_schedule__opponent__name', 'game_schedule__opponent__abbreviation',
                            'game_schedule__date', 'game_schedule__team_win_loss',
                            'game_schedule__indicator', 'game_schedule__competition__name', 'game_schedule__game_type',
                            'game_schedule__competition__year__year','game_schedule__team_scores', 'game_schedule__opponent_scores'))


    player_stats_df = player_stats_df.rename(columns={'player_name__id':'player_id', })          
    player_stats_df['total_rebounds'] = player_stats_df['offensive_rebs'] + player_stats_df['defensive_rebs']
    player_stats_df['game_schedule__date'] = (pd.to_datetime(player_stats_df['game_schedule__date'])).dt.strftime('%d/%m/%Y')
    player_stats_df['fg_percent'] = (((player_stats_df['field_goal_made'] / player_stats_df['field_goal_attempts']) * 100).round(1)).fillna(0)
    # This lambda is to abbreviate the League Name with the first letter of each words  (e.g., "Programming Languages" becomes "PL")
    player_stats_df['game_schedule__competition__name'] = player_stats_df['game_schedule__competition__name'].apply(
                                                lambda x: "".join([word[0].upper() for word in str(x).split()]))
        
    # Calculation the efficiency of the games
    player_stats_df["efficiency"] = (
                                player_stats_df["points"]
                                + player_stats_df["total_rebounds"]
                                + player_stats_df["assists"]
                                + player_stats_df["steals"]
                                + player_stats_df["blocks"]
                                - (
                                    (player_stats_df["field_goal_attempts"] - player_stats_df["field_goal_made"])
                                    + (player_stats_df["ft_attempts"] - player_stats_df["ft_made"])
                                    + player_stats_df["turnovers"]
                                )
                            )         
    # Players Defence Calculation
    player_stats_df['def'] = player_stats_df['steals'] * 2 + player_stats_df['blocks'] * 2 + player_stats_df['defensive_rebs'] * 0.5 
    
    ##################################################################################################
    ####################################### TEAM TOTALS MATRIX #######################################
    ##################################################################################################
    all_games = Game.objects.all().prefetch_related('quarterly_scores')
    all_game_stats = PlayerStatLine.objects.filter(game_schedule__in=all_games)
    
    all_games_values = pd.DataFrame(
                all_game_stats.values('player_name__id', 'player_name__slug', 'player_name__jersey_number','player_name__player_name', 
                            'player_name__player_image','points', 'assists', 
                            'field_goal_attempts', 'field_goal_made','ft_attempts', 'ft_made',
                            'point_3_attempts', 'point_3_made',
                            'turnovers', 'minutes',  'blocks', 'steals', 'personal_fouls',
                            'offensive_rebs', 'defensive_rebs',
                            'team__name', 'game_schedule__opponent__name','game_schedule__opponent__abbreviation',
                            'game_schedule__date', 'game_schedule__team_win_loss',
                            'game_schedule__indicator', 'game_schedule__competition__name', 'game_schedule__game_type',
                            'game_schedule__competition__year__year','game_schedule__team_scores', 'game_schedule__opponent_scores'))

    # Number Of Games Played and Win or Loss
    all_games_values = all_games_values.rename(columns={'player_name__id':'player_id', })          
    all_games_values['total_rebounds'] = all_games_values['offensive_rebs'] + all_games_values['defensive_rebs']
    all_games_values['game_schedule__date'] = (pd.to_datetime(all_games_values['game_schedule__date'])).dt.strftime('%d/%m/%Y')
    
    # This lambda is to abbreviate the League Name with the first letter of each words  (e.g., "Programming Languages" becomes "PL")
    all_games_values['game_schedule__competition__name'] = all_games_values['game_schedule__competition__name'].apply(
                                                lambda x: "".join([word[0].upper() for word in str(x).split()]))
        
    # Calculation the efficiency of the games
    all_games_values["efficiency"] = (
                                all_games_values["points"]
                                + all_games_values["total_rebounds"]
                                + all_games_values["assists"]
                                + all_games_values["steals"]
                                + all_games_values["blocks"]
                                - (
                                    (all_games_values["field_goal_attempts"] - all_games_values["field_goal_made"])
                                    + (all_games_values["ft_attempts"] - all_games_values["ft_made"])
                                    + all_games_values["turnovers"]
                                )
                            )         
    # Players Defence Calculation
    
    all_games_values['def'] = all_games_values['steals'] * 2 + all_games_values['blocks'] * 2 + all_games_values['defensive_rebs'] * 0.5 
   

    team_matrix_df = all_games_values[all_games_values['game_schedule__game_type'].isin(["regular"])]
    team_matrix_df = team_matrix_df[~team_matrix_df['game_schedule__team_scores'].isin([0])]
    team_matrix_df = team_matrix_df[[ "player_name__player_name", 'points', "total_rebounds",'assists','field_goal_attempts', 'field_goal_made',  'point_3_attempts', 'point_3_made',
                                                                    'ft_attempts', 'ft_made', 'offensive_rebs', 'defensive_rebs','turnovers',  'blocks', 'steals', 'personal_fouls',
                                                                          'efficiency', 'def']]
    team_matrix_df = team_matrix_df.rename(columns={"points":"PTS","total_rebounds":"REB","assists":"AST","field_goal_made":"FGM","field_goal_attempts":"FGA",
                                                    "point_3_made":"3PM", "point_3_attempts":"3PA", "ft_made": "FTM", "ft_attempts":"FTA", "offensive_rebs":"ORB", "defensive_rebs":"DRB",
                                                    "turnovers":"TOV","steals":"STL","blocks":"BLK","personal_fouls":"PF","efficiency":"EFF", 'def':'DEF',})                                                                      
    
    #Accumulation.sum() and mean()
    team_sum_matrix_df = team_matrix_df.groupby(["player_name__player_name"])[['PTS','REB','AST','FGM','FGA','3PM','3PA','FTM','FTA','ORB','DRB', 'TOV','STL','BLK','PF','EFF', 'DEF']].sum().sort_values(by='PTS',ascending=True)  
    team_mean_matrix_df = team_matrix_df.groupby(["player_name__player_name"])[['PTS','REB','AST','FGM','FGA','3PM','3PA','FTM','FTA','ORB','DRB', 'TOV','STL','BLK','PF','EFF', 'DEF']].mean().round(1).sort_values(by='PTS',ascending=True)  
    
   
    ###################################################################################################
    ##################################################################################################
    ###################################### INDIVIDUAL SUMMARY ###########################################
    ##################################################################################################
    regular_season_games_played_df = player_stats_df[player_stats_df['game_schedule__game_type'].isin(["regular"])]
    regular_season_games_played_df = regular_season_games_played_df[~regular_season_games_played_df['game_schedule__team_scores'].isin([0])]
    regular_season_games_played_df = regular_season_games_played_df[['game_schedule__date','game_schedule__indicator','game_schedule__team_win_loss', 'game_schedule__opponent__name', 'game_schedule__opponent__abbreviation',
                                                                    'points', "total_rebounds",'assists','field_goal_attempts', 'field_goal_made',  'point_3_attempts', 'point_3_made',
                                                                    'ft_attempts', 'ft_made', 'offensive_rebs', 'defensive_rebs','turnovers',  'blocks', 'steals', 'personal_fouls',
                                                                          'efficiency', 'def']]

    regular_season_games_played_df['fg_percent'] = (((regular_season_games_played_df['field_goal_made'] / regular_season_games_played_df['field_goal_attempts']) * 100).round(1)).fillna(0)
    regular_season_games_played_df["vs_opp_win_loss"] =  regular_season_games_played_df['game_schedule__team_win_loss'].replace({'Win':'W', 'Loss':'L'})+'-'+regular_season_games_played_df['game_schedule__indicator']+'-'+ regular_season_games_played_df['game_schedule__opponent__abbreviation'] 
    regular_season_games_played_df["GM_DAY"] =  regular_season_games_played_df['game_schedule__date']+'-'+regular_season_games_played_df["vs_opp_win_loss"] 
    
    # Rename Columns 
    regular_season_games_played_df = regular_season_games_played_df.rename(columns={"points":"PTS","total_rebounds":"REB","assists":"AST","field_goal_made":"FGM","field_goal_attempts":"FGA", 'fg_percent':'FG%',
                                                    "point_3_made":"3PM", "point_3_attempts":"3PA", "ft_made": "FTM", "ft_attempts":"FTA", "offensive_rebs":"ORB", "defensive_rebs":"DRB",
                                                    "turnovers":"TOV","steals":"STL","blocks":"BLK","personal_fouls":"PF","efficiency":"EFF", 'def':'DEF',})  
    ###################################################################################################
    # Average Stats Of The Player
    mean_points = regular_season_games_played_df['PTS'].mean().astype(float).round(1)
    mean_rebounds = regular_season_games_played_df['REB'].mean().astype(float).round(1)
    mean_assists = regular_season_games_played_df['AST'].mean().astype(float).round(1)
    mean_effiency = regular_season_games_played_df['EFF'].mean().astype(float).round(1)
    ###################################################################################################
    #BAr Chart to display total stats of the player
    total_stats = regular_season_games_played_df.sum(numeric_only=True)
    # FIELD GOALS (Total)
    fg_made = int(total_stats['FGM']) 
    fg_missed = int(total_stats['FGA'] - fg_made)

    # THREE POINTERS (Total) 
    three_p_made = int(total_stats['3PM']) 
    three_p_missed = int(total_stats['3PA'] - three_p_made)

    # FREE THROWS (Total)
    ft_made = int(total_stats['FTM'])
    ft_missed = int(total_stats['FTA'] - ft_made)
    ###################################################################################################
    
    # Last 5 games 
    last_5_games = regular_season_games_played_df.tail(5)
    last_5_games['2PM'] = (last_5_games['FGM'] - last_5_games['3PM'])
    
    
    
    print('L 5 G')
    print(last_5_games)
    
    # Line Chart for all Games Played in the regular Season
    line_chart_games = regular_season_games_played_df.groupby(["GM_DAY"])[['PTS']].sum()
    fg_percent_line_chart = regular_season_games_played_df['FG%']
    

    # Player Total Game Summary
    player_summary = regular_season_games_played_df.describe()
    player_summary_heatmap = player_summary.loc[['max', '75%', '50%', '25%', 'min', 'std', 'mean']]


                                                 
    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    context = {

        'player_details': player_details,
        'competition': competition,

        'mean_points': mean_points,
        'mean_rebounds': mean_rebounds,
        'mean_assists': mean_assists,
        #All Players Summary
        'sum_x': team_sum_matrix_df.columns.tolist(),
        'sum_y': team_sum_matrix_df.index.tolist(),
        'sum_z': team_sum_matrix_df.values.tolist(),

        # Players Mean
        'mean_x': team_mean_matrix_df.columns.tolist(),
        'mean_y': team_mean_matrix_df.index.tolist(),
        'mean_z': team_mean_matrix_df.values.tolist(),
        
        # Player Summary
        'summary_x': player_summary_heatmap.columns.tolist(),
        'summary_y': player_summary_heatmap.index.tolist(),
        'summary_z': player_summary_heatmap.values.tolist(), #These are now floats (e.g. 29.333)

        # Line Chart GAmes
        'gameLabel': line_chart_games.index.tolist(),
        'gameValues': line_chart_games.values.tolist(),
        'fg_percentValues': fg_percent_line_chart.values.tolist(),


       
        # Labels for the Bar Chart
        'bar_labels': ['PTS','REB','AST','FGM','FGA','3PM','3PA','FTM','FTA','ORB','DRB', 'TOV','STL','BLK','PF','EFF', 'DEF'],
        # The calculated totals for the Bar Chart
        'bar_data': total_stats[['PTS','REB','AST','FGM','FGA','3PM','3PA','FTM','FTA','ORB','DRB', 'TOV','STL','BLK','PF','EFF', 'DEF']].tolist(),
        # Doughnut Data: [Made, Missed]
        # Passing the [Made, Missed] pairs directly to the Doughnuts
        'fg_stats': [fg_made, fg_missed],
        'three_p_stats': [three_p_made, three_p_missed],
        'ft_stats': [ft_made, ft_missed],
        

    }

    return render(request, 'player-dashboard.html', context)
"""


def player_stats_charts(request, player_slug):
    player_details = get_object_or_404(Player, slug=player_slug)
    other_players = Player.objects.exclude(slug=player_slug).order_by('player_name')
    competition = player_details.team.competitions
    
    # Get the player's statistics
    tournament_stats = PlayerStatLine.objects.filter(player_name=player_details)
    
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)

    # 1. THE IF CONDITION CHECK
    if tournament_stats.exists():
        # ---- PANDAS ANALYTICS PATH ----
        player_stats_df = pd.DataFrame(
            tournament_stats.values(
                'player_name__id', 'player_name__slug', 'player_name__jersey_number','player_name__player_name', 
                'player_name__player_image','points', 'assists', 
                'field_goal_attempts', 'field_goal_made', 'ft_attempts', 'ft_made',
                'point_3_attempts', 'point_3_made',
                'turnovers', 'minutes',  'blocks', 'steals', 'personal_fouls',
                'offensive_rebs', 'defensive_rebs',
                'team__name', 'game_schedule__opponent__name', 'game_schedule__opponent__abbreviation',
                'game_schedule__date', 'game_schedule__team_win_loss',
                'game_schedule__indicator', 'game_schedule__competition__name', 'game_schedule__game_type',
                'game_schedule__competition__year__year','game_schedule__team_scores', 'game_schedule__opponent_scores'
            )
        )

        player_stats_df = player_stats_df.rename(columns={'player_name__id':'player_id'})          
        player_stats_df['total_rebounds'] = player_stats_df['offensive_rebs'] + player_stats_df['defensive_rebs']
        player_stats_df['game_schedule__date'] = (pd.to_datetime(player_stats_df['game_schedule__date'])).dt.strftime('%d/%m/%Y')
        player_stats_df['fg_percent'] = (((player_stats_df['field_goal_made'] / player_stats_df['field_goal_attempts']) * 100).round(1)).fillna(0)
        
        player_stats_df['game_schedule__competition__name'] = player_stats_df['game_schedule__competition__name'].apply(
            lambda x: "".join([word[0].upper() for word in str(x).split()])
        )
            
        player_stats_df["efficiency"] = (
            player_stats_df["points"]
            + player_stats_df["total_rebounds"]
            + player_stats_df["assists"]
            + player_stats_df["steals"]
            + player_stats_df["blocks"]
            - (
                (player_stats_df["field_goal_attempts"] - player_stats_df["field_goal_made"])
                + (player_stats_df["ft_attempts"] - player_stats_df["ft_made"])
                + player_stats_df["turnovers"]
            )
        )         
        player_stats_df['def'] = player_stats_df['steals'] * 2 + player_stats_df['blocks'] * 2 + player_stats_df['defensive_rebs'] * 0.5 
        
        # TEAM TOTALS MATRIX
        all_games = Game.objects.all().prefetch_related('quarterly_scores')
        all_game_stats = PlayerStatLine.objects.filter(game_schedule__in=all_games)
        
        all_games_values = pd.DataFrame(
            all_game_stats.values(
                'player_name__id', 'player_name__slug', 'player_name__jersey_number','player_name__player_name', 
                'player_name__player_image','points', 'assists', 
                'field_goal_attempts', 'field_goal_made','ft_attempts', 'ft_made',
                'point_3_attempts', 'point_3_made',
                'turnovers', 'minutes',  'blocks', 'steals', 'personal_fouls',
                'offensive_rebs', 'defensive_rebs',
                'team__name', 'game_schedule__opponent__name','game_schedule__opponent__abbreviation',
                'game_schedule__date', 'game_schedule__team_win_loss',
                'game_schedule__indicator', 'game_schedule__competition__name', 'game_schedule__game_type',
                'game_schedule__competition__year__year','game_schedule__team_scores', 'game_schedule__opponent_scores'
            )
        )

        all_games_values = all_games_values.rename(columns={'player_name__id':'player_id'})          
        all_games_values['total_rebounds'] = all_games_values['offensive_rebs'] + all_games_values['defensive_rebs']
        all_games_values['game_schedule__date'] = (pd.to_datetime(all_games_values['game_schedule__date'])).dt.strftime('%d/%m/%Y')
        
        all_games_values['game_schedule__competition__name'] = all_games_values['game_schedule__competition__name'].apply(
            lambda x: "".join([word[0].upper() for word in str(x).split()])
        )
            
        all_games_values["efficiency"] = (
            all_games_values["points"]
            + all_games_values["total_rebounds"]
            + all_games_values["assists"]
            + all_games_values["steals"]
            + all_games_values["blocks"]
            - (
                (all_games_values["field_goal_attempts"] - all_games_values["field_goal_made"])
                + (all_games_values["ft_attempts"] - all_games_values["ft_made"])
                + all_games_values["turnovers"]
            )
        )         
        all_games_values['def'] = all_games_values['steals'] * 2 + all_games_values['blocks'] * 2 + all_games_values['defensive_rebs'] * 0.5 

        team_matrix_df = all_games_values[all_games_values['game_schedule__game_type'].isin(["regular"])]
        team_matrix_df = team_matrix_df[~team_matrix_df['game_schedule__team_scores'].isin([0])]
        team_matrix_df = team_matrix_df[[ "player_name__player_name", 'points', "total_rebounds",'assists','field_goal_attempts', 'field_goal_made',  'point_3_attempts', 'point_3_made',
                                             'ft_attempts', 'ft_made', 'offensive_rebs', 'defensive_rebs','turnovers',  'blocks', 'steals', 'personal_fouls',
                                             'efficiency', 'def']]
        team_matrix_df = team_matrix_df.rename(columns={"points":"PTS","total_rebounds":"REB","assists":"AST","field_goal_made":"FGM","field_goal_attempts":"FGA",
                                                        "point_3_made":"3PM", "point_3_attempts":"3PA", "ft_made": "FTM", "ft_attempts":"FTA", "offensive_rebs":"ORB", "defensive_rebs":"DRB",
                                                        "turnovers":"TOV","steals":"STL","blocks":"BLK","personal_fouls":"PF","efficiency":"EFF", 'def':'DEF'})                                        
        
        team_sum_matrix_df = team_matrix_df.groupby(["player_name__player_name"])[['PTS','REB','AST','FGM','FGA','3PM','3PA','FTM','FTA','ORB','DRB', 'TOV','STL','BLK','PF','EFF', 'DEF']].sum().sort_values(by='PTS',ascending=True)  
        team_mean_matrix_df = team_matrix_df.groupby(["player_name__player_name"])[['PTS','REB','AST','FGM','FGA','3PM','3PA','FTM','FTA','ORB','DRB', 'TOV','STL','BLK','PF','EFF', 'DEF']].mean().round(1).sort_values(by='PTS',ascending=True)  
        
        # INDIVIDUAL SUMMARY
        regular_season_games_played_df = player_stats_df[player_stats_df['game_schedule__game_type'].isin(["regular"])]
        regular_season_games_played_df = regular_season_games_played_df[~regular_season_games_played_df['game_schedule__team_scores'].isin([0])]
        regular_season_games_played_df = regular_season_games_played_df[['game_schedule__date','game_schedule__indicator','game_schedule__team_win_loss', 'game_schedule__opponent__name', 'game_schedule__opponent__abbreviation',
                                                                            'points', "total_rebounds",'assists','field_goal_attempts', 'field_goal_made',  'point_3_attempts', 'point_3_made',
                                                                            'ft_attempts', 'ft_made', 'offensive_rebs', 'defensive_rebs','turnovers',  'blocks', 'steals', 'personal_fouls',
                                                                            'efficiency', 'def']]

        regular_season_games_played_df['fg_percent'] = (((regular_season_games_played_df['field_goal_made'] / regular_season_games_played_df['field_goal_attempts']) * 100).round(1)).fillna(0)
        regular_season_games_played_df["vs_opp_win_loss"] =  regular_season_games_played_df['game_schedule__team_win_loss'].replace({'Win':'W', 'Loss':'L'})+'-'+regular_season_games_played_df['game_schedule__indicator']+'-'+ regular_season_games_played_df['game_schedule__opponent__abbreviation'] 
        regular_season_games_played_df["GM_DAY"] =  regular_season_games_played_df['game_schedule__date']+'-'+regular_season_games_played_df["vs_opp_win_loss"] 
        
        regular_season_games_played_df = regular_season_games_played_df.rename(columns={"points":"PTS","total_rebounds":"REB","assists":"AST","field_goal_made":"FGM","field_goal_attempts":"FGA", 'fg_percent':'FG%',
                                                                                        "point_3_made":"3PM", "point_3_attempts":"3PA", "ft_made": "FTM", "ft_attempts":"FTA", "offensive_rebs":"ORB", "defensive_rebs":"DRB",
                                                                                        "turnovers":"TOV","steals":"STL","blocks":"BLK","personal_fouls":"PF","efficiency":"EFF", 'def':'DEF'})  
        
        mean_points = regular_season_games_played_df['PTS'].mean().astype(float).round(1)
        mean_rebounds = regular_season_games_played_df['REB'].mean().astype(float).round(1)
        mean_assists = regular_season_games_played_df['AST'].mean().astype(float).round(1)
        
        total_stats = regular_season_games_played_df.sum(numeric_only=True)
        fg_made = int(total_stats['FGM']) 
        fg_missed = int(total_stats['FGA'] - fg_made)
        three_p_made = int(total_stats['3PM']) 
        three_p_missed = int(total_stats['3PA'] - three_p_made)
        ft_made = int(total_stats['FTM'])
        ft_missed = int(total_stats['FTA'] - ft_made)
        
        last_5_games = regular_season_games_played_df.tail(5).copy()
        last_5_games['2PM'] = (last_5_games['FGM'] - last_5_games['3PM'])
        
        line_chart_games = regular_season_games_played_df.groupby(["GM_DAY"])[['PTS']].sum()
        fg_percent_line_chart = regular_season_games_played_df['FG%']
        
        player_summary = regular_season_games_played_df.describe()
        player_summary_heatmap = player_summary.loc[['max', '75%', '50%', '25%', 'min', 'std', 'mean']]

        # Context built with data sets
        context = {
            'player_details': player_details,
            'competition': competition,
            'has_stats': True,
            'mean_points': mean_points,
            'mean_rebounds': mean_rebounds,
            'mean_assists': mean_assists,
            'sum_x': team_sum_matrix_df.columns.tolist(),
            'sum_y': team_sum_matrix_df.index.tolist(),
            'sum_z': team_sum_matrix_df.values.tolist(),
            'mean_x': team_mean_matrix_df.columns.tolist(),
            'mean_y': team_mean_matrix_df.index.tolist(),
            'mean_z': team_mean_matrix_df.values.tolist(),
            'summary_x': player_summary_heatmap.columns.tolist(),
            'summary_y': player_summary_heatmap.index.tolist(),
            'summary_z': player_summary_heatmap.values.tolist(),
            'gameLabel': line_chart_games.index.tolist(),
            'gameValues': line_chart_games.values.tolist(),
            'fg_percentValues': fg_percent_line_chart.values.tolist(),
            'bar_labels': ['PTS','REB','AST','FGM','FGA','3PM','3PA','FTM','FTA','ORB','DRB', 'TOV','STL','BLK','PF','EFF', 'DEF'],
            'bar_data': total_stats[['PTS','REB','AST','FGM','FGA','3PM','3PA','FTM','FTA','ORB','DRB', 'TOV','STL','BLK','PF','EFF', 'DEF']].tolist(),
            'fg_stats': [fg_made, fg_missed],
            'three_p_stats': [three_p_made, three_p_missed],
            'ft_stats': [ft_made, ft_missed],
        }
    else:
        # ---- DJANGO FALLBACK PATH (No stats exist) ----
        context = {
            'player_details': player_details,
            'competition': competition,
            'has_stats': False,
            'mean_points': 0,
            'mean_rebounds': 0,
            'mean_assists': 0,
            # Pass blank lists so your javascript chart elements won't throw null reference errors
            'sum_x': [], 'sum_y': [], 'sum_z': [],
            'mean_x': [], 'mean_y': [], 'mean_z': [],
            'summary_x': [], 'summary_y': [], 'summary_z': [],
            'gameLabel': [], 'gameValues': [], 'fg_percentValues': [],
            'bar_labels': [], 'bar_data': [],
            'fg_stats': [0, 0], 'three_p_stats': [0, 0], 'ft_stats': [0, 0],
        }

    return render(request, 'player-dashboard.html', context)


###########################################################################
##########################################################################
##########################################################################
# Apex Charts...
def player_shot_chart(request, player_slug): 
    player_details = get_object_or_404(Player, slug=player_slug,)
    other_players = Player.objects.exclude(slug=player_slug).order_by('player_name')
    competition = player_details.team.competitions
    

    # Get the player's statistics
    tournament_stats = PlayerStatLine.objects.filter(player_name=player_details)
    other_players_stats = PlayerStatLine.objects.filter(player_name__in=other_players)
    #charts = ShotCharts.objects.filter(player=player_details)
    


    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    if tournament_stats.exists():
        player_stats_df = pd.DataFrame(
                    tournament_stats.values('player_name__id','player_name__slug', 'player_name__jersey_number','player_name__player_name', 
                                'player_name__player_image','points', 'assists', 
                                'field_goal_attempts', 'field_goal_made', 'ft_attempts', 'ft_made',
                                'point_3_attempts', 'point_3_made',
                                'turnovers', 'minutes',  'blocks', 'steals', 'personal_fouls',
                                'offensive_rebs', 'defensive_rebs',
                                'team__name', 'game_schedule__opponent__name', 'game_schedule__opponent__abbreviation',
                                'game_schedule__date', 'game_schedule__team_win_loss',
                                'game_schedule__indicator', 'game_schedule__competition__name', 'game_schedule__game_type',
                                'game_schedule__competition__year__year','game_schedule__team_scores', 'game_schedule__opponent_scores'))
        # Create the mapping dictionary
        column_mapping = {
            'player_name__id': 'player_id','player_name__jersey_number': 'jersey_number','player_name__player_name': 'player_name','player_name__player_image': 'player_image',
            'field_goal_attempts': 'fga','field_goal_made': 'fgm','point_3_attempts': 'p3a','point_3_made': 'p3m',
            'ft_attempts': 'fta','ft_made': 'ftm','offensive_rebs': 'oreb','defensive_rebs': 'dreb','personal_fouls': 'pf',
            'team__name': 'team_name','game_schedule__opponent__name': 'opponent_name','game_schedule__opponent__abbreviation': 'opponent_abbr',
            'game_schedule__date': 'game_date','game_schedule__team_win_loss': 'result','game_schedule__indicator': 'location', # e.g., @ or vs
            'game_schedule__competition__name': 'competition','game_schedule__game_type': 'game_type','game_schedule__competition__year__year': 'season',
            'game_schedule__team_scores': 'team_score','game_schedule__opponent_scores': 'opponent_score'
        }

        # Apply the rename
        player_stats_df.rename(columns=column_mapping, inplace=True)

                
        player_stats_df['rebs'] = player_stats_df['oreb'] + player_stats_df['dreb']
        player_stats_df['game_date'] = (pd.to_datetime(player_stats_df['game_date']))#.dt.strftime('%d/%m/%Y')
        #player_stats_df['fg_%'] = (((player_stats_df['fgm'] / player_stats_df['fga']) * 100).round(1)).fillna(0)
        # This lambda is to abbreviate the League Name with the first letter of each words  (e.g., "Programming Languages" becomes "PL")
        player_stats_df['competition'] = player_stats_df['competition'].apply(
                                                    lambda x: "".join([word[0].upper() for word in str(x).split()]))
            
        # Calculation the efficiency of the games
        player_stats_df["efficiency"] = (
                                    player_stats_df["points"]
                                    + player_stats_df["rebs"]
                                    + player_stats_df["assists"]
                                    + player_stats_df["steals"]
                                    + player_stats_df["blocks"]
                                    - (
                                        (player_stats_df["fga"] - player_stats_df["fgm"])
                                        + (player_stats_df["fta"] - player_stats_df["ftm"])
                                        + player_stats_df["turnovers"]
                                    )
                                )         
        # Players Defence Calculation
        player_stats_df['def'] = player_stats_df['steals'] * 2 + player_stats_df['blocks'] * 2 + player_stats_df['dreb'] * 0.5 
        


        # Players Defence Calculation
        player_stats_df = player_stats_df.sort_values(by='game_date', ascending=False)
        
        ###################################################################################################
        ##################################################################################################
        ###################################################################################################

        #point_trend['game_schedule__date'] = point_trend['game_schedule__date'].astype("string")
        


        last_5_df = player_stats_df[player_stats_df['game_type'].isin(["regular"])].copy()
        last_5_df = last_5_df[~last_5_df['team_score'].isin([0])]
        last_5_df['game_date'] = last_5_df['game_date'].dt.date
        last_5_df['game_date'] = last_5_df['game_date'].astype("string")
        last_5_games_df = last_5_df.head()
        last_5_games_df['minutes'] = last_5_games_df['minutes'].astype(float)
        #cols = ['fgm', 'fga', '3pm', '3pa', 'ftm', 'fta', 'points']
        #last_5_games_df[cols] = last_5_games_df[cols].astype(float)
    
        last_5_games_list = last_5_games_df.to_dict('records')
        last_5_games_json = json.dumps(last_5_games_list)
    
        print(last_5_games_json)

        context = {
            'player_details': player_details,
            'competition': competition,
            'charts': ShotCharts.objects.filter(player=player_details),
            'last_5_games_json': last_5_games_json,
            'last_5_games': last_5_games_list,
        }


        return render(request, 'shot-charts.html', context)
    else:
        context = {
            'player_details': player_details,
            'competition': competition,
          
        }


        return render(request, 'shot-charts.html', context)

############################################################################
##############################################################################
##############################################################################

# UPDATE PLAYER

class PlayerUpdateView(SuperuserRequiredMixin, View):
    """def get(self, request, player_slug, competition_slug,):
        competition = get_object_or_404(Competition, slug=competition_slug)
        player = get_object_or_404(Player, slug=player_slug, team=competition.team)
        form = PlayerForm(request.POST or None, instance=player)
        return render(request, 'players_update.html', {'form': form, 'player': player, 'competition': competition})
    """
    def get(self, request, player_slug, competition_slug):
        competition = get_object_or_404(Competition, slug=competition_slug)
        player = Player.objects.filter(slug=player_slug).first()
        form = PlayerForm(request.POST or None, instance=player)     
        return render(request, 'players_update.html', {
            'form': form, 
            'player': player, 
            'competition': competition
        })    

    def post(self, request, player_slug, competition_slug):
        competition = get_object_or_404(Competition, slug=competition_slug)
        update_player = get_object_or_404(Player, slug=player_slug, team=competition.team)
        form = PlayerForm(request.POST, request.FILES, instance=update_player)
        if form.is_valid():
            form.save()
            messages.success(request, "Player Updated Successfully :)")
            return redirect('players-id', competition_slug=competition_slug, slug=player_slug)

        return render(request, 'players_update.html', {'form': form, 'update_players': update_player, 'competition': competition})




# Player Delete Function
@user_passes_test(is_superuser, login_url='/')
def delete_player(request, slug, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    team = competition.team 
    player = get_object_or_404(Player, slug=slug, team=team)
    player.delete()
    messages.success(request, "Player deleted successfully.")
    return redirect('team-roster', competition_slug=competition_slug, team_slug=team.slug)


      




####################################################################################
####################################################################################
# Team Staff
####################################################################################
####################################################################################
@method_decorator(user_passes_test(is_superuser, login_url='/'), name='dispatch')
class StaffCreateView(APIView):
    def get(self, request):
        form = TeamStaffForm()
        
        submitted = 'submitted' in request.GET
        return render(request, 'staff_registration.html', {"form": form,  'submitted': submitted})

    def post(self, request):
        form = TeamStaffForm(request.POST, request.FILES)
        
        if form.is_valid():
            team = form.save()
            
            messages.success(request, "Staff Added Successfully :)")
            return HttpResponseRedirect('/staff_create?submitted=True')
        else:
            messages.error(request, "There were errors in the form. Please correct them and try again.")
            print("staff Form Errors:", form.errors)  # Debug: Print team form errors
            
        return render(request, 'staff_registration.html', {"form": form, "team": team, 'submitted': False})


# Class Base View For Team Details
class StaffDetailView(APIView):
    def get(self, request, pk):
        staff_details = get_object_or_404(TeamStaff, slug=slug)
       

        context = { }
        return render(request, 'staff_details.html', context)



# UPDATE STAFF
@method_decorator(user_passes_test(is_superuser, login_url='/'), name='dispatch')
class StaffUpdateView(View):
    def get(self, request, competition_slug, staff_slug):
        competition = get_object_or_404(Competition, slug=competition_slug)
        staff = get_object_or_404(TeamStaff, slug=staff_slug, team=competition.team)
        form = TeamStaffForm(request.POST or None, instance=staff)
        return render(request, 'staff_update.html', {'form': form, 'staff': staff, 'staff': staff, 'competition': competition})

    def post(self, request,  competition_slug, staff_slug):
        competition = get_object_or_404(Competition,  slug=competition_slug)
        staff = get_object_or_404(TeamStaff, slug=staff_slug, team=competition.team)

        form = TeamStaffForm(request.POST or None, instance=staff)
        if form.is_valid():
            form.save()

            return redirect('team-roster', competition_slug=competition.slug )    


        return render(request, 'staff_update.html', {'form': form, 'staff': staff, 'staff': staff, 'competition': competition})





# Player Delete Function
@method_decorator(user_passes_test(is_superuser, login_url='/'), name='dispatch')
class StaffDeleteView(APIView): 
    pass       




####################################################################################
####################################################################################
# Opponents
####################################################################################
####################################################################################
# Class Base View Creating Opponents
class OpponentCreateView(SuperuserRequiredMixin, APIView):
    def get(self, request):
        form = OpponentForm()
        return render(request, 'opponents_registration.html', {"form": form, })

    def post(self, request):
        form = OpponentForm(request.POST, request.FILES) 
        
        if form.is_valid():
            # SUCCESS PATH
            team = form.save()    
            messages.success(request, "Team Added Successfully :)")
            # Redirect to GET endpoint to clear the form data
            return HttpResponseRedirect('/opponent create?')
        else:
            # FAILURE PATH
            print(form.errors) 
            messages.error(request, "There were errors in the form. Please correct them and try again.")
            
            # 🚀 FIX: Only return the form object, not the non-existent 'team' object
            return render(request, 'opponents_registration.html', {"form": form})


#  Class Base View For Opponent List
class OpponentListView(APIView):
    def get(self, request):
        opponents = Opponent.objects.all()
        #players = opponents.opponent_player.all()
        print(opponents)
        #return Response(serializer.data) 
        return render(request, 'opponents_list.html', {'opponents':opponents})            



# Class Base View For Team Details
class OpponentDetailView(APIView):
    def get(self, request, slug):
        opponent_details = get_object_or_404(Opponent, slug=slug)
        
        if opponent_details:
            opp_players = Player.objects.filter(opponent=opponent_details).order_by('-jersey_number')
        else:
            opp_players = "Non rgistered players for this team."
        

        context = {
            'team_details': {
                'pk': opponent_details.slug,  # Include the primary key
                'logo': opponent_details.logo.url,
                'name': opponent_details.name,
                'opp_players': opp_players,
                
                
            },
            'opp_players': opp_players,
        }
        return render(request, 'opponents_details.html', context)


# Class Base View For Update
class OpponentUpdateView(APIView):
    # Handle GET and POST requests to UPDATE team details
    def get(self, request, slug):
        update_opponents = get_object_or_404(Opponent, slug=slug)
        form = OpponentForm(request.POST or None, instance=update_opponents)
        return render(request, 'opponent_update.html', {'form': form, 'update_opponents': update_opponents})

    def post(self, request, slug):
        update_opponents = get_object_or_404(Opponent, slug=slug)
        form = OpponentForm(request.POST, request.FILES, instance=update_opponents)

        if form.is_valid():
            form.save()
            # Return a valid update message.
            messages.success(request, (" Team Updated Sucessfully ):"))
            return redirect('opponent-id', pk=pk)
        return render(request, 'opponent_update.html', {'form': form, 'update_opponents': update_opponents})         
                       


# Function Base View For Deleting 
# DELETE COMPETITION
@user_passes_test(is_superuser, login_url='/')
def delete_opponent(request, slug):
    opponent = get_object_or_404(Opponent, slug=slug)
    opponent.delete()
    # Return an 'invalid login' error message.
    messages.success(request, (" Team deleted successfully ):"))
    return redirect('opponent-list')        



####################################################################################
####################################################################################
# News View
####################################################################################
####################################################################################








gameScoresFormSet = inlineformset_factory(Game, QuarterlyScores, form=QuarterlyScoresForm, extra=1, can_delete=False, max_num=1)

class GameCreateView(SuperuserRequiredMixin, APIView):

    def get(self, request, competition_slug):
        #  Pre-fill the competition field using initial
        form = GameForm(initial={'competition': competition_slug})
        formset = gameScoresFormSet()
        return render(request, 'game_registration.html', {
            "form": form,
            "formset": formset,
            "competition_id": competition_slug
        })

    def post(self, request, competition_slug):
        form = GameForm(request.POST, request.FILES)
        formset = gameScoresFormSet(request.POST, request.FILES)

        if form.is_valid():
            game = form.save()
            # Binding formset to the newly created game
            formset = gameScoresFormSet(request.POST, instance=game)

            if formset.is_valid():
                formset.save()
                messages.success(request, "Game and Scores Added Successfully :)")
                
                return redirect('game-list', competition_slug=competition_slug)
            else:
                # If scores fail, delete the game so you don't have a game without scores
                game.delete()
                messages.error(request, "Score form has errors.")
        else:
            messages.error(request, "Game form has errors.")

        # If errors, re-render with both forms
        return render(request, 'game_registration.html', {
            "form": form,
            "formset": formset,
            "competition_id": competition_slug
        })


class GameListView(APIView):
   def get(self, request, competition_slug): 
        competition = get_object_or_404(Competition, slug=competition_slug)
        all_competition = Competition.objects.all()
        
        # Using the 'quarterly_scores' name here!
        games = competition.competition.all().prefetch_related('quarterly_scores').order_by('-date')
        
        other_games = Game.objects.exclude(competition=competition).prefetch_related('quarterly_scores')
        
        return render(request, 'game_list.html', {
            'games': games, 
            'competition': competition,
            'all_competition': all_competition,
            'other_games': other_games,
        })




class GameScheduleView(APIView):
   def get(self, request, competition_slug): 
        competition = get_object_or_404(Competition, slug=competition_slug)
      
        # Using the 'quarterly_scores' name here!
        games = Game.objects.filter(competition=competition).order_by('-date')
        other_competitions_games =  Game.objects.exclude(competition=competition)
        game_stats = PlayerStatLine.objects.filter(game_schedule__in=games)
        
        # Fetch standings and the related game type
        tournament_standing = Standing.objects.filter(
            competition=competition,
        ).select_related('team', 'opponent',)

        #SEt up pagination
        paginator = Paginator(GalleryImages.objects.all(), 6) 
        page_number = request.GET.get('page')
        images = paginator.get_page(page_number)
        ######################################################
      
        if game_stats.exists():
            wins = 0
            losses = 0
            games_with_records = []  # Creating a new list to hold the games with their calculated records

            for w_l in games: # Calculating the Win - Loss Records 
                if w_l.team_win_loss == 'Win':
                    wins += 1
                elif w_l.team_win_loss == 'Loss':
                    losses += 1
                w_l.running_record = f"{wins}-{losses}" 

                # Using 'game_stats' related_name to find the highest values fo the stats of each game by using the django aggregate function
                top_pts = w_l.game_stats.order_by('-points').first()
                top_reb = w_l.game_stats.annotate(total_rebs=F('offensive_rebs') + F('defensive_rebs')).order_by('-total_rebs').first()
                top_ast = w_l.game_stats.order_by('-assists').first()

                # This is to format the names of the players name 
                #Points 
                if top_pts and top_pts.player_name:
                    parts = top_pts.player_name.player_name.split()
                    w_l.leader_pts = f"{parts[0][0]}. {parts[-1]} {top_pts.points}"
                    w_l.leader_pts_id = top_pts.player_name.slug
                else:
                    w_l.leader_pts = " "
                    w_l.leader_pts_id = None

                # Rebounds
                if top_reb and top_reb.player_name:
                    parts = top_reb.player_name.player_name.split()
                    w_l.leader_reb = f"{parts[0][0]}. {parts[-1]} {top_reb.total_rebs}"
                    w_l.leader_reb_id = top_reb.player_name.slug
                else:
                    w_l.leader_reb = " "
                    w_l.leader_reb_id = None

                # Assists
                if top_ast and top_ast.player_name:
                    parts = top_ast.player_name.player_name.split()
                    w_l.leader_ast = f"{parts[0][0]}. {parts[-1]} {top_ast.assists}"
                    w_l.leader_ast_id = top_ast.player_name.pk
                else:
                    w_l.leader_ast = " "
                    w_l.leader_ast_id = None

                # Adding the modified game object the final list
                games_with_records.append(w_l)
            else:
                games_with_records = []   

         
        #####################################################
        ######################################################
        #####################################################    
        # Get the player's statistics
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
        if games.exists():
            # Convert to DataFrame
            all_games_df = pd.DataFrame(
                        games.values('id', 'slug', 'competition__name','competition__year__year','date','time','team__name', 'team__team_logo', 'team__city','indicator','opponent__name', 'opponent__logo',
                                        'team_scores', 'opponent_scores', 'opponent__city','team_win_loss', 'game_venue__name', 'game_type',
                                    ))

            # Let's convert it to datetime column 
            stats_df = pd.DataFrame( game_stats.values('game_schedule__date',  'game_schedule_id', 'player_name__id', 'player_name__player_name',
                                            'points','assists', 'offensive_rebs','defensive_rebs', 'game_schedule__game_type',  ))
            stats_df = stats_df.rename(columns={'game_schedule__date': 'date'}) 
        
            stats_df['rebounds'] = stats_df['offensive_rebs'] + stats_df['defensive_rebs']    

            #######################################################################################################
            ######################################################################################################
            #######################################################################################################
            regular_season_games_played_df = all_games_df[all_games_df['game_type'].isin(["regular"])].copy()
            regular_season_games_played_df_stats_df = stats_df[stats_df['game_schedule__game_type'].isin(["regular"])].copy()
            
            # Top performers of the games
            pts_leaders = regular_season_games_played_df_stats_df.loc[regular_season_games_played_df_stats_df.groupby('date')['points'].idxmax()].sort_values('date', ascending=False)
            reb_leaders = regular_season_games_played_df_stats_df.loc[regular_season_games_played_df_stats_df.groupby('date')['rebounds'].idxmax()].sort_values('date', ascending=False)
            ast_leaders = regular_season_games_played_df_stats_df.loc[regular_season_games_played_df_stats_df.groupby('date')['assists'].idxmax()].sort_values('date', ascending=False)
            #playoff_games = all_games_df[all_games_df['game_type'].isin(["playoff"])].copy()
            
            
            regular_season_games_played_df = regular_season_games_played_df.drop_duplicates(subset=['id']) 
            regular_season_games_played_df = regular_season_games_played_df.merge(pts_leaders, how= 'left',on='date').merge(reb_leaders, how= 'left',on='date').merge(ast_leaders, how= 'left',on='date')               
            
            
            # Create columns for cumulative wins and losses
            regular_season_games_played_df['is_win'] = (regular_season_games_played_df['team_win_loss'] == 'Win').astype(int)
            regular_season_games_played_df['is_loss'] = (regular_season_games_played_df['team_win_loss'] == 'Loss').astype(int)


            # Usiing cumsum() to get the running total
            regular_season_games_played_df['cum_wins'] = regular_season_games_played_df['is_win'].cumsum()
            regular_season_games_played_df['cum_losses'] = regular_season_games_played_df['is_loss'].cumsum()

            # Creating the "1-0", "1-1" string column
            regular_season_games_played_df['running_record'] = regular_season_games_played_df['cum_wins'].astype(str) + "-" + regular_season_games_played_df['cum_losses'].astype(str)
            print('REGULAR SEASON GAMES')   
            #print(regular_season_games_played_df)
            #######################################################################################################
            ######################################################################################################
            #######################################################################################################
            # Convert to DataFrame
            other_competitions_df = pd.DataFrame(
                        other_competitions_games.values('id', 'slug', 'competition__name','date','time','team__name', 'team__team_logo', 'team__city','indicator','opponent__name', 'opponent__logo',
                                        'team_scores', 'opponent_scores', 'opponent__city','team_win_loss', 'game_venue__name', 'game_type'))
            international_games = other_competitions_df[other_competitions_df['game_type'].isin(["international"])].copy()

            #######################################################################################################
            ######################################################################################################
            #######################################################################################################
            def player_of_the_month(month, pts):
                # Players Stats For Best Performer Of The Month
                montly_stats_df = pd.DataFrame(
                            game_stats.values('player_name__id','player_name__jersey_number','player_name__player_name', 
                                        'player_name__player_image','points', 'assists', 
                                    'offensive_rebs', 'defensive_rebs', 'game_schedule__date'))
                montly_stats_df['total_rebounds'] = montly_stats_df['offensive_rebs'] + montly_stats_df['defensive_rebs']   
                montly_stats_df['game_date'] = (pd.to_datetime(montly_stats_df['game_schedule__date'])) 
                montly_stats_df['year']    = pd.DatetimeIndex(montly_stats_df['game_schedule__date']).year
                montly_stats_df['month']   = pd.DatetimeIndex(montly_stats_df['game_schedule__date']).month
                                
                montly_stats_df = montly_stats_df.groupby(['player_name__player_name','player_name__player_image', 'player_name__jersey_number', 'month', 'year',])[['points','total_rebounds','assists']].mean().round(1).reset_index()
                month_may = montly_stats_df[montly_stats_df['month'] == month ][['player_name__player_name', 'player_name__jersey_number', 'player_name__player_image','points','total_rebounds','assists']].sort_values(by=pts, ascending=False).head(1).iloc[0]      
                print("Montly Stats")  
                #print(montly_stats_df)               
                print()
                print() 
                print("May")
                
                return month_may     
                
                
                
            #player_of_the_month(5, 'points')

            """
            montly_stats_df = pd.DataFrame(
                            game_stats.values('player_name__id','player_name__jersey_number','player_name__player_name', 
                                    'player_name__player_image','points', 'assists', 
                                'offensive_rebs', 'defensive_rebs', 'game_schedule__date'))
            montly_stats_df['total_rebounds'] = montly_stats_df['offensive_rebs'] + montly_stats_df['defensive_rebs']   
            montly_stats_df['game_date'] = (pd.to_datetime(montly_stats_df['game_schedule__date'])) 
            montly_stats_df['year']    = pd.DatetimeIndex(montly_stats_df['game_schedule__date']).year
            montly_stats_df['month']   = pd.DatetimeIndex(montly_stats_df['game_schedule__date']).month
                            
            montly_stats_df = montly_stats_df.groupby(['player_name__player_name','player_name__player_image', 'game_date',  'month', 'year',])[['points','total_rebounds','assists']].sum().reset_index()
            month_may = montly_stats_df[montly_stats_df['month'] == 5 ][['player_name__player_name', 'player_name__player_image','points','total_rebounds','assists']].sort_values(by='points', ascending=False).head().iloc[0]      
            print(month_may)
            print()
            #montly_stats = montly_stats_df.groupby([ 'month', 'player_name__player_name','player_name__player_image','year'])[[ 'points','total_rebounds','assists']].sum()
            """
        
            
            
            

            
            ######################################################################################################
            #####################################################################################################
            # 2. Convert to DataFrame
            standing_df = pd.DataFrame(
                tournament_standing.values( 'competition__name', 'game_type',
                    'team__name', 'team__team_logo', 
                    'opponent__name', 'opponent__logo',
                    'w', 'l', 'home_record', 'away_record', 
                    'ppg', 'opp_ppg', 'strk', 'last_5', 
                )
            ).sort_values('w', ascending=False).reset_index(drop=True)


            standing_df['team__name'] = standing_df['team__name'].fillna(standing_df['opponent__name'])
            standing_df['opponent__name'] = standing_df['opponent__name'].fillna(standing_df['team__name'])
            standing_df['team__team_logo'] = standing_df['team__team_logo'].fillna(standing_df['opponent__logo'])                             
            standing_df['opponent__logo'] = standing_df['opponent__logo'].fillna(standing_df['team__team_logo'])
            #######################################################################################################
            ######################################################################################################
            # Using the same names here as we do in the HTML ?key=
            game_type_val = request.GET.get('game_type')
            #date_val = request.GET.get('date')
            #competition_val = request.GET.get('competition_type')
            #color_val = request.GET.get('color_type')
            #gender_val = request.GET.get('gender_type')
        

        

            #######################################################################################################
            ######################################################################################################
            

        
        

            return render(request, 'game-schedule.html', {
                'games': games_with_records, 
                'competition': competition, 
                'standing_df': standing_df.to_dict('records'),
                'regular_season_games_played_df': regular_season_games_played_df.to_dict('records'),
                #'playoff_games': playoff_games.to_dict('records'),
                'other_competitions_df': international_games.to_dict('records'),
                # Player Of The Month
                'month_may': player_of_the_month(5, 'points'), #[:1],
                # Gallery Images
                'team_images': images,
            
            })        
        else:
            return render(request, 'game-schedule.html', {
                 
                'competition': competition, 
              
                # Gallery Images
                'team_images': images,
            
            })  

# Game Stats To PDF
def game_stats_pdf(request, slug):
    buf = io.BytesIO()
    # Using 0.4 inch margins to ensure all the advanced columns fit perfectly side-by-side
    doc = SimpleDocTemplate(
        buf, 
        pagesize=landscape(letter), 
        topMargin=0.4*inch, 
        bottomMargin=0.4*inch, 
        leftMargin=0.4*inch, 
        rightMargin=0.4*inch
    )
    elements = []
    styles = getSampleStyleSheet()

    # 1. RETRIEVE CORE DATA
    game = get_object_or_404(Game, slug=slug)
    print(game)

    # 2. HEADER TITLE BLOCK (FIBA Style PDF Layout)
  
    title_style = styles['Heading1']
    title_style.alignment = 1  # Center
    elements.append(Paragraph("<b>STATS HUB — GAME STATISTICS</b>", title_style))
    
    # --- CHANGE THIS SECTION ---
    # Create a clean sub-headline style right here
    sub_title_style = styles['Normal']
    sub_title_style.alignment = 1      # Center alignment (0=Left, 1=Center, 2=Right)
    sub_title_style.fontSize = 11      # Clear text size map
    sub_title_style.leading = 14       # Line spacing so text doesn't overlap
    
    sub_text = f"<b>{game.team.name.upper()} {game.team_scores} vs {game.opponent_scores} {game.opponent.name.upper()}</b><br/>Date: {game.date}"
    elements.append(Paragraph(sub_text, sub_title_style))
    elements.append(Spacer(1, 0.15 * inch))

    # 3. QUARTER PROGRESSION TABLE (Matches your PDF scoring sequence)
    # Note: Replace these strings with your dynamic quarter properties if available in your model
    score_data = [
        ['Team', 'Q1', 'Q2', 'Q3', 'Q4', 'Total'],
        [game.team.name[:15].upper(), '14', '13', '17', '12', str(game.team_scores)],
        [game.opponent.name[:15].upper(), '12', '8', '7', '9', str(game.opponent_scores)]
    ]
    score_table = Table(score_data, colWidths=[1.8*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.8*inch])
    score_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#35ad79")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 0.25 * inch))

    # COMPACT REUSABLE STATS GENERATOR FOR BOTH TEAMS
    def generate_team_stat_table(team_obj, primary_theme=True):
        headers = [[
            'No.', 'NAME', 'MIN', 'PTS', 'REB', 'AST', 'FG M/A', 'FG%', '3P M/A', '3P%', 'FT M/A', 'FT%', 
            'ORB', 'DRB', 'REB',  'STL', 'BLK', 'TOV', 'PF', '+/-', 'EFF', 'DEF'
        ]]
        rows = []
        
        # Accumulator metrics for team row totals at the bottom
        t_pts = t_ast = t_pf = t_to = t_st = t_bs = 0
        t_oreb = t_dreb = t_treb = t_plus_minus = t_eff = t_def = 0
        t_fgm = t_fga = t_3pm = t_3pa = t_ftm = t_fta = 0
        
        # Extract the lookup name correctly
        team_name_str = team_obj.name if hasattr(team_obj, 'name') else str(team_obj)

        # --- FIX: Dynamic Filter Arguments ---
        # Base filter tracking the match instance
        filter_kwargs = {'game_schedule': game}
        
        if primary_theme:
            # Home team checks the team name column
            filter_kwargs['team__name__iexact'] = team_name_str
        else:
            # Opponent team checks the opponent name column!
            filter_kwargs['opponent__name__iexact'] = team_name_str

        # Execute the cleanly routed query
        player_stats = PlayerStatLine.objects.filter(**filter_kwargs).order_by('player_name_id')
        
        for s in player_stats:
            total_reb = s.offensive_rebs + s.defensive_rebs
            efficiency = (s.points + total_reb + s.assists + s.steals + s.blocks
                          - ((s.field_goal_attempts - s.field_goal_made)
                             + (s.ft_attempts - s.ft_made) + s.turnovers))
            
            defense = s.steals * 2 + s.blocks * 2 + s.defensive_rebs * 0.5 
            
            fg_pct = round((s.field_goal_made / s.field_goal_attempts) * 100, 1) if s.field_goal_attempts > 0 else 0.0
            pt3_pct = round((s.point_3_made / s.point_3_attempts) * 100, 1) if s.point_3_attempts > 0 else 0.0
            ft_pct = round((s.ft_made / s.ft_attempts) * 100, 1) if s.ft_attempts > 0 else 0.0
            
            rows.append([
                str(s.player_name.jersey_number),
                str(s.player_name.player_name).upper() + ("*" if s.starter else ""),
                str(s.minutes),
                str(s.points),
                str(total_reb),
                str(s.assists),
                f"{s.field_goal_made}/{s.field_goal_attempts}",
                f"{fg_pct}%",
                f"{s.point_3_made}/{s.point_3_attempts}",
                f"{pt3_pct}%",
                f"{s.ft_made}/{s.ft_attempts}",
                f"{ft_pct}%",
                str(s.offensive_rebs),
                str(s.defensive_rebs),
                str(total_reb),
                str(s.steals),
                str(s.blocks),
                str(s.turnovers),
                str(s.personal_fouls),
                str(),
                str(efficiency),
                str(defense)
            ])
            
            # Totals scaling counter logic...
            t_pts += s.points
            t_ast += s.assists
            t_pf += s.personal_fouls
            t_to += s.turnovers
            t_st += s.steals
            t_bs += s.blocks
            t_oreb += s.offensive_rebs
            t_dreb += s.defensive_rebs
            t_treb += total_reb
            t_fgm += s.field_goal_made
            t_fga += s.field_goal_attempts
            t_3pm += s.point_3_made
            t_3pa += s.point_3_attempts
            t_ftm += s.ft_made
            t_fta += s.ft_attempts
            t_eff += efficiency
            t_def += defense

        team_fg_pct = round((t_fgm / t_fga) * 100, 1) if t_fga > 0 else 0.0
        team_3p_pct = round((t_3pm / t_3pa) * 100, 1) if t_3pa > 0 else 0.0
        team_ft_pct = round((t_ftm / t_fta) * 100, 1) if t_fta > 0 else 0.0

        # Construct totals footprint row array data
        # --- FIX: Ensure your columns align precisely (Added a missing str() space for column mapping alignment) ---
        rows.append([
            '', 'TOTALS', '200', str(t_pts), str(t_treb), str(t_ast),
            f"{t_fgm}/{t_fga}", f"{team_fg_pct}%",
            f"{t_3pm}/{t_3pa}", f"{team_3p_pct}%",
            f"{t_ftm}/{t_fta}", f"{team_ft_pct}%",
            str(t_oreb), str(t_dreb), str(t_treb),
            str(t_st),  str(t_bs),  str(t_to),  str(t_pf), '', str(t_eff), str(t_def)
        ])
        
        # Exact width display rules mapping across 22 structural table columns
        # --- FIX: Extended col_widths configuration list explicitly to match your 22 headers! ---
        col_widths = [
            0.3*inch, 1.3*inch, 0.4*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.6*inch, 0.5*inch, 0.6*inch, 0.5*inch, 0.6*inch, 0.5*inch,
            0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.3*inch, 0.4*inch, 0.4*inch
        ]
        
        table = Table(headers + rows, colWidths=col_widths)
        header_bg = colors.HexColor("#35ad79") if primary_theme else colors.HexColor("#333333")
        
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), header_bg),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5), # Dropped slightly for flawless rendering within 0.4 margins
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.whitesmoke, colors.white]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#e2ede8") if primary_theme else colors.HexColor("#eaeaea")), 
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        return table


    # 5. GENERATE DATA CHANNELS AND APPEND TO MAIN PDF STORY STREAM
    elements.append(Paragraph(f"<b>{game.team.name.upper()} STATISTICS</b>", styles['Normal']))
    elements.append(Spacer(1, 0.05 * inch))
    elements.append(generate_team_stat_table(game.team, primary_theme=True))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"<b>{game.opponent.name.upper()} STATISTICS</b>", styles['Normal']))
    elements.append(Spacer(1, 0.05 * inch))
    elements.append(generate_team_stat_table(game.opponent, primary_theme=False))

    # 6. COMPILE, SAVE FILE STREAM, AND DEPLOY DOWNLOAD ATTACHMENT
    doc.build(elements)
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=f"StatsHub_BoxScore_{game.id}.pdf")








# Game Detail View          
class GameDetailView(APIView):
    def get(self, request, pk, competition_id=None):
        if competition_id:
            competition = get_object_or_404(Competition, pk=competition_id)
            if competition.is_current_competition:
                team = competition.team
                opponent = competition.opponents

                game_details = get_object_or_404(Game, pk=pk, team=team)
                game_date = game_details.date.strftime(f"%Y-%m-%d")
                readable_date = game_details.date.strftime(f"%B %d, %Y")
                #opponent_game_details = get_object_or_404(Game, pk=pk, opponent=opponent)
                
                
                players = team.players.all()
                stats = PlayerStatLine.objects.filter(game_schedule=game_details) # Get the player's statistics of this game
                all_games = competition.competition.all().prefetch_related('quarterly_scores')
                #  Returns only the stats for the games in this competition.
                all_game_stats = PlayerStatLine.objects.filter(game_schedule__in=all_games)

                # Fetch standings and the related game type
                tournament_standing = Standing.objects.filter(competition=competition).select_related('team', 'opponent',)
                quarterly_scores = get_object_or_404(QuarterlyScores, game=game_details)  
                other_games = Game.objects.exclude(pk=pk).order_by('date')

                # Team players: where the team matches the game's home team
                #team_players = PlayerStatLine.objects.filter(team=game_details.team, game_schedule=game_details).order_by('-points')
                # Opponent players: where the team matches the game's opponent team!
                #opp_players = PlayerStatLine.objects.filter(opponent=game_details.opponent, game_schedule=game_details).order_by('-points')
                
                #print(team_players)
                
                #print("OPPONENT PLAYERS")
                #print(opp_players)
                ###############################################################################################
                ###################################Conversion To Pandas DataFrame #####################################
                ###############################################################################################
                pd.set_option("display.max_columns", None)
                pd.set_option("display.max_rows", None)

                #if all_games.exists():
                # Convert to DataFrame
                all_games_df = pd.DataFrame(
                            all_games.values('date','time','team__name', 'indicator','opponent__name', 
                                            'team_scores', 'opponent_scores', 'team_win_loss', 'game_venue', 'game_type'))
                # Getting the International Games
                international_games = pd.DataFrame(
                            other_games.values('id','date','time','team__name', 'team__team_logo','indicator','opponent__name', 
                                            'opponent__logo','team_scores', 'opponent_scores', 'team_win_loss', 'game_venue__name', 'game_type'))                            

                # Getting the regular season and playoffs games
                regular_season = all_games_df[all_games_df['game_type'].isin(["regular"])]
                #playoffs = all_games_df[all_games_df['game_type'].isin(["playoff"])]
                
                # International games
                int_games_in_other_games = international_games[international_games['game_type'].isin(["international"])]
                
                
              
                ###############################################################################################
                ###################################Conversion To Pandas DataFrame #####################################
                ###############################################################################################
                # All Game Statistics
                all_game_stats_df = pd.DataFrame(
                            all_game_stats.values('game_schedule__date','player_name__player_name', 'team__name', 
                                                  'offensive_rebs', 'defensive_rebs', 'assists', 'game_schedule__game_type'))
                                                        
                # Filtering the stats by games
                regular_season_games_played_df = all_game_stats_df[all_game_stats_df['game_schedule__game_type'].isin(["regular"])].copy()                                  
                regular_season_games_played_df['total_rebounds'] = regular_season_games_played_df['offensive_rebs'] + regular_season_games_played_df['defensive_rebs']
                regular_season_games_played_df = regular_season_games_played_df[['game_schedule__date', 'player_name__player_name', 'team__name', 
                                                        'offensive_rebs', 'defensive_rebs','total_rebounds', 'assists']]
                regular_season_games_played_df = regular_season_games_played_df.groupby('game_schedule__date')[[ 'player_name__player_name', 'team__name', 
                                                        'offensive_rebs', 'defensive_rebs','total_rebounds', 'assists']].sum().reset_index()                                        
                regular_season_games_played_df = regular_season_games_played_df.rename(columns={'game_schedule__date': 'date'}) 
                # Merging or concatinating to Calculating the Mean scores of the team scores and the opponent scores
                merge_df = regular_season.merge(regular_season_games_played_df, how= 'left',on='date')
                merge_df  = merge_df [~merge_df['team_scores'].isin([0])]
                mean_merge_df = merge_df[['team_scores', 'opponent_scores','offensive_rebs', 
                                        'defensive_rebs','total_rebounds', 'assists']].mean().astype(float) 
                #print(mean_merge_df)
                # Calculate averages                        
                ###############################################################################################
                ###############################################################################################
                ###############################################################################################
                # Players Stats For Best Performer
                stats_df = pd.DataFrame(
                            stats.values('player_name__id','player_name__jersey_number','team__name', 'opponent__name','player_name__player_name', 
                                        'player_name__player_image','points', 'assists', 
                                        'field_goal_attempts', 'field_goal_made', 'ft_attempts', 'ft_made',
                                        'point_3_attempts', 'point_3_made',
                                        'turnovers', 'minutes',  'blocks', 'steals',
                                         'personal_fouls',
                                        'player_name__team__name','offensive_rebs', 'defensive_rebs'))

                stats_df = stats_df.rename(columns={'player_name__id':'player_id', })          
                stats_df['total_rebounds'] = stats_df['offensive_rebs'] + stats_df['defensive_rebs']
                stats_df['fg_percent'] = ((stats_df['field_goal_made'] / stats_df['field_goal_attempts']) * 100).fillna(0)
                stats_df['point_3_percent'] = ((stats_df['point_3_made'] / stats_df['point_3_attempts']) * 100).fillna(0)
                stats_df['ft_percent'] = ((stats_df['ft_made'] / stats_df['ft_attempts']) * 100).fillna(0)
                stats_df['team__name'] = stats_df['team__name'].fillna(stats_df['opponent__name'])
                stats_df['opponent__name'] = stats_df['opponent__name'].fillna(stats_df['team__name'])

                stats_df["efficiency"] = (
                                            stats_df["points"]
                                            + stats_df["total_rebounds"]
                                            + stats_df["assists"]
                                            + stats_df["steals"]
                                            + stats_df["blocks"]
                                            - (
                                                (stats_df["field_goal_attempts"] - stats_df["field_goal_made"])
                                                + (stats_df["ft_attempts"] - stats_df["ft_made"])
                                                + stats_df["turnovers"]
                                            )
                                        )
                            
                # Calculate the weighted defensive score
                stats_df['def'] = stats_df['steals'] * 2 + stats_df['blocks'] * 2 + stats_df['defensive_rebs'] * 0.5 
                ######################################################################################################
                #######################################################################################################
                #######################################################################################################
                # Team Top Players Of the game
                team_players = stats_df[stats_df['team__name'].isin(['Python'])].copy()
                team_players[['player_name__player_name', 'surname']] = team_players['player_name__player_name'].str.split(" ", n=1, expand=True)
                team_players['player_name__player_name'] = team_players['player_name__player_name'].apply(
                                                            lambda x: "".join([word[0].upper() for word in str(x).split()]))
                team_players['player_name'] = team_players['player_name__player_name']+'. '+team_players['surname']
                print("TEAM PLAYERS")
                print(team_players)
                # Opponent Top Players Of the game
                opponent_players = stats_df[~stats_df['opponent__name'].isin(["Python"])].copy()
                opponent_players[['player_name__player_name', 'surname']] = opponent_players['player_name__player_name'].str.split(" ", n=1, expand=True)
                opponent_players['player_name__player_name'] = opponent_players['player_name__player_name'].apply(
                                                            lambda x: "".join([word[0].upper() for word in str(x).split()]))
                opponent_players['player_name'] = opponent_players['player_name__player_name']+'. '+opponent_players['surname']



                # Opponent Top Point
                opp_top_points = opponent_players.groupby(
                            ["player_id","player_name__jersey_number","player_name",
                            "player_name__player_image", 'opponent__name']
                        )[['points', 'total_rebounds', 'assists', 'field_goal_attempts', 'field_goal_made',  'ft_attempts', 'ft_made',
                        'offensive_rebs', 'defensive_rebs','turnovers', 'minutes',  ]].sum().sort_values("points", ascending=False).head(1).reset_index()

                # Opponent Top Rebound
                opp_top_rebounds = opponent_players.groupby(
                            ["player_id","player_name__jersey_number","player_name",
                            "player_name__player_image", 'opponent__name']
                        )[['points', 'total_rebounds', 'assists', 'field_goal_attempts', 'field_goal_made',  'ft_attempts', 'ft_made',
                        'offensive_rebs', 'defensive_rebs','turnovers', 'minutes',  ]].sum().sort_values("total_rebounds", ascending=False).head(1).reset_index()

                # Opponent Top Assist
                opp_top_assists = opponent_players.groupby(
                            ["player_id","player_name__jersey_number","player_name",
                            "player_name__player_image", 'opponent__name']
                        )[['points', 'total_rebounds', 'assists', 'field_goal_attempts', 'field_goal_made',  'ft_attempts', 'ft_made',
                        'offensive_rebs', 'defensive_rebs','turnovers', 'minutes',  ]].sum().sort_values("assists", ascending=False).head(1).reset_index()
                            
                
                
                # Function to get the best performer of the game
                def team_best_performer(team_opp, stat):

                    performance_df = (
                        team_opp.groupby(
                            ["player_id","player_name__jersey_number","player_name",
                            "player_name__player_image","player_name__team__name", 'opponent__name']
                        )[['points', 'total_rebounds', 'assists', 'field_goal_attempts', 'field_goal_made',  'ft_attempts', 'ft_made',
                        'offensive_rebs', 'defensive_rebs','turnovers', 'minutes',  ]].sum().sort_values(stat, ascending=False).head(1).reset_index()
                    ) 

                    return performance_df

                # These lines is to call the function
                top_points = team_best_performer(team_players, 'points')
                top_rebounds = team_best_performer(team_players, 'total_rebounds')
                top_assists = team_best_performer(team_players, 'assists')

               
                ###############################################################################################
                ###############################################################################################
                ###############################################################################################

                #Accumulation.sum() Team
                total_stats_df = team_players.groupby(["player_name__player_name"])[['points', 'offensive_rebs',
                                        'defensive_rebs', 'total_rebounds',
                                        'field_goal_made', 'field_goal_attempts','ft_attempts', 'ft_made',
                                        'point_3_attempts', 'point_3_made','assists', 'blocks', 'steals',
                                        'turnovers', 'personal_fouls','efficiency', 'def']].sum().reset_index()
                total_stats_df = total_stats_df.drop(columns=['player_name__player_name']).sum()
                
                # Sum up all FG makes and attempts across players
                total_stats_df['fg_percent'] = ((total_stats_df['field_goal_made'] / total_stats_df['field_goal_attempts']) * 100)
                #total_stats_df['fg_percent'] = ((total_stats_df['field_goal_made'] / total_stats_df['field_goal_attempts']) * 100)
                total_stats_df['point_3_percent'] = ((total_stats_df['point_3_made'] / total_stats_df['point_3_attempts']) * 100)
                total_stats_df['ft_percent'] = ((total_stats_df['ft_made'] / total_stats_df['ft_attempts']) * 100)
                ###############################################################################################
                 #Accumulation.sum() Opponent
                opp_total_stats_df = opponent_players.groupby(["player_name__player_name"])[['points', 'offensive_rebs',
                                        'defensive_rebs', 'total_rebounds',
                                        'field_goal_made', 'field_goal_attempts','ft_attempts', 'ft_made',
                                        'point_3_attempts', 'point_3_made','assists', 'blocks', 'steals',
                                        'turnovers', 'personal_fouls','efficiency', 'def']].sum().reset_index()
                opp_total_stats_df = opp_total_stats_df.drop(columns=['player_name__player_name']).sum()
                
                # Sum up all FG makes and attempts across players
                opp_total_stats_df['fg_percent'] = ((opp_total_stats_df['field_goal_made'] / opp_total_stats_df['field_goal_attempts']) * 100).round(1)
                opp_total_stats_df['point_3_percent'] = ((opp_total_stats_df['point_3_made'] / opp_total_stats_df['point_3_attempts']) * 100).round(1)
                opp_total_stats_df['ft_percent'] = ((opp_total_stats_df['ft_made'] / opp_total_stats_df['ft_attempts']) * 100).round(1)
               
                ###############################################################################################
                ###############################################################################################

                # Django aggegate Function
                home_totals = stats.aggregate(
                points=Sum('points'),
                field_goal_attempts=Sum('field_goal_attempts'),
                field_goal_made=Sum('field_goal_made'),
                point_3_attempts=Sum('point_3_attempts'),
                point_3_made=Sum('point_3_made'),
             
                ft_attempts=Sum('ft_attempts'),
                ft_made=Sum('ft_made'),
                offensive_rebs=Sum('offensive_rebs'),
                defensive_rebs=Sum('defensive_rebs'),
                
                blocks=Sum('blocks'),
                assists=Sum('assists'),
                steals=Sum('steals'),
                turnovers=Sum('turnovers'),
                personal_fouls=Sum('personal_fouls'),
                #plus_minus=Sum(Cast(F('plus_minus'), IntegerField())),
                
                                                                        )
                home_totals['total_rebounds'] = home_totals['offensive_rebs'] + home_totals['defensive_rebs']
                home_totals['fg_percent'] = (home_totals['field_goal_made'] / home_totals['field_goal_attempts'] * 100) if home_totals['field_goal_attempts'] else 0
                home_totals['point_3_percent'] = (home_totals['point_3_made'] / home_totals['point_3_attempts'] * 100) if home_totals['point_3_attempts'] else 0
                home_totals['ft_percent'] = (home_totals['ft_made'] / home_totals['ft_attempts'] * 100) if home_totals['ft_attempts'] else 0

                home_totals["efficiency"] = (
                                            home_totals["points"]
                                            + home_totals["total_rebounds"]
                                            + home_totals["assists"]
                                            + home_totals["steals"]
                                            + home_totals["blocks"]
                                            - (
                                                (home_totals["field_goal_attempts"] - home_totals["field_goal_made"])
                                                + (home_totals["ft_attempts"] - home_totals["ft_made"])
                                                + home_totals["turnovers"]
                                            )
                                        )
                            
                # Calculate the weighted defensive score
                home_totals['def'] = home_totals['steals'] * 2 + home_totals['blocks'] * 2 + home_totals['defensive_rebs'] * 0.5 
                ###############################################################################################
                ###############################################################################################
                ###############################################################################################
               
                ###############################################################################################
                ########################################## STANDINGS ##########################################
                ###############################################################################################
                # Convert tournament standing to DataFrame
                standing_df = pd.DataFrame(
                    tournament_standing.values( 'competition__name', 'game_type',
                        'team__name', 'team__team_logo', 
                        'opponent__name', 'opponent__logo',
                        'w', 'l', 'home_record', 'away_record', 
                        'ppg', 'opp_ppg', 'strk', 'last_5', 
                    )
                ).sort_values('w', ascending=False).reset_index(drop=True)
                
                # Filling the NANs with values
                standing_df['team__name'] = standing_df['team__name'].fillna(standing_df['opponent__name'])
                standing_df['opponent__name'] = standing_df['opponent__name'].fillna(standing_df['team__name'])
                standing_df['team__team_logo'] = standing_df['team__team_logo'].fillna(standing_df['opponent__logo'])                             
                standing_df['opponent__logo'] = standing_df['opponent__logo'].fillna(standing_df['team__team_logo'])
                print()
               
                ###############################################################################################
                ###############################################################################################
                ###############################################################################################

              



                # Pass them to the context
                context = {
                    'game_details': game_details,
                    'players': players,
                    'team_players': team_players.to_dict('records'),
                    'opponent_players': opponent_players.to_dict('records'),
                    
                    'competition': competition,
                    'opponent': opponent, 
                    'game_date': game_date,
                    'readable_date': readable_date,
                    'quarterly_scores': quarterly_scores,
                    'other_games': other_games,
                    'int_games_in_other_games': int_games_in_other_games.to_dict('records'),
                    'standing_df': standing_df.to_dict('records'),
                    'home_totals': home_totals,

                    #Top Leaders of the game
                    'top_points_df': top_points.to_dict('records'),
                    'top_rebounds_df': top_rebounds.to_dict('records'),
                    'top_assist_df': top_assists.to_dict('records'),
                    'opp_top_points': opp_top_points.to_dict('records'),
                    'opp_top_rebounds': opp_top_rebounds.to_dict('records'),
                    'opp_top_assists': opp_top_assists.to_dict('records'),
                    
                    # Sum Totals
                    'overall_sum_df' : total_stats_df,
                    'opp_total_stats_df': opp_total_stats_df,
                    
                    'mean_merge_df': mean_merge_df


                }

                return render(request, 'game-overview.html', context)

        # Fallback if IDs are missing or invalid
        return render(request, 'game-overview.html', {
            'error': 'Invalid competition or game ID.'
        })





PlayerStatsFormSet = inlineformset_factory(Game, PlayerStatLine, form=PlayerStatLineForm, fk_name='game_schedule', extra=0,can_delete=False)

class GameUpdateView(SuperuserRequiredMixin, APIView):
    def get(self, request, competition_slug, game_slug):
        competition = get_object_or_404(Competition, slug=competition_slug)
        update_game = get_object_or_404(Game, slug=game_slug, competition=competition)

        form = GameForm(instance=update_game)
        score_formset = gameScoresFormSet(instance=update_game)

        players = Player.objects.filter(team=update_game.team)
        stats_qs = PlayerStatLine.objects.filter(game_schedule=update_game)

        if stats_qs.exists():
            # Show existing stats
            stats_formset = PlayerStatsFormSet(instance=update_game, queryset=stats_qs)
        else:
            # Build initial rows for each player
            initial_data = [{'player_name': p} for p in players]
            StatsFormSetWithExtra = inlineformset_factory(Game, PlayerStatLine, form=PlayerStatLineForm, extra=len(players), can_delete=False)
            stats_formset = StatsFormSetWithExtra(instance=update_game, queryset=PlayerStatLine.objects.none(), initial=initial_data)

        return render(request, 'game_update.html', {
            'form': form,
            'formset': score_formset,
            'stats_formset': stats_formset,
            'update_game': update_game,
            'competition_id': competition_id,
        })

    def post(self, request, competition_slug, game_slug):
        competition = get_object_or_404(Competition, slug=competition_slug)
        update_game = get_object_or_404(Game, slug=game_slug, competition=competition)

        form = GameForm(request.POST, request.FILES, instance=update_game)
        score_formset = gameScoresFormSet(request.POST, instance=update_game)
        stats_formset = PlayerStatsFormSet(request.POST, instance=update_game)

        if form.is_valid() and score_formset.is_valid() and stats_formset.is_valid():
            game = form.save()
            score_formset.save()
            stats = stats_formset.save(commit=False)
            for stat in stats:
                stat.team = game.team
                stat.opponents = game.opponent
                stat.save()
            messages.success(request, "Game and player stats updated successfully!")
            return redirect('game-list', competition_id=competition_id)


        return render(request, 'game_update.html', {
            'form': form,
            'formset': score_formset,
            'stats_formset': stats_formset,
            'update_game': update_game,
            'competition_slug': competition_slug,
        })



# Function Base View For Deleting 

@user_passes_test(is_superuser, login_url='/')
def delete_game(request, game_slug, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    game = get_object_or_404(Game, slug=game_slug, competition=competition)
    game.delete()
    # Return an  error message.
    messages.success(request, (" Game deleted successfully ):"))
    return redirect('game-list',competition_slug=competition_slug)    



####################################################################################
####################################################################################
# Class Base View Creating Opponents
class StandingCreateView(SuperuserRequiredMixin, APIView):
    def get(self, request, competition_slug):
        form = StandingForm(initial={'competition': competition_slug})
        return render(request, 'standing_registration.html', {"form": form, "competition_id": competition_slug })

    def post(self, request, competition_slug):
        form = StandingForm(request.POST, request.FILES) 
        
        if form.is_valid():
            # SUCCESS PATH
            standing = form.save()    
            messages.success(request, "Standing Added Successfully :)")
            # Redirect to GET endpoint to clear the form data
            return HttpResponseRedirect('/standing create?', competition_slug=competition_slug)
            #return redirect('view-standing', competition_id=competition_id)
        else:
            # FAILURE PATH
            print(form.errors) 
            messages.error(request, "There were errors in the form. Please correct them and try again.")
            
            # 🚀 FIX: Only return the form object, not the non-existent 'team' object
            return render(request, 'standing_registration.html', 
                                    {"form": form, "competition_id": competition_slug})



# Standing List View

class StandingListView(APIView):
   def get(self, request, slug): 
        competition = get_object_or_404(Competition, slug=slug)
        all_games = Game.objects.filter(competition=competition).prefetch_related('quarterly_scores')
        
        # Fetch all competitions for the dropdown
        all_competitions = Competition.objects.all()
        
        
        
        # Get the player's statistics
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
        if all_games.exists():
            # Convert to DataFrame
            all_games_df = pd.DataFrame(
                        all_games.values('date','time','team__name', 'indicator','opponent__name', 
                                        'team_scores', 'opponent_scores', 'team_win_loss', 'game_venue', 'game_type'))

            # 1. Fetch standings and the related game type
            tournament_standing = Standing.objects.filter(
                competition=competition,
            ).select_related('team', 'opponent',)

            # 2. Convert to DataFrame
            standing_df = pd.DataFrame(
                tournament_standing.values( 'competition__name', 'game_type',
                    'team__name', 'team__team_logo', 
                    'opponent__name', 'opponent__logo',
                    'w', 'l', 'home_record', 'away_record', 
                    'ppg', 'opp_ppg', 'strk', 'last_5', 
                )
            ).sort_values('w', ascending=False).reset_index(drop=True)

            # 3. Clean up
            standing_df['team__name'] = standing_df['team__name'].fillna(standing_df['opponent__name'])
            standing_df['opponent__name'] = standing_df['opponent__name'].fillna(standing_df['team__name'])
            standing_df['team__team_logo'] = standing_df['team__team_logo'].fillna(standing_df['opponent__logo'])                             
            standing_df['opponent__logo'] = standing_df['opponent__logo'].fillna(standing_df['team__team_logo'])
            standing_df['ppg_diff'] = standing_df['ppg'] - standing_df['opp_ppg']
            standing_df['win_pct'] = ((standing_df['w'] / (standing_df['w'] + standing_df['l'])) * 100).round(1)
            print("*"*30)
            print("Standing All Games".upper()) 
            print("*"*30)
            print(all_games_df.describe()) 
        

                                            
            
        
            
            return render(request, 'standings.html', {
                'standings': tournament_standing, 
                'competition': competition,
                'standing_df': standing_df.to_dict('records'),
                'all_games': all_games,
                'all_competitions': all_competitions,
            
            })
        else:
            return render(request, 'standings.html', {
           
            'competition': competition,
           
        
            })    

####################################################################################
####################################################################################    
@user_passes_test(is_superuser, login_url='/')
def careerRecordCreate(request, competition_id):
    if request.method == "POST":
        form = CareerRecordsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, "Record Added Successfully ):)")
            return redirect('create-records', competition_id=competition_id)
            #return HttpResponseRedirect('competition', competition_id=competition_id) 
        else:
            pass
    else: 
        form = CareerRecordsForm()

    return render(request, 'career_records_registration.html', {"form" : form, "competition_id": competition_id}) 


def careerRecordList(request, competition_id): 
    competition = get_object_or_404(Competition, pk=competition_id)
    team = competition.team
    
    # Fetch players for this team and "prefetch" their career records
    # This avoids the "N+1" problem (making a database hit for every player)
    players_with_records = team.players.all().prefetch_related('career_records')
    
    return render(request, 'career_record_list.html', {
        'players': players_with_records,
        'competition': competition, 
    })


  
@user_passes_test(is_superuser, login_url='/')
def careerRecordUpdate(request, competition_id, pk): 
    competition = get_object_or_404(Competition, pk=competition_id)
    update_record = get_object_or_404(CareerRecords, pk=pk)

    if request.method == "POST":
        form = CareerRecordsForm(request.POST, request.FILES, instance=update_record)
        
        if form.is_valid():
            form.save() 
            messages.success(request, "Record Updated Successfully! :)")
            return redirect('record-list', competition_id=competition_id)
    else: 
        # 3. Initialize the form with the existing data
        form = CareerRecordsForm(instance=update_record)

    return render(request, 'career_update.html', {
        "form": form, 
        "competition_id": competition_id,
        "record": update_record
    })


# Function Base View For Deleting 
# DELETE COMPETITION
@user_passes_test(is_superuser, login_url='/')
def delete_record(request, pk, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    delete_record = get_object_or_404(CareerRecords, pk=pk,)
    delete_record.delete()
    
    messages.success(request, f"Records for {delete_record} have been deleted.")
    return redirect('record-list',competition_id=competition_id)    

    
    
####################################################################################
####################################################################################
# News View
####################################################################################
####################################################################################
@user_passes_test(is_superuser, login_url='/')
def NewsCreate(request, competition_id):
    if request.method == "POST":
        form = TeamNewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, "News Added Successfully ):)")
            return redirect('create-news', competition_id=competition_id)
            
        else:
            pass
    else: 
        form = TeamNewsForm()

    return render(request, 'news-create.html', {"form" : form, "competition_id": competition_id}) 

  

def NewsList(request, competition_slug): 
    competition = get_object_or_404(Competition, slug=competition_slug)
    # Fetch players for this team and "prefetch" their career records
    news =  TeamNews.objects.filter(competition=competition).select_related('competition')
    #news = competition.competition_news.all()#.prefetch_related('competition_news')
    print("NEWS")
    print(news)
    return render(request, 'news-list.html', {
        'news_list': news,
        'competition': competition, 
    })


@user_passes_test(is_superuser, login_url='/')
def NewsUpdate(request, competition_id, pk): 
    competition = get_object_or_404(Competition, pk=competition_id)
    update_news = get_object_or_404(TeamNews, pk=pk)

    if request.method == "POST":
        form = TeamNewsForm(request.POST, request.FILES, instance=update_news)
        
        if form.is_valid():
            form.save() 
            messages.success(request, "News Updated Successfully! :)")
            return redirect('news-list', competition_id=competition_id)
    else: 
        # 3. Initialize the form with the existing data
        form = TeamNewsForm(instance=update_news)

    return render(request, 'news-update.html', {
        "form": form, 
        "competition_id": competition_id,
        "news_update": update_news
    })


# Function Base View For Deleting 
# DELETE COMPETITION
@user_passes_test(is_superuser, login_url='/')
def delete_news(request, pk, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    delete_news = get_object_or_404(TeamNews, pk=pk,)
    delete_news.delete()
    
    messages.success(request, f"Records for {delete_news} have been deleted.")
    return redirect('news-list',competition_id=competition_id)    

####################################################################################
####################################################################################
####################################################################################
####################################################################################
def baseNews(request, competition_id): 
    competition = get_object_or_404(Competition, pk=competition_id)
   
    return render(request, 'base.html', {
        # News Section
        'team_news': TeamNews.objects.filter(competition=competition, category='Team').order_by('-published_date')[:1],
        'hot_news': TeamNews.objects.filter(competition=competition, category='Hot').order_by('-published_date')[:1],
        'league_news': TeamNews.objects.filter(competition=competition, category='League')[:2],

        'competition': competition, 
    })


####################################################################################
####################################################################################
# News View
####################################################################################
####################################################################################
@user_passes_test(is_superuser, login_url='/')
def AwardCreate(request):
    if request.method == "POST":
        form = AwardsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, "Award Added Successfully ):)")
            return redirect('create-award')
            
        else:
            pass
    else: 
        form = AwardsForm()

    return render(request, 'award-create.html', {"form" : form,}) 

  

def AwardList(request): 
    
    awards =  Awards.objects.all().order_by('date')
    
    print("Awards")
    print(awards)
    return render(request, 'awards-list.html', {
        'awards': awards,
   
    })


@user_passes_test(is_superuser, login_url='/')
def AwardUpdate(request, pk): 
    
    update_award = get_object_or_404(Awards, pk=pk)

    if request.method == "POST":
        form = TeamNewsForm(request.POST, request.FILES, instance=update_award)
        
        if form.is_valid():
            form.save() 
            messages.success(request, "Award Updated Successfully! :)")
            return redirect('award-list', )
    else: 
        # 3. Initialize the form with the existing data
        form = TeamNewsForm(instance=update_award)

    return render(request, 'award-update.html', {
        "form": form, 
        
        "award_update": update_award
    })



####################################################################################
################################# Contact View #####################################
####################################################################################
####################################################################################
def contactCreate(request):
    if request.method == "POST":
        form = ContactForm(request.POST) 
        
        if form.is_valid():
            form.save()  # Saves the contact entry into the database
            
            # Use extra_tags to let JavaScript identify that a modal needs to be triggered
            messages.success(request, "Subscription successful! Please check your email.",
                extra_tags='open_contact_modal'
            )
            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})

#(python manage.py import_opponent_stats file.csv)

# Contact View
def contact(request):
    return render(request, 'contact-us.html', {})  

@user_passes_test(is_superuser, login_url='/')
def contactList(request):
    # This code only runs if the user is a superuser.
    contacts = Contact.objects.all().order_by('-date_submitted')
    context = {'contacts': contacts}
    return render(request, 'contactList.html', context)    


# Delete contact
@user_passes_test(is_superuser, login_url='/')
def delete_contact(request, pk): 
    contact = get_object_or_404(Contact,pk=pk,)
    contact.delete()
    return redirect('contact-list')    








####################################################################################
####################################################################################


####################################################################################
####################################################################################
def NewsletterSubscriberCreate(request):
    if request.method == "POST":
        print("--- NEWSLETTER TEST: POST SUBMISSION ATTEMPT! ---")
        print("DATA RECEIVED:", request.POST)
        
        form = NewsletterSubscriberForm(request.POST) 
        
        if form.is_valid():
            cleaned_data = form.cleaned_data
            email_address = cleaned_data.get('email')
            whatsapp_number = cleaned_data.get('phone') # Captured your WhatsApp field safely

            form.save()
            print(f"--- SUCCESS: Saved {email_address} to Database ---")

            # --- Emails execute using your live Gmail SMTP credentials ---
            subject = 'Thank you for subscribing!'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [
                email_address, 
                'solomonezrababalefty@yahoo.com', 
                'ezraoffshorecertifiedpro@gmail.com'
            ]

            context = {
                'name': email_address,
                'whatsapp': whatsapp_number
            }
            html_message = render_to_string('email/welcome-newsletter.html', context)

            plain_message = (
                f"Hello,\n\n"
                "Thank you for your Subscription!\n\n"
                "At STATSHUB, we specialize in advanced sports team analytics, web software development, "
                "and premium athletic apparel and gear.\n\n"
                "In the meantime, feel free to check out our latest dashboard updates or browse our catalog.\n\n"
                "Best regards,\n"
                "The STATSHUB Team\n"
                "info@statshub.com\n"
            )

            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=email_from,
                    recipient_list=recipient_list,
                    html_message=html_message,
                )
                logger.info("Newsletter welcome email sent successfully to %s", email_address)
                messages.success(request, "Subscription successful! Please check your email.")
                print("--- EMAIL STATUS: Sent successfully via Gmail SMTP! ---")
            except Exception as e:
                logger.error(f"Error sending newsletter email to {email_address}: {e}", exc_info=True)
                messages.error(request, "Subscription saved, but there was an issue sending your email.")
                print(f"--- EMAIL ERROR: {e} ---")

            return redirect("home")
        else:
            print("NEWSLETTER FORM ERRORS:", form.errors.as_data())
    else:
        form = NewsletterSubscriberForm()

    # CHANGE THIS: Render your actual page template (e.g., 'home.html' or 'index.html') 
    # instead of 'base.html' so it doesn't break your site layout on a GET request.
    return render(request, "home.html", {"form": form})





@user_passes_test(is_superuser)
def subscriberList(request, login_url='/'):
    # This code only runs if the user is a superuser.
    subscribers = NewsletterSubscriber.objects.all().order_by('-date_subscribed')
    context = {'subscribers': subscribers}
    return render(request, 'subscribers.html', context)    



# Delete contact
@user_passes_test(is_superuser, login_url='/')
def delete_subscriber(request, slug): 
    subscriber = get_object_or_404(NewsletterSubscriber,slug=slug,)
    subscriber.delete()
    return redirect('subscriber-list')

####################################################################################
####################################################################################
####################################################################################
####################################################################################
def search(request):
    searched = request.GET.get('s', '').strip()

    if not searched:
        messages.warning(request, "Please enter a search term.")
        return render(request, 'search-results.html', {})

    searched_players = Player.objects.filter(
        Q(player_name__icontains=searched) |
        Q(position__icontains=searched) |
        Q(jersey_number__icontains=searched) |
        Q(team__name__icontains=searched) |
        Q(opponent__name__icontains=searched)
    ).order_by('team__name', 'player_name')

    if not searched_players.exists():
        messages.info(request, f'No players found for "{searched}". Try another search.')

    return render(request, 'search-results.html', {
        'searched': searched,
        'searched_players': searched_players
    })

####################################################################################
####################################################################################
####################################################################################
####################################################################################
@user_passes_test(is_superuser, login_url='/')
def galleryCreate(request):
    if request.method == "POST":
        form = GalleryImagesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, "Image Added Successfully ):)")
            return redirect('create-image')
            
        else:
            pass
    else: 
        form = GalleryImagesForm()

    return render(request, 'gallery-create.html', {"form" : form,}) 

  

def galleryList(request): 
    
    images =  GalleryImages.objects.all()
    return render(request, 'gallery.html', {
        'images': images,
   
    })


@user_passes_test(is_superuser, login_url='/')
def update_image(request, pk): 
    
    update_image = get_object_or_404(GalleryImages, pk=pk)

    if request.method == "POST":
        form = GalleryImagesForm(request.POST, request.FILES, instance=update_image)
        
        if form.is_valid():
            form.save() 
            messages.success(request, "Image Updated Successfully! :)")
            return redirect('gallery', )
    else: 
        # 3. Initialize the form with the existing data
        form = GalleryImagesForm(instance=update_image)

    return render(request, 'gallery-update.html', {
        "form": form, 
        
        "image_update": update_image
    })

# Delete
@user_passes_test(is_superuser, login_url='/')
def delete_image(request, pk): 
    
    delete_image = get_object_or_404(GalleryImages, pk=pk)
    delete_image.delete()
    return redirect('gallery')


####################################################################################
####################################################################################
####################################################################################
####################################################################################
@user_passes_test(is_superuser, login_url='/')
def chartCreate(request):
    if request.method == "POST":
        form = ShotChartForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, "Chart Created Successfully ):)")
            return redirect('create-chart')
            
        else:
            pass
    else: 
        form = ShotChartForm()

    return render(request, 'shot-chart-create.html', {"form" : form,}) 

  



@user_passes_test(is_superuser, login_url='/')
def update_chart(request, slug): 

    update_chart = get_object_or_404(ShotCharts, slug=slug)
    player_id = update_chart.player.slug

    if request.method == "POST":
        form = ShotChartForm(request.POST, request.FILES, instance=update_chart)
        
        if form.is_valid():
            form.save() 
            messages.success(request, "Chart Updated Successfully! :)")
            return redirect('shot-charts', player_pk=player_id )
    else: 
        # 3. Initialize the form with the existing data
        form = ShotChartForm(instance=update_chart)

    return render(request, 'shot-chart-update.html', {
        "form": form, 
        
        "update_chart": update_chart
    })

# Delete
@user_passes_test(is_superuser, login_url='/')
def delete_chart(request, slug): 
    
    delete_chart = get_object_or_404(ShotCharts, slug=slug)
    delete_chart.delete()
    return redirect('charts')







