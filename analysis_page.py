# analysis_page.py

import math
import streamlit as st
import pandas as pd
import altair as alt

from tmdb_client import TMDBClient
from imdb_client import IMDbClient


# ===================== Helpers IMDb =====================

def safe_get_imdb_client() -> IMDbClient | None:
    """Retourne un client IMDb si la clé est dispo dans st.secrets, sinon None."""
    api_key = st.secrets.get("RAPIDAPI_IMDB_KEY")
    if not api_key:
        return None
    try:
        return IMDbClient(api_key=api_key)
    except Exception:
        return None


def parse_imdb_ratings_with_histogram(imdb_rating_data: dict | None):
    """
    Essaie de récupérer :
      - rating (float)
      - rating_count (int)
      - histogram (dict "1"→count, ..., "10"→count)

    Supporte plusieurs formats :
      - plat : { rating, ratingCount, ratingsHistograms: {...} }
      - GraphQL-like : { data: { title: { ratingsSummary, ratingsHistograms } } }
    """
    rating = None
    rating_count = None
    histogram = None

    if not isinstance(imdb_rating_data, dict):
        return None, None, None

    # ---- 1) Format plat ----
    rating = imdb_rating_data.get("rating") or imdb_rating_data.get("imdbRating")
    rating_count = (
        imdb_rating_data.get("ratingCount")
        or imdb_rating_data.get("voteCount")
        or imdb_rating_data.get("imdbVotes")
    )

    rh = imdb_rating_data.get("ratingsHistograms")
    if isinstance(rh, dict):
        block = rh.get("IMDb Users") or rh.get("IMDb users")
        if isinstance(block, dict):
            h = block.get("histogram")
            if isinstance(h, dict):
                histogram = h

    # ---- 2) Format data.title.* ----
    data_block = imdb_rating_data.get("data")
    if isinstance(data_block, dict):
        title_block = data_block.get("title", {})
        if isinstance(title_block, dict):
            rs = title_block.get("ratingsSummary")
            if isinstance(rs, dict):
                if rating is None:
                    rating = rs.get("aggregateRating")
                if rating_count is None:
                    rating_count = rs.get("voteCount")

            rh2 = title_block.get("ratingsHistograms")
            if isinstance(rh2, dict) and histogram is None:
                block2 = rh2.get("IMDb Users") or rh2.get("IMDb users")
                if isinstance(block2, dict):
                    h2 = block2.get("histogram")
                    if isinstance(h2, dict):
                        histogram = h2

    # Conversion propre du count en int
    if isinstance(rating_count, str):
        try:
            rating_count = int(rating_count.replace(",", ""))
        except ValueError:
            rating_count = None

    return rating, rating_count, histogram


def compute_imdb_hist_stats(hist: dict | None):
    """
    À partir d'un histogramme IMDb (clés '1'..'10'), calcule :
      - std des notes
      - share_high (>= 8)
      - share_low (<= 4)
      - polarization = share_high + share_low
    """
    if not isinstance(hist, dict) or not hist:
        return None, None, None, None

    buckets = []
    for k, v in hist.items():
        try:
            note = int(k)
            count = int(v)
            if count < 0:
                continue
            buckets.append((note, count))
        except Exception:
            continue

    if not buckets:
        return None, None, None, None

    total = sum(c for _, c in buckets)
    if total == 0:
        return None, None, None, None

    # Moyenne
    mean = sum(note * count for note, count in buckets) / total

    # Variance / std
    var = sum(count * (note - mean) ** 2 for note, count in buckets) / total
    std = math.sqrt(var)

    # Parts high / low
    high = sum(count for note, count in buckets if note >= 8)
    low = sum(count for note, count in buckets if note <= 4)

    share_high = high / total
    share_low = low / total
    polarization = share_high + share_low

    return std, share_high, share_low, polarization


# ===================== Chargement & enrichissement des données =====================

