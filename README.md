# 🎬 Movies Things Dashboard

Une expérience interactive et immersive pour explorer, analyser et prédire le monde du cinéma en combinant les données TMDB et IMDb.

## 📋 Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Configuration](#configuration)
- [Structure du projet](#structure-du-projet)
- [Utilisation](#utilisation)
- [Technologies](#technologies)

## 🎯 Aperçu

**Movies Things** est un dashboard Streamlit conçu pour les amateurs de cinéma et data scientists passionnés. Il offre une exploration complète des données cinématographiques à travers quatre sections principales :

- **Découverte** : Visualisez les derniers films en salle avec un carrousel esthétique
- **Comparaison** : Analysez en détail un film ou comparez deux films côte à côte
- **Data Analyse** : Explorez les tendances à travers genres, langues, notes et structures de votes
- **Machine Learning** : Prédisez la probabilité qu'un film remporte l'Oscar

## ✨ Fonctionnalités

### 👀 Découverte

Plongez dans les sorties cinéma actuelles avec une interface moderne :

- **Top 10 Carrousel** : Classez les films par popularité, meilleure note ou nombre de votes
- **Distribution des notes** : Visualisez l'histogramme des évaluations TMDB
- **Explore par tranche de notes** : Naviguez parmi les films d'une plage de notes spécifique
- **Analyse par pays/genre** : Découvrez les meilleures productions par langue et la répartition des genres
- **Popularité vs note** : Identifiez les pépites sous-estimées ou les blockbusters consensuels

### 📊 Comparaison

**Mode Analyse d'un film** :
- Recherche dynamique et enrichie de films TMDB
- Fiche détaillée avec poster, infos et indicateurs clés
- Trois visualisations au choix :
  - Répartition des notes IMDb (histogramme 1→10)
  - Revenus par pays/région (IMDb ou fallback TMDB)
  - Top 5 acteurs/doubleurs par popularité

**Mode Comparaison de deux films** :
- Interface côte à côte avec affiches
- Tableau comparatif complet (budget, revenus, notes, dates)
- Graphiques d'évaluations TMDB vs IMDb
- Analyse financière et ROI
- Comparaison du casting

### 📈 Data Analyse

Une analyse complète et explorable des films populaires :

- **Filtres globaux** : Année, langue originale, genre, nombre minimum de votes
- **Synthèse rapide** : Métriques clés (médiane, nombre de films)
- **Analyse des genres** : Notes moyennes, variabilité, top 10
- **Analyse temporelle** : Évolution des sorties et des notes par année
- **Structure des votes IMDb** : Écart-type, polarisation (parts de votes hauts/bas)
- **Analyse par langue** : Notes comparées et parts de marché
- **Matrice de corrélations** : Liens entre budget, popularité, revenus, notes

### 🤖 Machine Learning

Prédisez le potentiel Oscar d'un film :

- **Recherche intelligente** : Trouvez n'importe quel film TMDB
- **Construction de features** : Genres, notes TMDB/IMDb, runtime, prix présélectionnés
- **Modèle XGBoost** : Prédiction de probabilité d'Oscar basée sur Data_Final.csv
- **Résultats visuels** : Jauge de probabilité, barre de progression, interprétation
- **Détails du modèle** : Transparence sur les données et la méthodologie

### 🎨 Bonus : Expérience utilisateur

- **Animation d'intro** : Générique cinéma stylisé avec effets texte dynamiques
- **Musique ambiante** : Lecteur YouTube intégré (activable via bouton 🔊/🔇)
- **Design moderne** : Gradient noir-rouge, glassmorphism, animations au survol
- **Navigation fluide** : Carrousel de pages avec pastilles de progression
- **Responsive** : Adapté aux différentes tailles d'écran

## 🚀 Installation

### Prérequis

- Python 3.9+
- pip ou conda

### Étapes

```bash
# 1. Cloner le repository
git clone https://github.com/ton-repo/movies-things-dashboard.git
cd movies-things-dashboard

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les secrets (voir section Configuration)

# 5. Lancer l'application
streamlit run app.py
```

## 🔑 Configuration

### Secrets Streamlit

Crée un fichier `.streamlit/secrets.toml` à la racine du projet :

```toml
# TMDB API
TMDB_API_KEY = "ta_clé_api_v3_tmdb"
TMDB_API_READ_TOKEN = "ton_token_read_v4_tmdb"

# IMDb API (via RapidAPI)
RAPIDAPI_IMDB_KEY = "ta_clé_rapidapi_imdb"
```

### Obtenir les clés

1. **TMDB** : Inscris-toi sur [themoviedb.org](https://www.themoviedb.org/settings/api)
2. **IMDb via RapidAPI** : Accède à [rapidapi.com](https://rapidapi.com/SAdrian/api/imdb-api) et subscribe
3. Copie tes clés dans `.streamlit/secrets.toml`

### Fichiers modèle ML

Place les fichiers suivants dans un dossier `models/` à la racine :

```
models/
├── oscar_pipeline.joblib      # Pipeline XGBoost entraîné
└── oscar_train_cols.joblib    # Liste des colonnes d'entraînement
```

## 📁 Structure du projet

```
movies-things-dashboard/
├── app.py                      # Point d'entrée principal
├── discovery_page.py           # Page Découverte
├── compare_page.py             # Page Comparaison
├── analysis_page.py            # Page Data Analyse
├── ml_page.py                  # Page Machine Learning
├── tmdb_client.py              # Client API TMDB
├── imdb_client.py              # Client API IMDb
├── models/
│   ├── oscar_pipeline.joblib
│   └── oscar_train_cols.joblib
├── .streamlit/
│   └── secrets.toml            # Configuration sécurisée (à créer)
├── requirements.txt            # Dépendances Python
└── README.md                   # Ce fichier
```

## 💻 Utilisation

### Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre dans ton navigateur sur `http://localhost:8501`

### Parcours utilisateur

1. **Landing page** : Clique sur "🎬 Commencer l'expérience"
2. **Animation intro** : Regarde le générique cinéma (8 secondes)
3. **Navigation** : Utilise les boutons ⬅️/➡️ pour naviguer entre les sections
4. **Exploration** : Utilise les filtres et sélecteurs dans chaque page
5. **Musique** : Bascule la musique ambiante avec le bouton 🔊 en haut à droite

### Conseils

- **Découverte** : Parfait pour trouver des films en salle
- **Comparaison** : Utilise-le pour analyser tes films préférés
- **Data Analyse** : Applique les filtres pour affiner ton exploration
- **ML** : Teste la prédiction sur tes films favoris (résultats à interpréter avec prudence)

## 🛠️ Technologies

| Technologie | Utilisation |
|---|---|
| **Streamlit** | Framework principal pour l'interface |
| **Pandas** | Manipulation et analyse de données |
| **Altair** | Visualisations interactives |
| **XGBoost** | Modèle de prédiction ML |
| **Joblib** | Sérialisation des modèles |
| **NumPy** | Calculs numériques |
| **TMDB API** | Données cinématographiques |
| **IMDb API** (RapidAPI) | Données box office et votes détaillés |

## 📊 Sources de données

- **TMDB** : Films populaires, détails, genres, budgets, revenus, casting
- **IMDb** : Notes détaillées, histogrammes de votes, box office par région

## 🎨 Design & Style

- **Palette** : Noir profond (#050505) + rouge cinéma (#ed2b12)
- **Typographie** : Benguiat ITC pour les titres (style cinéma vintage)
- **Effets** : Gradients, glassmorphism, shadows profondes, animations fluides
- **CSS personnalisé** : Injecté globalement pour une cohérence maximale

## ⚠️ Limitations & Notes

- Les données IMDb peuvent être incomplètes pour certains films (API limitée)
- Les prédictions ML sont basées sur le dataset d'entraînement (à interpréter avec contexte)
- Le modèle prédit sur des "Best Picture Oscars" (adapter si autre catégorie)
- Les revenus TMDB sont approximatifs ; IMDb est plus fiable
- Rate limiting sur les appels API (utilisation de cache Streamlit)

## 🤝 Contribution

Les contributions sont bienvenues ! Pour proposer des améliorations :

1. Fork le projet
2. Crée une branche (`git checkout -b feature/AmazingFeature`)
3. Commit tes changements (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvre une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**BENOSMANE YACINE** 
**BENMOULOUD MEHDI**

---

**Bon streaming ! 🍿🎬**

Plonge-toi dans les données et découvre les secrets du septième art.