import pandas as pd
from pathlib import Path
import sys
import numpy as np

DEFAULT_KEYS = ['Player', 'Born', 'Squad']
META_COLS = ['Rk', 'Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', 'Born', 'Matches']

# Colonnes communes à tous les postes
COMMON_COLS = [
    'Rk', 'Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', 'Born', 'MainPos',
    'MP', 'Starts', 'Min', '90s', 'CrdY', 'CrdR'
]

# Colonnes pertinentes pour les Défenseurs
DEFENDER_COLS = COMMON_COLS + [

    'Tkl', 'TklW', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Tkl%', 
    'Blocks', 'Int', 'Tkl+Int', 'Clr', 'Err',
    
    'Won', 'Lost_misc', 'Won%',
    
    'Cmp', 'Att_passing', 'Cmp%', 'TotDist', 'PrgDist',
    'PrgP', 'PrgP_passing', 'KP', '1/3', 'PPA',

    'Touches', 'Def Pen', 'Def 3rd_possession', 'Mid 3rd_possession',
    'Carries', 'PrgC', 'PrgDist_possession',
    
    'Ast', 'xAG', 'xA', 'A-xAG',
    
    'Recov',
    
    'Fls', 'Fld',
    
    'Min%', 'Compl', 'Subs', 'PPM', 'onG', 'onGA', '+/-', '+/-90'
]

# Colonnes pertinentes pour les Milieux de terrain
MIDFIELDER_COLS = COMMON_COLS + [

    'Cmp', 'Att_passing', 'Cmp%', 'TotDist', 'PrgDist',
    'KP', '1/3', 'PPA', 'CrsPA', 'PrgP', 'PrgP_passing',
    'Ast', 'xAG', 'xA', 'A-xAG',
    
    'Live', 'Dead', 'FK', 'TB', 'Sw', 'Crs', 'TI', 'CK',
    
    'Touches', 'Mid 3rd_possession', 'Att 3rd_possession',
    'Att_possession', 'Succ', 'Succ%', 'Tkld', 'Tkld%',
    'Carries', 'TotDist_possession', 'PrgDist_possession', 
    'PrgC', 'PrgC_possession', 'CPA', 'Rec', 'PrgR',
    
    'Tkl', 'TklW', 'Mid 3rd', 'Int', 'Tkl+Int', 'Recov',
    
    'Gls', 'Sh_shooting', 'SoT', 'SoT%', 'Sh/90', 'SoT/90',
    'xG', 'npxG', 'G-xG', 'np:G-xG',
    
    'Won', 'Lost_misc', 'Won%',
    
    'Fls', 'Fld',
    
    'Min%', 'Compl', 'Subs', 'PPM', 'onG', 'onGA', '+/-', '+/-90',
    'onxG', 'onxGA', 'xG+/-', 'xG+/-90'
]

# Colonnes pertinentes pour les Attaquants
FORWARD_COLS = COMMON_COLS + [

    'Gls', 'Sh_shooting', 'SoT', 'SoT%', 'Sh/90', 'SoT/90',
    'G/Sh', 'G/SoT', 'Dist', 'FK_shooting',
    'xG', 'npxG', 'xG_shooting', 'npxG_shooting', 'npxG/Sh',
    'G-xG', 'np:G-xG', 'PK', 'PKatt',
    
    'Ast', 'KP', 'xAG', 'xA', 'A-xAG', 'PPA', 'CrsPA',
    
    'Touches', 'Att 3rd_possession', 'Att Pen',
    'Att_possession', 'Succ', 'Succ%', 'Tkld', 'Tkld%',
    'Carries', 'PrgC', 'PrgDist_possession', 'CPA', 'Mis', 'Dis',
    
    'PrgR', 'PrgC_possession', '1/3_possession',
    
    'Cmp', 'Att_passing', 'Cmp%', 'PrgP',
    
    'Fls', 'Fld', 'Recov',
    
    'Won', 'Lost_misc', 'Won%',
    
    'Min%', 'Compl', 'Subs', 'PPM', 'onG', 'onGA', '+/-', '+/-90',
    'onxG', 'onxGA', 'xG+/-', 'xG+/-90'
]

