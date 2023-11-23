import requests
import pandas as pd

nba_data = requests.get("https://stats.nba.com/stats/playercareerstats")
nba_data_json = nba_data.json()
df = pd.DataFrame(nba_data_json)
print('A')
print(df.head(20))