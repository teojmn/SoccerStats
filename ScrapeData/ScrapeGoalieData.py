import pandas as pd

url = "https://fbref.com/en/comps/Big5/2023-2024/keepers/players/2023-2024-Big-5-European-Leagues-Stats"

tables = pd.read_html(url, header=1)

keepers_df = tables[0]

keepers_df = keepers_df.loc[:, ~keepers_df.columns.str.contains('^Unnamed')]

keepers_df.to_csv("keepers_cleaned.csv", index=False)