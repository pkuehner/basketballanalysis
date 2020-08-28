import pandas as pd
import json
import requests
from nba_api.stats.static import teams
from nba_api.stats.endpoints import boxscoreadvancedv2
from nba_api.stats.endpoints import boxscoreplayertrackv2
from nba_api.stats.endpoints import boxscoredefensive
from nba_api.stats.endpoints import playbyplayv2
from nba_api.stats.endpoints import boxscoresummaryv2

from eventTypes import eventTypes
from own_endpoints import get_rotation
import time
import numpy as np
from numpy import array
from scipy.cluster.vq import vq, kmeans2, whiten
import textprocessor
import rotation_tools

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
game = './games/playbyplay/0021900002.json'
game_sum = './games/summary/0021900002.json'
game_rot = './games/rotation/0021900002.json'

game_data = pd.read_json(game_sum)
home_team = teams.find_team_name_by_id(game_data.loc[0, 'HOME_TEAM_ID'])
away_team = teams.find_team_name_by_id(game_data.loc[0, 'VISITOR_TEAM_ID'])

pbp_data = pd.read_json(game)
x = {}
starters_by_period = rotation_tools.get_starters_by_period(game_rot, game_sum)
lineups = {'home': [], 'away': []}
possessions = {'home': {}, 'away': {}}
shots = {'home': {'2ptm': 0, '3ptm': 0, 'ftm': 0, '2pta': 0, '3pta': 0, 'fta': 0},
         'away': {'2ptm': 0, '3ptm': 0, 'ftm': 0, '2pta': 0, '3pta': 0, 'fta': 0}}
stats = {'home': {}, 'away': {}}
current_period = -1
old_game_time = 0
last_shot_team = 'neutral'
curr_team = 'neutral'
def handle_game_time(pcstring, period_change, period_is_ot):
    nums = pcstring.split(':')
    timeSec = int(nums[0])*60+int(nums[1])
    diff = old_game_time-timeSec
    if(period_change):
        constant_time = 720
        if period_is_ot:
            constant_time = 300
        stats['home'][str(lineups['home'])]['min'] += constant_time - timeSec
        stats['away'][str(lineups['away'])]['min'] += constant_time - timeSec
    else:
        stats['home'][str(lineups['home'])]['min'] += diff
        stats['away'][str(lineups['away'])]['min'] += diff
    return timeSec


def add_ast(playerId):
    stats[curr_team][str(lineups[curr_team])]['ast'] += 1

def add_lineup_to_stats():
    if not str(lineups[curr_team]) in stats[curr_team]:
        stats[curr_team][str(lineups[curr_team])] = {'lineup':lineups[curr_team], '2ptm': 0, '3ptm': 0, 'ftm': 0, '2pta': 0, '3pta': 0, 'fta': 0, 'poss': 0, 'tov': 0, 'ast': 0, 'foul_s':0, 'foul_reg':0, 'd_reb':0, 'o_reb':0, 'min': 0, 'subs': 0}
def add_possession():
    stats[curr_team][str(lineups[curr_team])]['poss'] += 1

def add_turnover():
    stats[curr_team][str(lineups[curr_team])]['tov'] += 1

def add_reb():
    reb_type = 'd_reb'
    if last_shot_team == curr_team:
        reb_type = 'o_reb'
    stats[curr_team][str(lineups[curr_team])][reb_type] += 1

def add_sub(new_lineup):
    stats[curr_team][str(lineups[curr_team])]['subs'] += 1


def add_foul(foul_type):
    if(foul_type == 'S'):
        stats[curr_team][str(lineups[curr_team])]['foul_s'] += 1
    elif('off' not in foul_type.lower()):
        stats[curr_team][str(lineups[curr_team])]['foul_reg'] += 1

def add_shot(made, typea, typem):
    stats[curr_team][str(lineups[curr_team])][typea] += 1
    if made:
        stats[curr_team][str(lineups[curr_team])][typem] += 1

for i in range(len(pbp_data['HOMEDESCRIPTION'])):
    current_period_new = pbp_data.loc[i, 'PERIOD'] - 1
    play_clock = pbp_data.loc[i, 'PCTIMESTRING']
    period_changed = current_period_new > current_period
    period_is_ot = current_period_new >= 5
    if period_changed:
        last_shot_team = 'neutral'
        current_period = current_period_new
        print('Period Start')
        lineups['home'] = sorted(starters_by_period[current_period]['home'])
        lineups['away'] = sorted(starters_by_period[current_period]['away'])
        curr_team = 'home'
        add_lineup_to_stats()
        curr_team = 'away'
        add_lineup_to_stats()
        curr_team = 'neutral'

    old_game_time = handle_game_time(play_clock, period_changed, period_is_ot)

    if pbp_data.loc[i, 'HOMEDESCRIPTION'] is not None:
        x['text'] = pbp_data.loc[i, 'HOMEDESCRIPTION']
        curr_team = 'home'
    elif pbp_data.loc[i, 'VISITORDESCRIPTION'] is not None:
        x['text'] = pbp_data.loc[i, 'VISITORDESCRIPTION']
        curr_team = 'away'
    else:
        x['text'] = ''
        continue
    event = tp.process_item(x)
    print(event)
    if event['type'] == eventTypes.SUB:
        playerOutId = pbp_data.loc[i, 'PLAYER1_ID']
        playerInId = pbp_data.loc[i, 'PLAYER2_ID']
        lineup_new = [x if x != playerOutId else int(playerInId) for x in lineups[curr_team]]
        add_sub(lineup_new)
        lineups[curr_team] = lineup_new
        add_lineup_to_stats()
    elif event['type'] == eventTypes.SHOT:
        last_shot_team = curr_team
        add_possession()
        if (event['3pa'] == 1):
            add_shot(event['shot_made'], '3pta', '3ptm')
        else:
            add_shot(event['shot_made'], '2pta', '2ptm')
        if (event['ast_player'] is not None):
            add_ast(pbp_data.loc[i, 'PLAYER2_ID'])
    elif event['type'] == eventTypes.FREE_THROW:
        last_shot_team = curr_team
        add_shot(event['shot_made'], 'fta', 'ftm')
        if (event['fta_ovr'] > 1 and event['fta_no'] == 1):
            if('technical' not in event['shot_type'].lower()):
                add_possession()


    elif event['type'] == eventTypes.TURNOVER or event['type'] == eventTypes.TEAM_TURNOVER:
        add_possession()
        add_turnover()
    elif event['type'] == eventTypes.FOUL:
        add_foul(event['foul_type'])
    elif event['type'] == eventTypes.REBOUND:
        add_reb()
        last_shot_team = 'neutral'
    elif event['type'] == eventTypes.TEAM_REBOUND:
        add_reb()
        last_shot_team = 'neutral'


print(stats)
secs = 0
for key in stats['away'].keys():
    secs+= stats['away'][key]['o_reb']
print(secs)
with open('test_game.json', 'w') as fp:
    json.dump(stats, fp)




