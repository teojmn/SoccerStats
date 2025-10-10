import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from data.loader import (
    load_and_prepare_data, 
    calculate_percentiles, 
    get_position_metrics, 
    get_metric_labels,
    load_kpi_natural_names,
    get_natural_name
)

# Configuration
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Couleurs
POSITION_COLORS = {
    'FW': '#e74c3c',
    'MF': '#2ecc71', 
    'DF': '#3498db',
    'GK': '#f39c12'
}

LEAGUE_COLORS = {
    'Premier League': '#37003c',
    'La Liga': '#ff6600',
    'Serie A': '#004c99',
    'Bundesliga': '#d20515',
    'Ligue 1': '#083c7c'
}

# CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: white;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    .kpi-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        text-align: center;
    }
    .kpi-container h3 {
        color: #007bff;
        margin: 0;
        font-size: 2rem;
    }
    .kpi-container p {
        margin: 0.5rem 0 0 0;
        color: #6c757d;
    }
    

</style>
""", unsafe_allow_html=True)

# Fonction helper pour formatter les noms de métriques
def format_metric_name(metric_name, natural_names_map=None):
    """Retourne le nom naturel d'une métrique avec fallback sur le nom technique."""
    if natural_names_map is None:
        # Charger depuis get_metric_labels qui inclut maintenant les natural_names
        metric_labels = get_metric_labels()
        return metric_labels.get(metric_name, metric_name)
    return natural_names_map.get(metric_name, metric_name)

# Fonctions graphiques
def create_scatter_plot(data, x_col, y_col, color_col='Position', size_col=None, title="Scatter Plot"):
    """Crée un scatter plot interactif."""
    color_map = POSITION_COLORS if color_col == 'Position' else LEAGUE_COLORS
    
    fig = px.scatter(
        data, 
        x=x_col, 
        y=y_col,
        color=color_col,
        size=size_col,
        hover_data=['Player', 'Squad', 'League'],
        title=title,
        color_discrete_map=color_map
    )
    
    fig.update_layout(
        hovermode='closest',
        showlegend=True,
        height=600
    )
    
    return fig

def create_bar_chart(data, x_col, y_col, color_col=None, title="Bar Chart"):
    if color_col:
        color_map = POSITION_COLORS if color_col == 'Position' else LEAGUE_COLORS
        fig = px.bar(data, x=x_col, y=y_col, color=color_col, title=title, color_discrete_map=color_map)
    else:
        fig = px.bar(data, x=x_col, y=y_col, title=title)
    
    fig.update_layout(height=500)
    return fig

def create_radar_chart(data, player_names, position):
    position_metrics = get_position_metrics()
    metric_labels = get_metric_labels()
    
    metrics = position_metrics.get(position, {}).get('radar', [])
    if not metrics:
        return go.Figure()
    
    fig = go.Figure()
    
    pos_data = data[data['Position'] == position]
    colors = ['#e74c3c', '#2ecc71', '#3498db', '#f39c12', '#9b59b6']
    
    # Calculer min/max pour chaque métrique pour la normalisation
    metrics_ranges = {}
    for metric in metrics:
        if metric in pos_data.columns and pos_data[metric].notna().sum() > 0:
            metrics_ranges[metric] = {
                'min': pos_data[metric].min(),
                'max': pos_data[metric].max()
            }
    
    for i, player_name in enumerate(player_names):
        player_data = pos_data[pos_data['Player'] == player_name]
        
        if player_data.empty:
            continue
            
        values = []
        labels = []
        hover_texts = []
        
        for metric in metrics:
            if metric in player_data.columns and player_data[metric].notna().any():
                value = player_data[metric].iloc[0]
                
                # Normaliser la valeur entre 0 et 100 pour l'affichage radar
                if metric in metrics_ranges:
                    min_val = metrics_ranges[metric]['min']
                    max_val = metrics_ranges[metric]['max']
                    if max_val > min_val:
                        normalized_value = ((value - min_val) / (max_val - min_val)) * 100
                    else:
                        normalized_value = 50
                    
                    values.append(normalized_value)
                    labels.append(metric_labels.get(metric, metric))
                    # Ajouter la valeur réelle au hover
                    hover_texts.append(f"{value:.2f}")
        
        if values:
            # Fermer le radar
            values.append(values[0])
            labels.append(labels[0])
            hover_texts.append(hover_texts[0])
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=labels,
                fill='toself',
                name=player_name,
                line_color=colors[i % len(colors)],
                text=hover_texts,
                hovertemplate='<b>%{theta}</b><br>Valeur: %{text}<br><extra></extra>'
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title=f"Profil {position} (Normalisé 0-100)",
        height=600
    )
    
    return fig

# Fonctions pour les filtres
def create_sidebar_filters(data):
    """Crée les filtres dans la sidebar."""
    st.sidebar.header("Filtres")
    
    filters = {}
    
    # Filtre Position
    if 'Position' in data.columns:
        positions = st.sidebar.multiselect(
            "Position",
            options=sorted(data['Position'].unique()),
            default=sorted(data['Position'].unique())
        )
        filters['positions'] = positions
    
    # Filtre Ligue
    if 'League' in data.columns:
        leagues = st.sidebar.multiselect(
            "Ligue",
            options=sorted(data['League'].unique()),
            default=sorted(data['League'].unique())
        )
        filters['leagues'] = leagues
    
    # Filtre Âge
    if 'Age' in data.columns:
        age_range = st.sidebar.slider(
            "Tranche d'âge",
            min_value=int(data['Age'].min()),
            max_value=int(data['Age'].max()),
            value=(int(data['Age'].min()), int(data['Age'].max()))
        )
        filters['age_range'] = age_range
    
    # Filtre Nationalité -> utiliser 'Nation' uniquement
    if 'Nation' in data.columns and data['Nation'].notna().any():
        nation_values = [str(v) for v in data['Nation'].dropna().unique()]
        selected = st.sidebar.multiselect(
            "Nationalité",
            options=sorted(nation_values),
            default=sorted(nation_values)
        )
        filters['nations'] = {'col': 'Nation', 'values': selected}
    
    return filters

def apply_filters(data, filters):
    """Applique les filtres aux données."""
    df = data.copy()
    
    if 'positions' in filters and filters['positions']:
        df = df[df['Position'].isin(filters['positions'])]
    
    if 'leagues' in filters and filters['leagues']:
        df = df[df['League'].isin(filters['leagues'])]
    
    if 'age_range' in filters and 'Age' in df.columns:
        min_age, max_age = filters['age_range']
        df = df[(df['Age'] >= min_age) & (df['Age'] <= max_age)]
    
    # Si tu veux un filtre minutes (ajoute slider dans create_sidebar_filters)
    if 'min_minutes' in filters and 'Min' in df.columns:
        df = df[df['Min'] >= filters['min_minutes']]
    
    # Application du filtre Nationalité : filtrer simplement par inclusion
    if 'nations' in filters and filters['nations']:
        nat = filters['nations']
        col = nat.get('col')
        vals = nat.get('values', [])
        if col and vals:
            df = df[df[col].isin(vals)]
    
    return df