@st.cache_data(show_spinner=True)
def load_analysis_data(language: str = "fr-FR", nb_pages: int = 5) -> pd.DataFrame:
    """
    Charge un jeu de données riche pour l'analyse :
    - films populaires TMDB sur plusieurs pages
    - détails par film (budget, runtime, revenue)
    - stats IMDb (note, votes, dispersion, polarisation) si dispo
    - features dérivées (année, mois, genre principal, etc.)
    """
    client = TMDBClient(
        api_key_v3=st.secrets.get("TMDB_API_KEY"),
        read_token_v4=st.secrets.get("TMDB_API_READ_TOKEN"),
        language=language,
    )

    imdb_client = safe_get_imdb_client()

    # Films populaires
    genre_map = client.get_genre_map()
    movies = client.get_popular_movies(nb_pages=nb_pages)
    df = client.movies_to_dataframe(movies, genre_map)

    # Détails TMDB + IMDb par film
    details_by_id: dict[int, dict] = {}
    imdb_stats_by_id: dict[int, dict] = {}

    for m in movies:
        mid = m.get("id")
        if mid is None:
            continue

        # Détails TMDB
        try:
            d = client.get_movie_details(mid)
        except Exception:
            d = {}
        details_by_id[mid] = d

        # IMDb (optionnel)
        rating = None
        rating_count = None
        hist = None
        std = None
        share_high = None
        share_low = None
        polarization = None

        if imdb_client:
            imdb_id = d.get("imdb_id")
            if imdb_id:
                try:
                    imdb_raw = imdb_client.get_ratings(imdb_id)
                    rating, rating_count, hist = parse_imdb_ratings_with_histogram(
                        imdb_raw
                    )
                    std, share_high, share_low, polarization = compute_imdb_hist_stats(
                        hist
                    )
                except Exception:
                    pass

        imdb_stats_by_id[mid] = {
            "imdb_rating": rating,
            "imdb_votes": rating_count,
            "imdb_std": std,
            "imdb_share_high": share_high,
            "imdb_share_low": share_low,
            "imdb_polarization": polarization,
        }

    def _map_detail(movie_id, field):
        d = details_by_id.get(movie_id, {})
        value = d.get(field)
        # On remplace les 0 par NaN pour éviter de fausser les stats
        if isinstance(value, (int, float)) and value == 0:
            return None
        return value

    df["budget"] = df["id"].map(lambda x: _map_detail(x, "budget"))
    df["runtime"] = df["id"].map(lambda x: _map_detail(x, "runtime"))
    df["revenue"] = df["id"].map(lambda x: _map_detail(x, "revenue"))

    # Ajout IMDb (si dispo)
    df["imdb_rating"] = df["id"].map(
        lambda x: imdb_stats_by_id.get(x, {}).get("imdb_rating")
    )
    df["imdb_votes"] = df["id"].map(
        lambda x: imdb_stats_by_id.get(x, {}).get("imdb_votes")
    )
    df["imdb_std"] = df["id"].map(
        lambda x: imdb_stats_by_id.get(x, {}).get("imdb_std")
    )
    df["imdb_share_high"] = df["id"].map(
        lambda x: imdb_stats_by_id.get(x, {}).get("imdb_share_high")
    )
    df["imdb_share_low"] = df["id"].map(
        lambda x: imdb_stats_by_id.get(x, {}).get("imdb_share_low")
    )
    df["imdb_polarization"] = df["id"].map(
        lambda x: imdb_stats_by_id.get(x, {}).get("imdb_polarization")
    )

    # Dates / temps
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["release_year"] = df["release_date"].dt.year
    df["release_month"] = df["release_date"].dt.to_period("M").astype("string")

    # Genre principal (premier genre de la liste)
    def _main_genre(genres):
        if isinstance(genres, list) and len(genres) > 0:
            return genres[0]
        return None

    df["main_genre"] = df["genres"].apply(_main_genre)

    return df.dropna(subset=["title"]).reset_index(drop=True)


# ===================== Page Data Analyse =====================


