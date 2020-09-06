import numpy as np
import json
import random
from nba_api.stats.static import players


def find_close_lineups(lineup_num, curr_team):
    lineup = lineups[curr_team][lineup_num]
    close_lineups = []
    for index, lineup2 in enumerate(lineups[curr_team]):
        sym_diff = set(lineup).symmetric_difference(lineup2)
        if len(sym_diff) == 2:
            close_lineups.append(index)
    return close_lineups


def calculate_percentage_for_substitution(lineup_num, curr_team):
    close_lineups = find_close_lineups(lineup_num, curr_team)
    all_min = 0
    for index in close_lineups:
        all_min += stats[curr_team][index]['min']
    percentages = {}
    for index in close_lineups:
        percentages[index] = stats[curr_team][index]['min'] / all_min
    return percentages


def calculate_percentage_for_possession(lineup_num, curr_team):
    columns = ['3pta', 'fta', 'tov', '2pta']
    percentages = {'3pta': 0, '2pta': 0, "tov": 0, 'fta': 0}
    if stats[curr_team][lineup_num]['poss'] != 0:
        for column in columns:
            percentages[column] += stats[curr_team][lineup_num][column] / stats[curr_team][lineup_num]['poss']
    percentages['fta'] /= 2
    return percentages


def calculate_shot_percentages(lineup_num, curr_team):
    columns = ['3pta', 'fta', '2pta']
    columns2 = ['3ptm', 'ftm', '2ptm']
    percentages = {'3pt': 0, '2pt': 0, 'ft': 0}
    for index, column in enumerate(columns):
        if stats[curr_team][lineup_num][column] != 0:
            percentages[column[:-1]] += stats[curr_team][lineup_num][columns2[index]] / stats[curr_team][lineup_num][
                column]
    return percentages


def calculate_percentage_for_reb(lineup_num, curr_team):
    shots = stats[curr_team][lineup_num]['poss'] - stats[curr_team][lineup_num]['tov']
    if shots != 0:
        percentages = {'o_reb': stats[curr_team][lineup_num]['o_reb'] / shots}
    else:
        percentages = {'o_reb': 0}
    return percentages

def print_lineup(lineup_num, curr_team):
    for player in lineups[curr_team][lineup_num]:
        print(players.find_player_by_id(player))

def change_lineup(lineup_num, curr_team):
    print(curr_team + ' exchanged to Lineup: ' + str(lineup_num))
    print_lineup(lineup_num, curr_team)
    curr_lineups[curr_team] = lineup_num
    sub_percentages[curr_team] = calculate_percentage_for_substitution(lineup_num, curr_team)
    shot_percentages[curr_team] = calculate_shot_percentages(lineup_num, curr_team)
    poss_percentages[curr_team] = calculate_percentage_for_possession(lineup_num, curr_team)
    reb_percentages[curr_team] = calculate_percentage_for_reb(lineup_num, curr_team)


def change_possession(curr_team):
    if curr_team == 'away':
        return 'home'
    else:
        return 'away'


with open('MIL.json') as json_file:
    stats = json.load(json_file)

curr_team = 'home'
if np.random.rand() <= 0.5:
    curr_team = 'away'
home_stats = stats['home']
away_stats = stats['away']
home_stats_list = [home_stats[x] for x in home_stats.keys()]
away_stats_list = [away_stats[x] for x in away_stats.keys()]
home_lineups = [x['lineup'] for x in home_stats_list]
away_lineups = [x['lineup'] for x in away_stats_list]
lineups = {
    'away': away_lineups,
    'home': home_lineups
}
stats = {
    'away': away_stats_list,
    'home': home_stats_list
}

home_stats_list = sorted(home_stats_list, key=lambda k: k['min'], reverse=True)
away_stats_list = sorted(away_stats_list, key=lambda k: k['min'], reverse=True)
calculate_percentage_for_substitution(2, 'home')
calculate_percentage_for_possession(2, 'home')
calculate_percentage_for_reb(2, 'home')
calculate_shot_percentages(2, 'home')

possessions = 0
curr_lineups = {'home': 0, 'away': 0}
sub_percentages = {'home': calculate_percentage_for_substitution(0, 'home'),
                   'away': calculate_percentage_for_substitution(0, 'away')}
poss_percentages = {'home': calculate_percentage_for_possession(0, 'home'),
                    'away': calculate_percentage_for_possession(0, 'away')}
shot_percentages = {'home': calculate_shot_percentages(0, 'home'), 'away': calculate_shot_percentages(0, 'away')}
reb_percentages = {'home': calculate_percentage_for_reb(0, 'home'), 'away': calculate_percentage_for_reb(0, 'away')}
sub_percentage = 0.1
scores = {'home': 0, 'away': 0}
while possessions != 225:
    possessions += 1
    x = np.random.rand()
    if x <= sub_percentage:
        options = sub_percentages[curr_team]
        x = np.random.rand()
        s = 0
        for key in options.keys():
            s += options[key]
            if x <= s:
                change_lineup(key, curr_team)
                break
        continue
    options = poss_percentages[curr_team]
    # print(poss_percentages)
    x = np.random.rand()
    s = 0
    for key in options.keys():
        s += options[key]
        if x <= s:
            if key == 'tov':
                print('tov by: ' + curr_team)
                curr_team = change_possession(curr_team)
            else:
                print(key + ' by: ' + curr_team)
                if np.random.rand() <= shot_percentages[curr_team][key[:-1]]:
                    print('Shot made')
                    if (key == '3pta'):
                        scores[curr_team] += 3
                    elif (key == '2pta'):
                        scores[curr_team] += 2
                    else:
                        scores[curr_team] += 1
                    print(scores)
                    curr_team = change_possession(curr_team)
                else:
                    if np.random.rand() <= reb_percentages[curr_team]['o_reb']:
                        print('Offensive Rebound by: ' + curr_team)
                    else:
                        curr_team = change_possession(curr_team)
                        print('Defensive Rebound by: ' + curr_team)
            break
