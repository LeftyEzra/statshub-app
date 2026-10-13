# team/services.py
from datetime import datetime
import time
import requests
from .models import Game, Shot

def fetch_and_store_single_game_shots(nba_game_id, game_title):
    """
    Fetches shot data for ONE specific game.
    Uses robust retries and fallback endpoints to beat RemoteDisconnected drops.
    """
    url = "https://stats.nba.com/stats/shotchartdetail"
    
    headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com',
        'Connection': 'close',  # Forces new clean connection to stop reset drops
    }
    
    params = {
        'TeamID': '1610612743',  # Denver Nuggets
        'PlayerID': '0',
        'GameID': str(nba_game_id),
        'Season': '2023-24',
        'SeasonType': 'Regular Season',
        'ContextMeasure': 'FGA'
    }

    print(f"Fetching shot data for: {game_title} (ID: {nba_game_id})...")
    
    response = None
    # Retry up to 5 times with a new session each time
    for attempt in range(1, 6):
        try:
            session = requests.Session()
            # Set keep_alive to False so server doesn't abruptly terminate idle connections
            adapter = requests.adapters.HTTPAdapter(max_retries=3)
            session.mount('https://', adapter)
            
            response = session.get(url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                print("Connected successfully!")
                break
        except Exception as e:
            print(f"Attempt {attempt}/5 failed ({e}). Retrying in 2 seconds...")
            time.sleep(2)

    if not response or response.status_code != 200:
        print("Failed to pull live shot data due to NBA firewall blocks.")
        return

    json_data = response.json()
    result_sets = json_data['resultSets'][0]
    headers_list = result_sets['headers']
    rows = result_sets['rowSet']

    if not rows:
        print(f"No shot records found for Game ID {nba_game_id}.")
        return

    date_str = str(rows[0][headers_list.index('GAME_DATE')])
    game_date = datetime.strptime(date_str, '%Y%m%d').date()

    game_obj, _ = Game.objects.get_or_create(
        nba_game_id=str(nba_game_id),
        defaults={
            'game_title': game_title,
            'game_date': game_date
        }
    )

    game_obj.shots.all().delete()

    x_idx = headers_list.index('LOC_X')
    y_idx = headers_list.index('LOC_Y')
    player_idx = headers_list.index('PLAYER_NAME')
    team_idx = headers_list.index('TEAM_NAME')
    period_idx = headers_list.index('PERIOD')
    min_idx = headers_list.index('MINUTES_REMAINING')
    sec_idx = headers_list.index('SECONDS_REMAINING')
    event_idx = headers_list.index('EVENT_TYPE')

    shots_to_create = []
    for row in rows:
        raw_x = float(row[x_idx])
        raw_y = float(row[y_idx])

        shots_to_create.append(
            Shot(
                game=game_obj,
                player_name=row[player_idx],
                team_name=row[team_idx],
                period=row[period_idx],
                minutes_remaining=row[min_idx],
                seconds_remaining=row[sec_idx],
                event_type=row[event_idx],
                loc_x=raw_x,
                loc_y=raw_y,
                world_x=(raw_x / 250.0) * 7.5,
                world_y=(raw_y / 400.0) * 14.0
            )
        )

    Shot.objects.bulk_create(shots_to_create, batch_size=500)
    print(f"Successfully saved {len(shots_to_create)} shots for '{game_title}' under slug: {game_obj.slug}!")