# Tabs
def show_overview(data):
    """Page vue d'ensemble."""
    st.header("Vue d'ensemble")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Répartition par ligue")
        
        if 'League' in data.columns:
            league_stats = data.groupby('League').agg({
                'Player': 'count',
                'Age': 'mean',
                'Min': 'mean' if 'Min' in data.columns else 'count'
            }).round(1)
            league_stats.columns = ['Joueurs', 'Âge moyen', 'Minutes moyennes']
            
            fig_leagues = create_bar_chart(
                league_stats.reset_index(),
                x_col='League',
                y_col='Joueurs',
                title="Nombre de joueurs par ligue"
            )
            st.plotly_chart(fig_leagues, use_container_width=True)
    
    with col2:
        st.subheader("Top 10 nationalités")
        
        # Choisir la colonne disponible pour la nationalité
        if 'Country' in data.columns and data['Country'].notna().any():
            col = 'Country'
        elif 'Nation' in data.columns and data['Nation'].notna().any():
            col = 'Nation'
        else:
            col = None
        
        if col:
            top_countries = data[col].dropna().astype(str).value_counts().head(10)
            df_countries = top_countries.reset_index()
            df_countries.columns = ['Nation', 'Count']
            fig_countries = create_bar_chart(
                df_countries,
                x_col='Nation',
                y_col='Count',
                title="Joueurs par nationalité"
            )
            st.plotly_chart(fig_countries, use_container_width=True)
    
    # Récupérer tous les postes disponibles
    positions = sorted(data['Position'].unique())
    
    # Créer autant de colonnes que de postes (max 4 par ligne)
    positions_per_row = 4
    
    for i in range(0, len(positions), positions_per_row):
        cols = st.columns(min(positions_per_row, len(positions) - i))
        
        for j, col in enumerate(cols):
            if i + j < len(positions):
                pos = positions[i + j]
                
                with col:
                    
                    pos_label = {
                        'FW': 'Attaquants',
                        'MF': 'Milieux',
                        'DF': 'Défenseurs',
                        'GK': 'Gardiens'
                    }

                    st.markdown(f"Top 5 {pos_label.get(pos, pos)}")

                    # Filtrer par poste
                    pos_data = data[data['Position'] == pos]
                    
                    # Choisir la métrique principale selon le poste
                    position_metrics = get_position_metrics()
                    
                    if pos in position_metrics and position_metrics[pos]['primary']:
                        main_metric = position_metrics[pos]['primary'][0]
                        
                        if main_metric in pos_data.columns:
                            top_players = pos_data.nlargest(5, main_metric)[['Player', 'Squad', main_metric]]
                            top_players[main_metric] = top_players[main_metric].round(2)
                            
                            # Renommer la colonne métrique pour plus de clarté
                            metric_labels = get_metric_labels()
                            top_players = top_players.rename(columns={
                                main_metric: metric_labels.get(main_metric, main_metric)
                            })
                            
                            st.dataframe(top_players, hide_index=True, use_container_width=True, height=220)
                        else:
                            st.info(f"Métrique {main_metric} non disponible")
                    else:
                        st.info("Pas de métrique définie pour ce poste")


