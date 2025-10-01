import pandas as pd

# URL de la page FBref
url = "https://fbref.com/en/comps/Big5/2023-2024/playingtime/players/2023-2024-Big-5-European-Leagues-Stats"

playing_time_df = pd.read_html(url, header=1)[0]

playing_time_df = playing_time_df.loc[:, ~playing_time_df.columns.str.contains('^Unnamed')]

playing_time_df = playing_time_df[playing_time_df['Player'] != 'Player']

playing_time_df = playing_time_df.reset_index(drop=True)

playing_time_df.to_csv("playing_time_cleaned.csv", index=False)