from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import mixins


from team.models import Season, Competition, Team, TeamStaff, Game, Player, PlayerStatLine, QuarterlyScores, Opponent
from .forms import SeasonForm, OpponentForm, CompetitionForm, TeamForm, TeamStaffForm, PlayerForm, GameForm, QuarterlyScoresForm
from .forms import SponsorForm
from datetime import datetime, timedelta # Module to represent the difference between two dates
from django.utils.timezone import now
from django.contrib import messages
from django .utils import timezone
from calendar import HTMLCalendar
from datetime import date


from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import  ListView, DetailView
from django.shortcuts import render, get_object_or_404
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


#To geneate pdf
#from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
#from reportlab.lib.pagesizes import letter
from django.http import FileResponse
#from reportlab.lib.units import inch
#from reportlab.pdfgen import canvas
#from reportlab.lib import colors
import io



# Create your views here.

@api_view(['GET'])
def getData(request):
    return render(request, 'home.html', {})

####################################################################################
####################################################################################
# Registration forms for testing purposes
####################################################################################
####################################################################################    

#PlayerFormSet = inlineformset_factory(Team, Player, form=PlayerForm, extra=1, can_delete=False, max_num=15)



# View to handle all registrations forms
def registration_page(request):
    return render(request, 'registrations.html', {})


####################################################################################
####################################################################################
####################################################################################
####################################################################################

# Function to convert date of birth of players to number
def calculate_age(birthdate):
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

####################################################################################
####################################################################################
# Season Create View
####################################################################################
####################################################################################
# Using the generic view of django
class SeasonCreateView(CreateView):
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
class SeasonDetailView(APIView):
    def get(self, request, pk):
        season_details = get_object_or_404(Season, pk=pk)
        
        context = {
                'season_details': {
                'pk': season_details.pk,  # Include the primary key
                'year': season_details.year,
                'name': season_details.name,
                'is_current_season': season_details.is_current_season,
                },
            }

        return render(request, 'season_details.html', context)


# Class Base View For Update
class SeasonUpdateView(APIView):
    # Handle GET and POST requests to UPDATE team details
    def get(self, request, pk):
        season_update = get_object_or_404(Season, pk=pk)
        form = SeasonForm(request.POST or None, instance=season_update)
        return render(request, 'season_update.html', {'form': form, 'season_updates': season_update})

    def post(self, request, pk):
        season_updates = get_object_or_404(Season, pk=pk)
        form = SeasonForm(request.POST, request.FILES, instance=season_updates)
        

        if form.is_valid():
            form.save()
            messages.success(request, (" Season Updated Sucessfully ):")) # Return a valid update message.
            return redirect('season-id', pk=pk)
        return render(request, 'season_update.html', {'form': form, 'season_updates': season_updates})    


# Function Base View For Deleting 
# DELETE SEASON
def delete_season(request, pk):
    season = get_object_or_404(Season, pk=pk)
    season.delete()
    # Return an 'invalid login' error message.
    messages.success(request, (" Season deleted successfully ):"))
    return redirect('season-competition-list')        


####################################################################################
####################################################################################
# Competition
####################################################################################
####################################################################################
# Using the generic view of django
# Class Base View Creating Competition
class CompetitionCreateView(APIView):
    def get(self, request):
        form = CompetitionForm()
        
        submitted = 'submitted' in request.GET
        return render(request, 'competition_registration.html', {"form": form,  'submitted': submitted})

    def post(self, request):
        form = CompetitionForm(request.POST, request.FILES)
        if form.is_valid():
            competition = form.save()
            messages.success(request, "Competition Added Successfully :)")
            return HttpResponseRedirect('/competition_create?submitted=True')
        else:
            messages.error(request, "There were errors in the form. Please correct them and try again.")
        return render(request, 'competition_registration.html', {"form": form, "competition": competition, 'submitted': False})



#Season List View
class CompetitionListView(APIView):
    def get(self, request):
        pass
   


