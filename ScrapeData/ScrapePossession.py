import pandas as pd

# URL de la page FBref
url = "https://fbref.com/en/comps/Big5/2023-2024/possession/players/2023-2024-Big-5-European-Leagues-Stats"

possession_df = pd.read_html(url, header=1)[0]

possession_df = possession_df.loc[:, ~possession_df.columns.str.contains('^Unnamed')]

possession_df = possession_df[possession_df['Player'] != 'Player']

possession_df = possession_df.reset_index(drop=True)

possession_df.to_csv("possession_cleaned.csv", index=False)