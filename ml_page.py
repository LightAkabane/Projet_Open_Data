import math
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import streamlit as st
import joblib

from tmdb_client import TMDBClient
from imdb_client import IMDbClient


# =========================================================
# Chargement du modèle & des colonnes
# =========================================================
@st.cache_resource
def load_model_and_columns():
    """
    Charge le pipeline entraîné + la liste des colonnes d'entraînement.
    On importe XGBClassifier ici pour que joblib puisse le "déserialiser".
    """
    from xgboost import XGBClassifier  # noqa: F401

    pipeline = joblib.load("models/oscar_pipeline.joblib")
    train_cols: List[str] = joblib.load("models/oscar_train_cols.joblib")
    return pipeline, train_cols


@st.cache_resource
def get_tmdb_client() -> TMDBClient:
    return TMDBClient()


@st.cache_resource
def get_imdb_client() -> IMDbClient:
    return IMDbClient()


# =========================================================
# Helpers pour récupérer proprement IMDb
# =========================================================
def safe_get_imdb_ratings(imdb_client: IMDbClient, imdb_id: str | None) -> Dict[str, Any] | None:
    if not imdb_id:
        return None
    try:
        return imdb_client.get_ratings(imdb_id)
    except Exception:
        return None


def safe_get_imdb_business(imdb_client: IMDbClient, imdb_id: str | None) -> Dict[str, Any] | None:
    if not imdb_id:
        return None
    try:
        return imdb_client.get_business(imdb_id)
    except Exception:
        return None


def extract_lifetime_gross_usd(business_json: Dict[str, Any] | None) -> float | None:
    """
    Extrait le box office total si disponible.
    """
    if not business_json:
        return None

    try:
        box_office = business_json.get("boxOffice") or {}
        total = box_office.get("totalLifetimeGross") or {}
        total_total = total.get("total") or {}
        amount = total_total.get("amount")
        return float(amount) if amount is not None else None
    except Exception:
        return None


# =========================================================
# Construction des features pour un film TMDB
# =========================================================
def build_features_for_movie(
    tmdb_client: TMDBClient,
    imdb_client: IMDbClient,
    tmdb_movie: Dict[str, Any],
    train_cols: List[str],
) -> pd.DataFrame:
    """
    Construit UNE ligne de features dans le même format que X dans Data_Final.csv.
    """

    movie_id = tmdb_movie["id"]
    details = tmdb_client.get_movie_details(movie_id)

    # --------- Récup données TMDB / IMDb ---------
    imdb_id = details.get("imdb_id")
    imdb_ratings = safe_get_imdb_ratings(imdb_client, imdb_id)

    notes_tmdb = details.get("vote_average")
    runtime = details.get("runtime")
    notes_imdb = imdb_ratings.get("rating") if imdb_ratings else np.nan

    notes_rt = np.nan
    notes_meta = np.nan

    bafta = False
    dga = False
    pga = False
    sag = False
    gg = False
    nomination_count = 0

    # Genres TMDB -> dummies
    all_genres_cols = [
        "Action", "Adventure", "Animation", "Comedy", "Crime",
        "Documentary", "Drama", "Family", "Fantasy", "History",
        "Horror", "Music", "Mystery", "Romance", "Science Fiction",
        "Thriller", "War", "Western",
    ]

    genre_flags = {g: 0 for g in all_genres_cols}

    tmdb_genres = details.get("genres") or []
    genre_names = {g.get("name") for g in tmdb_genres if g.get("name")}

    for g in all_genres_cols:
        if g in genre_names:
            genre_flags[g] = 1

    unnamed_0_2 = 0

    base_row = {
        "Unnamed: 0.2": unnamed_0_2,
        "BAFTA": bafta,
        "DGA": dga,
        "PGA": pga,
        "SAG": sag,
        "GG": gg,
        "NotesTMDb": notes_tmdb,
        "Runtime": runtime,
        "NotesIMDb": notes_imdb,
        "NotesRottenTomatoes": notes_rt,
        "NotesMetacritic": notes_meta,
        "nomination_count": nomination_count,
    }

    base_row.update(genre_flags)

    df = pd.DataFrame([base_row])

    # --------- Alignement sur les colonnes d'entraînement ---------
    for col in train_cols:
        if col not in df.columns:
            df[col] = 0

    extra_cols = [c for c in df.columns if c not in train_cols]
    if extra_cols:
        df = df.drop(columns=extra_cols)

    df = df[train_cols]

    return df