# Class Base View For Team Details
class CompetitionDetailView(APIView):
    def get(self, request, pk):
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
class CompetitionUpdateView(APIView):
    # Handle GET and POST requests to UPDATE team details
    def get(self, request, pk):
        competition_update = get_object_or_404(Competition, pk=pk)
        form = CompetitionForm(request.POST or None, instance=competition_update)
        return render(request, 'competition_update.html', {'form': form, 'competition_updates': competition_update})

    def post(self, request, pk):
        competition_updates = get_object_or_404(Competition, pk=pk)
        form = CompetitionForm(request.POST, request.FILES, instance=competition_updates)

        if form.is_valid():
            form.save()

            # Return a valid update message.
            messages.success(request, (" Competition Updated Sucessfully ):"))
            return redirect('season-competition-list',)
        return render(request, 'competition_update.html', {'form': form, 'competition_updates': competition_updates})    


# Function Base View For Deleting 
# DELETE COMPETITION
class CompetitionDeleteView(APIView):
    def delete(self, request, pk):
        competition = get_object_or_404(Competition, pk=pk)
        competition.delete()
        return redirect('season-competition-list') 
          



####################################################################################
####################################################################################
# Team View
####################################################################################
####################################################################################

# Class Base View Creating Team
class TeamCreateView(APIView):
    def get(self, request):
        form = TeamForm()
        return render(request, 'team_registration.html', {"form": form, })

    def post(self, request):
        form = TeamForm(request.POST, request.FILES)   
        if form.is_valid():
            team = form.save()     
            messages.success(request, "Team Added Successfully :)")
            return HttpResponseRedirect('/team_create?')
        else:
            messages.error(request, "There were errors in the form. Please correct them and try again.")
            
        return render(request, 'team_registration.html', {"form": form, "team": team, })


#  Class Base View For Opponent List
class TeamListView(APIView):
    def get(self, request, competition_id, ): 
        
        competition = get_object_or_404(Competition, pk=competition_id)
       
        #games = get_object_or_404(Game, pk=game_id, competition=competition).distinct().order_by('date')
        team = competition.team
        
        
        return render(request, 'team_list.html', {'team':team})        


# Make sure 'calculate_age' is imported or defined
class TeamDetailView(APIView):
    # Setting competition_id and team_id to None allows django to view same view in to different cases
    # Ahome page without a parameter and a detailed team view ith specific competition and the team in the competition.
    def get(self, request, competition_id=None, team_id=None ): 
        if competition_id and team_id and competition.is_current_competition:
            
            try:
                competition = get_object_or_404(Competition, pk=competition_id)
                team = get_object_or_404(Team, pk=team_id, competition=competition)
            except Http404:
                return render(request, 'team_detail.html', {'error':'Competition and Team not found.'})

        else:
            competition = Competition.objects.filter(is_current_competition=True).first() #latest('start_date')
            team = competition.team_competition.all() # Fixing if incase theres no competition selected.
           

       
        #games = get_object_or_404(Game, pk=game_id, competition=competition).distinct().order_by('date')
        team = competition.team
        team_details = team
        opponents = competition.opponents.all().order_by('name')
        
    
        # Filter game schedules for the specific team and competition
        games= competition.competition.all().order_by('date')   
        #quarterly_scores = QuarterlyScores.objects.filter(competition=quarterly_scores) 

        # game = get_object_or_404(GameSchedule, pk=pk)
        # = get_object_or_404(QuarterlyScores, competition=quarterly_scores)
        #quarterly_scores = QuarterlyScores.objects.filter(games=game)

        
        
        # 2. FILTER the players by the team AND the competition
        # The Players model has a ForeignKey to Competition named 'for_this_competition'
        players = team_details.players.all()
        staff = TeamStaff.objects.filter(team=team_details,  )
        
        # 3. Calculate age for the FILTERED players
        for player in players:
            player.age = calculate_age(player.date_of_birth) 

        # 4. Prepare Context
        context = {
           
         
           
            'team_detail': {
                'pk': team_details.pk, 
                'team_logo': team_details.team_logo.url,
                'name': team_details.name,
                # ... other team details ...
                
            },
            'competition': competition,
            'players': players, # The filtered list of players
            'opponents': opponents,
            'staff': staff,
        
            
            # If you want to use the game_id later:
            'games': games,
            #'quarterly_scores':quarter_scores, 
            'team': team,
        }
            
        return render(request, 'team_details.html', context)

  



