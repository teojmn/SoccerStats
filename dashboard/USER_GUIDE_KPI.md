# 📖 Guide Utilisateur - Nouvel Onglet KPI

## 🚀 Introduction

L'onglet "Analyse KPI" a été entièrement repensé pour vous offrir des outils d'analyse avancés des performances des joueurs. Ce guide vous explique comment utiliser toutes les nouvelles fonctionnalités.

## 🎯 Accès à l'Onglet KPI

1. **Lancez l'application** : `streamlit run app.py`
2. **Naviguez** vers l'onglet "Analyse KPI" (6ème onglet)
3. **Sélectionnez** votre poste d'analyse (Attaquants/Défenseurs)

## 🔧 Configuration Initiale

### **Sélection du Poste**
- **⚽ Attaquants** : Analyses des performances offensives
- **🛡️ Défenseurs** : Analyses des performances défensives

### **Mode d'Analyse**
Choisissez parmi 4 modes spécialisés :

1. **🔍 Vue d'ensemble** - Panorama général des KPI
2. **📊 KPI Détaillés** - Analyses approfondies par métrique
3. **🏅 Comparaisons** - Comparaisons entre joueurs/équipes
4. **📈 Tendances** - Analyses des patterns et évolutions

### **Filtres Optionnels**
- **Équipes** : Sélectionnez les clubs à analyser
- **Âge** : Définissez une tranche d'âge
- **Minutes** : Seuil minimum de temps de jeu

## 📊 Guide par Mode d'Analyse

### 🔍 **Mode "Vue d'ensemble"**

#### **Métriques les Plus Impactantes**
- **Identification automatique** des KPI les plus discriminants
- **Cartes informatives** avec définitions et statistiques
- **Ranking** par coefficient de variation

#### **Analyse des Corrélations**
- **Matrice visuelle** des corrélations entre KPI
- **Insights automatiques** sur les relations significatives
- **Interprétation** : forte (>0.7), modérée (0.5-0.7), faible (<0.5)

#### **Distribution des Performances**
- **Sélection interactive** de la métrique à analyser
- **Histogramme** avec box plot intégré
- **Comparaison par équipe** (top 10)
- **Statistiques descriptives** complètes

**💡 Cas d'usage** : Découvrir les tendances générales et identifier les métriques clés à approfondir.

### 📊 **Mode "KPI Détaillés"**

#### **Sélection des Métriques**
- **Multi-sélection** jusqu'à 6 KPI simultanément
- **Définitions contextuelles** avec justifications
- **Formules de calcul** pour transparence

#### **Types d'Analyse Disponibles**

##### **Scatter Plots**
- **Corrélation** entre 2 métriques
- **Ligne de tendance** automatique
- **Interprétation** de la force de corrélation
- **Coloration** par équipe

##### **Distributions**
- **Histogrammes** pour toutes les métriques sélectionnées
- **Tableau comparatif** des statistiques
- **Coefficient de variation** pour mesurer la dispersion

##### **Rankings**
- **Classements** sur la métrique choisie
- **Top N** personnalisable (5-20 joueurs)
- **Graphique en barres** interactif
- **Tableau détaillé** avec toutes les métriques

**💡 Cas d'usage** : Analyser en profondeur des métriques spécifiques et comprendre leurs relations.

### 🏅 **Mode "Comparaisons"**

#### **👤 Joueurs vs Joueurs**
- **Sélection multiple** jusqu'à 5 joueurs
- **Radar percentilé** (0-100% vs population)
- **Tableau comparatif** détaillé
- **Couleurs distinctives** par joueur

#### **⚽ Équipes vs Équipes**
- **Statistiques d'équipe** : moyenne, médiane, écart-type
- **Graphique avec barres d'erreur** pour visualiser la variabilité
- **Box plots** pour voir les distributions complètes
- **Nombre de joueurs** par équipe

#### **🎯 Joueur vs Moyenne du Poste**
- **Benchmarking automatique** contre la moyenne
- **Graphique en barres groupées** (joueur vs moyenne)
- **Calcul des écarts** absolus et en pourcentage
- **Coloration sémantique** : vert (>+10%), rouge (<-10%), jaune (neutre)

**💡 Cas d'usage** : Évaluer et comparer des performances individuelles ou collectives.

### 📈 **Mode "Tendances"**

#### **📅 Tendances par Âge**
- **Groupes d'âge automatiques** : ≤20, 21-23, 24-26, 27-30, 30+ ans
- **Graphiques par groupe** avec moyennes
- **Scatter plot âge/performance** avec courbe de tendance
- **Statistiques par tranche** d'âge

