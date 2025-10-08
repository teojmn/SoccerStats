import os
import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_and_prepare_data():
    """Charge et prépare toutes les données des 4 postes."""
    # Chemin vers ressources à partir de ce fichier
    base_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'ressources', 'normalized_data'))

    files = {
        'FW': 'assembled_data_FW_normalized.csv',
        'MF': 'assembled_data_MF_normalized.csv',
        'DF': 'assembled_data_DF_normalized.csv',
        'GK': 'keepers_enrichis_normalized.csv'
    }

    all_data = []
    for position, filename in files.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
            except Exception as e:
                st.warning(f"Impossible de lire {filename} : {e}")
                continue

            # Marquer le poste
            df['Position'] = position

            # Veiller à la présence de colonnes clés
            if 'Player' not in df.columns:
                df['Player'] = df.iloc[:, 0].astype(str)

            all_data.append(df)
        else:
            st.warning(f"Fichier non trouvé: {filepath}")

    if not all_data:
        st.error("Aucun fichier de données trouvé dans ressources/normalized_data.")
        return pd.DataFrame()

    # Concaténation
    data = pd.concat(all_data, ignore_index=True, sort=False)

    # Nettoyage et enrichissement
    data = clean_and_enrich_data(data)

    return data

def clean_and_enrich_data(data: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et enrichit les données."""
    df = data.copy()

    # Player -> string
    if 'Player' in df.columns:
        df['Player'] = df['Player'].astype(str)

    # Age numérique et tranches
    if 'Age' in df.columns:
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
        df['Age_Group'] = pd.cut(
            df['Age'],
            bins=[-1, 21, 25, 29, 200],
            labels=['U21', '22-25', '26-29', '30+'],
            include_lowest=True
        )

    # Normalisation des noms de ligues (si Comp présent)
    if 'Comp' in df.columns:
        league_mapping = {
            'eng Premier League': 'Premier League',
            'es La Liga': 'La Liga',
            'it Serie A': 'Serie A',
            'de Bundesliga': 'Bundesliga',
            'fr Ligue 1': 'Ligue 1'
        }
        df['League'] = df['Comp'].map(league_mapping).fillna(df['Comp'])
    else:
        df['League'] = np.nan

    # Extraction du code pays (Country) depuis 'Nation' si possible
    if 'Nation' in df.columns:
        # Cherche un code à 3 lettres (ex: ESP, FRA) sinon prend tout
        df['Country'] = df['Nation'].astype(str).str.extract(r'([A-Z]{3})', expand=False)
        # Si extraction vide, essayer d'extraire première partie (avant espace ou ,)
        missing_country = df['Country'].isna()
        if missing_country.any():
            df.loc[missing_country, 'Country'] = df.loc[missing_country, 'Nation'].astype(str).str.split().str[-1].str.upper()
    else:
        df['Country'] = np.nan

    # Min / 90s : harmonisation
    if 'Min' in df.columns and '90s' not in df.columns:
        # Si '90s' absent mais Min présent : créer 90s
        df['90s'] = pd.to_numeric(df['Min'], errors='coerce') / 90.0
    elif '90s' in df.columns and 'Min' not in df.columns:
        # Si Min absent mais 90s présent : créer Min
        df['90s'] = pd.to_numeric(df['90s'], errors='coerce')
        df['Min'] = df['90s'] * 90.0
    else:
        # Forcer types numériques si présents
        if 'Min' in df.columns:
            df['Min'] = pd.to_numeric(df['Min'], errors='coerce')
        if '90s' in df.columns:
            df['90s'] = pd.to_numeric(df['90s'], errors='coerce')

    # Experience binned using Min
    if 'Min' in df.columns:
        df['Experience'] = pd.cut(
            df['Min'],
            bins=[-1, 900, 1800, 2700, 1e9],
            labels=['Peu utilisé', 'Rotation', 'Titulaire', 'Indispensable'],
            include_lowest=True
        )

    # Filtrer joueurs avec trop peu de minutes (450 min = 5*90)
    if 'Min' in df.columns:
        df = df[df['Min'].fillna(0) >= 450]
    elif '90s' in df.columns:
        df = df[df['90s'].fillna(0) >= 5]

    # Nettoyage final : reset index
    df = df.reset_index(drop=True)

    return df

def calculate_percentiles(data: pd.DataFrame, position: str = None, league: str = None) -> pd.DataFrame:
    """Calcule les percentiles pour les métriques clés (_per_90)."""
    df = data.copy()

    if position:
        df = df[df['Position'] == position]
    if league:
        df = df[df['League'] == league]

    metric_cols = [col for col in df.columns if col.endswith('_per_90') and df[col].notna().sum() > 0]

    for col in metric_cols:
        # Percentile par colonne
        df[f'{col}_percentile'] = df[col].rank(pct=True, method='max') * 100

    return df

def get_position_metrics():
    """Retourne les métriques importantes par poste."""
    return {
        'FW': {
            'primary': ['Gls_per_90', 'SoT_per_90', 'xG_per_90'],
            'secondary': ['Ast_per_90', 'xAG_per_90', 'KP_per_90', 'PrgC_per_90'],
            'radar': ['Gls_per_90', 'SoT_per_90', 'xG_per_90', 'Ast_per_90', 'xAG_per_90', 'KP_per_90']
        },
        'MF': {
            'primary': ['KP_per_90', 'xAG_per_90', 'PrgP_per_90'],
            'secondary': ['Ast_per_90', 'PPA_per_90', 'Touches_per_90', 'Recov_per_90'],
            'radar': ['KP_per_90', 'xAG_per_90', 'PrgP_per_90', 'PPA_per_90', 'Touches_per_90', 'Recov_per_90']
        },
        'DF': {
            'primary': ['TklW_per_90', 'Int_per_90', 'Recov_per_90'],
            'secondary': ['PrgP_per_90', 'Clr_per_90', 'Won_per_90'],
            'radar': ['TklW_per_90', 'Int_per_90', 'Recov_per_90', 'PrgP_per_90', 'Clr_per_90']
        },
        'GK': {
            'primary': ['Saves_per_90', 'GA_per_90', 'Save%_per_90'],
            'secondary': ['PSxG_per_90', 'CS%_per_90'],
            'radar': ['Saves_per_90', 'Save%_per_90', 'PSxG_per_90', 'CS%_per_90']
        }
    }

def get_metric_labels():
    """Retourne les labels français pour les métriques."""
    return {
        'Gls_per_90': 'Buts/90',
        'SoT_per_90': 'Tirs cadrés/90',
        'xG_per_90': 'xG/90',
        'Ast_per_90': 'Passes D/90',
        'xAG_per_90': 'xAG/90',
        'KP_per_90': 'Passes clés/90',
        'PrgP_per_90': 'Passes prog./90',
        'PrgC_per_90': 'Courses prog./90',
        'PPA_per_90': 'Passes zone finale/90',
        'Touches_per_90': 'Touches/90',
        'TklW_per_90': 'Tacles réussis/90',
        'Int_per_90': 'Interceptions/90',
        'Recov_per_90': 'Récupérations/90',
        'Clr_per_90': 'Dégagements/90',
        'Won_per_90': 'Duels gagnés/90',
        'Saves_per_90': 'Arrêts/90',
        'GA_per_90': 'Buts encaissés/90',
        'Save%_per_90': '% Arrêts',
        'PSxG_per_90': 'PSxG/90',
        'CS%_per_90': '% Clean sheets'
    }