import pandas as pd
import numpy as np
import streamlit as st
import os

@st.cache_data
def load_and_prepare_data():
    """Charge et prépare toutes les données des 4 postes."""
    
    # Chemins relatifs depuis le répertoire dashboard
    base_path = "../ressources/normalized_data/"
    
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
            df = pd.read_csv(filepath)
            df['Position'] = position
            all_data.append(df)
        else:
            st.warning(f"Fichier non trouvé: {filepath}")
    
    if not all_data:
        st.error("Aucun fichier de données trouvé!")
        return pd.DataFrame()
    
    # Concaténation
    data = pd.concat(all_data, ignore_index=True, sort=False)
    
    # Nettoyage et enrichissement
    data = clean_and_enrich_data(data)
    
    return data

def clean_and_enrich_data(data):
    """Nettoie et enrichit les données."""
    
    # Conversion de l'âge en numérique
    if 'Age' in data.columns:
        data['Age'] = pd.to_numeric(data['Age'], errors='coerce')
        
        # Création des tranches d'âge
        data['Age_Group'] = pd.cut(
            data['Age'], 
            bins=[0, 21, 25, 29, 50], 
            labels=['U21', '22-25', '26-29', '30+'],
            include_lowest=True
        )
    
    # Normalisation des noms de ligues
    if 'Comp' in data.columns:
        league_mapping = {
            'eng Premier League': 'Premier League',
            'es La Liga': 'La Liga', 
            'it Serie A': 'Serie A',
            'de Bundesliga': 'Bundesliga',
            'fr Ligue 1': 'Ligue 1'
        }
        data['League'] = data['Comp'].map(league_mapping).fillna(data['Comp'])
    
    # Extraction du pays (code à 3 lettres)
    if 'Nation' in data.columns:
        data['Country'] = data['Nation'].str.extract(r'([A-Z]{3})')
    
    # Calcul des 90s si pas déjà fait
    if 'Min' in data.columns and '90s' not in data.columns:
        data['90s'] = data['Min'] / 90
    elif '90s' in data.columns and 'Min' not in data.columns:
        data['Min'] = data['90s'] * 90
    
    # Classification par expérience
    if 'Min' in data.columns:
        data['Experience'] = pd.cut(
            data['Min'], 
            bins=[0, 900, 1800, 2700, float('inf')], 
            labels=['Peu utilisé', 'Rotation', 'Titulaire', 'Indispensable'],
            include_lowest=True
        )
    
    # Filtrage minimum 450 minutes (5 matchs complets)
    if 'Min' in data.columns:
        data = data[data['Min'] >= 450]
    
    return data

def calculate_percentiles(data, position=None, league=None):
    """Calcule les percentiles pour les métriques clés."""
    
    df = data.copy()
    
    # Filtrage selon position et ligue
    if position:
        df = df[df['Position'] == position]
    if league:
        df = df[df['League'] == league]
    
    # Colonnes métriques (celles qui finissent par _per_90)
    metric_cols = [col for col in df.columns if col.endswith('_per_90') and df[col].notna().sum() > 0]
    
    # Calcul des percentiles
    for col in metric_cols:
        df[f'{col}_percentile'] = df[col].rank(pct=True) * 100
    
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