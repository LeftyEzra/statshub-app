from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from team.models import Competition, Team, TeamStaff, Game, Player, PlayerStatLine, QuarterlyScores, Opponent
from team.serializers import CompetitionSerializer, TeamSerializer, StaffSerializer, GameSerializer, PlayerSerializer, PlayerStatsLineSerializer
from team.serializers import QuarterlyScoreLineSerializer, OpponentSerializer, GameSerializer, TeamDetailSerializer
from .forms import OpponentForm
from datetime import datetime, timedelta # Module to represent the fifference between two dates
from django.utils.timezone import now
from django .utils import timezone
from calendar import HTMLCalendar
from datetime import date
from django.contrib import messages
from django.db.models import Q

@api_view(['GET'])
def getData(request):
    time = datetime.now()#.strftime("%H:%M")
    context = {'name' : "Python Language", 
               'Purpose': 'RestFrame Work Tutorial',
               'time': 'time'}
    return Response(context)
    #return render(request, 'home.html', context)

# Create your views here.


# Function to convert date of birth of players to number
def calculate_age(birthdate):
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

####################################################################################
####################################################################################
# Competition View
####################################################################################
####################################################################################

# Competition Create
class CompetitionCreateView(APIView):
    def post(self, request):
        serializer = CompetitionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

# Competition List
class CompetitionListView(APIView):
    def get(self, request):
        competitions = Competition.objects.all()
        serializer = CompetitionSerializer(competitions, many=True)
        return Response(serializer.data)
             

# Competition Details
class CompetitionDetailView(APIView):
    def get(self, request, pk):
        competition = get_object_or_404(Competition, pk=pk)
        serializer = CompetitionSerializer(competition)
        return Response(serializer.data)
        


# Update Competition
class CompetitionUpdateView(APIView):
    def put(self, request, pk):
        competition = get_object_or_404(Competition, pk=pk)
        serializer = CompetitionSerializer(competition, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
          
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
              


# # Competition Delete
class CompetitionDeleteView(APIView):
    def delete(self, request, pk):
        competition = get_object_or_404(Competition, pk=pk)
        competition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





####################################################################################
####################################################################################
# Team View
####################################################################################
####################################################################################

# Team Create
class TeamCreateView(APIView):
    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

# Team List
class TeamListView(APIView):
    def get(self, request):
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data) 

     

# Team Details
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
        games = Game.objects.filter(
            Q(team=team_details) & 
            Q(competition=competition)  ).distinct().order_by('date')
        
        
        # 2. FILTER the players by the team AND the competition
        # The Players model has a ForeignKey to Competition named 'for_this_competition'
        players = team_details.players.all()
        staff = TeamStaff.objects.filter(team=team_details,  )
        
        # 3. Calculate age for the FILTERED players
        for player in players:
            player.age = calculate_age(player.date_of_birth)


        # Aggregate Data for Serialization
        # Prepare a dictionary with ALL the data you want to return
        data_to_serialize = {
            'team': team_details,
            'competition': competition,
            'staff': staff,
            'players': players,
            'opponents': opponents,
        }
    
        serializer = TeamDetailSerializer(data_to_serialize)
        return Response(serializer.data, status=status.HTTP_200_OK)
   

# Update Team
class TeamUpdateView(APIView):
    def put(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        serializer = TeamSerializer(team, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
           
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                

# Team Delete
class TeamDeleteView(APIView):
    def delete(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


 
####################################################################################
####################################################################################
# Staff View
####################################################################################
####################################################################################
# Staff Create View
class StaffCreateView(APIView):
    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
     

#Staff Detail View
class StaffDetailView(APIView):
    def get(self, request, pk):
        staff = get_object_or_404(Staff, pk=pk)
        serializer = StaffSerializer(player)
        return Response(serializer.data)


# Staff Update View
class StaffUpdateView(APIView):
    def put(self, request, pk):
        staff = get_object_or_404(Staff, pk=pk)
        serializer = StaffSerializer(staff_create, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)         


#Staff Delete View
class StaffDeleteView(APIView):
    def delete(self, request, pk):
        staff = get_object_or_404(staff, pk=pk)
        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

###################################################################################
####################################################################################
# Team View
####################################################################################
####################################################################################
# Class Base View For Opponent Create
class OpponentCreateView(APIView):
    def post(self, request):
        serializer = OpponentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  Class Base View For Opponent List
class OpponentListView(APIView):
    def get(self, request):
        opponents = Opponent.objects.all()
        serializer = OpponentSerializer(opponents, many=True)
        return Response(serializer.data) 
             

# Team Details
class OpponentDetailView(APIView):
    def get(self, request, pk):
        opponent = get_object_or_404(Opponent, pk=pk)
        serializer = OpponentSerializer(opponent)
        return Response(serializer.data)


# Update Team
class OpponentUpdateView(APIView):
    def put(self, request, pk):
        opponent = get_object_or_404(Opponent, pk=pk)
        serializer = OpponentSerializer(opponent, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)       


# Team Delete
class OpponentDeleteView(APIView):
    def delete(self, request, pk):
        opponent = get_object_or_404(Opponent, pk=pk)
        opponent.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


####################################################################################
####################################################################################
# Games View
####################################################################################
####################################################################################
#View Game Create
class GameCreateView(APIView):
    def post(self, request):
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

#View Game List
class GameListView(APIView):
    def get(self, request):
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data) 
       
   
#View Game Details
class GameDetailView(APIView):
    def get(self, request, pk):
        game = get_object_or_404(Game, pk=pk)
        serializer = GameSerializer(game)
        return Response(serializer.data)
       

# Update Game
class GameUpdateView(APIView):
    def put(self, request, competition_id, pk):
        competition = get_object_or_404(Competition, pk=competition_id)
        update_game = get_object_or_404(Game, pk=pk, team=competition.team)
        serializer = GameSerializer(update_game, data=request.data)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, (" Game Updated Sucessfully ):"))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)             


