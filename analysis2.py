import pandas as pd
import requests
from nba_api.stats.endpoints import leaguedashplayerstats
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
data = leaguedashplayerstats.LeagueDashPlayerStats(per_mode_detailed='Per36', measure_type_detailed_defense='Advanced',
                                                   timeout=10);
data = data.get_data_frames()[0]
columns = ['OFF_RATING'
    , 'DEF_RATING'
             , 'NET_RATING'
    , 'AST_PCT', 'AST_TO', 'AST_RATIO', 'OREB_PCT',
           'DREB_PCT', 'EFG_PCT', 'TS_PCT', 'FGM',

           ]
data = data[data['GP'] > 15]
data = data[data['MIN'] > 10]
player_names = data['PLAYER_NAME']
data = data[columns]
for column in columns:
    data[column] = data[column] / np.abs(np.average(data[column]))

data['DEF_RATING'] = 1 / data['DEF_RATING']
data["sum"] = data.sum(axis=1)
data['names'] = player_names
data = data.sort_values(by=['sum'])
print(data.tail(20))
