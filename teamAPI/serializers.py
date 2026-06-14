# This serializer.py files is a translator between complex data types,
# like django models and simple data fotmat like JSON or XML.
# The purpose is to convert python datatypes into JSON, XML or other content datatypes.
# Also convert parsed data back into complex data types, after cross checking and validating the incoming data.
# For every Foriegn Key you want to display as a name from .models, Use StringRelatedField.

from rest_framework import serializers
from team.models import Competition
from team.models import Team
from team.models import Game
from team.models import Season
from team.models import Player
from team.models import PlayerStatLine
from team.models import QuarterlyScores
from team.models import Opponent
from team.models import TeamStaff



# Creating a competion serializer
class CompetitionSerializer(serializers.ModelSerializer):
    
    # Use StringRelatedField for Foreign Keys you want to display as a name
    year = serializers.StringRelatedField()
    team = serializers.StringRelatedField()
    opponents = serializers.StringRelatedField()
    
    class Meta: # Defines the model and fields that should be included.
        model = Competition
        fields = '__all__'



# Creating a Game Schedule serializer

class GameSerializer(serializers.ModelSerializer):

    # Use StringRelatedField for Foreign Keys you want to display as a name
    competition = serializers.StringRelatedField()
    team = serializers.StringRelatedField()
    opponent = serializers.StringRelatedField()

    class Meta:
        model = Game
        fields = '__all__'


# Quarterly Scores 
class QuarterlyScoreLineSerializer(serializers.ModelSerializer):

    # Use StringRelatedField for Foreign Keys you want to display as a name
    game = serializers.StringRelatedField()
    quarterly_scores_for = serializers.StringRelatedField()
    

    class Meta: # Defines the model and fields that should be included.
        model = QuarterlyScores
        fields = '__all__'  



# Creating a Team serializer
class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'



# Creating a Team serializer
class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamStaff
        fields = '__all__'



# Opponents
class OpponentSerializer(serializers.ModelSerializer):
    # Use StringRelatedField for Foreign Keys you want to display as a name
    competitions = serializers.StringRelatedField()
    year = serializers.StringRelatedField()


    class Meta:
        model = Opponent
        fields = '__all__'


# Creating a competion serializer
class PlayerSerializer(serializers.ModelSerializer):
    # Use StringRelatedField for Foreign Keys you want to display as a name
    team = serializers.StringRelatedField()
    year = serializers.StringRelatedField()
    for_this_competition = serializers.StringRelatedField()

    class Meta: # Defines the model and fields that should be included.
        model = Player
        fields = '__all__'
        
# Creating a competion serializer
class PlayerStatsLineSerializer(serializers.ModelSerializer):

    # Use StringRelatedField for Foreign Keys you want to display as a name
    player_name = serializers.StringRelatedField()
    team = serializers.StringRelatedField()
    opponents = serializers.StringRelatedField()
    game_schedule = serializers.StringRelatedField()
    game_time = serializers.StringRelatedField()



    class Meta: # Defines the model and fields that should be included.
        model = PlayerStatLine
        fields = '__all__'        


# Master Serializers To Hold Team Details
class TeamDetailSerializer(serializers.Serializer):

    # Team/Competition are single objects
    team = TeamSerializer()
    staff = StaffSerializer(many=True)       
    competition = CompetitionSerializer()

    # Opponents/Games/Players are querysets (lists), so many=True is the recommmended option
    opponents = OpponentSerializer(many=True)
    #games = GameSerializer(many=True)
    players = PlayerSerializer(many=True) # Assuming PlayerSerializer exists

    
           