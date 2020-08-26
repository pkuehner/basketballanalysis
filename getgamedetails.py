import pandas as pd
import requests
from nba_api.stats.endpoints import boxscoreadvancedv2
from nba_api.stats.endpoints import boxscoreplayertrackv2
from nba_api.stats.endpoints import boxscoredefensive
from nba_api.stats.endpoints import playbyplayv2
from nba_api.stats.endpoints import boxscoresummaryv2
from own_endpoints import get_rotation
import time
import numpy as np
from numpy import array
from scipy.cluster.vq import vq, kmeans2, whiten

# Basic Request


custom_headers = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://stats.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true'
}

games = pd.read_json('games_19_20.json')
count = 0;
maxlen = len(np.unique(games['GAME_ID']))
games = np.unique(games['GAME_ID'])
for game in games:
    error = True
    while(error):
        print(game)
        try:
            data = boxscoresummaryv2.BoxScoreSummaryV2(game_id='00'+str(game),
                                                               timeout=10)
            data = data.get_data_frames()[0]
            data.to_json('games/summary/'+'00'+str(game)+'.json')
            error = False
        except:
            error = True
            time.sleep(20)

# Only available after v1.1.0
# Proxy Support, Custom Headers Support, Timeout Support (in seconds)

