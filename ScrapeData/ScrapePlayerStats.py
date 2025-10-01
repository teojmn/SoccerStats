import pandas as pd

# URL de la page FBref
url = "https://fbref.com/en/comps/Big5/2023-2024/stats/players/2023-2024-Big-5-European-Leagues-Stats"

players_df = pd.read_html(url, header=1)[0]

players_df = players_df.loc[:, ~players_df.columns.str.contains('^Unnamed')]

players_df = players_df[players_df['Player'] != 'Player']

players_df = players_df.reset_index(drop=True)

players_df.to_csv("players_cleaned.csv", index=False)