def show_by_position(data):
    """Page analyse par poste."""
    st.header("⚽ Analyse par poste")
    
    # Sélection du poste
    positions = data['Position'].unique()
    selected_position = st.selectbox("Choisir un poste", positions)
    
    pos_data = data[data['Position'] == selected_position]
    position_metrics = get_position_metrics()
    # Labels spécifiques pour l'onglet "Analyse par poste"
    # (définis ici pour garder le contrôle du texte affiché dans ce tab)
    metric_labels = {
        'Gls_per_90': 'Buts par match',
        'SoT_per_90': 'Tirs cadrés / 90',
        'xG_per_90': 'Buts attendus / 90',
        'Ast_per_90': 'Passes D / 90',
        'xAG_per_90': 'Passes D attendues / 90',
        'KP_per_90': 'Passes clés / 90',
        'PrgP_per_90': 'Passes progressives / 90',
        'PrgC_per_90': 'Courses progressives / 90',
        'Touches_per_90': 'Touches / 90',
        'TklW_per_90': 'Tacles réussis / 90',
        'Int_per_90': 'Interceptions / 90',
        'Recov_per_90': 'Récupérations / 90',
        'Clr_per_90': 'Dégagements / 90',
        'Won_per_90': 'Duels gagnés / 90',
        'Saves_per_90': 'Arrêts / 90',
        'GA_per_90': 'Buts encaissés / 90',
        'Save%_per_90': '% Arrêts',
        # ajoute d'autres mappings ici si nécessaire
    }
    
    if selected_position in position_metrics:
        metrics = position_metrics[selected_position]
        
        # Métriques principales
        st.subheader(f"Métriques clés - {selected_position}")
        
        primary_metrics = metrics['primary']
        available_primary = [m for m in primary_metrics if m in pos_data.columns]
        
        if len(available_primary) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                # afficher des libellés lisibles mais retourner la colonne réelle
                x_metric = st.selectbox(
                    "Métrique X",
                    options=available_primary,
                    format_func=lambda k: metric_labels.get(k, k),
                    key=f"{selected_position}_x"
                )
            
            with col2:
                y_metric = st.selectbox(
                    "Métrique Y",
                    options=available_primary,
                    index=1 if len(available_primary) > 1 else 0,
                    format_func=lambda k: metric_labels.get(k, k),
                    key=f"{selected_position}_y"
                )
            
            if x_metric != y_metric:
                fig = create_scatter_plot(
                    pos_data, x_metric, y_metric, 'League',
                    title=f"{metric_labels.get(y_metric, y_metric)} vs {metric_labels.get(x_metric, x_metric)} - {selected_position}"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Top performers
        st.subheader(f"🏆 Top 10 - {selected_position}")
        
        if available_primary:
            main_metric = available_primary[0]
            top_players = pos_data.nlargest(10, main_metric)[['Player', 'Squad', 'League', main_metric]]
            top_players[main_metric] = top_players[main_metric].round(2)
            # Renommer la colonne principale par son libellé lisible
            top_players = top_players.rename(columns={ main_metric: metric_labels.get(main_metric, main_metric) })
            st.dataframe(top_players, use_container_width=True)

def show_player_comparison(data):
    """Page comparaison de joueurs."""
    st.header("Comparaison de joueurs")
    
    # Sélection du poste d'abord
    positions = data['Position'].unique()
    selected_position = st.selectbox("Choisir un poste pour comparer", positions)
    
    pos_data = data[data['Position'] == selected_position]
    
    # Sélection des joueurs
    players = st.multiselect(
        "Choisir des joueurs à comparer (max 4)",
        options=sorted(pos_data['Player'].unique()),
        max_selections=4
    )
    
    if len(players) >= 2:
        # Radar chart
        st.subheader("Profils radar")
        fig_radar = create_radar_chart(data, players, selected_position)
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Tableau comparatif
        st.subheader("Comparaison détaillée")
        
        position_metrics = get_position_metrics()
        if selected_position in position_metrics:
            all_metrics = position_metrics[selected_position]['primary'] + position_metrics[selected_position]['secondary']
            available_metrics = [m for m in all_metrics if m in pos_data.columns]
            
            comparison_data = pos_data[pos_data['Player'].isin(players)][['Player', 'Squad', 'League'] + available_metrics]
            comparison_data = comparison_data.round(2)
            st.dataframe(comparison_data, use_container_width=True)

def show_player_profile(data):
    """Page fiche joueur individuelle."""
    st.header("👤 Fiche joueur")
    
    # Sélection du joueur
    player_name = st.selectbox("Choisir un joueur", sorted(data['Player'].unique()))
    
    player_data = data[data['Player'] == player_name]
    
    if not player_data.empty:
        player_info = player_data.iloc[0]
        
        # Header avec infos principales
        col1, col2, col3,  = st.columns(3)
        
        with col1:
            st.metric("Poste", player_info['Position'])
        
        with col2:
            st.metric("Club", player_info['Squad'])
        
        with col3:
            st.metric("Ligue", player_info['League'])
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            if 'Age' in player_info:
                st.metric("Âge", f"{player_info['Age']:.0f} ans")
        
        with col5:
            if 'Country' in player_info:
                st.metric("Nationalité", player_info['Country'])

        with col6:
            if 'MP' in player_info:
                st.metric("Matchs joués", f"{player_info['MP']:.0f}")

        
        # Métriques spécifiques au poste
        position = player_info['Position']
        position_metrics = get_position_metrics()
        
        if position in position_metrics:
            st.subheader("Performances clés")
            
            primary_metrics = position_metrics[position]['primary']
            available_metrics = [m for m in primary_metrics if m in player_data.columns and pd.notna(player_info[m])]
            
            cols = st.columns(len(available_metrics))
            metric_labels = get_metric_labels()
            
            for i, metric in enumerate(available_metrics):
                with cols[i]:
                    value = player_info[metric]
                    label = metric_labels.get(metric, metric)
                    st.metric(label, f"{value:.2f}")

        
        # Radar individuel vs moyenne du poste
        st.subheader("Profil vs moyenne du poste")
        fig_radar = create_radar_chart(data, [player_name], position)
        st.plotly_chart(fig_radar, use_container_width=True)

        st.subheader("Comparaison détaillée avec la moyenne du poste")

        # Toutes les métriques disponibles pour le poste
        all_metrics = position_metrics[position]['primary'] + position_metrics[position]['secondary']
        available_metrics = [m for m in all_metrics if m in player_data.columns and pd.notna(player_info[m])]

        # Calculer les moyennes du poste
        pos_data = data[data['Position'] == position]
        comparison_data = []

        for metric in available_metrics[:8]:  # Limiter à 8 métriques
            player_value = player_info[metric]
            avg_value = pos_data[metric].mean()
            
            comparison_data.append({
                'Métrique': metric_labels.get(metric, metric),
                'Joueur': player_value,
                'Moyenne poste': avg_value
            })

        df_comparison = pd.DataFrame(comparison_data)

        # Graphique en barres groupées
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Joueur',
            x=df_comparison['Métrique'],
            y=df_comparison['Joueur'],
            marker_color='#e74c3c'
        ))
        fig.add_trace(go.Bar(
            name='Moyenne du poste',
            x=df_comparison['Métrique'],
            y=df_comparison['Moyenne poste'],
            marker_color='#95a5a6'
        ))

        fig.update_layout(
            barmode='group',
            title='Comparaison avec la moyenne du poste',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

def show_leagues_nations(data):
    """Page analyse ligues et nations."""
    st.header("Ligues & Nations")
    
    # Analyse par ligue
    st.subheader("Comparaison des ligues")
    
    if 'League' in data.columns and 'Position' in data.columns:
        league_position = data.groupby(['League', 'Position']).size().reset_index(name='Count')
        
        fig = px.bar(
            league_position, 
            x='League', 
            y='Count', 
            color='Position',
            title="Répartition des joueurs par ligue et poste",
            color_discrete_map=POSITION_COLORS
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top nations
    st.subheader("Représentation par nationalité")
    
    # Choisir la colonne disponible pour la nationalité
    if 'Country' in data.columns and data['Country'].notna().any():
        col = 'Country'
    elif 'Nation' in data.columns and data['Nation'].notna().any():
        col = 'Nation'
    else:
        col = None

    if col:
        country_stats = data[col].dropna().astype(str).value_counts().head(15)
        df_countries = country_stats.reset_index()
        df_countries.columns = ['Nation', 'Count']

        fig = px.bar(
            df_countries,
            x='Count',
            y='Nation',
            orientation='h',
            title="Top 15 des nationalités",
            labels={'Count': 'Nombre de joueurs', 'Nation': 'Pays'}
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

def show_methodology():
    """Page méthodologie."""
    st.header("Méthodologie")
    
    st.markdown("""
    ## Objectif
    Ce dashboard analyse les performances des joueurs des 5 principales ligues européennes 
    pour la saison 2023-2024, en utilisant des métriques avancées normalisées par 90 minutes.
    
    ## Sources de données
    - **Ligues couvertes** : Premier League, La Liga, Serie A, Bundesliga, Ligue 1
    - **Source** : FBref.com (statistiques officielles)
    - **Période** : Saison 2023-2024
    - **Seuil minimum** : 450 minutes jouées (équivalent à 5 matchs complets)
    
    ## Métriques clés
    
    ### Attaquants (FW)
    - **Buts/90** : Nombre de buts marqués par 90 minutes
    - **xG/90** : Expected Goals (buts attendus selon la qualité des occasions)
    - **Tirs cadrés/90** : Nombre de tirs cadrés par 90 minutes
    
    ### Milieux (MF)
    - **Passes clés/90** : Passes menant directement à un tir
    - **xAG/90** : Expected Assisted Goals (passes décisives attendues)
    - **Passes progressives/90** : Passes vers l'avant de plus de 10 yards
    
    ### Défenseurs (DF)
    - **Tacles réussis/90** : Nombre de tacles réussis par 90 minutes
    - **Interceptions/90** : Ballons interceptés par 90 minutes
    - **Récupérations/90** : Ballons récupérés par 90 minutes
    
    ### Gardiens (GK)
    - **Arrêts/90** : Nombre d'arrêts par 90 minutes
    - **PSxG/90** : Post-Shot Expected Goals (performance vs qualité des tirs)
    - **% Arrêts** : Pourcentage de tirs arrêtés
    
    ## Normalisation
    Toutes les statistiques sont **normalisées par 90 minutes** pour permettre une comparaison 
    équitable entre joueurs ayant des temps de jeu différents.

    ## Percentiles
    Les radars affichent les percentiles calculés au sein de chaque poste,
    permettant de situer un joueur par rapport à ses pairs (0-100%).
    """)

# Ajout de la fonction pour charger les KPI
@st.cache_data
def load_kpi_data():
    """Charge les données KPI depuis les fichiers CSV."""
    kpi_data = {}
    base_path = os.path.join(os.path.dirname(__file__), '..', 'ressources', 'KPI')
    
    kpi_files = {
        'FW': 'kpi_fw.csv',
        'DF': 'KPI_df.csv',
    }
    
    for position, filename in kpi_files.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                kpi_data[position] = df
            except Exception as e:
                st.warning(f"Erreur lors du chargement de {filename}: {e}")
    
    return kpi_data

@st.cache_data
def load_kpi_definitions():
    """Charge les définitions des KPI depuis les fichiers de résumé."""
    definitions = {}
    base_path = os.path.join(os.path.dirname(__file__), '..', 'ressources', 'KPI')
    
    definition_files = {
        'FW': 'kpi_sum_FW.csv',
        'DF': 'KPI_sum_DF.csv',
    }
    
    for position, filename in definition_files.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                definitions[position] = df.set_index('KPI').to_dict('index')
            except Exception as e:
                st.warning(f"Erreur lors du chargement des définitions {filename}: {e}")
    
    return definitions

def show_kpi_analysis(data):
    """🚀 Tableau de bord KPI avancé - Analyse approfondie des performances."""
    
    # En-tête superflu retiré selon les demandes utilisateur
    
    # Charger les données KPI et leurs définitions
    kpi_data = load_kpi_data()
    kpi_definitions = load_kpi_definitions()
    
    if not kpi_data:
        st.error("❌ Aucune donnée KPI disponible.")
        return
    
    # === SECTION 1: SÉLECTION ET CONFIGURATION ===
    st.markdown("### 🎯 Configuration de l'analyse")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        available_positions = list(kpi_data.keys())
        position_labels = {'FW': '⚽ Attaquants', 'DF': '🛡️ Défenseurs', 'MF': '🎯 Milieux', 'GK': '🥅 Gardiens'}
        
        selected_position = st.selectbox(
            "Choisir un poste",
            available_positions,
            format_func=lambda x: position_labels.get(x, x),
            key="main_position_select"
        )
    
    with col2:
        analysis_mode = st.selectbox(
            "Mode d'analyse",
            ["🔍 Vue d'ensemble", "📊 KPI Détaillés", "🏅 Comparaisons", "📈 Tendances"],
            key="analysis_mode"
        )
    
    with col3:
        st.markdown("**Options d'affichage**")
        # Option retirée car redondante avec les filtres généraux du dashboard
    
    if selected_position not in kpi_data:
        st.error(f"❌ Données KPI non disponibles pour {selected_position}")
        return
    
    kpi_df = kpi_data[selected_position]
    kpi_def = kpi_definitions.get(selected_position, {})
    
    # Obtenir les métriques KPI disponibles
    if selected_position == 'FW':
        player_col = 'Player'
        squad_col = 'Squad'
        exclude_cols = ['Age', 'Min', '90s', 'MainPos']
    else:  # DF
        player_col = 'Nom du joueur'
        squad_col = 'Équipe'  
        exclude_cols = ['Poste']
    
    numeric_cols = kpi_df.select_dtypes(include=[np.number]).columns.tolist()
    kpi_metrics = [col for col in numeric_cols if col not in exclude_cols]
    
    # Appliquer les filtres généraux du dashboard
    filtered_df = kpi_df.copy()
    # Les filtres sont maintenant gérés au niveau global du dashboard
    
    st.markdown("---")
    
    # === SECTION 2: INDICATEURS CLÉS ===
    st.markdown("### 📋 Indicateurs de l'échantillon")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 2rem;">{len(filtered_df)}</h2>
            <p style="margin: 0; opacity: 0.8;">Joueurs analysés</p>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        teams_count = filtered_df[squad_col].nunique() if squad_col in filtered_df.columns else 0
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1rem; border-radius: 10px; text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 2rem;">{teams_count}</h2>
            <p style="margin: 0; opacity: 0.8;">Équipes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        if 'Age' in filtered_df.columns:
            avg_age = filtered_df['Age'].mean()
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 1rem; border-radius: 10px; text-align: center; color: white;">
                <h2 style="margin: 0; font-size: 2rem;">{avg_age:.1f}</h2>
                <p style="margin: 0; opacity: 0.8;">Âge moyen</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Données non disponibles pour ce poste
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%); 
                        padding: 1rem; border-radius: 10px; text-align: center; color: white;">
                <h2 style="margin: 0; font-size: 2rem;">N/A</h2>
                <p style="margin: 0; opacity: 0.8;">Âge moyen</p>
            </div>
            """, unsafe_allow_html=True)
    
    with kpi_col4:
        if 'Min' in filtered_df.columns:
            avg_minutes = filtered_df['Min'].mean()
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                        padding: 1rem; border-radius: 10px; text-align: center; color: white;">
                <h2 style="margin: 0; font-size: 2rem;">{avg_minutes:.0f}</h2>
                <p style="margin: 0; opacity: 0.8;">Minutes moy.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Données non disponibles pour ce poste
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%); 
                        padding: 1rem; border-radius: 10px; text-align: center; color: white;">
                <h2 style="margin: 0; font-size: 2rem;">N/A</h2>
                <p style="margin: 0; opacity: 0.8;">Minutes moy.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with kpi_col5:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    padding: 1rem; border-radius: 10px; text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 2rem;">{len(kpi_metrics)}</h2>
            <p style="margin: 0; opacity: 0.8;">KPI analysés</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === SECTION 3: CONTENU SELON LE MODE SÉLECTIONNÉ ===
    
    if analysis_mode == "🔍 Vue d'ensemble":
        show_kpi_overview(filtered_df, kpi_metrics, kpi_def, player_col, squad_col)
    
    elif analysis_mode == "📊 KPI Détaillés":
        show_kpi_detailed(filtered_df, kpi_metrics, kpi_def, player_col, squad_col)
    
    elif analysis_mode == "🏅 Comparaisons":
        show_kpi_comparisons(filtered_df, kpi_metrics, kpi_def, player_col, squad_col)
    
    elif analysis_mode == "📈 Tendances":
        show_kpi_trends(filtered_df, kpi_metrics, kpi_def, player_col, squad_col)

def show_kpi_overview(df, metrics, definitions, player_col, squad_col):
    """Vue d'ensemble des KPI."""
    st.markdown("### 🔍 Vue d'ensemble des performances")
    
    if not metrics:
        st.warning("Aucune métrique KPI disponible")
        return
    
    # === TOP MÉTRIQUES ===
    st.markdown("#### 🏆 Métriques les plus impactantes")
    
    # Calculer la variance normalisée pour identifier les métriques les plus discriminantes
    metric_importance = []
    for metric in metrics:
        if df[metric].std() > 0:
            cv = df[metric].std() / df[metric].mean() if df[metric].mean() != 0 else 0
            metric_importance.append((metric, cv, df[metric].mean(), df[metric].std()))
    
    # Trier par coefficient de variation
    metric_importance.sort(key=lambda x: x[1], reverse=True)
    top_metrics = metric_importance[:6]
    
    cols = st.columns(3)
    for i, (metric, cv, mean_val, std_val) in enumerate(top_metrics):
        with cols[i % 3]:
            # Obtenir la définition si disponible
            definition = definitions.get(metric, {})
            justification = definition.get('Justification', 'Métrique de performance')
            
            st.markdown(f"""
            <div style="border: 2px solid #e1e5e9; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
                <h4 style="color: #1f77b4; margin-top: 0;">{metric}</h4>
                <p style="font-size: 0.85em; color: #666; margin: 0.5rem 0;">{justification}</p>
                <div style="display: flex; justify-content: space-between;">
                    <span><strong>Moyenne:</strong> {mean_val:.2f}</span>
                    <span><strong>Écart-type:</strong> {std_val:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === ANALYSE DE CORRÉLATION ===
    st.markdown("#### 🔗 Analyse des corrélations")
    
    if len(metrics) >= 3:
        # Sélectionner les métriques les plus importantes pour la corrélation
        top_metrics_names = [m[0] for m in metric_importance[:8]]
        
        corr_matrix = df[top_metrics_names].corr()
        
        # Graphique de corrélation avec annotations
        fig_corr = px.imshow(
            corr_matrix,
            title="Matrice de corrélation des KPI principaux",
            color_continuous_scale="RdBu",
            aspect="auto",
            text_auto=True
        )
        fig_corr.update_layout(height=600)
        fig_corr.update_traces(texttemplate="%{z:.2f}", textfont_size=10)
        
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Insights sur les corrélations
        st.markdown("##### 💡 Insights clés")
        
        # Trouver les corrélations les plus fortes (hors diagonale)
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.3:  # Seuil de corrélation significative
                    corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
        
        corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        if corr_pairs:
            insight_cols = st.columns(2)
            for i, (metric1, metric2, corr_val) in enumerate(corr_pairs[:6]):
                with insight_cols[i % 2]:
                    direction = "🔺 Positive" if corr_val > 0 else "🔻 Négative"
                    strength = "forte" if abs(corr_val) > 0.7 else "modérée" if abs(corr_val) > 0.5 else "faible"
                    
                    # Utilisons les composants natifs Streamlit pour éviter les problèmes de thème
                    with st.container():
                        st.markdown(f"**{metric1}** ↔ **{metric2}**")
                        st.caption(f"{direction} ({corr_val:.2f}) - Corrélation {strength}")
                        st.divider()
    
    st.markdown("---")
    
    # === DISTRIBUTION GÉNÉRALE ===
    st.markdown("#### 📊 Distribution des performances")
    
    if len(metrics) >= 1:
        # Permettre à l'utilisateur de choisir une métrique pour voir sa distribution
        selected_metric = st.selectbox(
            "Choisir une métrique pour analyser sa distribution:",
            metrics,
            format_func=lambda m: format_metric_name(m),
            key="overview_metric_dist"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Histogramme
            fig_hist = px.histogram(
                df, 
                x=selected_metric,
                title=f"Distribution - {format_metric_name(selected_metric)}",
                nbins=25,
                marginal="box"
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Box plot par équipe (top 10)
            if squad_col in df.columns:
                top_teams = df[squad_col].value_counts().head(10).index
                df_top_teams = df[df[squad_col].isin(top_teams)]
                
                fig_box = px.box(
                    df_top_teams,
                    x=squad_col,
                    y=selected_metric,
                    title=f"{format_metric_name(selected_metric)} par équipe (Top 10)"
                )
                fig_box.update_xaxes(tickangle=45)
                fig_box.update_layout(height=400)
                st.plotly_chart(fig_box, use_container_width=True)
        
        with col3:
            # Statistiques descriptives
            stats = df[selected_metric].describe()
            
            # Utilisons les métriques natives de Streamlit pour éviter les problèmes de thème
            st.markdown(f"##### 📈 Statistiques - {selected_metric}")
            
            col_stats1, col_stats2 = st.columns(2)
            with col_stats1:
                st.metric("Minimum", f"{stats['min']:.2f}")
                st.metric("Q1 (25%)", f"{stats['25%']:.2f}")
                st.metric("Médiane", f"{stats['50%']:.2f}")
                st.metric("Q3 (75%)", f"{stats['75%']:.2f}")
            with col_stats2:
                st.metric("Maximum", f"{stats['max']:.2f}")
                st.metric("Moyenne", f"{stats['mean']:.2f}")
                st.metric("Écart-type", f"{stats['std']:.2f}")

def show_kpi_detailed(df, metrics, definitions, player_col, squad_col):
    """Analyse détaillée des KPI avec sélection interactive."""
    st.markdown("### 📊 Analyse détaillée des KPI")
    
    if not metrics:
        st.warning("Aucune métrique KPI disponible")
        return
    
    # === SÉLECTION DE MÉTRIQUES ===
    st.markdown("#### 🎯 Sélection des métriques à analyser")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_metrics = st.multiselect(
            "Choisir les métriques à analyser (max 6):",
            metrics,
            default=metrics[:4],
            max_selections=6,
            format_func=lambda m: format_metric_name(m),
            key="detailed_metrics_select"
        )
    
    with col2:
        if len(selected_metrics) >= 2:
            comparison_type = st.selectbox(
                "Type de comparaison:",
                ["Scatter plots", "Radar charts", "Distributions", "Rankings"],
                key="comparison_type"
            )
    
    if not selected_metrics:
        st.warning("Veuillez sélectionner au moins une métrique.")
        return
    
    st.markdown("---")
    
    # === DÉFINITIONS DES MÉTRIQUES SÉLECTIONNÉES ===
    st.markdown("#### 📋 Définitions des métriques sélectionnées")
    
    def_cols = st.columns(min(3, len(selected_metrics)))
    for i, metric in enumerate(selected_metrics):
        with def_cols[i % 3]:
            definition = definitions.get(metric, {})
            justification = definition.get('Justification', 'Description non disponible')
            calcul = definition.get('Calcul', 'Formule non disponible')
            
            # Utilisons les composants natifs pour éviter les problèmes de thème
            with st.expander(f"📊 {metric}", expanded=False):
                st.markdown(f"**Description:** {justification}")
                st.code(calcul, language="text")
    
    st.markdown("---")
    
    # === ANALYSES SELON LE TYPE SÉLECTIONNÉ ===
    
    if comparison_type == "Scatter plots" and len(selected_metrics) >= 2:
        st.markdown("#### 📈 Analyses de corrélation")
        
        scatter_col1, scatter_col2 = st.columns(2)
        with scatter_col1:
            x_metric = st.selectbox("Axe X:", selected_metrics, 
                                   format_func=lambda m: format_metric_name(m),
                                   key="scatter_x")
        with scatter_col2:
            y_metric = st.selectbox("Axe Y:", selected_metrics, 
                                  index=1 if len(selected_metrics) > 1 else 0,
                                  format_func=lambda m: format_metric_name(m),
                                  key="scatter_y")
        
        if x_metric != y_metric:
            # Calcul de la corrélation
            correlation = df[x_metric].corr(df[y_metric])
            
            # Graphique scatter avec ligne de tendance
            fig_scatter = px.scatter(
                df,
                x=x_metric,
                y=y_metric,
                color=squad_col if squad_col in df.columns else None,
                hover_data=[player_col] if player_col in df.columns else None,
                title=f"{y_metric} vs {x_metric} (r = {correlation:.3f})",
                trendline="ols"
            )
            fig_scatter.update_layout(height=600)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Interprétation de la corrélation
            if abs(correlation) > 0.7:
                strength = "forte"
                color = "#28a745"
            elif abs(correlation) > 0.5:
                strength = "modérée"
                color = "#ffc107"
            else:
                strength = "faible"
                color = "#dc3545"
            
            direction = "positive" if correlation > 0 else "négative"
            
            st.markdown(f"""
            <div style="background: {color}20; border-left: 4px solid {color}; padding: 1rem; margin: 1rem 0;">
                <strong>💡 Interprétation:</strong> Corrélation {direction} {strength} (r = {correlation:.3f}) 
                entre {x_metric} et {y_metric}.
            </div>
            """, unsafe_allow_html=True)
    
    elif comparison_type == "Distributions":
        st.markdown("#### 📊 Analyse des distributions")
        
        # Graphiques de distribution pour toutes les métriques sélectionnées
        n_cols = min(3, len(selected_metrics))
        cols = st.columns(n_cols)
        
        for i, metric in enumerate(selected_metrics):
            with cols[i % n_cols]:
                fig_dist = px.histogram(
                    df,
                    x=metric,
                    title=f"Distribution - {metric}",
                    nbins=20,
                    marginal="box"
                )
                fig_dist.update_layout(height=400)
                st.plotly_chart(fig_dist, use_container_width=True)
        
        # Tableau comparatif des statistiques
        st.markdown("##### 📋 Statistiques comparatives")
        
        stats_df = df[selected_metrics].describe().round(3).T
        stats_df['CV'] = (stats_df['std'] / stats_df['mean']).round(3)  # Coefficient de variation
        
        st.dataframe(stats_df, use_container_width=True)
    
    elif comparison_type == "Rankings":
        st.markdown("#### 🏅 Classements par métrique")
        
        ranking_metric = st.selectbox(
            "Choisir la métrique pour le classement:",
            selected_metrics,
            format_func=lambda m: format_metric_name(m),
            key="ranking_metric"
        )
        
        n_top = st.slider("Nombre de joueurs à afficher:", 5, 20, 10, key="ranking_n_top")
        
        # Top performers
        top_performers = df.nlargest(n_top, ranking_metric)
        
        # Graphique en barres
        fig_ranking = px.bar(
            top_performers,
            x=player_col,
            y=ranking_metric,
            color=squad_col if squad_col in df.columns else None,
            title=f"Top {n_top} - {ranking_metric}",
            text=ranking_metric
        )
        fig_ranking.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_ranking.update_xaxes(tickangle=45)
        fig_ranking.update_layout(height=500)
        st.plotly_chart(fig_ranking, use_container_width=True)
        
        # Tableau détaillé
        display_cols = [player_col, squad_col] if squad_col in df.columns else [player_col]
        display_cols.extend(selected_metrics)
        
        if 'Age' in df.columns:
            display_cols.insert(-len(selected_metrics), 'Age')
        
        ranking_table = top_performers[display_cols].round(3)
        ranking_table.index = range(1, len(ranking_table) + 1)  # Numérotation à partir de 1
        
        st.markdown("##### 📋 Classement détaillé")
        st.dataframe(ranking_table, use_container_width=True)

def show_kpi_comparisons(df, metrics, definitions, player_col, squad_col):
    """Comparaisons avancées entre joueurs et équipes."""
    st.markdown("### 🏅 Comparaisons avancées")
    
    if not metrics:
        st.warning("Aucune métrique KPI disponible")
        return
    
    # === TYPE DE COMPARAISON ===
    comparison_mode = st.selectbox(
        "Type de comparaison:",
        ["👤 Joueurs vs Joueurs", "⚽ Équipes vs Équipes", "🎯 Joueur vs Moyenne Poste"],
        key="comparison_mode"
    )
    
    st.markdown("---")
    
    if comparison_mode == "👤 Joueurs vs Joueurs":
        st.markdown("#### 👤 Comparaison entre joueurs")
        
        # Sélection de joueurs
        selected_players = st.multiselect(
            "Choisir les joueurs à comparer (max 5):",
            df[player_col].tolist(),
            max_selections=5,
            key="players_comparison"
        )
        
        if len(selected_players) >= 2:
            # Métriques à comparer
            comparison_metrics = st.multiselect(
                "Métriques à comparer:",
                metrics,
                default=metrics[:6],
                format_func=lambda m: format_metric_name(m),
                key="players_comparison_metrics"
            )
            
            if comparison_metrics:
                # Données des joueurs sélectionnés
                players_data = df[df[player_col].isin(selected_players)]
                
                # Graphique radar
                fig_radar = go.Figure()
                
                colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
                
                for i, player in enumerate(selected_players):
                    player_data = players_data[players_data[player_col] == player]
                    if not player_data.empty:
                        values = []
                        for metric in comparison_metrics:
                            # Normaliser par percentile
                            percentile = (df[metric] <= player_data[metric].iloc[0]).mean() * 100
                            values.append(percentile)
                        
                        # Fermer le radar
                        values.append(values[0])
                        metrics_labels = comparison_metrics + [comparison_metrics[0]]
                        
                        fig_radar.add_trace(go.Scatterpolar(
                            r=values,
                            theta=metrics_labels,
                            fill='toself',
                            name=player,
                            line=dict(color=colors[i % len(colors)])
                        ))
                
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    title="Profils comparés (Percentiles 0-100)",
                    height=600
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
                
                # Tableau comparatif détaillé
                st.markdown("##### 📊 Tableau comparatif")
                
                comparison_table = players_data[[player_col, squad_col] + comparison_metrics].round(3)
                st.dataframe(comparison_table, use_container_width=True, hide_index=True)
    
    elif comparison_mode == "⚽ Équipes vs Équipes":
        st.markdown("#### ⚽ Comparaison entre équipes")
        
        if squad_col in df.columns:
            # Sélection d'équipes
            selected_teams = st.multiselect(
                "Choisir les équipes à comparer:",
                sorted(df[squad_col].unique()),
                default=sorted(df[squad_col].unique())[:5],
                key="teams_comparison"
            )
            
            if selected_teams:
                # Métrique à analyser
                team_metric = st.selectbox(
                    "Métrique à analyser:",
                    metrics,
                    key="team_comparison_metric"
                )
                
                # Calculer les moyennes par équipe
                team_stats = df[df[squad_col].isin(selected_teams)].groupby(squad_col)[team_metric].agg([
                    'mean', 'median', 'std', 'count'
                ]).round(3)
                team_stats.columns = ['Moyenne', 'Médiane', 'Écart-type', 'Nb joueurs']
                team_stats = team_stats.sort_values('Moyenne', ascending=False)
                
                # Graphique en barres avec barres d'erreur
                fig_teams = px.bar(
                    team_stats.reset_index(),
                    x=squad_col,
                    y='Moyenne',
                    error_y='Écart-type',
                    title=f"Comparaison équipes - {team_metric}",
                    text='Moyenne'
                )
                fig_teams.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig_teams.update_xaxes(tickangle=45)
                fig_teams.update_layout(height=500)
                st.plotly_chart(fig_teams, use_container_width=True)
                
                # Tableau des stats
                st.markdown("##### 📊 Statistiques par équipe")
                st.dataframe(team_stats, use_container_width=True)
                
                # Box plot pour voir la distribution
                st.markdown("##### 📦 Distribution par équipe")
                
                fig_box = px.box(
                    df[df[squad_col].isin(selected_teams)],
                    x=squad_col,
                    y=team_metric,
                    title=f"Distribution de {team_metric} par équipe"
                )
                fig_box.update_xaxes(tickangle=45)
                fig_box.update_layout(height=400)
                st.plotly_chart(fig_box, use_container_width=True)
    
    elif comparison_mode == "🎯 Joueur vs Moyenne Poste":
        st.markdown("#### 🎯 Joueur vs Moyenne du poste")
        
        # Sélection du joueur
        selected_player = st.selectbox(
            "Choisir un joueur:",
            df[player_col].tolist(),
            key="player_vs_position"
        )
        
        if selected_player:
            player_data = df[df[player_col] == selected_player].iloc[0]
            
            # Métriques à analyser
            analysis_metrics = st.multiselect(
                "Métriques à analyser:",
                metrics,
                default=metrics[:8],
                key="player_vs_position_metrics"
            )
            
            if analysis_metrics:
                # Calculer les moyennes du poste
                position_averages = df[analysis_metrics].mean()
                
                # Créer le graphique de comparaison
                comparison_data = []
                
                for metric in analysis_metrics:
                    player_val = player_data[metric]
                    position_avg = position_averages[metric]
                    
                    comparison_data.append({
                        'Métrique': metric,
                        'Joueur': player_val,
                        'Moyenne poste': position_avg,
                        'Différence': player_val - position_avg,
                        'Différence %': ((player_val - position_avg) / position_avg * 100) if position_avg != 0 else 0
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                
                # Graphique en barres groupées
                fig_comparison = go.Figure()
                
                fig_comparison.add_trace(go.Bar(
                    name='Joueur',
                    x=comparison_df['Métrique'],
                    y=comparison_df['Joueur'],
                    marker_color='#ff7f0e',
                    text=comparison_df['Joueur'].round(2),
                    textposition='outside'
                ))
                
                fig_comparison.add_trace(go.Bar(
                    name='Moyenne poste',
                    x=comparison_df['Métrique'],
                    y=comparison_df['Moyenne poste'],
                    marker_color='#1f77b4',
                    text=comparison_df['Moyenne poste'].round(2),
                    textposition='outside'
                ))
                
                fig_comparison.update_layout(
                    barmode='group',
                    title=f'Comparaison: {selected_player} vs Moyenne du poste',
                    height=500
                )
                fig_comparison.update_xaxes(tickangle=45)
                
                st.plotly_chart(fig_comparison, use_container_width=True)
                
                # Tableau des différences
                st.markdown("##### 📊 Analyse des écarts")
                
                # Colorier les différences
                def highlight_differences(val):
                    if val > 10:
                        return 'background-color: #d4edda; color: #155724'  # Vert
                    elif val < -10:
                        return 'background-color: #f8d7da; color: #721c24'  # Rouge
                    else:
                        return 'background-color: #fff3cd; color: #856404'  # Jaune
                
                styled_comparison = comparison_df.round(3).style.applymap(
                    highlight_differences, subset=['Différence %']
                )
                
                st.dataframe(styled_comparison, use_container_width=True, hide_index=True)

def show_kpi_trends(df, metrics, definitions, player_col, squad_col):
    """Analyse des tendances et patterns dans les KPI."""
    st.markdown("### 📈 Analyse des tendances")
    
    if not metrics:
        st.warning("Aucune métrique KPI disponible")
        return
    
    # === ANALYSE PAR ÂGE ===
    if 'Age' in df.columns:
        st.markdown("#### 📅 Tendances par âge")
        
        age_metric = st.selectbox(
            "Métrique à analyser selon l'âge:",
            metrics,
            key="age_trend_metric"
        )
        
        # Créer des groupes d'âge
        df_age = df.copy()
        df_age['Groupe_Age'] = pd.cut(df_age['Age'], 
                                    bins=[15, 20, 23, 26, 30, 40], 
                                    labels=['≤20 ans', '21-23 ans', '24-26 ans', '27-30 ans', '30+ ans'])
        
        # Analyse par groupe d'âge
        age_analysis = df_age.groupby('Groupe_Age')[age_metric].agg(['mean', 'median', 'count']).round(3)
        age_analysis.columns = ['Moyenne', 'Médiane', 'Effectif']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique en barres
            fig_age_bar = px.bar(
                age_analysis.reset_index(),
                x='Groupe_Age',
                y='Moyenne',
                title=f"Moyenne de {age_metric} par groupe d'âge",
                text='Moyenne'
            )
            fig_age_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_age_bar.update_layout(height=400)
            st.plotly_chart(fig_age_bar, use_container_width=True)
        
        with col2:
            # Scatter plot âge vs métrique
            fig_age_scatter = px.scatter(
                df,
                x='Age',
                y=age_metric,
                color=squad_col if squad_col in df.columns else None,
                title=f"{age_metric} vs Âge",
                trendline="lowess"
            )
            fig_age_scatter.update_layout(height=400)
            st.plotly_chart(fig_age_scatter, use_container_width=True)
        
        # Tableau par groupe d'âge
        st.markdown("##### 📊 Statistiques par groupe d'âge")
        st.dataframe(age_analysis, use_container_width=True)
    
    st.markdown("---")
    
    # === ANALYSE PAR TEMPS DE JEU ===
    if 'Min' in df.columns:
        st.markdown("#### ⏱️ Tendances par temps de jeu")
        
        minutes_metric = st.selectbox(
            "Métrique à analyser selon le temps de jeu:",
            metrics,
            key="minutes_trend_metric"
        )
        
        # Créer des groupes de temps de jeu
        df_minutes = df.copy()
        df_minutes['Groupe_Minutes'] = pd.cut(df_minutes['Min'], 
                                            bins=[0, 500, 1000, 1500, 2500, 5000], 
                                            labels=['<500 min', '500-1000', '1000-1500', '1500-2500', '2500+ min'])
        
        # Analyse par groupe de minutes
        minutes_analysis = df_minutes.groupby('Groupe_Minutes')[minutes_metric].agg(['mean', 'median', 'count']).round(3)
        minutes_analysis.columns = ['Moyenne', 'Médiane', 'Effectif']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Box plot
            fig_minutes_box = px.box(
                df_minutes.dropna(subset=['Groupe_Minutes']),
                x='Groupe_Minutes',
                y=minutes_metric,
                title=f"Distribution de {minutes_metric} par temps de jeu"
            )
            fig_minutes_box.update_layout(height=400)
            st.plotly_chart(fig_minutes_box, use_container_width=True)
        
        with col2:
            # Scatter avec taille proportionnelle aux minutes
            fig_minutes_scatter = px.scatter(
                df,
                x='Min',
                y=minutes_metric,
                size='Min',
                color=squad_col if squad_col in df.columns else None,
                title=f"{minutes_metric} vs Minutes jouées",
                hover_data=[player_col]
            )
            fig_minutes_scatter.update_layout(height=400)
            st.plotly_chart(fig_minutes_scatter, use_container_width=True)
        
        st.markdown("##### 📊 Impact du temps de jeu")
        st.dataframe(minutes_analysis, use_container_width=True)
    
    st.markdown("---")
    
    # === ANALYSE MULTI-DIMENSIONNELLE ===
    st.markdown("#### 🎯 Analyse multi-dimensionnelle")
    
    if len(metrics) >= 3:
        # Sélection de 3 métriques pour l'analyse 3D
        multi_metrics = st.multiselect(
            "Choisir 3 métriques pour l'analyse 3D:",
            metrics,
            default=metrics[:3],
            max_selections=3,
            key="multi_dim_metrics"
        )
        
        if len(multi_metrics) == 3:
            # Graphique 3D
            fig_3d = px.scatter_3d(
                df,
                x=multi_metrics[0],
                y=multi_metrics[1],
                z=multi_metrics[2],
                color=squad_col if squad_col in df.columns else None,
                size='Min' if 'Min' in df.columns else None,
                hover_data=[player_col],
                title=f"Analyse 3D: {multi_metrics[0]} × {multi_metrics[1]} × {multi_metrics[2]}"
            )
            fig_3d.update_layout(height=600)
            st.plotly_chart(fig_3d, use_container_width=True)
            
            # Analyse de clustering (optionnel)
            if st.checkbox("Afficher l'analyse de clustering", key="show_clustering"):
                from sklearn.cluster import KMeans
                from sklearn.preprocessing import StandardScaler
                
                # Préparer les données pour le clustering
                clustering_data = df[multi_metrics].fillna(df[multi_metrics].mean())
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(clustering_data)
                
                # K-means clustering
                n_clusters = st.slider("Nombre de clusters:", 2, 8, 4, key="n_clusters")
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                clusters = kmeans.fit_predict(scaled_data)
                
                # Ajouter les clusters au dataframe
                df_clustered = df.copy()
                df_clustered['Cluster'] = clusters
                
                # Graphique avec clusters
                fig_cluster = px.scatter_3d(
                    df_clustered,
                    x=multi_metrics[0],
                    y=multi_metrics[1],
                    z=multi_metrics[2],
                    color='Cluster',
                    hover_data=[player_col],
                    title=f"Clustering des joueurs ({n_clusters} groupes)"
                )
                fig_cluster.update_layout(height=600)
                st.plotly_chart(fig_cluster, use_container_width=True)
                
                # Analyse des clusters
                st.markdown("##### 📊 Profils des clusters")
                cluster_analysis = df_clustered.groupby('Cluster')[multi_metrics].mean().round(3)
                st.dataframe(cluster_analysis, use_container_width=True)

# Application principale
def main():
    st.markdown("""
    <div class="main-header">
        <h1>Football Analytics Dashboard</h1>
        <p>Analyse des performances - Top 5 ligues européennes 2023-24</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chargement des données
    try:
        with st.spinner("Chargement des données..."):
            data = load_and_prepare_data()
            # Charger les noms naturels des KPI
            natural_names_map = load_kpi_natural_names()
            
        if data.empty:
            st.error("Aucune donnée disponible")
            return
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return
    
    # Filtres globaux
    filters = create_sidebar_filters(data)
    filtered_data = apply_filters(data, filters)
    
    # KPIs globaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-container">
            <h3>{len(filtered_data):,}</h3>
            <p>Joueurs analysés</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if 'Age' in filtered_data.columns and not filtered_data['Age'].isna().all():
            avg_age = round(filtered_data['Age'].median())
            st.markdown(f"""
            <div class="kpi-container">
            <h3>{avg_age}</h3>
            <p>Âge médian</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if 'Min' in filtered_data.columns:
            avg_minutes = filtered_data['Min'].median()
            st.markdown(f"""
            <div class="kpi-container">
                <h3>{avg_minutes:.0f}</h3>
                <p>Minutes médianes</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if 'League' in filtered_data.columns:
            leagues_count = filtered_data['League'].nunique()
            st.markdown(f"""
            <div class="kpi-container">
                <h3>{leagues_count}</h3>
                <p>Ligues représentées</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Onglets (ajout de l'onglet "Analyse KPI")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Vue d'ensemble", 
        "Par poste", 
        "Comparaison", 
        "Fiche joueur",
        "Ligues & Nations",
        "Analyse KPI",
        "Méthodologie"
    ])
    
    with tab1:
        show_overview(filtered_data)
    
    with tab2:
        show_by_position(filtered_data)
    
    with tab3:
        show_player_comparison(filtered_data)
    
    with tab4:
        show_player_profile(filtered_data)
    
    with tab5:
        show_leagues_nations(filtered_data)
    
    with tab6:
        show_kpi_analysis(filtered_data)
    
    with tab7:
        show_methodology()

if __name__ == "__main__":
    main()