# Class Base View For Team Details
"""class TeamDetailView(APIView):

    def get(self, request, pk):
        team_details = get_object_or_404(Team, pk=pk)
        #competition = get_object_or_404(Competition, pk=competition_id)
        #games = get_object_or_404(Game, pk=game_id, competition=competition)
        #team_images = GalleryImages.objects.filter(team_pictures=team_details).first()
        players = team_details.players.all()  # Using the foreign key Team related_name 'players'

        #pd.set_option("display.max_columns", None)
        #pd.set_option("display.max_rows", None)

        for player in players:
            player.age = calculate_age(player.date_of_birth)  # Calculate the player's age


        context = {
            'team_detail': {
                'pk': team_details.pk,  # Include the primary key
                'team_logo': team_details.team_logo.url,
                'name': team_details.name,
                'home_jersey_color': team_details.home_jersey_color,
                'away_jersey_color': team_details.away_jersey_color,
                #'games_won': standings.games_won if standings else 0,
                #'games_lost': standings.games_lost if standings else 0,
                'facebook_link' : team_details.facebook_link,
                'twitter_link' : team_details.twitter_link,
                'instagram_link' : team_details.instagram_link,
                'youtube_link' : team_details.youtube_link,
                'tiktok_link' : team_details.tiktok_link,
                'for_this_competition': team_details.for_this_competition
               
                # other team details fields as required
            },

            #'gallery_images': team_images.image.url if team_images else None,  # Pass the URL or None
            #'competition': competition,
            #'team_images': team_images,
            #'games': games_with_details,  # Use enriched game data
            'players': players,
            #'points_scored_per_game': points_scored_per_game,
            #'points_conceded_per_game': points_conceded_per_game,
            #'total_points_scored': total_points_scored,
            #'total_points_conceded': total_points_conceded,
            #'games_played': games_played,    
        }
            
        
        return render(request, 'team_details.html', context)"""


