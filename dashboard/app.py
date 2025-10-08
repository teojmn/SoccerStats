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
    get_metric_labels
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
        'DF': 'kpi_df.csv',
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

def show_kpi_analysis(data):
    """Analyse des KPI par poste."""
    st.header("📊 Analyse des KPI")
    
    # Charger les données KPI
    kpi_data = load_kpi_data()
    
    if not kpi_data:
        st.warning("Aucune donnée KPI disponible.")
        return
    
    # Sélection du poste
    available_positions = list(kpi_data.keys())
    selected_position = st.selectbox("Choisir un poste pour l'analyse KPI", available_positions)
    
    if selected_position not in kpi_data:
        st.error(f"Données KPI non disponibles pour {selected_position}")
        return
    
    kpi_df = kpi_data[selected_position]
    
    # Vue d'ensemble des KPI
    st.subheader(f"Vue d'ensemble - {selected_position}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Nombre de joueurs", len(kpi_df))
        st.metric("Équipes représentées", kpi_df['Squad'].nunique() if 'Squad' in kpi_df.columns else "N/A")
    
    with col2:
        if 'Age' in kpi_df.columns:
            st.metric("Âge moyen", f"{kpi_df['Age'].mean():.1f} ans")
        if 'Min' in kpi_df.columns:
            st.metric("Minutes moyennes", f"{kpi_df['Min'].mean():.0f}")
    
    # Sélection des métriques KPI à analyser
    st.subheader("Analyse des métriques clés")
    
    # Obtenir les colonnes numériques (KPI)
    numeric_cols = kpi_df.select_dtypes(include=[np.number]).columns.tolist()
    # Exclure les colonnes d'info de base
    exclude_cols = ['Age', 'Min', '90s']
    kpi_metrics = [col for col in numeric_cols if col not in exclude_cols]
    
    if len(kpi_metrics) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            x_metric = st.selectbox("Métrique X", kpi_metrics, key="kpi_x")
        
        with col2:
            y_metric = st.selectbox("Métrique Y", kpi_metrics, 
                                  index=1 if len(kpi_metrics) > 1 else 0, key="kpi_y")
        
        if x_metric != y_metric:
            # Graphique de corrélation
            fig_scatter = px.scatter(
                kpi_df, 
                x=x_metric, 
                y=y_metric,
                hover_data=['Player', 'Squad'] if 'Player' in kpi_df.columns else None,
                title=f"{y_metric} vs {x_metric}",
                color='Squad' if 'Squad' in kpi_df.columns else None
            )
            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Top performers par métrique
    st.subheader("Top 10 par métrique")
    
    if kpi_metrics:
        selected_metric = st.selectbox("Choisir une métrique", kpi_metrics, key="kpi_top")
        
        # Créer le top 10
        top_players = kpi_df.nlargest(10, selected_metric)
        
        if 'Player' in top_players.columns:
            display_cols = ['Player', 'Squad', selected_metric]
            if 'Age' in top_players.columns:
                display_cols.insert(-1, 'Age')
            
            top_players_display = top_players[display_cols].copy()
            top_players_display[selected_metric] = top_players_display[selected_metric].round(3)
            
            st.dataframe(top_players_display, hide_index=True, use_container_width=True)
            
            # Graphique en barres
            fig_bar = px.bar(
                top_players_display.head(10),
                x='Player',
                y=selected_metric,
                title=f"Top 10 - {selected_metric}",
                color='Squad' if 'Squad' in top_players_display.columns else None
            )
            fig_bar.update_xaxis(tickangle=45)
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Distribution des métriques
    st.subheader("Distribution des métriques")
    
    if kpi_metrics:
        selected_dist_metric = st.selectbox("Métrique pour distribution", kpi_metrics, key="kpi_dist")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogramme
            fig_hist = px.histogram(
                kpi_df,
                x=selected_dist_metric,
                title=f"Distribution - {selected_dist_metric}",
                nbins=20
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Box plot
            fig_box = px.box(
                kpi_df,
                y=selected_dist_metric,
                title=f"Box Plot - {selected_dist_metric}"
            )
            st.plotly_chart(fig_box, use_container_width=True)
    
    # Corrélations entre métriques
    if len(kpi_metrics) >= 3:
        st.subheader("Matrice de corrélation")
        
        # Sélectionner un sous-ensemble de métriques pour la corrélation
        selected_corr_metrics = st.multiselect(
            "Sélectionner les métriques pour la corrélation",
            kpi_metrics,
            default=kpi_metrics[:5],  # 5 premières par défaut
            key="kpi_corr"
        )
        
        if len(selected_corr_metrics) >= 2:
            corr_data = kpi_df[selected_corr_metrics].corr()
            
            fig_corr = px.imshow(
                corr_data,
                title="Matrice de corrélation",
                color_continuous_scale="RdBu",
                aspect="auto"
            )
            fig_corr.update_layout(height=500)
            st.plotly_chart(fig_corr, use_container_width=True)
    
    # Analyse par équipe
    if 'Squad' in kpi_df.columns and len(kpi_metrics) > 0:
        st.subheader("Analyse par équipe")
        
        squad_metric = st.selectbox("Métrique pour analyse par équipe", kpi_metrics, key="kpi_squad")
        
        # Moyenne par équipe
        squad_avg = kpi_df.groupby('Squad')[squad_metric].agg(['mean', 'count']).reset_index()
        squad_avg.columns = ['Squad', 'Moyenne', 'Nombre de joueurs']
        squad_avg = squad_avg.sort_values('Moyenne', ascending=False)
        
        fig_squad = px.bar(
            squad_avg.head(15),
            x='Squad',
            y='Moyenne',
            title=f"Moyenne par équipe - {squad_metric}",
            hover_data=['Nombre de joueurs']
        )
        fig_squad.update_xaxis(tickangle=45)
        fig_squad.update_layout(height=400)
        st.plotly_chart(fig_squad, use_container_width=True)

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