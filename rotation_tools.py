import pandas as pd


def get_starters_by_period(game_rot, game_sum):
    rot_data = pd.read_json(game_rot)
    sum_data = pd.read_json(game_sum)
    home_id = sum_data.loc[0, 'HOME_TEAM_ID']
    visitor_id = sum_data.loc[0, 'VISITOR_TEAM_ID']
    lineups = {}
    for i in range(sum_data.loc[0, 'LIVE_PERIOD']):
        if i < 4:
            threshold = i*7200
        else:
            threshold = 4*7200+(i-4)*3000
        rot_data_1 = rot_data[rot_data['IN_TIME_REAL'] <= threshold]
        rot_data_1 = rot_data_1[rot_data_1['OUT_TIME_REAL'] > threshold]
        lineup_home = rot_data_1[rot_data_1['TEAM_ID']==home_id]
        lineup_away = rot_data_1[rot_data_1['TEAM_ID']==visitor_id]
        lineups[i] = {'home': lineup_home['PERSON_ID'].tolist(), 'away': lineup_away['PERSON_ID'].tolist()}
    return lineups