def load_csv_files(data_dir=".", files=None, verbose=True):
    if files is None:
        files = [
            "players_cleaned.csv",
            "defensive_cleaned.csv", 
            "misc_cleaned.csv",
            "passing_cleaned.csv",
            "passing_types_cleaned.csv",
            "playing_time_cleaned.csv",
            "possession_cleaned.csv",
            "shooting_cleaned.csv"
        ]
    
    dataframes = {}
    data_path = Path(data_dir)
    
    for filename in files:
        filepath = data_path / filename
        try:
            if verbose: 
                print(f"  - Chargement de {filename}")
            df = pd.read_csv(filepath)
            dataframes[filename] = df
            if verbose: 
                print(f"    {df.shape[0]} lignes, {df.shape[1]} colonnes")
        except FileNotFoundError:
            if verbose: 
                print(f"  - ATTENTION: {filepath} n'existe pas!")
    
    return dataframes

def remove_goalkeepers(df, pos_col='Pos', verbose=True):
    if pos_col not in df.columns:
        if verbose: 
            print(f"Colonne {pos_col} absente, pas de suppression GK.")
        return df
    
    initial = len(df)
    df = df[~df[pos_col].str.startswith('GK', na=False)].copy()
    
    if verbose:
        print(f"Suppression GK: {initial-len(df)} supprimés, {len(df)} restants")
    
    return df

def assemble_data(dataframes, keys=DEFAULT_KEYS, meta_cols=META_COLS, verbose=True):
    """Assemble tous les dataframes en un seul"""
    if not dataframes:
        raise ValueError("Vérifier chemin des fichiers.")
    
    main_name = "players_cleaned.csv"
    
    if main_name not in dataframes:
        main_name = list(dataframes.keys())[0]
    
    main = dataframes[main_name].copy()
    if verbose: 
        print(f"\nDataframe principal: {main_name} ({main.shape})")
    
    for fname, df in dataframes.items():
        if fname == main_name: 
            continue
        
        missing = [k for k in keys if k not in df.columns]
        if missing:
            if verbose: 
                print(f"  {fname} ignoré (manque {missing})")
            continue
        
        before = len(df)
        df = df.drop_duplicates(subset=keys, keep='first')
        if verbose and before != len(df):
            print(f"  {fname}: {before-len(df)} doublons supprimés")
        
        add_cols = [c for c in df.columns if c not in meta_cols]
        merge_cols = keys + add_cols
        
        main = main.merge(
            df[merge_cols], 
            on=keys, 
            how='left', 
            suffixes=('', f'_{fname.replace("_cleaned.csv", "")}')
        )
        
        if verbose: 
            print(f"{fname} fusionné → {main.shape}")
    
    return main

def extract_main_position(df, pos_col='Pos', verbose=True):
    df['MainPos'] = df[pos_col].str.split(',').str[0].str.strip()
    
    if verbose:
        print(f"\n=== Distribution des postes principaux ===")
        print(df['MainPos'].value_counts())
    
    return df

def aggregate_transfers(df, verbose=True):
    sum_cols = [
        'MP', 'Starts', 'Min', 'Gls', 'Ast', 'G+A', 'G-PK', 'PK', 'PKatt', 'CrdY', 'CrdR', 'Matches'
    ]
    mean_cols = [
        'Min%', 'PPM', '+/-90', 'Sh/90', 'SoT/90', 'Cmp%', 'Won%', 'Succ%', 'Tkld%', 'SoT%', 'G/Sh', 'G/SoT'
    ]

    id_cols = ['Player', 'Born', 'Age']

    df = df.sort_values(by=['Player', 'Born', 'Age', 'Squad', 'Comp'])
    last_rows = df.groupby(id_cols, as_index=False).last()
    sum_df = df.groupby(id_cols)[[col for col in sum_cols if col in df.columns]].sum(min_count=1).reset_index()
    mean_df = df.groupby(id_cols)[[col for col in mean_cols if col in df.columns]].mean().reset_index()

    merged = last_rows.drop(columns=[col for col in sum_cols + mean_cols if col in last_rows.columns], errors='ignore') \
        .merge(sum_df, on=id_cols, how='left') \
        .merge(mean_df, on=id_cols, how='left')

    if verbose:
        n_avant = len(df)
        n_apres = len(merged)
        print(f"\n[Transferts] Joueurs avant fusion : {n_avant}, après fusion : {n_apres}")

    return merged

