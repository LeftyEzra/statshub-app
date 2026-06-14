import os
import django
import csv
from django.core.management.base import BaseCommand
from team.models import PlayerStatLine, Player, Team, GameSchedule, Competition
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, time

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_basketball_website.settings')
django.setup()

class Command(BaseCommand):
    help = "Imports player stats from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help=r"C:\Users\user\Downloads\2025-BAL-Stats.csv")

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        player_name = Player.objects.get(player_name=row['Player'])
                        player_team, _ = Team.objects.get_or_create(team_name=row['player_team'])
                        opponent, _ = Team.objects.get_or_create(team_name=row['opponent'])

                        try:
                            date_object = datetime.strptime(row['game_schedule'], '%Y-%m-%d').date()
                            time_object = datetime.strptime(row['game_time'], '%H:%M:%S').time() #add this line.
                            game_schedule, created = GameSchedule.objects.get_or_create(
                                date=date_object,
                                time=time_object, #add this line.
                                home_team=player_team,
                                away_team=opponent,
                            )
                        except ValueError as e:
                            self.stderr.write(self.style.ERROR(f"Invalid date/time format: {e} - row: {row}"))
                            continue
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f"GameSchedule error: {e} - row: {row}"))
                            continue

                        PlayersStats.objects.create(
                            player_name=player_name,
                            player_team=player_team,
                            opponent=opponent,
                            game_schedule=game_schedule,
                            game_time=row['game_time'],
                            minutes=row['Min'],
                            points=row['Pts'],
                            field_goal_attempts=row['FGA'],
                            field_goal_made=row['FGM'],
                            #fg_percent=row['FG%'],
                            point_3_attempts=row['3PA'],
                            point_3_made=row['3PM'],
                            #point_3_percent=row['3P%'],
                            
                            ft_attempts=row['FTA'],
                            ft_made=row['FTM'],
                            #ft_percent=row['FT%'],
                            offensive_rebs=row['OFF'],
                            defensive_rebs=row['DEF'],
                            total_rebounds=row['REB'],
                            blocks=row['BLK'],
                            assists=row['AST'],
                            steals=row['STL'],
                            turnovers=row['TO'],
                            personal_fouls=0,
                            plus_minus=row['+/-'],
                            efficiency=0,
                        )
                    except ObjectDoesNotExist as e:
                        self.stderr.write(self.style.ERROR(f"Object not found: {e} - row: {row}"))
                        continue
                    except ValueError as e:
                        self.stderr.write(self.style.ERROR(f"Value error: {e} - row: {row}"))
                        continue
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"General error: {e} - row: {row}"))
                        continue

            self.stdout.write(self.style.SUCCESS("Data import completed successfully!"))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"General error: {e}"))


# python manage.py import_opponent_stats semifinals_game1.csv            


"""
import os
import django
import csv
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

from team.models import PlayerStatLine, Player, Team, Opponent, GameSchedule

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_basketball_website.settings')
django.setup()

class Command(BaseCommand):
    help = "Imports player stats from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # Resolve teams
                        team_name = row['Team']
                        opponent_name = row['Opponent']
                        player_name_str = row['Player']

                        player_team = Team.objects.get(team_name=team_name)
                        opponent = Opponent.objects.get(name=opponent_name)

                        # Resolve game schedule
                        try:
                            date_object = datetime.strptime(row['game_schedule'], '%Y-%m-%d').date()
                            time_object = datetime.strptime(row['game_time'], '%H:%M:%S').time()
                            game_schedule, _ = GameSchedule.objects.get_or_create(
                                date=date_object,
                                time=time_object,
                                home_team=player_team if team_name == "Python" else opponent,
                                away_team=opponent if team_name == "Python" else player_team,
                            )
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f"GameSchedule error: {e} - row: {row}"))
                            continue

                        # Resolve player
                        if team_name == "Python":
                            # Link to registered Python players
                            player = Player.objects.get(player_name=player_name_str, team=player_team)
                        else:
                            # Opponent players: create if missing
                            player, _ = Player.objects.get_or_create(
                                player_name=player_name_str,
                                opponent=opponent,
                                defaults={"position": "SP"}  # minimal info
                            )

                        # Create stat line
                        PlayerStatLine.objects.create(
                            player_name=player,
                            team=player_team if team_name == "Python" else None,
                            opponent=opponent,
                            game_schedule=game_schedule,
                            minutes=float(row['MIN']),
                            starter=row['Starter'].lower() == "true",
                            points=int(row['PTS']),
                            field_goal_attempts=int(row['FGA']),
                            field_goal_made=int(row['FGM']),
                            point_3_attempts=int(row['3PA']),
                            point_3_made=int(row['3PM']),
                            ft_attempts=int(row['FTA']),
                            ft_made=int(row['FTM']),
                            offensive_rebs=int(row['REB_O']),
                            defensive_rebs=int(row['REB_D']),
                            assists=int(row['AST']),
                            steals=int(row['ST']),
                            blocks=int(row['BS']),
                            turnovers=int(row['TO']),
                            personal_fouls=int(row['PF']),
                        )

                    except ObjectDoesNotExist as e:
                        self.stderr.write(self.style.ERROR(f"Object not found: {e} - row: {row}"))
                        continue
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"General error: {e} - row: {row}"))
                        continue

            self.stdout.write(self.style.SUCCESS("Data import completed successfully!"))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"General error: {e}"))

"""