# =========================================================
# Formatage du résultat
# =========================================================
def format_movie_option(movie: Dict[str, Any]) -> str:
    title = movie.get("title") or movie.get("original_title") or "Titre inconnu"
    release_date = movie.get("release_date") or ""
    year_display = release_date[:4] if release_date else "????"
    vote = movie.get("vote_average")
    if vote is not None:
        return f"{title} ({year_display}) - Note TMDB {vote:.1f}"
    return f"{title} ({year_display})"


def render_prediction_result(proba_oscar: float, selected_movie: Dict[str, Any]):
    """Affiche le résultat de la prédiction avec style."""
    
    st.markdown("---")
    
    # Déterminer la couleur et le message selon la probabilité
    if proba_oscar >= 0.7:
        color = "🟢"
        sentiment = "Très prometteur !"
        description = "Ce film a une forte chance de remporter l'Oscar selon le modèle."
    elif proba_oscar >= 0.5:
        color = "🟡"
        sentiment = "Candidat potentiel"
        description = "Ce film pourrait être un prétendant crédible à l'Oscar."
    elif proba_oscar >= 0.3:
        color = "🟠"
        sentiment = "Chance modérée"
        description = "Ce film a une chance, mais d'autres sont plus favorisés."
    else:
        color = "🔴"
        sentiment = "Moins probable"
        description = "Selon le modèle, ce film a peu de chances de remporter l'Oscar."

    # Affichage du résultat
    col_result, col_sentiment = st.columns([1.5, 2])
    
    with col_result:
        st.metric(
            label="Probabilité estimée",
            value=f"{proba_oscar * 100:.1f}%",
            delta=None,
        )
    
    with col_sentiment:
        st.markdown(f"### {color} {sentiment}")
        st.caption(description)
    
    # Barre de progression
    st.progress(min(max(proba_oscar, 0.0), 1.0))
    
    # Informations contextuelles
    with st.expander("📊 Détails du modèle", expanded=False):
        st.markdown("""
        - **Type de modèle** : XGBoost Classifier
        - **Données d'entraînement** : Data_Final.csv
        - **Features** : Notes TMDB/IMDb, genres, prix présélectionnés, runtime
        - **Cible** : Probabilité de remporter l'Oscar (Best Picture)
        """)


