import pandas as pd

# URL de la page FBref
url = "https://fbref.com/en/comps/Big5/2023-2024/keepers/players/2023-2024-Big-5-European-Leagues-Stats"

keepers_df = pd.read_html(url, header=1)[0]

keepers_df = keepers_df.loc[:, ~keepers_df.columns.str.contains('^Unnamed')]

keepers_df = keepers_df[keepers_df['Player'] != 'Player']

keepers_df = keepers_df.reset_index(drop=True)

keepers_df.to_csv("keepers_cleaned.csv", index=False)