# FUNCTION VIEW TEAM ROSTER
def team_roster(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    team = competition.team
    team_details = team
    players = team_details.players.all()  # Using the foreign key Team related_name 'players'
    staff = TeamStaff.objects.filter(team=team_details)
    return render(request, 'team_roster.html', {'competition':competition,'team_details': team_details, 'players': players,  'staffs': staff})



# Class Base View For Update
class TeamUpdateView(APIView):
    # Handle GET and POST requests to UPDATE team details
    def get(self, request, competition_id, ): 
        competition = get_object_or_404(Competition, pk=competition_id)
        team = competition.team
        update_team = team
        form = TeamForm(request.POST or None, instance=update_team)
        return render(request, 'team_update.html', {'form': form, 'update_team': update_team})

    def post(self, request, competition_id,):
        competition = get_object_or_404(Competition, pk=competition_id)
        update_team = competition.team
        form = TeamForm(request.POST, request.FILES, instance=update_team)

        if form.is_valid():
            form.save()
            # Return a valid update message.
            messages.success(request, (" Team Updated Sucessfully ):"))
            return redirect('team-id', competition_id=competition_id)#Error Here.......
        return render(request, 'team_update.html', {'form': form, 'update_team': update_team})    

     
####################################################################################
####################################################################################
# Players View
####################################################################################
####################################################################################


# Class Base View Creating Opponents
class PlayerCreateView(APIView):
    def get(self, request):
        form = PlayerForm()
        
        submitted = 'submitted' in request.GET
        return render(request, 'players_registration.html', {"form": form,  'submitted': submitted})

    def post(self, request):
        form = PlayerForm(request.POST, request.FILES)
        
        if form.is_valid():
            player = form.save()
            
            messages.success(request, "Player Added Successfully :)")
            return HttpResponseRedirect('/player_create?submitted=True')
        else:
            messages.error(request, "There were errors in the form. Please correct them and try again.")
            print("Player Form Errors:", form.errors)  # Debug: Print team form errors
            
        return render(request, 'players_registration.html', {"form": form, "player": player, 'submitted': False})


#  Class Base View For Opponent List
class PlayerListView(APIView):
    def get(self, request, pk):
        teams_details = get_object_or_404(Team, pk=pk)
        players = teams_details.players.all() 
        return render(request, 'team_roster.html', {'players':players})        

"""
# In views.py (PlayerDetailView - Correction)

class PlayerDetailView(APIView): 
   
    def get(self, request, pk, competition_id=None): 
        
       
        player_details = get_object_or_404(Player, pk=pk)

        player_details.age = calculate_age(player_details.date_of_birth)
        
        
        # 4. Filter the player's stats by the player name
        player_stats_query = PlayerStats.objects.filter(player_name=player_details).values()
        
        # Check if any stats exist before proceeding
        if player_stats_query.exists():
            # Create a DataFrame (assuming 'pd' is imported for pandas)
            player_stats = pd.DataFrame(list(player_stats_query))

            # Calculate Mean Stats
            mean_points = round(player_stats['points'].mean(), 1)
            mean_rebounds = round(player_stats['total_rebounds'].mean(), 1) # Adjust field name if necessary
            mean_assists = round(player_stats['assists'].mean(), 1)

            # Get Last 5 Games
            last_5_games = player_stats.tail(5)
            last_5_games = last_5_games.to_dict(orient='records')

        else:
            # Provide default values if no stats are found to prevent errors
            mean_points, mean_rebounds, mean_assists = 0.0, 0.0, 0.0
            last_5_games = []

        # 5. Build the Context Dictionary
        context = {
            'player_details': player_details,
            'mean_points': mean_points,
            'mean_rebounds': mean_rebounds,
            'mean_assists': mean_assists,
            'last_5_games': last_5_games,
            # Add other details like height, weight, etc. here if they are not 
            # already attributes of player_details (e.g., player_details.height)
        }

        # 6. Render the template
        return render(request, 'players_detail.html', context)
"""


class PlayerDetailView(APIView):
    def get(self, request, pk, competition_id=None):
        if competition_id:
            competition = get_object_or_404(Competition, pk=competition_id)
            if competition.is_current_competition:
                team= competition.team
                player_details = get_object_or_404(Player, pk=pk, team=team)
                player_details.age = calculate_age(player_details.date_of_birth)  # Calculate the player's age
            
                #player_details = get_object_or_404(Player, pk=pk)
                #player_details.age = calculate_age(player_details.date_of_birth)  # Calculate the player's age
                

                # Get the player's statistics
                #player_stats = PlayersStats.objects.filter(player_name=player_details)

            
                # Create a DataFrame from player_stats with points and total_rebounds
                """player_stats = pd.DataFrame(
                    player_stats.values('game_schedule__date','game_schedule__competition_game_schedule__name','opponent__team_name','minutes','points','field_goal_attempts',
                                        'field_goal_made','fg_percent', 'point_3_made','point_3_attempts','point_3_percent',
                                        'ft_made','ft_attempts','ft_percent','offensive_rebs','defensive_rebs','total_rebounds',
                                        'assists', 'steals','blocks',  'turnovers', 'personal_fouls','plus_minus', 'efficiency','win_lose', 'home_scores', 'away_scores' ))

                # Fetch the player_stats query
                player_stats_query = PlayersStats.objects.values(
                    'game_schedule__date',
                    'game_schedule__competition_game_schedule__name',  # Fetch full competition name
                    'opponent__team_name',
                    'points',
                    'minutes',
                    'total_rebounds',
                    'assists',
                    'field_goal_made',
                    'field_goal_attempts',
                    'fg_percent',
                    'point_3_made',
                    'point_3_attempts',
                    'point_3_percent',
                    'ft_made',
                    'ft_attempts',
                    'ft_percent',
                    'offensive_rebs',
                    'defensive_rebs',
                    'blocks',
                    'steals',
                    'turnovers',
                    'personal_fouls',
                    'plus_minus',
                    'efficiency'
                )
                """

                # Abbreviate competition name
                def abbreviate_name(name):
                    if "Basketball Africa League" in name:
                        return name.replace("Basketball Africa League 2025", "BAL 2025")
                    else:
                        print(f"Competition name does not exist :(")
                    return name

                #player_stats['game_schedule__competition_game_schedule__name'] = player_stats[
                #    'game_schedule__competition_game_schedule__name'
                #].apply(abbreviate_name)


                # Calculate averages
                """mean_points = player_stats['points'].mean()
                mean_rebounds = player_stats['total_rebounds'].mean()
                mean_assists = player_stats['assists'].mean()

                # Convert them to a rounded value or float
                mean_points = round(mean_points, 1)
                mean_rebounds = round(mean_rebounds, 1)
                mean_assists = round(mean_assists, 1)

                # Last 5 games
                last_5_games = player_stats.tail(5)
                last_5_games = last_5_games.to_dict(orient='records')"""



                # Pass them to the context
                context = {
                    'player_details': player_details,
                    #'last_5_games': last_5_games,

                    #'mean_points': mean_points,
                    #'mean_rebounds': mean_rebounds,
                    #'mean_assists': mean_assists,

                
                }


                return render(request, 'players_detail.html', context)

        # Fallback if IDs are missing or invalid
        return render(request, 'players_details.html', {
            'error': 'Invalid competition or team ID.'
        })

# UPDATE PLAYER
class PlayerUpdateView(APIView):
    def get(self, request, pk, competition_id,):
        competition = get_object_or_404(Competition, pk=competition_id)
        player = get_object_or_404(Player, pk=pk, team=competition.team)
        form = PlayerForm(request.POST or None, instance=player)
        return render(request, 'players_update.html', {'form': form, 'player': player, 'competition': competition})

    def post(self, request, pk, competition_id):
        competition = get_object_or_404(Competition, pk=competition_id)
        update_player = get_object_or_404(Player, pk=pk, team=competition.team)
        form = PlayerForm(request.POST, request.FILES, instance=update_player)
        if form.is_valid():
            form.save()
            messages.success(request, "Player Updated Successfully :)")
            return redirect('players-id', pk=pk, competition_id=competition.id)

        return render(request, 'players_update.html', {'form': form, 'update_players': update_player, 'competition': competition})




# Player Delete Function
class PlayerDeleteView(APIView):
    def get(self, request, pk):
        player = get_object_or_404(Player, pk=pk)
        team_id = player.team.pk # Fetch the particular player  of the team.
        player.delete()
        messages.success(request, "Player deleted successfully.")
        return redirect('team-roster', pk=team_id)

####################################################################################
####################################################################################
# Team Staff
####################################################################################
####################################################################################
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
        staff_details = get_object_or_404(TeamStaff, pk=pk)
       

        context = { }
        return render(request, 'staff_details.html', context)



# UPDATE STAFF
class StaffUpdateView(View):
    def get(self, request, competition_id, staff_id):
        competition = get_object_or_404(Competition, pk=competition_id)
        staff = get_object_or_404(TeamStaff,pk=staff_id, team=competition.team)
        form = TeamStaffForm(request.POST or None, instance=staff)
        return render(request, 'staff_update.html', {'form': form, 'staff': staff, 'staff': staff, 'competition': competition})

    def post(self, request, competition_id, staff_id):
        competition = get_object_or_404(Competition, pk=competition_id)
        staff = get_object_or_404(TeamStaff,pk=staff_id, team=competition.team)

        form = TeamStaffForm(request.POST or None, instance=staff)
        if form.is_valid():
            form.save()

            return redirect('team-roster', competition_id=competition.id )    


        return render(request, 'staff_update.html', {'form': form, 'staff': staff, 'staff': staff, 'competition': competition})





# Player Delete Function
class StaffDeleteView(APIView):
    def get(self, request, pk): 
        staff = get_object_or_404(TeamStaff, pk=pk)
        team_id = staff.team.pk # Fetch the particular player  of the team.
        staff.delete()
        messages.success(request, "Staff deleted successfully.")
        return redirect('team-roster', pk=team_id)        
####################################################################################
####################################################################################
# Opponent View
####################################################################################
####################################################################################

# Class Base View Creating Opponents
class OpponentCreateView(APIView):
    def get(self, request):
        form = OpponentForm()
        
        submitted = 'submitted' in request.GET
        return render(request, 'opponents_registration.html', {"form": form,  'submitted': submitted})

    def post(self, request):
        form = OpponentForm(request.POST, request.FILES)
        
        if form.is_valid():
            team = form.save()
            
            messages.success(request, "Opponents Added Successfully :)")
            return HttpResponseRedirect('/opponent_create?submitted=True')
        else:
            messages.error(request, "There were errors in the form. Please correct them and try again.")
            print("Team Form Errors:", form.errors)  # Debug: Print team form errors
            
        return render(request, 'opponents_registration.html', {"form": form, "team": team, 'submitted': False})


#  Class Base View For Opponent List
class OpponentListView(APIView):
    def get(self, request):
        opponents = Opponent.objects.all()
       
        #return Response(serializer.data) 
        return render(request, 'opponents_list.html', {'opponents':opponents})        


# Class Base View For Team Details
class OpponentDetailView(APIView):
    def get(self, request, pk):
        opponent_details = get_object_or_404(Opponent, pk=pk)

        context = {
            'team_details': {
                'pk': opponent_details.pk,  # Include the primary key
                'logo': opponent_details.logo.url,
                'name': opponent_details.name,
                'year': opponent_details.year,
                'competition': opponent_details.competitions 
            },
        }
        return render(request, 'opponents_details.html', context)


# Class Base View For Update
class OpponentUpdateView(APIView):
    # Handle GET and POST requests to UPDATE team details
    def get(self, request, pk):
        update_opponents = get_object_or_404(Opponent, pk=pk)
        form = OpponentForm(request.POST or None, instance=update_opponents)
        return render(request, 'update_opponent.html', {'form': form, 'update_opponents': update_opponents})

    def post(self, request, pk):
        update_opponents = get_object_or_404(Opponent, pk=pk)
        form = OpponentForm(request.POST, request.FILES, instance=update_opponents)

        if form.is_valid():
            form.save()
            # Return a valid update message.
            messages.success(request, (" Team Updated Sucessfully ):"))
            return redirect('opponent-id', pk=pk)
        return render(request, 'update_opponent.html', {'form': form, 'update_opponents': update_opponents})    


# Function Base View For Deleting 
# DELETE COMPETITION
def delete_opponent(request, pk):
    opponent = get_object_or_404(Opponent, pk=pk)
    opponent.delete()
    # Return an 'invalid login' error message.
    messages.success(request, (" Team deleted successfully ):"))
    return redirect('opponent-list')        



####################################################################################
####################################################################################
# Game View
####################################################################################
####################################################################################

# Class Base View Creating Opponents
class OpponentCreateView(APIView):
    def get(self, request):
        form = OpponentForm()
        
        submitted = 'submitted' in request.GET
        return render(request, 'opponents_registration.html', {"form": form,  'submitted': submitted})

# Class Base View Creating Team
class GameCreateView(APIView):
    def get(self, request):
        form = GameForm()
        return render(request, 'game_registration.html', {"form": form,})

    def post(self, request):
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "New Game Added Successfully :)")
            return HttpResponseRedirect('/game_create?')
        else:
            messages.error(request, "There were errors in the form. Please correct them and try again.")
            print("Game Form Errors:", form.errors)  # Debug: Print team form errors
            
        return render(request, 'game_registration.html', {"form": form, "game": game, })        


