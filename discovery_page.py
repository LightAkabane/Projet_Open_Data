# discovery_page.py

import streamlit as st
import pandas as pd
import altair as alt
import streamlit.components.v1 as components
from tmdb_client import TMDBClient

# ===================== CSS scroll horizontal + cartes top 10 =====================

TOP10_CSS = """
<style>

:root {
    --color-bg: #050509;
    --color-card: rgba(15, 15, 20, 0.95);
    --color-border: rgba(255, 255, 255, 0.06);
    --color-border-strong: rgba(237, 43, 18, 0.65);
    --color-accent: #ed2b12;
    --color-accent-soft: rgba(237, 43, 18, 0.16);
    --color-text-main: #f7f7f7;
    --color-text-muted: #9a9a9a;
    --color-chip-bg: rgba(255, 255, 255, 0.03);
}

* {
    box-sizing: border-box;
}

/* ===================== CONTAINER & SCROLL ===================== */

.top10-container {
    width: 100%;
    padding: 0.5rem 0 0.25rem 0;
}

.top10-scroll {
    display: flex;
    flex-direction: row;
    gap: 1.2rem;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 0.75rem 0.25rem 0.4rem 0.25rem;
    scroll-behavior: smooth;
}

.top10-scroll::-webkit-scrollbar {
    height: 8px;
}
.top10-scroll::-webkit-scrollbar-track {
    background: #050509;
}
.top10-scroll::-webkit-scrollbar-thumb {
    background: linear-gradient(to right, #ed2b12, #ff7847);
    border-radius: 999px;
}

/* ===================== MOVIE CARD ===================== */

.movie-card {
    flex: 0 0 240px;
    position: relative;
    transform-origin: center;
    transition: transform 0.25s ease, filter 0.25s ease;
    padding: 0.35rem;
}

.movie-card-inner {
    position: relative;
    border-radius: 18px;
    padding: 0.75rem;
    background: radial-gradient(circle at top left, rgba(237, 43, 18, 0.16), transparent 55%),
                radial-gradient(circle at bottom right, rgba(255, 255, 255, 0.04), transparent 55%),
                var(--color-card);
    border: 1px solid var(--color-border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 100%;
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.65);
    backdrop-filter: blur(12px);
}

/* Hover global de la carte */
.movie-card:hover {
    transform: translateY(-6px) scale(1.015);
    filter: brightness(1.05);
}

.movie-card:hover .movie-card-inner {
    border-color: var(--color-border-strong);
}

/* ===================== RANK BADGE ===================== */

.movie-rank {
    position: absolute;
    top: 0.6rem;
    left: 0.6rem;
    z-index: 2;
    padding: 0.12rem 0.65rem;
    border-radius: 999px;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 700;
    background: rgba(5, 5, 5, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-muted);
}

/* Style spécial top 3 : badge podium */

.movie-card[data-rank="1"] .movie-rank,
.movie-card[data-rank="2"] .movie-rank,
.movie-card[data-rank="3"] .movie-rank {
    background: rgba(0, 0, 0, 0.9);
    border-color: rgba(255, 255, 255, 0.22);
    color: var(--color-text-main);
}

.movie-card[data-rank="1"] .movie-rank {
    background: linear-gradient(135deg, #fce38a, #f38181);
    color: #1a0d0d;
}
.movie-card[data-rank="2"] .movie-rank {
    background: linear-gradient(135deg, #d7d2cc, #304352);
    color: #080808;
}
.movie-card[data-rank="3"] .movie-rank {
    background: linear-gradient(135deg, #f6d365, #fda085);
    color: #1a0d0d;
}

/* On neutralise l'ancien glow */
.background-glow {
    display: none;
}

/* ===================== POSTER ===================== */

.movie-poster-wrapper {
    position: relative;
    margin-bottom: 0.65rem;
    border-radius: 14px;
    overflow: hidden;
    background: radial-gradient(circle at top, rgba(237, 43, 18, 0.5), #050509);
}

.movie-poster {
    width: 100%;
    height: auto;
    border-radius: 14px;
    object-fit: cover;
    display: block;
    transform-origin: center;
    transition: transform 0.35s ease, filter 0.35s ease;
}

.movie-card:hover .movie-poster {
    transform: scale(1.05);
    filter: saturate(1.15);
}

/* ===================== CONTENT ===================== */

.movie-title {
    font-weight: 700;
    font-size: 0.98rem;
    margin-bottom: 0.25rem;
    line-height: 1.3;
    letter-spacing: 0.03em;
    color: var(--color-text-main);
}

.movie-meta {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    margin-bottom: 0.45rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
}

.movie-metrics {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-bottom: 0.45rem;
}

.metric-pill {
    padding: 0.22rem 0.55rem;
    border-radius: 999px;
    background: var(--color-chip-bg);
    border: 1px solid var(--color-accent-soft);
    color: #ffb199;
    font-size: 0.78rem;
    white-space: nowrap;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    opacity: 0.95;
    transition: all 0.2s ease;
}

.metric-pill::before {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 999px;
    background: var(--color-accent);
    opacity: 0.9;
}

.metric-pill:hover {
    border-color: var(--color-border-strong);
    opacity: 1;
    transform: translateY(-1px);
}

.movie-genres {
    font-size: 0.78rem;
    color: var(--color-text-muted);
    line-height: 1.45;
    margin-top: auto;
}

/* ===================== RESPONSIVE ===================== */

@media (max-width: 900px) {
    .movie-card {
        flex: 0 0 200px;
    }
}

@media (max-width: 600px) {
    .movie-card {
        flex: 0 0 180px;
    }
    .movie-title {
        font-size: 0.9rem;
    }
}

</style>
"""

