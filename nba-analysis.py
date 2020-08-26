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
columns = ['E_OFF_RATING', 'OFF_RATING'
    , 'DEF_RATING'
    , 'NET_RATING'
    , 'AST_PCT', 'AST_TO', 'AST_RATIO', 'OREB_PCT',
           'DREB_PCT', 'E_TOV_PCT', 'EFG_PCT', 'TS_PCT',
           'USG_PCT', 'PACE',
             'FGM', 'FGA']
data = data[data['GP'] > 5]
data = data[data['MIN'] > 5]
player_names = data['PLAYER_NAME']
data = data[columns]
for column in columns:
    data[column] = data[column] / np.average(data[column])


centroids, labels = kmeans2(data.to_numpy(), k=50)
print(player_names)
labels_2 = {}
for index, label in enumerate(labels):
    if label in labels_2:
        labels_2[label].append(index)
    else:
        labels_2[label] = [index]
print(labels_2)

ct = 0
for cluster in labels_2:
    print('\nCluster: '+ str(ct))
    for index in labels_2[cluster]:
        print(player_names.iloc[index])
    ct+=1