#  Class Base View For Opponent List
class GameListView(APIView):
   def get(self, request, competition_id, ): 
        
        competition = get_object_or_404(Competition, pk=competition_id)
        team = competition.team
        team_details = team
        games= competition.competition.all()  # Using the foreign key Team related_name 'players'
        return render(request, 'game_list.html', {'games':games, 'competition':competition})       



# Class Base View For Update
class GameUpdateView(APIView):
    def get(self, request, competition_id, pk): 
        competition = get_object_or_404(Competition, pk=competition_id)
        team = competition.team
        update_game = get_object_or_404(Game,pk=pk, team=competition.team)
        form = GameForm(request.POST or None, instance=update_game)
        return render(request, 'game_update.html', {'form': form, 'update_game': update_game})

    def post(self, request, competition_id, pk):
        competition = get_object_or_404(Competition, pk=competition_id)
        update_game = get_object_or_404(Game, pk=pk, team=competition.team)
        form = GameForm(request.POST or None, instance=update_game)
        if form.is_valid():
            form.save()
            messages.success(request, (" Game Updated Sucessfully ):"))
            return redirect('game-list', competition_id=competition_id)
        return render(request, 'game_update.html', {'form': form, 'update_game': update_game})





####################################################################################
####################################################################################
# Quarterly Scores
####################################################################################
####################################################################################