# ===================== Chargement rapide =====================


@st.cache_data(show_spinner=False)
def load_movies_data(language: str = "fr-FR") -> pd.DataFrame:
    """
    Charge les films 'now_playing' depuis TMDB et les transforme en DataFrame.
    """
    client = TMDBClient(
        api_key_v3=st.secrets.get("TMDB_API_KEY"),
        read_token_v4=st.secrets.get("TMDB_API_READ_TOKEN"),
        language=language,
    )

    genre_map = client.get_genre_map()
    movies = client.get_now_playing_movies(nb_pages=1)
    df = client.movies_to_dataframe(movies, genre_map)

    return df.dropna(subset=["title"]).reset_index(drop=True)


# ===================== Carrousel horizontal Top 10 =====================


def render_top10_carousel(df: pd.DataFrame):
    st.markdown("### 🏆 Top 10 des dernières sorties")
    st.caption("Classement construit à partir des films 'now playing' renvoyés par TMDB.")

    critere = st.selectbox(
        "Classer par…",
        ["Popularité", "Meilleure note", "Plus gros budget"],
        index=0,
        help="Classement basé sur les attributs TMDB des films actuellement en salle.",
    )

    # --- tri ---
    if critere == "Popularité":
        df_top = df.sort_values("popularity", ascending=False).head(10)

    elif critere == "Meilleure note":
        df_top = df[df["vote_count"] >= 20]
        df_top = df_top.sort_values("vote_average", ascending=False).head(10)

    else:
        st.warning("L'API now_playing ne renvoie pas le budget. Fallback → popularité.")
        df_top = df.sort_values("popularity", ascending=False).head(10)

    # --- construction HTML ---
    cards_html = [TOP10_CSS]
    cards_html.append('<div class="top10-container"><div class="top10-scroll">')

    for rank, row in enumerate(df_top.itertuples(), start=1):
        poster_url = TMDBClient.build_poster_url(row.poster_path, "w342")
        genres = ", ".join(row.genres) if isinstance(row.genres, list) else ""

        meta = []
        if getattr(row, "release_year", None):
            meta.append(str(row.release_year))
        if getattr(row, "original_language", None):
            meta.append(row.original_language.upper())
        meta_str = " • ".join(meta)

        poster_html = ""
        if poster_url:
            poster_html = f"""
            <div class="movie-poster-wrapper">
                <img src="{poster_url}" class="movie-poster" />
            </div>
            """

        cards_html.append(
            f"""
        <div class="movie-card" data-rank="{rank}">
            <div class="movie-card-inner">
                <div class="movie-rank">#{rank}</div>
                {poster_html}
                <div class="movie-title">{row.title}</div>
                <div class="movie-meta">{meta_str}</div>
                <div class="movie-metrics">
                    <span class="metric-pill">⭐ {row.vote_average:.1f}</span>
                    <span class="metric-pill">🔥 {row.popularity:.0f}</span>
                </div>
                <div class="movie-genres">{genres}</div>
            </div>
        </div>
        """
        )

    cards_html.append("</div></div>")

    components.html("".join(cards_html), height=550, scrolling=False)


