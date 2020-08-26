import requests
import json
import pandas as pd


def get_rotation(gameID):
    url = 'https://stats.nba.com/stats/gamerotation?GameID=' + gameID + '&LeagueID=00&RotationStat=PLAYER_PTS'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
        'Host': 'stats.nba.com',
        'Referer': 'https://stats.nba.com/game/' + gameID + '/rotations/', 'x-nba-stats-origin': 'stats'}
    # x-nba-stats-token: true}
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)['resultSets']
    headers = data[0]['headers']
    rows = data[0]['rowSet']
    rows1 = data[1]['rowSet']
    rows.extend(rows1)
    df = pd.DataFrame(rows, columns=headers)
    return df