# Class Base View Creating Team
class QuarterlyScoresCreateView(APIView):
    def get(self, request):
        form = QuarterlyScoresForm()
        return render(request, 'quarter_scores_registration.html', {"form": form,})

    def post(self, request):
        form = QuarterlyScoresForm(request.POST, request.FILES)
        if form.is_valid():
            scores = form.save()
            messages.success(request, "New Scores Added Successfully :)")
            return HttpResponseRedirect('/scores_create?')
        else:
            messages.error(request, "There were errors in the form. Please correct them and try again.")
            print("Scores Form Errors:", form.errors)  # Debug: Print team form errors
            
        return render(request, 'quarter_scores_registration.html', {"form": form, "scores": scores, })  


#  Class Base View For Opponent List
class QuarterlyScoresListView(APIView):
   def get(self, request, competition_id, ): 

        competition = get_object_or_404(Competition, pk=competition_id)
        game = competition.competition.all()
        quarterly_scores = competition.quarterly_scores.all()
        #quarterly_scores = QuarterlyScores.objects.filter(game=quarterly_scores)
        return render(request, 'quarter_scores_list.html', {'quarterly_scores':quarterly_scores, 'games':game, 'competition':competition}) 



class QuarterlyScoresUpdateView(APIView):
    def get(self, request, competition_id, pk): 
        competition = get_object_or_404(Competition, pk=competition_id)
        team = competition.team
        update_scores = get_object_or_404(QuarterlyScores,pk=pk,)
        form = QuarterlyScoresForm(request.POST or None, instance=update_scores)
        return render(request, 'quarter_scores_update.html', {'form': form, 'update_scores': update_scores})

    def post(self, request, competition_id, pk):
        competition = get_object_or_404(Competition, pk=competition_id)
        team = competition.team
        update_scores = get_object_or_404(QuarterlyScores,pk=pk,)
        form = QuarterlyScoresForm(request.POST or None, instance=update_scores)
        if form.is_valid():
            form.save()
            messages.success(request, (" Scores Updated Sucessfully ):"))
            return redirect('scores-list', competition_id=competition_id)
        return render(request, 'quarter_scores_update.html', {'form': form, 'update_scores': update_scores})  