# ===================== Section Data Analyse / Exploration =====================


def render_exploration_section(df: pd.DataFrame):
    st.markdown("### 📊 Explorer les sorties en salle")
    st.caption("Un regard data sur les films actuellement en salle : distributions, pays, genres…")

    df_explo = df.copy()
    df_explo = df_explo.dropna(subset=["vote_average", "popularity"])

    # ---------- KPIs ----------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🎬 Nombre de films", f"{len(df_explo):d}")
    with col2:
        st.metric("⭐ Médiane des notes", f"{df_explo['vote_average'].median():.1f}")
    with col3:
        st.metric("🔥 Médiane popularité", f"{df_explo['popularity'].median():.1f}")
    with col4:
        nb_genres = len(
            sorted(
                set(
                    g
                    for lst in df_explo["genres"]
                    if isinstance(lst, list)
                    for g in lst
                )
            )
        )
        st.metric("🎭 Genres distincts", f"{nb_genres:d}")

    st.markdown("---")

    # ---------- DISTRIBUTION DES NOTES ----------
    st.markdown("#### 🎯 Distribution des notes TMDB")

    chart_notes = (
        alt.Chart(df_explo)
        .mark_bar()
        .encode(
            x=alt.X(
                "vote_average:Q",
                bin=alt.Bin(step=0.5),
                title="Note moyenne TMDB",
            ),
            y=alt.Y("count():Q", title="Nombre de films"),
            tooltip=[alt.Tooltip("count():Q", title="Nombre de films")],
        )
        .properties(height=260)
    )

    st.altair_chart(chart_notes, use_container_width=True)

    st.caption(
        "On voit la distribution des notes pour les films actuellement en salle. "
        "Classique : ça se concentre souvent entre 6 et 7."
    )

    st.markdown("---")

    # ---------- PAYS & GENRES ----------
    st.markdown("#### 🌍 Classement par pays & répartition des genres")

    # --- Données genres ---
    df_genres = df_explo.explode("genres").dropna(subset=["genres"])

    df_genres_agg = (
        df_genres.groupby("genres")
        .agg(
            nb_films=("id", "count"),
            popularite_moy=("popularity", "mean"),
        )
        .reset_index()
        .sort_values("nb_films", ascending=False)
        .head(12)
    )

    # --- Deux colonnes : gauche = pays, droite = donut genres ---
    col_left, col_right = st.columns(2)

    # ======= COLONNE GAUCHE : CLASSEMENT PAR PAYS =======
    with col_left:
        st.markdown("##### 🏳️ Classement des films par pays (langue originale)")

        # On garde uniquement les langues avec un minimum de films
        df_lang_counts = (
            df_explo.groupby("original_language")
            .agg(nb_films=("id", "count"))
            .reset_index()
            .sort_values("nb_films", ascending=False)
        )
        df_lang_counts = df_lang_counts[df_lang_counts["nb_films"] >= 3]

        lang_options = df_lang_counts["original_language"].tolist()

        if len(lang_options) == 0:
            st.info("Pas assez de films par langue pour construire un classement par pays.")
        else:
            selected_lang = st.selectbox(
                "Choisis un pays / une langue",
                options=lang_options,
                format_func=lambda x: x.upper(),
            )

            df_lang = (
                df_explo[df_explo["original_language"] == selected_lang]
                .sort_values("vote_average", ascending=False)
                .head(10)
            )

            chart_country = (
                alt.Chart(df_lang)
                .mark_bar()
                .encode(
                    x=alt.X("vote_average:Q", title="Note moyenne TMDB"),
                    y=alt.Y("title:N", sort="-x", title="Film"),
                    color=alt.value("#ed2b12"),
                    tooltip=[
                        alt.Tooltip("title:N", title="Titre"),
                        alt.Tooltip("vote_average:Q", title="Note", format=".1f"),
                        alt.Tooltip("vote_count:Q", title="Nb de votes"),
                        alt.Tooltip("popularity:Q", title="Popularité", format=".1f"),
                    ],
                )
                .properties(height=350)
            )

            st.altair_chart(chart_country, use_container_width=True)
            st.caption(
                "Classement des derniers films sortis pour ce pays (via la langue originale), triés par note moyenne."
            )

    # ======= COLONNE DROITE : DONUT GENRES =======
    with col_right:
        st.markdown("##### 🥯 Répartition relative des genres (top 12)")

        if not df_genres_agg.empty:
            df_genres_agg["part"] = (
                df_genres_agg["nb_films"] / df_genres_agg["nb_films"].sum()
            )

            donut_chart = (
                alt.Chart(df_genres_agg)
                .mark_arc(innerRadius=60, outerRadius=120)
                .encode(
                    theta=alt.Theta("nb_films:Q", title="Nombre de films"),
                    color=alt.Color("genres:N", title="Genre"),
                    tooltip=[
                        alt.Tooltip("genres:N", title="Genre"),
                        alt.Tooltip("nb_films:Q", title="Nombre de films"),
                        alt.Tooltip("part:Q", title="Part", format=".0%"),
                    ],
                )
                .properties(height=350)
            )

            st.altair_chart(donut_chart, use_container_width=True)
        else:
            st.info("Pas assez d'information de genres pour construire le graphique.")

    st.caption(
        "À gauche : le top des films par pays (langue originale). "
        "À droite : la répartition des genres parmi les sorties récentes."
    )

    st.markdown("---")

    # ---------- SCATTER POPULARITÉ VS NOTE ----------
    st.markdown("#### 🔥 Popularité vs note")

    df_scatter = df_explo[
        df_explo["popularity"] <= df_explo["popularity"].quantile(0.98)
    ]

    scatter_chart = (
        alt.Chart(df_scatter)
        .mark_circle(size=70, opacity=0.7)
        .encode(
            x=alt.X("vote_average:Q", title="Note moyenne TMDB"),
            y=alt.Y("popularity:Q", title="Popularité"),
            color=alt.Color(
                "original_language:N",
                legend=alt.Legend(title="Langue"),
            ),
            tooltip=[
                alt.Tooltip("title:N", title="Titre"),
                alt.Tooltip("vote_average:Q", title="Note", format=".1f"),
                alt.Tooltip("popularity:Q", title="Popularité", format=".1f"),
                alt.Tooltip("original_language:N", title="Langue"),
            ],
        )
        .properties(height=320)
    )

    st.altair_chart(scatter_chart, use_container_width=True)

    st.caption(
        "Les films bien notés et très populaires (en haut à droite) sont les meilleurs candidats pour alimenter ta reco."
    )


# ===================== Page principale =====================


def render_discovery_page():
    st.markdown("## 👀 Découverte")
    st.caption(
        "Les derniers films sortis, classés selon ton critère, avec une vue data pour comprendre le paysage en salle."
    )

    with st.spinner("Chargement des films..."):
        df = load_movies_data("fr-FR")

    # 1) Top 10 esthétique
    render_top10_carousel(df)

    st.markdown("---")

    # 2) Section exploration / data analyse
    render_exploration_section(df)
