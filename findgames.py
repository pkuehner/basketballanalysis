import pandas as pd
import requests
from nba_api.stats.endpoints import leaguegamefinder
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

# Only available after v1.1.0
# Proxy Support, Custom Headers Support, Timeout Support (in seconds)
data = leaguegamefinder.LeagueGameFinder(season_nullable='2019-20', season_type_nullable='Regular Season', league_id_nullable='00')
data = data.get_data_frames()[0]
data.to_json('games_19_20.json')