def filter_relevant_columns(df, position, verbose=True):
    if position == 'DF':
        relevant_cols = DEFENDER_COLS
        position_name = "Défenseurs"
    elif position == 'MF':
        relevant_cols = MIDFIELDER_COLS
        position_name = "Milieux"
    elif position == 'FW':
        relevant_cols = FORWARD_COLS
        position_name = "Attaquants"
    else:
        return df
    
    available_cols = [col for col in relevant_cols if col in df.columns]
    missing_cols = [col for col in relevant_cols if col not in df.columns]
    
    if verbose and missing_cols:
        print(f"{position_name} - Colonnes manquantes ({len(missing_cols)}) : {missing_cols[:5]}...")
    
    df_filtered = df[available_cols].copy()
    
    if verbose:
        print(f"{position_name} : {len(available_cols)} colonnes pertinentes conservées (sur {len(df.columns)} totales)")
    
    return df_filtered

def split_by_position(df, verbose=True):
    df_DF = df[df['MainPos'] == 'DF'].copy()
    df_MF = df[df['MainPos'] == 'MF'].copy()
    df_FW = df[df['MainPos'] == 'FW'].copy()
    
    if verbose:
        print(f"\n=== Répartition par poste ===")
        print(f"  Défenseurs (DF) : {len(df_DF)} joueurs")
        print(f"  Milieux (MF)    : {len(df_MF)} joueurs")
        print(f"  Attaquants (FW) : {len(df_FW)} joueurs")
        print(f"  TOTAL           : {len(df_DF) + len(df_MF) + len(df_FW)} joueurs")
        
        total_classified = len(df_DF) + len(df_MF) + len(df_FW)
        if total_classified < len(df):
            unclassified = len(df) - total_classified
            print(f"Non classés  : {unclassified} joueurs")
    
    return df_DF, df_MF, df_FW

def save_position_files(df_DF, df_MF, df_FW, output_dir=".", verbose=True):
    """Sauvegarde les 3 fichiers par poste"""
    files_saved = []
    output_path = Path(output_dir)
    
    file_DF = output_path / 'assembled_data_DF.csv'
    df_DF.to_csv(file_DF, index=False)
    files_saved.append((file_DF.name, len(df_DF), df_DF.shape[1]))
    
    file_MF = output_path / 'assembled_data_MF.csv'
    df_MF.to_csv(file_MF, index=False)
    files_saved.append((file_MF.name, len(df_MF), df_MF.shape[1]))
    
    file_FW = output_path / 'assembled_data_FW.csv'
    df_FW.to_csv(file_FW, index=False)
    files_saved.append((file_FW.name, len(df_FW), df_FW.shape[1]))
    
    if verbose:
        print(f"\n=== Fichiers générés ===")
        for fname, rows, cols in files_saved:
            print(f"{fname} : {rows} lignes × {cols} colonnes")
    
    return files_saved

def main():
    print("=" * 60)
    print("ASSEMBLAGE DES DONNÉES PAR POSTE (v2)")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = "."
    
    print(f"Répertoire des données : {Path(data_dir).absolute()}")
    
    print("\n[1/6] Chargement des fichiers CSV...")
    dataframes = load_csv_files(data_dir=data_dir)
    
    if not dataframes:
        print("ERREUR : Aucun fichier CSV trouvé.")
        print("Usage :")
        print(f"python3 {sys.argv[0]} [chemin_vers_dossier_csv]")
        print(f"Exemple : python3 {sys.argv[0]} ./data")
        print(f"Exemple : python3 {sys.argv[0]} .")
        sys.exit(1)
    
    print("\n[2/6] Assemblage des données...")
    assembled = assemble_data(dataframes)
    
    print("\n[3/6] Suppression des gardiens...")
    assembled = remove_goalkeepers(assembled)
    
    print("\n[4/6] Gestion des transferts (fusion des lignes multi-clubs)...")
    assembled = aggregate_transfers(assembled)
    
    print("\n[5/6] Extraction du poste principal...")
    assembled = extract_main_position(assembled)
    
    df_DF, df_MF, df_FW = split_by_position(assembled)
    
    print("\n[6/6] Filtrage des colonnes pertinentes par poste...")
    df_DF = filter_relevant_columns(df_DF, 'DF', verbose=True)
    df_MF = filter_relevant_columns(df_MF, 'MF', verbose=True)
    df_FW = filter_relevant_columns(df_FW, 'FW', verbose=True)
    
    print("\n[Sauvegarde] Création du dossier ./ressources/cleaned_data si besoin...")
    Path("./ressources/cleaned_data").mkdir(parents=True, exist_ok=True)
    save_position_files(df_DF, df_MF, df_FW, output_dir="./ressources/cleaned_data")
    
    print("\n" + "=" * 60)
    print("ASSEMBLAGE TERMINÉ AVEC SUCCÈS")
    print("=" * 60)

if __name__ == "__main__":
    main()