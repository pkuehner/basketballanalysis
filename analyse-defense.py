import glob
import pandas as pd

df = pd.read_json('./games/cumulative/defense.json')
df = df.sort_values(by=['MATCHUP_FG3A'], ascending=False)
print(df.loc[:, ['PLAYER_NAME','MATCHUP_FG3A']])