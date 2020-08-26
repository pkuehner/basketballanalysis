import glob
import pandas as pd
import re

files = glob.glob("./games/regular/*.json")
awith = 0
mwith = 0
awithout = 0
mwithout = 0
gwith = 0
gwithout = 0

for file in files:
    df = pd.read_json(file)
    df = df[df['TEAM_ABBREVIATION'] == 'LAC']
    #print(df['MIN'])
    df = df[df['MIN'].str.contains('\d\d:\d\d', regex=True, na=False)]
    #print(df)
    if len(df) > 0:
        if len(df.loc[df['PLAYER_NAME'] == 'Paul George']) > 0:
            awith += df['FG3A'].sum()
            mwith += df['FG3M'].sum()
            gwith += 1
        else:
            awithout += df['FG3A'].sum()
            mwithout += df['FG3M'].sum()
            gwithout += 1

print(awith)
print(mwith)
print(gwith)
print()
print(awithout)
print(mwithout)
print(gwithout)


