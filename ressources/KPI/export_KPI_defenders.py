# === Export KPI Défenseurs vers CSV ===

import pandas as pd
import numpy as np

# Chargement du fichier source (à adapter)
df = pd.read_csv("./ressources/normalized_data/assembled_data_DF_normalized.csv")

# Sélection des colonnes pertinentes
# Adapter ces noms selon ton CSV
cols = {
    "Player": "Nom du joueur",
    "Squad": "Équipe",
    "Pos": "Poste",
    "TklW_per_90": "Tacles réussis/90",
    "Int_per_90": "Interceptions/90",
    "Press_per_90": "Pressions/90",
    "Clr_per_90": "Dégagements/90",
    "Blocks_per_90": "Blocs/90",
    "Aerials_Won": "Duels aériens gagnés",
    "Aerials_Lost": "Duels aériens perdus",
    "Fls_per_90": "Fautes/90",
    "CrdY_per_90": "Cartons jaunes/90",
    "Err_to_Shot_per_90": "Erreurs menant à tir/90",
    "PrgP_per_90": "Passes progressives/90",
    "PrgC_per_90": "Conduites progressives/90",
    "Cmp_pct": "Précision passes (%)"
}

# Ne garder que les colonnes disponibles
available_cols = {k: v for k, v in cols.items() if k in df.columns}
df_export = df[list(available_cols.keys())].copy()
df_export.rename(columns=available_cols, inplace=True)

# Calculer le % de duels aériens gagnés si les colonnes existent
if {"Aerials_Won", "Aerials_Lost"}.issubset(df.columns):
    df_export["% Duels aériens gagnés"] = (
        df["Aerials_Won"] / (df["Aerials_Won"] + df["Aerials_Lost"])
    ).round(3) * 100

# Export vers CSV
output_path = "./ressources/KPI/defenders_KPI_export.csv"
df_export.to_csv(output_path, index=False)

print(f"KPI exportés vers : {output_path}")
