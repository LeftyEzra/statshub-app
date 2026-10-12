# team/services.py
import time
from nba_api.library import http as base_http
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.library import http as stats_http
from .models import Shot

# Custom browser headers required to bypass NBA firewall drop
CUSTOM_HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
        ' like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.nba.com/',
    'Origin': 'https://www.nba.com',
    'Connection': 'keep-alive',
}


def fetch_and_store_nuggets_shots():
  """Fetches shot data from NBA API and saves it directly to PostgreSQL database."""
  print('Configuring NBA API request headers...')

  # Patch NBA API internal session headers globally
  stats_http.STATS_HEADERS = CUSTOM_HEADERS
  stats_http.NBAStatsHTTP.headers = CUSTOM_HEADERS
  stats_http.NBAStatsHTTP._session = None  # Force a fresh connection reset

  max_retries = 3
  df = None

  for attempt in range(1, max_retries + 1):
    try:
      print(
          f'Attempt {attempt}/{max_retries}: Fetching shot chart data from'
          ' NBA...'
      )

      # Fetch Denver Nuggets shots (Team ID: 1610612743)
      shot_data = shotchartdetail.ShotChartDetail(
          team_id=1610612743,
          player_id=0,
          season_nullable='2023-24',  # Use completed season for reliable data
          season_type_all_star='Regular Season',
          context_measure_simple='FGA',
          timeout=30,  # 30 second timeout
      )

      df = shot_data.get_data_frames()[0]
      if not df.empty:
        print(f'Successfully retrieved {len(df)} shot records!')
        break

    except Exception as e:
      print(f'Attempt {attempt} failed: {e}')
      time.sleep(2)  # Wait 2 seconds before retrying

  if df is None or df.empty:
    print('Failed to pull data from NBA API after retries.')
    return

  # Clear existing shots before inserting to avoid duplicates
  Shot.objects.all().delete()

  shots_to_create = []
  for _, row in df.iterrows():
    raw_x = float(row['LOC_X'])
    raw_y = float(row['LOC_Y'])

    # Convert NBA coordinates (feet/tenths) to 3D World Meters
    world_x = (raw_x / 250.0) * 7.5
    world_y = (raw_y / 400.0) * 14.0

    shots_to_create.append(
        Shot(
            player_name=row['PLAYER_NAME'],
            team_name=row['TEAM_NAME'],
            period=row['PERIOD'],
            minutes_remaining=row['MINUTES_REMAINING'],
            seconds_remaining=row['SECONDS_REMAINING'],
            event_type=row['EVENT_TYPE'],
            loc_x=raw_x,
            loc_y=raw_y,
            world_x=world_x,
            world_y=world_y,
        )
    )

  # Bulk insert into database
  Shot.objects.bulk_create(shots_to_create, batch_size=500)
  print(
      f'Successfully populated database with {len(shots_to_create)} Denver'
      ' Nuggets shots!'
  )