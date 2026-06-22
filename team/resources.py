from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import PlayerStatLine, Player, Team, Opponent

"""
This code is acting as a custom bridge between the raw, flat CSV file and the structured relational database. 
It ensures that even if there is pre-built opponent's rosters, the statistics import process will "fill in the gaps" automatically.

Step-by-step breakdown of the logic:
1. Telling django-import-export which columns to look for in the CSV. 
Even though player_name and team_name aren't necessarily direct fields in the PlayerStatLine model, 
It should capture them so it can use them as "search keys" to find the correct Player object.

2. The before_import_row Hook
Before Django attempts to save the row to the database, it pauses and runs this function.
Logic Branching (is_opponent): The code looks at your opponent column. 
This is the "toggle" to tell the code where to look:

If it’s an opponent: It looks up the Opponent record. 
It then uses get_or_create. This is a "safety first" command—it asks the database: 
"Does this player exist for this specific opponent?" If yes, it grabs that player; if no, 
it creates them immediately with a default jersey_number of 0.

If it’s main team: 
It assumes the player should already exist (Player.objects.get) 
because i want to strictly validate that the team roster is correct.

3. The "Glue" (Linking the Foreign Key)
PlayerStatLine model has a player field (a Foreign Key to Player). 
However, the CSV doesn't contain a player_id—it contains a name like "John Doe."

The line row['player'] = player.id is where it bridges that gap. 
Translated the human-readable "John Doe" into the technical database ID (player.id) 
that Django needs to build the relationship. 
By injecting this into the row dictionary, 
it is  effectively "tricking" the importer into thinking the CSV provided the ID all along.
"""

class GameStatsResource(resources.ModelResource):
    # 1. Map only the CSV-to-Model stats here
    player_name = fields.Field(column_name='Player', attribute='player_name')
    minutes = fields.Field(column_name='Min', attribute='minutes')
    points = fields.Field(column_name='Pts', attribute='points')
  
    assists = fields.Field(column_name='AST', attribute='assists')
    field_goal_made = fields.Field(column_name='FGM', attribute='field_goal_made')
    field_goal_attempts = fields.Field(column_name='FGA', attribute='field_goal_attempts')
    point_3_made = fields.Field(column_name='3PM', attribute='point_3_made')
    point_3_attempts = fields.Field(column_name='3PA', attribute='point_3_attempts')
    ft_made = fields.Field(column_name='FTM', attribute='ft_made')
    ft_attempts = fields.Field(column_name='FTA', attribute='ft_attempts')
    offensive_rebs = fields.Field(column_name='OFF', attribute='offensive_rebs')
    defensive_rebs = fields.Field(column_name='DEF', attribute='defensive_rebs')
    steals = fields.Field(column_name='STL', attribute='steals')
    blocks = fields.Field(column_name='BLK', attribute='blocks')
    turnovers = fields.Field(column_name='TO', attribute='turnovers')


    class Meta:
        model = PlayerStatLine
        # Include EVERY field from your model that needs to be saved
        fields = (
            'game_schedule', 'player_name', 'team', 'opponent', 
            'minutes', 'starter', 'points', 'field_goal_made', 
            'field_goal_attempts', 'point_3_made', 'point_3_attempts', 
            'ft_made', 'ft_attempts', 'offensive_rebs', 'defensive_rebs', 
            'blocks', 'assists', 'steals', 'turnovers'
        )
        import_id_fields = ('game_schedule', 'player_name')

        def before_import_row(self, row, **kwargs):
            p_name = row.get('Player')
            t_name = row.get('player_team')
            opp_name = row.get('opponent')
            
            # 1. Fetch the objects
            team_obj = Team.objects.get(slug=t_name) 
            opponent_obj = Opponent.objects.get(slug=opp_name)
            
            player_obj, _ = Player.objects.get_or_create(
                player_name=p_name,
                team=team_obj
            )
                
            # 2. Inject the OBJECTS into the row, not the slugs
            # django-import-export will handle the ForeignKey conversion
            row['player_name'] = player_obj.id 
            row['team'] = team_obj.id  # Because you set to_field='slug'
            row['opponent'] = opponent_obj.id