"""
import os
import django
import csv
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

from team.models import PlayerStatLine, Player, Team, Opponent, GameSchedule

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_basketball_website.settings')
django.setup()

# Mapping dictionaries
NAME_MAP = {
    # Example: map raw names from CSV to your DB names
    "OGEDENGBE BIDEMI": "Django Python",
    "OKEKE CHIDINMA": "Flask Python",
    "NUMPY": "NumPy",
    "TENSORFLOW": "TensorFlow",
    # Add more mappings as needed
}

TEAM_MAP = {
    # Map raw team names from CSV to your DB team/opponent names
    "Air Warriors": "Python",
    "Royal Aces": "Opponent",
    # Add more mappings as needed
}

class Command(BaseCommand):
    help = "Imports player stats from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # Normalize names
                        raw_team = row['Team'].strip()
                        raw_opponent = row['Opponent'].strip()
                        raw_player = row['Player'].strip()

                        team_name = TEAM_MAP.get(raw_team, raw_team)
                        opponent_name = TEAM_MAP.get(raw_opponent, raw_opponent)
                        player_name_str = NAME_MAP.get(raw_player, raw_player)

                        # Resolve team and opponent
                        player_team = Team.objects.get(team_name=team_name)
                        opponent = Opponent.objects.get(name=opponent_name)

                        # Resolve game schedule
                        date_object = datetime.strptime(row['game_schedule'], '%Y-%m-%d').date()
                        time_object = datetime.strptime(row['game_time'], '%H:%M:%S').time()
                        game_schedule, _ = GameSchedule.objects.get_or_create(
                            date=date_object,
                            time=time_object,
                            home_team=player_team if team_name == "Python" else opponent,
                            away_team=opponent if team_name == "Python" else player_team,
                        )

                        # Resolve player
                        if team_name == "Python":
                            player = Player.objects.get(player_name=player_name_str, team=player_team)
                        else:
                            player, _ = Player.objects.get_or_create(
                                player_name=player_name_str,
                                opponent=opponent,
                                defaults={"position": "SP"}  # minimal info
                            )

                        # Create stat line
                        PlayerStatLine.objects.create(
                            player_name=player,
                            team=player_team if team_name == "Python" else None,
                            opponent=opponent,
                            game_schedule=game_schedule,
                            minutes=float(row['MIN']),
                            starter=row['Starter'].lower() == "true",
                            points=int(row['PTS']),
                            field_goal_attempts=int(row['FGA']),
                            field_goal_made=int(row['FGM']),
                            point_3_attempts=int(row['3PA']),
                            point_3_made=int(row['3PM']),
                            ft_attempts=int(row['FTA']),
                            ft_made=int(row['FTM']),
                            offensive_rebs=int(row['REB_O']),
                            defensive_rebs=int(row['REB_D']),
                            assists=int(row['AST']),
                            steals=int(row['ST']),
                            blocks=int(row['BS']),
                            turnovers=int(row['TO']),
                            personal_fouls=int(row['PF']),
                        )

                    except ObjectDoesNotExist as e:
                        self.stderr.write(self.style.ERROR(f"Object not found: {e} - row: {row}"))
                        continue
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"General error: {e} - row: {row}"))
                        continue

            self.stdout.write(self.style.SUCCESS("Data import completed successfully!"))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"General error: {e}"))

"""


"""
import os
import django
import csv
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

from team.models import PlayerStatLine, Player, Team, Opponent, GameSchedule

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_basketball_website.settings')
django.setup()

class Command(BaseCommand):
    help = "Imports player stats from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        team_name = row['Team'].strip()
                        opponent_name = row['Opponent'].strip()
                        player_name_str = row['Player'].strip()

                        player_team = Team.objects.get(team_name=team_name)
                        opponent = Opponent.objects.get(name=opponent_name)

                        date_object = datetime.strptime(row['game_schedule'], '%Y-%m-%d').date()
                        time_object = datetime.strptime(row['game_time'], '%H:%M:%S').time()
                        game_schedule, _ = GameSchedule.objects.get_or_create(
                            date=date_object,
                            time=time_object,
                            home_team=player_team if team_name == "Python" else opponent,
                            away_team=opponent if team_name == "Python" else player_team,
                        )

                        if team_name == "Python":
                            player = Player.objects.get(player_name=player_name_str, team=player_team)
                        else:
                            player, _ = Player.objects.get_or_create(
                                player_name=player_name_str,
                                opponent=opponent,
                                defaults={"position": "SP"}
                            )

                        PlayerStatLine.objects.create(
                            player_name=player,
                            team=player_team if team_name == "Python" else None,
                            opponent=opponent,
                            game_schedule=game_schedule,
                            minutes=float(row['MIN']),
                            starter=row['Starter'].lower() == "true",
                            points=int(row['PTS']),
                            field_goal_attempts=int(row['FGA']),
                            field_goal_made=int(row['FGM']),
                            point_3_attempts=int(row['3PA']),
                            point_3_made=int(row['3PM']),
                            ft_attempts=int(row['FTA']),
                            ft_made=int(row['FTM']),
                            offensive_rebs=int(row['REB_O']),
                            defensive_rebs=int(row['REB_D']),
                            assists=int(row['AST']),
                            steals=int(row['ST']),
                            blocks=int(row['BS']),
                            turnovers=int(row['TO']),
                            personal_fouls=int(row['PF']),
                        )

                    except ObjectDoesNotExist as e:
                        self.stderr.write(self.style.ERROR(f"Object not found: {e} - row: {row}"))
                        continue
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"General error: {e} - row: {row}"))
                        continue

            self.stdout.write(self.style.SUCCESS("Data import completed successfully!"))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"General error: {e}"))

"""