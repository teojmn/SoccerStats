import pandas as pd

# URL de la page FBref
url = "https://fbref.com/en/comps/Big5/2023-2024/defense/players/2023-2024-Big-5-European-Leagues-Stats"

defense_df = pd.read_html(url, header=1)[0]

defense_df = defense_df.loc[:, ~defense_df.columns.str.contains('^Unnamed')]

defense_df = defense_df[defense_df['Player'] != 'Player']

defense_df = defense_df.reset_index(drop=True)

defense_df.to_csv("defensive_cleaned.csv", index=False)