####################################################################################
####################################################################################
# Sponsor
####################################################################################
####################################################################################

# Create Sponsor
def create_sponsor(request):
    if request.method == "POST":
        form = SponsorForm(request.POST, request.FILES)
        if form.is_valid():
            sponsor = form.save()
            messages.success(request, "New Scores Added Successfully :)")
            return HttpResponseRedirect('/list sponsor')
    else:
        form = SponsorForm()
        #messages.error(request, "There were errors in the form. Please correct them and try again.")

    return render(request, 'sponsor_create.html', {"form" : form, 'sponsor': sponsor})


#List Sponsor 
def list_sponsors(request):
    sponsor_list = Sponsor.objects.all().order_by('name')
    return render(request, 'sponsors_list.html',{"sponsor_lists": sponsor_list})

# Update Sponsor
def update_sponsor(request, pk): 
        update_sponsor = get_object_or_404(Sponsor,pk=pk,)
        form = SponsorForm(request.POST or None, instance=update_sponsor)
        if form.is_valid():
            form.save()
            messages.success(request, (" Scores Updated Sucessfully ):"))
            return redirect('sponsor-list', pk=pk)
        return render(request, 'sponsor_update.html', {'form': form, 'update_sponsors': update_sponsor})

# Delete Sponsor
def delete_sponsor(request, pk): 
        #sponsor = Sponsor.objects.get(pk=event_id)
        sponsor = get_object_or_404(Sponsor,pk=pk,)
        sponsor.delete()
        return redirect('sponsor-list')   ."""     

