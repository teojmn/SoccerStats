import pandas as pd

def normalize_stats(df, min_col='Min', exclude_cols=None):
    if exclude_cols is None:
        exclude_cols = ['Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', 'Born', 'MP', 'Starts', '90s']

    df = df[df[min_col] > 180].copy()

    numeric_cols = df.select_dtypes(include='number').columns
    target_cols = [col for col in numeric_cols if col not in exclude_cols and col != min_col]
    
    for col in target_cols:
        df[f'{col}_per_90'] = df[col] / df[min_col] * 90
    
    return df

df_def = pd.read_csv('./ressources/cleaned_data/assembled_data_DF.csv')
df_mid = pd.read_csv('./ressources/cleaned_data/assembled_data_MF.csv')
df_fw = pd.read_csv('./ressources/cleaned_data/assembled_data_FW.csv')
df_gk = pd.read_csv('./ressources/cleaned_data/keepers_enrichis.csv')

df_def_norm = normalize_stats(df_def)
df_mid_norm = normalize_stats(df_mid)
df_fw_norm = normalize_stats(df_fw)
df_gk_norm = normalize_stats(df_gk)

df_def_norm.to_csv('./ressources/normalized_data/assembled_data_DF_normalized.csv', index=False)
df_mid_norm.to_csv('./ressources/normalized_data/assembled_data_MF_normalized.csv', index=False)
df_fw_norm.to_csv('./ressources/normalized_data/assembled_data_FW_normalized.csv', index=False)
df_gk_norm.to_csv('./ressources/normalized_data/keepers_enrichis_normalized.csv', index=False)