import pandas as pd

keepers_df = pd.read_csv("./../ScrapeData/keepers_cleaned.csv")
goalieadv_df = pd.read_csv("./../ScrapeData/goalieadv_cleaned.csv")

new_columns = [col for col in goalieadv_df.columns if col not in keepers_df.columns]

merged_df = pd.merge(keepers_df, goalieadv_df[['Player'] + new_columns], on='Player', how='left')

if 'Matches' in merged_df.columns:
    merged_df = merged_df.drop(columns=['Matches'])

merged_df.to_csv("./../ressources/keepers_enrichis.csv", index=False)