import pandas as pd

# URL de la page FBref
url = "https://fbref.com/en/comps/Big5/2023-2024/misc/players/2023-2024-Big-5-European-Leagues-Stats"

misc_df = pd.read_html(url, header=1)[0]

misc_df = misc_df.loc[:, ~misc_df.columns.str.contains('^Unnamed')]

misc_df = misc_df[misc_df['Player'] != 'Player']

misc_df = misc_df.reset_index(drop=True)

misc_df.to_csv("misc_cleaned.csv", index=False)