import pandas as pd

# URL de la page FBref
url = "https://fbref.com/en/comps/Big5/2023-2024/gca/players/2023-2024-Big-5-European-Leagues-Stats"

gsc_df = pd.read_html(url, header=1)[0]

gsc_df = gsc_df.loc[:, ~gsc_df.columns.str.contains('^Unnamed')]

gsc_df = gsc_df[gsc_df['Player'] != 'Player']

gsc_df = gsc_df.reset_index(drop=True)

gsc_df.to_csv("gsc_cleaned.csvæ", index=False)