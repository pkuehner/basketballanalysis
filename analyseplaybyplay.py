import pandas as pd
import requests
from nba_api.stats.static import teams
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
import textprocessor

# Basic Request
import glob
tp = textprocessor.TextProcessor()
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
# files_reg = glob.glob("./games/summary/*.json")
# files_pbp = glob.glob("./games/playbyplay/*.json")
# for index, game in enumerate(files_pbp):
game = './games/playbyplay/0021900001.json'
game_sum = './games/summary/0021900001.json'
game_data = pd.read_json(game_sum)
home_team = teams.find_team_name_by_id(game_data.loc[0, 'HOME_TEAM_ID'])
away_team = teams.find_team_name_by_id(game_data.loc[0, 'VISITOR_TEAM_ID'])

pbp_data = pd.read_json(game)
x = {}
x['text']= pbp_data.loc[521,'HOMEDESCRIPTION']
print(tp.process_item(x))