#View Game Delete
class GameDeleteView(APIView):
    def delete(self, request, pk):
        game = get_object_or_404(Game, pk=pk)
        game.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



####################################################################################
####################################################################################
# Quaterly Score View
####################################################################################
####################################################################################

# Create Scores
class QuarterlyScoresCreateView(APIView):
    def post(self, request):
        serializer = QuarterlyScoreLineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

# Display Scores
class QuarterlyScoresListView(APIView):
    def get(self, request):
        scores = QuarterlyScores.objects.all()
        serializer = QuarterlyScoreLineSerializer(scores, many=True)
        return Response(serializer.data) 
           
#View Scores Details
class QuarterlyScoresDetailView(APIView):
    def get(self, request, pk):
        scores = get_object_or_404(QuarterlyScores, pk=pk)
        serializer = QuarterlyScoreLineSerializer(scores)
        return Response(serializer.data)


# Update Scores
class QuarterlyScoresUpdateView(APIView):
    def put(self, request, pk):
        scores = get_object_or_404(Game, pk=pk)
        serializer = QuarterlyScoreLineSerializer(scores, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)             


#View Scores Delete
class QuarterlyScoresDeleteView(APIView):
    def delete(self, request, pk):
        scores = get_object_or_404(QuarterlyScores, pk=pk)
        scores.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)        

####################################################################################
####################################################################################
# Players View
####################################################################################
####################################################################################
# Players Create View
class PlayerCreateView(APIView):
    def post(self, request):
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

# Players List View
class PlayerListView(APIView):
    def get(self, request):
        players = Player.objects.all()
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)        

#Players Detail View
class PlayerDetailView(APIView):
    def get(self, request, pk):
        player = get_object_or_404(Player, pk=pk)
        serializer = GameSerializer(player)
        return Response(serializer.data)


# Players Update View
class PlayerUpdateView(APIView):
    def put(self, request, pk):
        player = get_object_or_404(Player, pk=pk)
        serializer = PlayerSerializer(player, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)             


#Players Delete View
class PlayerDeleteView(APIView):
    def delete(self, request, pk):
        player = get_object_or_404(player, pk=pk)
        player.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





####################################################################################
####################################################################################
# Players Stats Line
####################################################################################
####################################################################################

# Players Stats Line Create
class PlayerStatsLineCreateView(APIView):
    def post(self, request):
        serializer = PlayerStatsLineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

# Players Stats Line List
class PlayerStatsLineListView(APIView):
    def get(self, request):
        playerstats = PlayerStatLine.objects.all()
        serializer = PlayerStatsLineSerializer(playerstats, many=True)
        return Response(serializer.data)        

# Players Stats Line Details
class PlayerStatsLineDetailView(APIView):
    def get(self, request, pk):
        playerstats = get_object_or_404(PlayerStatLine, pk=pk)
        serializer = PlayerStatsLineSerializer(playerstats)
        return Response(serializer.data)


# Players Stats Line Update
class PlayerStatsLineUpdateView(APIView):
    def put(self, request, pk):
        playerstats = get_object_or_404(PlayerStatLine, pk=pk)
        serializer = PlayerStatsLineSerializer(playerstats, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)             


# Players Stats Line Delete
class PlayerStatsLineDeleteView(APIView):
    def delete(self, request, pk):
        playerstats = get_object_or_404(PlayerStatLine, pk=pk)
        playerstats.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)