# services.py
import pandas as pd
from django.db.models import Sum

def get_game_detail_data(competition, game_details, team, opponent, stats, all_games, other_games, tournament_standing):
    """
    Handles all Pandas data processing, merging, and statistical aggregations 
    for the GameDetailView. Returns a dictionary of processed context data.
    """
    # Configure Pandas options
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)

    # Convert QuerySets to DataFrames
    all_games_df = pd.DataFrame(
        all_games.values('date', 'time', 'team__name', 'indicator', 'opponent__name', 
                         'team_scores', 'opponent_scores', 'team_win_loss', 'game_venue', 'game_type')
    )
    
    international_games = pd.DataFrame(
        other_games.values('id', 'slug', 'competition__slug', 'date', 'time', 'team__name', 'team__team_logo', 
                           'indicator', 'opponent__name', 'opponent__logo', 'team_scores', 'opponent_scores', 
                           'team_win_loss', 'game_venue__name', 'game_type')
    )

    regular_season = all_games_df[all_games_df['game_type'].isin(["regular"])]
    int_games_in_other_games = international_games[international_games['game_type'].isin(["international"])]

    all_game_stats_df = pd.DataFrame(
        all_game_stats.values('game_schedule__date', 'player_name__player_name', 'team__name', 
                              'offensive_rebs', 'defensive_rebs', 'assists', 'game_schedule__game_type')
    ) if 'all_game_stats' in locals() else pd.DataFrame()

    # Check if stats exist and dataframe is populated
    if stats.exists() and not all_game_stats_df.empty and 'offensive_rebs' in all_game_stats_df.columns:
        regular_season_games_played_df = all_game_stats_df[all_game_stats_df['game_schedule__game_type'].isin(["regular"])].copy()
        regular_season_games_played_df['total_rebounds'] = regular_season_games_played_df['offensive_rebs'] + regular_season_games_played_df['defensive_rebs']
        
        regular_season_games_played_df = regular_season_games_played_df.groupby('game_schedule__date')[[
            'player_name__player_name', 'team__name', 'offensive_rebs', 'defensive_rebs', 'total_rebounds', 'assists'
        ]].sum().reset_index()
        regular_season_games_played_df = regular_season_games_played_df.rename(columns={'game_schedule__date': 'date'})

        merge_df = regular_season.merge(regular_season_games_played_df, how='left', on='date')
        merge_df = merge_df[~merge_df['team_scores'].isin([0])]
        mean_merge_df = merge_df[['team_scores', 'opponent_scores', 'offensive_rebs', 
                                  'defensive_rebs', 'total_rebounds', 'assists']].mean().astype(float)

        # Player Stats
        stats_df = pd.DataFrame(
            stats.values('player_name__id', 'player_name__slug', 'player_name__jersey_number', 'team__name', 
                         'opponent__name', 'player_name__player_name', 'player_name__player_image', 'points', 
                         'assists', 'field_goal_attempts', 'field_goal_made', 'ft_attempts', 'ft_made',
                         'point_3_attempts', 'point_3_made', 'turnovers', 'minutes', 'blocks', 'steals',
                         'personal_fouls', 'player_name__team__name', 'offensive_rebs', 'defensive_rebs')
        )
        
        stats_df = stats_df.rename(columns={'player_name__id': 'player_id'})
        stats_df['total_rebounds'] = stats_df['offensive_rebs'] + stats_df['defensive_rebs']
        stats_df['fg_percent'] = ((stats_df['field_goal_made'] / stats_df['field_goal_attempts']) * 100).fillna(0)
        stats_df['point_3_percent'] = ((stats_df['point_3_made'] / stats_df['point_3_attempts']) * 100).fillna(0)
        stats_df['ft_percent'] = ((stats_df['ft_made'] / stats_df['ft_attempts']) * 100).fillna(0)
        stats_df['team__name'] = stats_df['team__name'].fillna(stats_df['opponent__name'])
        stats_df['opponent__name'] = stats_df['opponent__name'].fillna(stats_df['team__name'])

        stats_df["efficiency"] = (
            stats_df["points"] + stats_df["total_rebounds"] + stats_df["assists"] + 
            stats_df["steals"] + stats_df["blocks"] - 
            ((stats_df["field_goal_attempts"] - stats_df["field_goal_made"]) + 
             (stats_df["ft_attempts"] - stats_df["ft_made"]) + stats_df["turnovers"])
        )
        stats_df['def'] = stats_df['steals'] * 2 + stats_df['blocks'] * 2 + stats_df['defensive_rebs'] * 0.5

        # Team & Opponent Slicing
        team_players = stats_df[stats_df['team__name'].isin([team.name])].copy()
        team_players[['player_name__player_name', 'surname']] = team_players['player_name__player_name'].str.split(" ", n=1, expand=True)
        team_players['player_name__player_name'] = team_players['player_name__player_name'].apply(
            lambda x: "".join([word[0].upper() for word in str(x).split()])
        )
        team_players['player_name'] = team_players['player_name__player_name'] + '. ' + team_players['surname']

        opponent_players = stats_df[stats_df['opponent__name'].isin([opponent.name])].copy()
        opponent_players[['player_name__player_name', 'surname']] = opponent_players['player_name__player_name'].str.split(" ", n=1, expand=True)
        opponent_players['player_name__player_name'] = opponent_players['player_name__player_name'].apply(
            lambda x: "".join([word[0].upper() for word in str(x).split()])
        )
        opponent_players['player_name'] = opponent_players['player_name__player_name'] + '. ' + opponent_players['surname']

        def team_best_performer(team_opp, stat):
            return (
                team_opp.groupby([
                    "player_id", 'player_name__slug', "player_name__jersey_number", "player_name",
                    "player_name__player_image", "player_name__team__name", 'opponent__name'
                ])[['points', 'total_rebounds', 'assists', 'field_goal_attempts', 'field_goal_made', 
                    'ft_attempts', 'ft_made', 'offensive_rebs', 'defensive_rebs', 'turnovers', 'minutes']]
                .sum().sort_values(stat, ascending=False).head(1).reset_index()
            )

        top_points = team_best_performer(team_players, 'points')
        top_rebounds = team_best_performer(team_players, 'total_rebounds')
        top_assists = team_best_performer(team_players, 'assists')

        opp_top_points = opponent_players.groupby(["player_id", "player_name__jersey_number", "player_name", "player_name__player_image", 'opponent__name'])[['points', 'total_rebounds', 'assists', 'field_goal_attempts', 'field_goal_made', 'ft_attempts', 'ft_made', 'offensive_rebs', 'defensive_rebs', 'turnovers', 'minutes']].sum().sort_values("points", ascending=False).head(1).reset_index()
        opp_top_rebounds = opponent_players.groupby(["player_id", "player_name__jersey_number", "player_name", "player_name__player_image", 'opponent__name'])[['points', 'total_rebounds', 'assists', 'field_goal_attempts', 'field_goal_made', 'ft_attempts', 'ft_made', 'offensive_rebs', 'defensive_rebs', 'turnovers', 'minutes']].sum().sort_values("total_rebounds", ascending=False).head(1).reset_index()
        opp_top_assists = opponent_players.groupby(["player_id", "player_name__jersey_number", "player_name", "player_name__player_image", 'opponent__name'])[['points', 'total_rebounds', 'assists', 'field_goal_attempts', 'field_goal_made', 'ft_attempts', 'ft_made', 'offensive_rebs', 'defensive_rebs', 'turnovers', 'minutes']].sum().sort_values("assists", ascending=False).head(1).reset_index()

        total_stats_df = team_players.groupby(["player_name__player_name"])[['points', 'offensive_rebs', 'defensive_rebs', 'total_rebounds', 'field_goal_made', 'field_goal_attempts', 'ft_attempts', 'ft_made', 'point_3_attempts', 'point_3_made', 'assists', 'blocks', 'steals', 'turnovers', 'personal_fouls', 'efficiency', 'def']].sum().reset_index()
        total_stats_df = total_stats_df.drop(columns=['player_name__player_name']).sum()
        total_stats_df['fg_percent'] = (total_stats_df['field_goal_made'] / total_stats_df['field_goal_attempts']) * 100
        total_stats_df['point_3_percent'] = (total_stats_df['point_3_made'] / total_stats_df['point_3_attempts']) * 100
        total_stats_df['ft_percent'] = (total_stats_df['ft_made'] / total_stats_df['ft_attempts']) * 100

        opp_total_stats_df = opponent_players.groupby(["player_name__player_name"])[['points', 'offensive_rebs', 'defensive_rebs', 'total_rebounds', 'field_goal_made', 'field_goal_attempts', 'ft_attempts', 'ft_made', 'point_3_attempts', 'point_3_made', 'assists', 'blocks', 'steals', 'turnovers', 'personal_fouls', 'efficiency', 'def']].sum().reset_index()
        opp_total_stats_df = opp_total_stats_df.drop(columns=['player_name__player_name']).sum()
        opp_total_stats_df['fg_percent'] = ((opp_total_stats_df['field_goal_made'] / opp_total_stats_df['field_goal_attempts']) * 100).round(1)
        opp_total_stats_df['point_3_percent'] = ((opp_total_stats_df['point_3_made'] / opp_total_stats_df['point_3_attempts']) * 100).round(1)
        opp_total_stats_df['ft_percent'] = ((opp_total_stats_df['ft_made'] / opp_total_stats_df['ft_attempts']) * 100).round(1)

        # Django Aggregates
        home_totals = stats.aggregate(
            points=Sum('points'), field_goal_attempts=Sum('field_goal_attempts'), field_goal_made=Sum('field_goal_made'),
            point_3_attempts=Sum('point_3_attempts'), point_3_made=Sum('point_3_made'), ft_attempts=Sum('ft_attempts'),
            ft_made=Sum('ft_made'), offensive_rebs=Sum('offensive_rebs'), defensive_rebs=Sum('defensive_rebs'),
            blocks=Sum('blocks'), assists=Sum('assists'), steals=Sum('steals'), turnovers=Sum('turnovers'),
            personal_fouls=Sum('personal_fouls')
        )
        home_totals['total_rebounds'] = home_totals['offensive_rebs'] + home_totals['defensive_rebs']
        home_totals['fg_percent'] = (home_totals['field_goal_made'] / home_totals['field_goal_attempts'] * 100) if home_totals['field_goal_attempts'] else 0
        home_totals['point_3_percent'] = (home_totals['point_3_made'] / home_totals['point_3_attempts'] * 100) if home_totals['point_3_attempts'] else 0
        home_totals['ft_percent'] = (home_totals['ft_made'] / home_totals['ft_attempts'] * 100) if home_totals['ft_attempts'] else 0

        home_totals["efficiency"] = (
            home_totals["points"] + home_totals["total_rebounds"] + home_totals["assists"] + 
            home_totals["steals"] + home_totals["blocks"] - 
            ((home_totals["field_goal_attempts"] - home_totals["field_goal_made"]) + 
             (home_totals["ft_attempts"] - home_totals["ft_made"]) + home_totals["turnovers"])
        )
        home_totals['def'] = home_totals['steals'] * 2 + home_totals['blocks'] * 2 + home_totals['defensive_rebs'] * 0.5

        # Standings
        if tournament_standing.exists():
            standing_df = pd.DataFrame(
                tournament_standing.values('competition__name', 'game_type', 'team__name', 'team__team_logo', 
                                           'opponent__name', 'opponent__logo', 'w', 'l', 'home_record', 'away_record', 
                                           'ppg', 'opp_ppg', 'strk', 'last_5')
            ).sort_values('w', ascending=False).reset_index(drop=True)

            standing_df['team__name'] = standing_df['team__name'].fillna(standing_df['opponent__name'])
            standing_df['opponent__name'] = standing_df['opponent__name'].fillna(standing_df['team__name'])
            standing_df['team__team_logo'] = standing_df['team__team_logo'].fillna(standing_df['opponent__logo'])
            standing_df['opponent__logo'] = standing_df['opponent__logo'].fillna(standing_df['team__team_logo'])
            standing_records = standing_df.to_dict('records')
        else:
            standing_records = []

        return {
            'team_players': team_players.to_dict('records'),
            'opponent_players': opponent_players.to_dict('records'),
            'int_games_in_other_games': int_games_in_other_games.to_dict('records'),
            'standing_df': standing_records,
            'home_totals': home_totals,
            'top_points_df': top_points.to_dict('records'),
            'top_rebounds_df': top_rebounds.to_dict('records'),
            'top_assists_df': top_assists.to_dict('records'),
            'opp_top_points': opp_top_points.to_dict('records'),
            'opp_top_rebounds': opp_top_rebounds.to_dict('records'),
            'opp_top_assists': opp_top_assists.to_dict('records'),
            'overall_sum_df': total_stats_df,
            'opp_total_stats_df': opp_total_stats_df,
            'mean_merge_df': mean_merge_df,
            'has_stats': True
        }
    
    # Fallback empty structures if stats don't exist
    return {
        'team_players': [],
        'opponent_players': [],
        'int_games_in_other_games': [],
        'standing_df': [],
        'home_totals': {},
        'top_points_df': [],
        'top_rebounds_df': [],
        'top_assists_df': [],
        'opp_top_points': [],
        'opp_top_rebounds': [],
        'opp_top_assists': [],
        'overall_sum_df': {},
        'opp_total_stats_df': {},
        'mean_merge_df': pd.DataFrame(),
        'has_stats': False
    }