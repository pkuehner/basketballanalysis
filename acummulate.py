import glob
import pandas as pd
files = glob.glob("./games/defensive/*.json")
df = pd.read_json(files[0])
for file in files[1:]:
    data = pd.read_json(file)
    df = df.append(data)

print(df.columns)
print(df)
df = df.groupby(['PLAYER_ID', 'PLAYER_NAME']).sum().reset_index()
df.to_json('./games/cumulative/defense.json')