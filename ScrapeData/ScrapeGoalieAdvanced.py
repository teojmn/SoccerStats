import pandas as pd

# URL de la page FBref
url = "https://fbref.com/en/comps/Big5/2023-2024/keepersadv/players/2023-2024-Big-5-European-Leagues-Stats"

goalieadv_df = pd.read_html(url, header=1)[0]

goalieadv_df = goalieadv_df.loc[:, ~goalieadv_df.columns.str.contains('^Unnamed')]

goalieadv_df = goalieadv_df[goalieadv_df['Player'] != 'Player']

goalieadv_df = goalieadv_df.reset_index(drop=True)

goalieadv_df.to_csv("goalieadv_cleaned.csv", index=False)