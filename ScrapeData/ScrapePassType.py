import pandas as pd

# URL de la page FBref
url = "https://fbref.com/en/comps/Big5/2023-2024/passing_types/players/2023-2024-Big-5-European-Leagues-Stats"

passtype_df = pd.read_html(url, header=1)[0]

passtype_df = passtype_df.loc[:, ~passtype_df.columns.str.contains('^Unnamed')]

passtype_df = passtype_df[passtype_df['Player'] != 'Player']

passtype_df = passtype_df.reset_index(drop=True)

passtype_df.to_csv("passing_types_cleaned.csv", index=False)