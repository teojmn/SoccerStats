import pandas as pd

# URL de la page FBref
url = "https://fbref.com/en/comps/Big5/2023-2024/passing/players/2023-2024-Big-5-European-Leagues-Stats"

passing_df = pd.read_html(url, header=1)[0]

passing_df = passing_df.loc[:, ~passing_df.columns.str.contains('^Unnamed')]

passing_df = passing_df[passing_df['Player'] != 'Player']

passing_df = passing_df.reset_index(drop=True)

passing_df.to_csv("passing_cleaned.csv", index=False)