# =========================================================
# UI principale de la page ML
# =========================================================
def render_ml_page():
    # --------- En-tête avec style ---------
    st.markdown("""
    <style>
    .main-title {
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .subtitle {
        font-size: 1.1em;
        color: #888;
        margin-bottom: 1.5em;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-title">🏆 Prédicteur d\'Oscar</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Découvre la probabilité qu\'un film remporte l\'Oscar '
        'en basant sur ses caractéristiques</div>',
        unsafe_allow_html=True
    )

    # Chargement des clients et modèle
    tmdb_client = get_tmdb_client()
    imdb_client = get_imdb_client()

    try:
        pipeline, train_cols = load_model_and_columns()
    except Exception as e:
        st.error(
            "❌ Impossible de charger le modèle (`oscar_pipeline.joblib`) ou les colonnes "
            "(`oscar_train_cols.joblib`). Vérifie que les fichiers existent bien dans `models/`."
        )
        st.exception(e)
        return

    # --------- Section de recherche ---------
    st.markdown("### 🔍 Recherche du film")
    
    search_col, year_col = st.columns([3, 1])

    with search_col:
        query = st.text_input(
            "Titre du film",
            placeholder="Ex : Oppenheimer, Dune, Parasite...",
            label_visibility="collapsed"
        )

    with year_col:
        year_str = st.text_input(
            "Année (optionnel)",
            value="",
            placeholder="2024",
            label_visibility="collapsed"
        )

    if not query:
        st.info("💡 Commence par saisir le titre d'un film pour commencer")
        return

    # Parse l'année si fournie
    year_param: int | None = None
    if year_str.strip():
        try:
            year_param = int(year_str)
        except ValueError:
            st.warning("⚠️ Année invalide, je l'ignore pour la recherche.")
            year_param = None

    # Recherche TMDB
    with st.spinner("🔄 Recherche de films sur TMDB..."):
        try:
            search_results = tmdb_client.search_movies(query=query, year=year_param)
        except Exception as e:
            st.error("❌ Erreur lors de l'appel à l'API TMDB.")
            st.exception(e)
            return

    if not search_results:
        st.warning("😕 Aucun film trouvé avec ces critères. Essaie un autre titre ou enlève l'année.")
        return

    # --------- Sélection du film ---------
    st.markdown("### 📽️ Sélection du film")
    
    indexed_results: List[Tuple[int, Dict[str, Any]]] = list(enumerate(search_results))
    selected_idx = st.selectbox(
        "Choisis un film dans les résultats",
        options=[i for i, _ in indexed_results],
        format_func=lambda idx: format_movie_option(search_results[idx]),
        label_visibility="collapsed"
    )

    selected_movie = search_results[selected_idx]

    # --------- Affichage du film sélectionné ---------
    st.markdown("---")
    st.markdown("### 🎬 Détails du film")

    col_poster, col_info = st.columns([1, 2], gap="medium")

    with col_poster:
        poster_url = TMDBClient.build_poster_url(selected_movie.get("poster_path"))
        if poster_url:
            st.image(poster_url, use_container_width=True)
        else:
            st.info("Aucune affiche disponible")

    with col_info:
        title = selected_movie.get("title") or selected_movie.get("original_title")
        overview = selected_movie.get("overview") or "Pas de synopsis disponible."
        release_date = selected_movie.get("release_date") or "Date inconnue"
        vote_avg = selected_movie.get("vote_average")
        vote_count = selected_movie.get("vote_count")

        st.markdown(f"#### {title}")
        
        # Infos structurées
        col_date, col_rating = st.columns(2)
        with col_date:
            st.caption("📅 Date de sortie")
            st.markdown(release_date)
        with col_rating:
            st.caption("⭐ Note TMDB")
            if vote_avg is not None and vote_count is not None:
                st.markdown(f"{vote_avg:.1f}/10 ({vote_count} votes)")
            else:
                st.markdown("Non disponible")
        
        st.caption("📝 Synopsis")
        st.markdown(overview)

    # --------- Bouton de prédiction ---------
    st.markdown("---")
    
    predict_button = st.button(
        "🏆 Prédire la probabilité d'Oscar",
        use_container_width=True,
        type="primary"
    )

    if predict_button:
        with st.spinner("⏳ Construction des features et prédiction en cours..."):
            try:
                features_df = build_features_for_movie(
                    tmdb_client=tmdb_client,
                    imdb_client=imdb_client,
                    tmdb_movie=selected_movie,
                    train_cols=train_cols,
                )
                
                # Prédiction
                proba_all = pipeline.predict_proba(features_df)[0]

                classes = list(getattr(pipeline, "classes_", []))
                if classes and 1 in classes:
                    pos_idx = classes.index(1)
                else:
                    pos_idx = len(proba_all) - 1

                proba_oscar = float(proba_all[pos_idx])

            except Exception as e:
                st.error(
                    "❌ Erreur lors de la prédiction. Vérifie que les features sont cohérentes "
                    "avec celles utilisées lors de l'entraînement (Data_Final.csv)."
                )
                st.exception(e)
                return

        # Affichage du résultat
        render_prediction_result(proba_oscar, selected_movie)