def render_analysis_page():
    st.markdown("## 📊 Data Analyse TMDB + IMDb")
    st.caption(
        "Vue globale des films populaires : notes, popularité, budget, mais aussi structure des votes IMDb "
        "(dispersion, polarisation...)."
    )

    with st.spinner("Chargement et enrichissement des données TMDB & IMDb..."):
        df = load_analysis_data("fr-FR", nb_pages=5)

    if df.empty:
        st.warning("Impossible de charger les données TMDB pour l'analyse.")
        return

    # ----------------- FILTRES GLOBAUX -----------------
    st.markdown("### 🎚️ Filtres globaux")

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    # Années
    years = sorted(y for y in df["release_year"].dropna().unique())
    if years:
        year_min, year_max = int(min(years)), int(max(years))
    else:
        year_min, year_max = 2000, 2025

    with col_f1:
        year_range = st.slider(
            "Année de sortie",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max),
            step=1,
        )

    # Langues
    langs = sorted(df["original_language"].dropna().unique())
    with col_f2:
        selected_langs = st.multiselect(
            "Langue originale",
            options=langs,
            default=langs[:3] if len(langs) >= 3 else langs,
            format_func=lambda x: x.upper(),
        )

    # Genres
    genres = sorted(g for g in df["main_genre"].dropna().unique())
    with col_f3:
        selected_genres = st.multiselect(
            "Genre principal",
            options=genres,
            default=genres[:3] if len(genres) >= 3 else genres,
        )

    # Seuil de votes TMDB
    with col_f4:
        max_votes = int(df["vote_count"].fillna(0).max())
        min_votes = st.slider(
            "Nombre minimal de votes TMDB",
            min_value=0,
            max_value=max(50, max_votes),
            value=50,
            step=10,
        )

    # Application des filtres
    mask = pd.Series(True, index=df.index)

    mask &= df["release_year"].between(year_range[0], year_range[1])
    if selected_langs:
        mask &= df["original_language"].isin(selected_langs)
    if selected_genres:
        mask &= df["main_genre"].isin(selected_genres)
    mask &= df["vote_count"].fillna(0) >= min_votes

    df_filt = df[mask].copy()

    st.caption(
        f"Après filtres : **{len(df_filt)} films** (sur {len(df)} films populaires récupérés)."
    )

    if df_filt.empty:
        st.warning("Aucun film ne correspond à ces filtres. Relaxe un peu les contraintes 😉")
        return

    st.markdown("---")

    # ===================== 1. SYNTHÈSE RAPIDE =====================
    st.markdown("### 🧭 Synthèse rapide")

    col_k1, col_k2, col_k3, col_k4 = st.columns(4)

    with col_k1:
        st.metric("🎬 Nombre de films", f"{len(df_filt):d}")

    with col_k2:
        st.metric(
            "⭐ Note TMDB médiane",
            f"{df_filt['vote_average'].median():.1f}"
            if df_filt["vote_average"].notna().any()
            else "n/a",
        )

    with col_k3:
        if df_filt["imdb_rating"].notna().any():
            st.metric(
                "⭐ Note IMDb médiane",
                f"{df_filt['imdb_rating'].median():.1f}",
            )
        else:
            st.metric("⭐ Note IMDb médiane", "IMDb non dispo")

    with col_k4:
        if df_filt["imdb_votes"].notna().any():
            st.metric(
                "🗳️ Médiane votes IMDb",
                f"{int(df_filt['imdb_votes'].median()):,}",
            )
        else:
            st.metric("🗳️ Médiane votes IMDb", "n/a")

    col_k5, col_k6, col_k7, col_k8 = st.columns(4)

    with col_k5:
        if df_filt["imdb_std"].notna().any():
            st.metric("📦 Médiane σ IMDb", f"{df_filt['imdb_std'].median():.2f}")
        else:
            st.metric("📦 Médiane σ IMDb", "n/a")

    with col_k6:
        if df_filt["imdb_share_high"].notna().any():
            st.metric(
                "🟢 Part médiane votes 8–10",
                f"{100 * df_filt['imdb_share_high'].median():.1f}%",
            )
        else:
            st.metric("🟢 Part médiane votes 8–10", "n/a")

    with col_k7:
        if df_filt["imdb_share_low"].notna().any():
            st.metric(
                "🔴 Part médiane votes 1–4",
                f"{100 * df_filt['imdb_share_low'].median():.1f}%",
            )
        else:
            st.metric("🔴 Part médiane votes 1–4", "n/a")

    with col_k8:
        if df_filt["imdb_polarization"].notna().any():
            st.metric(
                "⚡ Polarisation médiane",
                f"{100 * df_filt['imdb_polarization'].median():.1f}%",
            )
        else:
            st.metric("⚡ Polarisation médiane", "n/a")

    st.markdown("---")

    # ===================== 2. ANALYSE DES GENRES =====================
    st.markdown("### 🎭 Analyse des genres")

    df_genres = df_filt.explode("genres").dropna(subset=["genres"])
    if df_genres.empty:
        st.info("Pas assez de données de genres pour cette sélection.")
    else:
        df_genres_agg = (
            df_genres.groupby("genres")
            .agg(
                note_moy_tmdb=("vote_average", "mean"),
                note_moy_imdb=("imdb_rating", "mean"),
                pop_moy=("popularity", "mean"),
                nb_films=("id", "count"),
                std_moy_imdb=("imdb_std", "mean"),
                pol_moy_imdb=("imdb_polarization", "mean"),
            )
            .reset_index()
        )

        df_genres_top = df_genres_agg.sort_values("nb_films", ascending=False).head(10)

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("#### ⭐ Note moyenne TMDB par genre")
            chart_note_tmdb = (
                alt.Chart(df_genres_top)
                .mark_bar()
                .encode(
                    x=alt.X("note_moy_tmdb:Q", title="Note moyenne TMDB"),
                    y=alt.Y("genres:N", sort="-x", title="Genre"),
                    color=alt.value("#ed2b12"),
                    tooltip=[
                        alt.Tooltip("genres:N", title="Genre"),
                        alt.Tooltip(
                            "note_moy_tmdb:Q", title="Note moyenne TMDB", format=".2f"
                        ),
                        alt.Tooltip("nb_films:Q", title="Nombre de films"),
                    ],
                )
                .properties(height=320)
            )
            st.altair_chart(chart_note_tmdb, use_container_width=True)

        with col_g2:
            st.markdown("#### ⭐ Note moyenne IMDb par genre (si dispo)")
            df_imdb_genre = df_genres_top.dropna(subset=["note_moy_imdb"])
            if df_imdb_genre.empty:
                st.info("Pas assez de données IMDb pour calculer les moyennes par genre.")
            else:
                chart_note_imdb = (
                    alt.Chart(df_imdb_genre)
                    .mark_bar()
                    .encode(
                        x=alt.X("note_moy_imdb:Q", title="Note moyenne IMDb"),
                        y=alt.Y("genres:N", sort="-x", title="Genre"),
                        color=alt.value("#ffb74d"),
                        tooltip=[
                            alt.Tooltip("genres:N", title="Genre"),
                            alt.Tooltip(
                                "note_moy_imdb:Q",
                                title="Note moyenne IMDb",
                                format=".2f",
                            ),
                            alt.Tooltip("nb_films:Q", title="Nombre de films"),
                        ],
                    )
                    .properties(height=320)
                )
                st.altair_chart(chart_note_imdb, use_container_width=True)

        st.caption(
            "À gauche : vision TMDB par genre. À droite : vision IMDb moyennée par genre (quand les données existent)."
        )

        # Boxplot des notes TMDB par genre
        st.markdown("#### 📦 Variabilité des notes TMDB par genre")
        df_box = df_genres[df_genres["vote_average"].notna()]
        if not df_box.empty:
            chart_box = (
                alt.Chart(df_box)
                .mark_boxplot()
                .encode(
                    x=alt.X("genres:N", title="Genre", sort="-y"),
                    y=alt.Y("vote_average:Q", title="Note TMDB"),
                    tooltip=[alt.Tooltip("genres:N", title="Genre")],
                )
                .properties(height=360)
            )
            st.altair_chart(chart_box, use_container_width=True)
            st.caption(
                "Les genres avec des boxplots serrés sont plus stables en qualité TMDB, "
                "ceux avec de longues moustaches ont des films très inégaux."
            )

    st.markdown("---")

    # ===================== 3. ANALYSE TEMPORELLE =====================
    st.markdown("### ⏱️ Analyse temporelle")

    df_time = df_filt.dropna(subset=["release_year"])
    if df_time.empty:
        st.info("Pas assez de dates de sortie pour construire une analyse temporelle.")
    else:
        df_year = (
            df_time.groupby("release_year")
            .agg(
                nb_films=("id", "count"),
                note_moy_tmdb=("vote_average", "mean"),
                note_moy_imdb=("imdb_rating", "mean"),
            )
            .reset_index()
            .sort_values("release_year")
        )

        col_t1, col_t2 = st.columns(2)

        with col_t1:
            st.markdown("#### 🎬 Nombre de films sortis par année")
            chart_nb = (
                alt.Chart(df_year)
                .mark_line(point=True)
                .encode(
                    x=alt.X("release_year:O", title="Année"),
                    y=alt.Y("nb_films:Q", title="Nombre de films"),
                    tooltip=[
                        alt.Tooltip("release_year:O", title="Année"),
                        alt.Tooltip("nb_films:Q", title="Films"),
                    ],
                )
                .properties(height=260)
            )
            st.altair_chart(chart_nb, use_container_width=True)

        with col_t2:
            st.markdown("#### ⭐ Notes moyennes TMDB / IMDb par année")

            df_year_long = df_year.melt(
                id_vars=["release_year"],
                value_vars=["note_moy_tmdb", "note_moy_imdb"],
                var_name="source",
                value_name="note_moy",
            )
            df_year_long["source"] = df_year_long["source"].map(
                {"note_moy_tmdb": "TMDB", "note_moy_imdb": "IMDb"}
            )

            chart_note_year = (
                alt.Chart(df_year_long)
                .mark_line(point=True)
                .encode(
                    x=alt.X("release_year:O", title="Année"),
                    y=alt.Y("note_moy:Q", title="Note moyenne"),
                    color=alt.Color(
                        "source:N",
                        title="Source",
                        scale=alt.Scale(range=["#ed2b12", "#ffb74d"]),
                    ),
                    tooltip=[
                        alt.Tooltip("release_year:O", title="Année"),
                        alt.Tooltip("source:N", title="Source"),
                        alt.Tooltip("note_moy:Q", title="Note moyenne", format=".2f"),
                    ],
                )
                .properties(height=260)
            )
            st.altair_chart(chart_note_year, use_container_width=True)

        st.caption(
            "Évolution dans le temps de la qualité moyenne perçue côté TMDB et côté IMDb."
        )

    st.markdown("---")

    # ===================== 3bis. STRUCTURE DES VOTES IMDb =====================
    st.markdown("### 🧪 Structure des votes IMDb")

    df_imdb = df_filt.dropna(subset=["imdb_std"])
    if df_imdb.empty:
        st.info("Pas assez de films avec histogramme IMDb pour analyser la structure des votes.")
    else:
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            st.markdown("#### 📦 Distribution de l'écart-type IMDb")
            chart_std = (
                alt.Chart(df_imdb)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "imdb_std:Q",
                        bin=alt.Bin(step=0.1),
                        title="σ IMDb (dispersion des notes)",
                    ),
                    y=alt.Y("count():Q", title="Nombre de films"),
                    tooltip=[alt.Tooltip("count():Q", title="Films")],
                )
                .properties(height=260)
            )
            st.altair_chart(chart_std, use_container_width=True)

        with col_s2:
            st.markdown("#### ⚡ Polarisation IMDb vs note moyenne IMDb")
            df_pol_scatter = df_imdb.dropna(
                subset=["imdb_polarization", "imdb_rating"]
            )
            if df_pol_scatter.empty:
                st.info("Pas assez de données pour le scatter polarisation vs note.")
            else:
                chart_pol_scatter = (
                    alt.Chart(df_pol_scatter)
                    .mark_circle(size=70, opacity=0.7)
                    .encode(
                        x=alt.X("imdb_rating:Q", title="Note IMDb"),
                        y=alt.Y(
                            "imdb_polarization:Q",
                            title="Polarisation (part votes 1–4 & 8–10)",
                        ),
                        color=alt.Color("main_genre:N", title="Genre principal"),
                        tooltip=[
                            alt.Tooltip("title:N", title="Titre"),
                            alt.Tooltip("main_genre:N", title="Genre"),
                            alt.Tooltip(
                                "imdb_rating:Q", title="Note IMDb", format=".1f"
                            ),
                            alt.Tooltip(
                                "imdb_polarization:Q",
                                title="Polarisation",
                                format=".2f",
                            ),
                            alt.Tooltip("imdb_votes:Q", title="Votes IMDb"),
                        ],
                    )
                    .properties(height=260)
                )
                st.altair_chart(chart_pol_scatter, use_container_width=True)

        st.caption(
            "À gauche : films plutôt consensuels (σ faible) vs controversés (σ fort). "
            "À droite : films très aimés ou détestés avec une forte polarisation des votes."
        )

    st.markdown("---")

    # ===================== 4. ANALYSE PAYS / LANGUES =====================
    st.markdown("### 🌍 Analyse par langue / pays")

    df_lang = (
        df_filt.groupby("original_language")
        .agg(
            nb_films=("id", "count"),
            note_moy_tmdb=("vote_average", "mean"),
            note_moy_imdb=("imdb_rating", "mean"),
            pol_moy_imdb=("imdb_polarization", "mean"),
            pop_moy=("popularity", "mean"),
        )
        .reset_index()
    )

    if df_lang.empty:
        st.info("Pas assez d'information de langue pour cette sélection.")
    else:
        df_lang = df_lang.sort_values("nb_films", ascending=False)
        df_lang["lang_label"] = df_lang["original_language"].str.upper()
        df_lang["part"] = df_lang["nb_films"] / df_lang["nb_films"].sum()

        col_l1, col_l2 = st.columns(2)

        with col_l1:
            st.markdown("#### 🏳️ Notes moyennes TMDB / IMDb par langue")

            df_lang_long = df_lang.melt(
                id_vars=["lang_label"],
                value_vars=["note_moy_tmdb", "note_moy_imdb"],
                var_name="source",
                value_name="note_moy",
            )
            df_lang_long["source"] = df_lang_long["source"].map(
                {"note_moy_tmdb": "TMDB", "note_moy_imdb": "IMDb"}
            )

            chart_lang = (
                alt.Chart(df_lang_long)
                .mark_bar()
                .encode(
                    x=alt.X("note_moy:Q", title="Note moyenne"),
                    y=alt.Y("lang_label:N", sort="-x", title="Langue"),
                    color=alt.Color(
                        "source:N",
                        title="Source",
                        scale=alt.Scale(range=["#ed2b12", "#ffb74d"]),
                    ),
                    tooltip=[
                        alt.Tooltip("lang_label:N", title="Langue"),
                        alt.Tooltip("source:N", title="Source"),
                        alt.Tooltip("note_moy:Q", title="Note moyenne", format=".2f"),
                    ],
                )
                .properties(height=320)
            )
            st.altair_chart(chart_lang, use_container_width=True)

        with col_l2:
            st.markdown("#### 🥧 Part de marché des langues (nombre de films)")

            chart_lang_share = (
                alt.Chart(df_lang)
                .mark_arc(innerRadius=60, outerRadius=120)
                .encode(
                    theta=alt.Theta("nb_films:Q", title="Nombre de films"),
                    color=alt.Color("lang_label:N", title="Langue"),
                    tooltip=[
                        alt.Tooltip("lang_label:N", title="Langue"),
                        alt.Tooltip("nb_films:Q", title="Nombre de films"),
                        alt.Tooltip("part:Q", title="Part", format=".0%"),
                    ],
                )
                .properties(height=320)
            )
            st.altair_chart(chart_lang_share, use_container_width=True)

        st.caption(
            "Langues les plus présentes dans les films populaires, et leur niveau moyen côté TMDB / IMDb."
        )

    st.markdown("---")

    # ===================== 5. CORRÉLATIONS GLOBALES =====================
    st.markdown("### 🔗 Corrélations & liens entre variables")

    numeric_cols = [
        "vote_average",
        "imdb_rating",
        "vote_count",
        "imdb_votes",
        "popularity",
        "budget",
        "runtime",
        "revenue",
        "imdb_std",
        "imdb_polarization",
        "imdb_share_high",
        "imdb_share_low",
    ]
    df_corr = df_filt[numeric_cols].dropna(how="all")

    if df_corr.empty:
        st.info(
            "Pas assez de données numériques (budget / runtime / IMDb) "
            "pour construire une matrice de corrélation."
        )
        return

    corr_matrix = df_corr.corr()
    corr_df = (
        corr_matrix.reset_index()
        .melt(id_vars="index", var_name="variable", value_name="correlation")
        .rename(columns={"index": "feature"})
    )

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("#### 🧩 Matrice de corrélation TMDB + IMDb")
        heatmap = (
            alt.Chart(corr_df)
            .mark_rect()
            .encode(
                x=alt.X("feature:N", title=""),
                y=alt.Y("variable:N", title=""),
                color=alt.Color(
                    "correlation:Q",
                    scale=alt.Scale(scheme="redblue", domain=(-1, 1)),
                    title="Corrélation",
                ),
                tooltip=[
                    alt.Tooltip("feature:N", title="Variable 1"),
                    alt.Tooltip("variable:N", title="Variable 2"),
                    alt.Tooltip("correlation:Q", title="Corrélation", format=".2f"),
                ],
            )
            .properties(height=320)
        )
        st.altair_chart(heatmap, use_container_width=True)

    with col_c2:
        st.markdown("#### 💸 Budget vs popularité (par genre principal)")

        df_scatter = df_filt.copy()
        df_scatter = df_scatter[
            df_scatter["budget"].notna() & df_scatter["popularity"].notna()
        ]
        if df_scatter.empty:
            st.info("Pas assez de films avec budget renseigné pour le scatter.")
        else:
            scatter = (
                alt.Chart(df_scatter)
                .mark_circle(size=70, opacity=0.7)
                .encode(
                    x=alt.X(
                        "budget:Q",
                        title="Budget (USD)",
                        scale=alt.Scale(type="log"),
                    ),
                    y=alt.Y("popularity:Q", title="Popularité TMDB"),
                    color=alt.Color(
                        "main_genre:N",
                        title="Genre principal",
                    ),
                    tooltip=[
                        alt.Tooltip("title:N", title="Titre"),
                        alt.Tooltip("main_genre:N", title="Genre"),
                        alt.Tooltip("budget:Q", title="Budget", format=".2s"),
                        alt.Tooltip("popularity:Q", title="Popularité", format=".1f"),
                        alt.Tooltip("vote_average:Q", title="Note TMDB", format=".1f"),
                        alt.Tooltip("imdb_rating:Q", title="Note IMDb", format=".1f"),
                        alt.Tooltip("imdb_std:Q", title="σ IMDb", format=".2f"),
                        alt.Tooltip(
                            "imdb_polarization:Q",
                            title="Polarisation",
                            format=".2f",
                        ),
                    ],
                )
                .properties(height=320)
            )
            st.altair_chart(scatter, use_container_width=True)

    st.caption(
        "Cette section met en évidence les liens entre budget, popularité, notes TMDB / IMDb, "
        "dispersion des votes, polarisation, etc. Bref : le mix complet pour jouer au data scientist."
    )
