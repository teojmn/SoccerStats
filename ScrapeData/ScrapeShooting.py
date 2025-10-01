import pandas as pd

# URL de la page FBref
url = "https://fbref.com/en/comps/Big5/2023-2024/shooting/players/2023-2024-Big-5-European-Leagues-Stats"

shooting_df = pd.read_html(url, header=1)[0]

shooting_df = shooting_df.loc[:, ~shooting_df.columns.str.contains('^Unnamed')]

shooting_df = shooting_df[shooting_df['Player'] != 'Player']

shooting_df = shooting_df.reset_index(drop=True)

shooting_df.to_csv("shooting_cleaned.csv", index=False)