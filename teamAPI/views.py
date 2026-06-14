from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from team.models import  Team, TeamStaff, Game, Player, PlayerStatLine, QuarterlyScores, Opponent
from .serializers import CompetitionSerializer, TeamSerializer, StaffSerializer, GameSerializer, PlayerSerializer, PlayerStatsLineSerializer
from .serializers import QuarterlyScoreLineSerializer, OpponentSerializer, GameSerializer, TeamDetailSerializer
#from .forms import OpponentForm
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




# Function to convert date of birth of players to number
def calculate_age(birthdate):
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age



# Competition Create
class CompetitionsCreateView(APIView):
    def post(self, request):
        serializer = CompetitionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  