#### **⏱️ Tendances par Temps de Jeu**
- **Groupes de minutes** : <500, 500-1000, 1000-1500, 1500-2500, 2500+
- **Box plots** par groupe de temps de jeu
- **Scatter avec taille** proportionnelle aux minutes
- **Impact du volume** de jeu sur les performances

#### **🎯 Analyse Multi-dimensionnelle**
- **Graphique 3D** avec 3 métriques au choix
- **Coloration** par équipe et taille par minutes
- **Rotation interactive** pour exploration

#### **🤖 Clustering (Optionnel)**
- **K-means automatique** avec normalisation
- **Nombre de clusters** personnalisable (2-8)
- **Visualisation 3D** des groupes
- **Profils moyens** par cluster

**💡 Cas d'usage** : Identifier des patterns cachés et des profils types de joueurs.

## 🎨 Éléments d'Interface

### **Indicateurs KPI (Header)**
- **Joueurs analysés** : Nombre après filtrage
- **Équipes** : Nombre de clubs représentés
- **Âge moyen** : Moyenne d'âge de l'échantillon
- **Minutes moyennes** : Temps de jeu moyen
- **KPI analysés** : Nombre de métriques disponibles

### **Couleurs Sémantiques**
- **🟢 Vert** : Performance supérieure (+10%+)
- **🔴 Rouge** : Performance inférieure (-10%+)
- **🟡 Jaune** : Performance normale (±10%)
- **🔵 Bleu** : Informations neutres

### **Graphiques Interactifs**
- **Hover** : Informations détaillées au survol
- **Zoom** : Clic-glisser pour zoomer
- **Légende** : Clic pour masquer/afficher des séries
- **Download** : Bouton pour sauvegarder (PNG, SVG, PDF)

## 🔍 Conseils d'Utilisation

### **Pour Débuter**
1. **Commencez** par la "Vue d'ensemble" pour identifier les KPI intéressants
2. **Explorez** les corrélations pour comprendre les relations
3. **Approfondissez** avec les "KPI Détaillés" sur les métriques clés

### **Pour l'Analyse Avancée**
1. **Utilisez** les comparaisons pour le benchmarking
2. **Explorez** les tendances pour identifier les patterns
3. **Combinez** plusieurs modes pour une analyse complète

### **Pour les Présentations**
1. **Capturez** les graphiques via le bouton téléchargement
2. **Notez** les insights automatiques affichés
3. **Utilisez** les tableaux pour les données précises

## ⚠️ Points d'Attention

### **Interprétation des Données**
- Les **percentiles** (0-100) sont calculés au sein du poste
- Les **corrélations** ne impliquent pas causalité
- Les **moyennes** peuvent masquer la variabilité

### **Filtres et Échantillons**
- Vérifiez la **taille de l'échantillon** après filtrage
- Les **équipes** avec peu de joueurs peuvent biaiser les moyennes
- Le **seuil de minutes** influence la représentativité

### **Performance**
- Les analyses **3D et clustering** peuvent être lentes sur gros échantillons
- Utilisez les **filtres** pour accélérer les calculs complexes
- Le **cache** conserve les données entre les sessions

## 🚀 Raccourcis et Astuces

### **Navigation Rapide**
- **Sidebar** : Modifiez les filtres globaux à tout moment
- **Modes** : Basculez rapidement entre les analyses
- **Métriques** : Les sélections sont conservées dans chaque mode

### **Analyses Efficaces**
- **Corrélations fortes** (>0.7) révèlent des redondances ou synergies
- **Coefficients de variation élevés** identifient les métriques discriminantes
- **Outliers** dans les scatter plots révèlent des profils exceptionnels

### **Optimisation Performance**
- **Limitez** le nombre de métriques en analyse détaillée
- **Filtrez** par équipes pour réduire la taille des données
- **Désactivez** le clustering si non nécessaire

## 📞 Support et Dépannage

### **Erreurs Communes**
- **"Aucune donnée"** : Vérifiez les filtres appliqués
- **Graphiques vides** : Sélectionnez des métriques différentes
- **Performance lente** : Réduisez l'échantillon ou les métriques

### **Limitations Connues**
- **Postes disponibles** : Actuellement FW et DF uniquement
- **Données temps réel** : Non supportées actuellement
- **Export** : Utiliser les boutons de téléchargement des graphiques

---

**🎯 Objectif** : Ce guide vous permet d'exploiter pleinement les capacités du nouvel onglet KPI pour vos analyses de performance footballistique.

**📞 Contact** : Pour tout support technique ou suggestions d'amélioration, utilisez les canaux habituels de l'équipe.