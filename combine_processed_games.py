import pandas as pd
import numpy as np
import json
games = pd.read_json('games_19_20.json')
games = np.unique(games['GAME_ID'])
stats_by_teams = {}

def combineStatsAgainst(team, game_stats):
    against_stats = {}
    result = {}
    for d in game_stats['stats'][team]:
        for k in game_stats['stats'][team][d].keys():
            if k not in ['lineup']:
                result[k] = result.get(k, 0) + game_stats['stats'][team][d][k]
    print(result)
    return result

def addToTeamStats(team, stats_for, stats_against):
    if not team in stats_by_teams:
        stats_by_teams[team] = {'for': {}, 'against':{}}
    for key in stats_for:
        stats_by_teams[team]['for'][key] = stats_by_teams[team]['for'].get(key, 0) + stats_for[key]
        stats_by_teams[team]['against'][key] = stats_by_teams[team]['against'].get(key, 0) + stats_against[key]
        print(stats_by_teams[team])




for game_id_1 in games:
    game_id = '00'+str(game_id_1)
    game_stats = {}
    json_file = open('./games/processed/'+str(game_id)+'.json')
    game_stats = json.load(json_file)
    json_file.close()
    home_team = game_stats['teams']['home']
    away_team = game_stats['teams']['away']
    home_stats = combineStatsAgainst('home', game_stats)
    away_stats = combineStatsAgainst('away', game_stats)
    addToTeamStats(home_team, home_stats, away_stats)
    addToTeamStats(away_team, away_stats, home_stats)

for key in stats_by_teams:
    with open('./games/processed_by_team/'+key+'.json', 'w') as fp:
        json.dump(stats_by_teams[key], fp)