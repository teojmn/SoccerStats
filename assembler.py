import pandas as pd
import os
from pathlib import Path

def load_csv_files():
    # Charge tous les fichiers CSV nécessaires

    scrape_data_dir = Path("ScrapeData")
    
    files_to_assemble = [
        "players_cleaned.csv",
        "defensive_cleaned.csv", 
        "gsc_cleaned.csv",
        "misc_cleaned.csv",
        "passing_cleaned.csv",
        "passing_types_cleaned.csv",
        "playing_time_cleaned.csv",
        "possession_cleaned.csv",
        "shooting_cleaned.csv"
    ]
    
    dataframes = {}
    
    print("Chargement des fichiers CSV...")
    for filename in files_to_assemble:
        filepath = scrape_data_dir / filename
        if filepath.exists():
            print(f"  - Chargement de {filename}")
            df = pd.read_csv(filepath)
            dataframes[filename] = df
            print(f"    Dimensions: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        else:
            print(f"  - ATTENTION: {filename} n'existe pas!")
    
    return dataframes

def identify_common_columns(dataframes):
    # Identifie les colonnes communes entre tous les dataframes

    if not dataframes:
        return set()
    
    first_df_name = list(dataframes.keys())[0]
    common_cols = set(dataframes[first_df_name].columns)
    
    for df_name, df in dataframes.items():
        common_cols = common_cols.intersection(set(df.columns))
    
    print(f"\nColonnes communes identifiées: {sorted(common_cols)}")
    return common_cols

def remove_goalkeepers(df):
    """
    Supprime les gardiens de but du dataframe
    """
    initial_count = len(df)
    df_filtered = df[df['Pos'] != 'GK'].copy()
    removed_count = initial_count - len(df_filtered)
    
    print(f"\nSuppression des gardiens de but...")
    print(f"  Joueurs supprimés: {removed_count}")
    print(f"  Joueurs restants: {len(df_filtered)}")
    
    return df_filtered

def assemble_data(dataframes):
    """
    Assemble tous les dataframes en utilisant Player, Born et Squad comme clés
    Cela permet de gérer les transferts de joueurs (même joueur dans plusieurs équipes)
    """
    if not dataframes:
        raise ValueError("Aucun dataframe à assembler")
    
    common_metadata_cols = ['Rk', 'Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', 'Born', 'Matches']
    main_df_name = "players_cleaned.csv"
    if main_df_name not in dataframes:
        main_df_name = list(dataframes.keys())[0]
    
    print(f"\nUtilisation de {main_df_name} comme dataframe principal")
    assembled_df = dataframes[main_df_name].copy()
    print(f"Dataframe principal: {assembled_df.shape[0]} lignes, {assembled_df.shape[1]} colonnes")
    
    main_keys = set(zip(assembled_df['Player'], assembled_df['Born'], assembled_df['Squad']))
    print(f"Clés uniques dans le dataframe principal (Player+Born+Squad): {len(main_keys)}")
    
    unique_players = assembled_df[['Player', 'Born']].drop_duplicates().shape[0]
    transfers = len(assembled_df) - unique_players
    print(f"Joueurs uniques: {unique_players}, Entrées de transferts: {transfers}")
    
    for df_name, df in dataframes.items():
        if df_name == main_df_name:
            continue
            
        print(f"\nAssemblage avec {df_name}...")
        
        required_cols = ['Player', 'Born', 'Squad']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"  ATTENTION: {df_name} ne contient pas les colonnes {missing_cols}, ignoré")
            continue
        
        df_unique_players = df[['Player', 'Born']].drop_duplicates().shape[0]
        df_transfers = len(df) - df_unique_players
        print(f"  Fichier: {len(df)} entrées, {df_unique_players} joueurs uniques, {df_transfers} transferts")
        
        # Vérifier les doublons exacts 
        df_exact_keys = set(zip(df['Player'], df['Born'], df['Squad']))
        exact_duplicates = len(df) - len(df_exact_keys)
        if exact_duplicates > 0:
            print(f"  ATTENTION: {df_name} contient {exact_duplicates} doublons exacts (même joueur+équipe)")
            # Garder seulement la première occurrence de chaque clé exacte
            df = df.drop_duplicates(subset=['Player', 'Born', 'Squad'], keep='first')
            print(f"  Après dédoublonnage: {df.shape[0]} lignes")
        
        cols_to_add = [col for col in df.columns if col not in common_metadata_cols]
        cols_to_merge = ['Player', 'Born', 'Squad'] + cols_to_add
        
        df_to_merge = df[cols_to_merge].copy()
        
        print(f"  Colonnes à ajouter: {len(cols_to_add)} colonnes")
        print(f"  Avant jointure: {assembled_df.shape}")
        
        assembled_df = assembled_df.merge(
            df_to_merge, 
            on=['Player', 'Born', 'Squad'], 
            how='left',
            suffixes=('', f'_{df_name.replace("_cleaned.csv", "")}')
        )
        
        print(f"  Après jointure: {assembled_df.shape}")
        
        # Vérification: le nombre de lignes ne devrait pas changer avec un left join
        if assembled_df.shape[0] != len(main_keys):

            print(f"  ATTENTION: Le nombre de lignes a changé de façon inattendue!")
            print(f"      Lignes attendues: {len(main_keys)}, Lignes obtenues: {assembled_df.shape[0]}")

    return assembled_df

def save_assembled_data(assembled_df, output_filename="assembled_data.csv"):
    # Sauvegarde le dataframe assemblé
    print(f"\nSauvegarde dans {output_filename}...")
    assembled_df.to_csv(output_filename, index=False)
    print(f"Fichier sauvegardé avec {assembled_df.shape[0]} lignes et {assembled_df.shape[1]} colonnes")


def main():
    """
    Fonction principale
    """
    print("ASSEMBLAGE DES DONNÉES DE FOOTBALL")
    print("="*50)
    
    try:
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        dataframes = load_csv_files()

        if not dataframes:
            print("Aucun fichier CSV trouvé à assembler!")
            return
        
        common_cols = identify_common_columns(dataframes)
        
        assembled_df = assemble_data(dataframes)
        
        # Supprimer les gardiens de but
        assembled_df = remove_goalkeepers(assembled_df)
        
        save_assembled_data(assembled_df)

        
    except Exception as e:
        print(f"\nErreur lors de l'assemblage: {str(e)}")
        raise

if __name__ == "__main__":
    main()