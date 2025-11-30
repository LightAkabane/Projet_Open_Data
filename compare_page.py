# compare_page.py

from typing import Optional, Dict, Any, List

import streamlit as st
import pandas as pd
import altair as alt

from tmdb_client import TMDBClient
from imdb_client import IMDbClient


# ========= Style global pour les badges d'info =========

BADGE_STYLE = (
    "display:inline-flex;"
    "align-items:center;"
    "padding:0.12rem 0.55rem;"
    "border-radius:999px;"
    "border:1px solid rgba(255,255,255,0.12);"
    "background:rgba(255,255,255,0.03);"
    "font-size:0.78rem;"
    "color:#dddddd;"
    "margin-right:0.35rem;"
    "margin-bottom:0.25rem;"
)


# ========= Clients TMDB / IMDb =========

@st.cache_resource(show_spinner=False)
def get_tmdb_client(language: str = "fr-FR") -> TMDBClient:
    return TMDBClient(
        api_key_v3=st.secrets.get("TMDB_API_KEY"),
        read_token_v4=st.secrets.get("TMDB_API_READ_TOKEN"),
        language=language,
    )


@st.cache_resource(show_spinner=False)
def get_imdb_client() -> IMDbClient:
    api_key = st.secrets.get("RAPIDAPI_IMDB_KEY")
    return IMDbClient(api_key=api_key)


@st.cache_data(show_spinner=False)
def search_movies_df(
    query: str,
    year: Optional[int] = None,
    language: str = "fr-FR",
) -> pd.DataFrame:
    """
    Recherche TMDB et renvoie un DataFrame propre pour alimenter le selectbox.
    """
    tmdb = get_tmdb_client(language)
    genre_map = tmdb.get_genre_map()
    movies = tmdb.search_movies(query=query, year=year)
    df = tmdb.movies_to_dataframe(movies, genre_map)
    return df.dropna(subset=["title"]).reset_index(drop=True)


# ========= Helper robuste pour parser la réponse IMDb get-ratings =========

def parse_imdb_ratings(imdb_rating_data: Optional[Dict[str, Any]]):
    """
    Essaie de récupérer :
      - rating (float)
      - rating_count (int)
      - histogram (dict "1"→count, ..., "10"→count)

    en supportant plusieurs formats :
      - plat : { rating, ratingCount, ratingsHistograms: {...} }
      - GraphQL-like : { data: { title: { ratingsSummary, ratingsHistograms } } }
    """
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    histogram: Optional[Dict[str, Any]] = None

    if not isinstance(imdb_rating_data, dict):
        return None, None, None

    # ---- 1) Format plat ----
    if rating is None:
        rating = imdb_rating_data.get("rating") or imdb_rating_data.get("imdbRating")
    if rating_count is None:
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


# ========= Revenue par pays / région =========
# Utilise IMDb business en priorité, sinon proxy TMDB

COUNTRY_TO_REGION = {
    "US": "Amérique du Nord",
    "CA": "Amérique du Nord",
    "MX": "Amérique du Nord",
    "FR": "Europe",
    "DE": "Europe",
    "GB": "Europe",
    "ES": "Europe",
    "IT": "Europe",
    "BE": "Europe",
    "NL": "Europe",
    "SE": "Europe",
    "NO": "Europe",
    "DK": "Europe",
    "FI": "Europe",
    "CN": "Asie",
    "JP": "Asie",
    "KR": "Asie",
    "IN": "Asie",
    "HK": "Asie",
    "TW": "Asie",
    "AU": "Océanie",
    "NZ": "Océanie",
    "BR": "Amérique du Sud",
    "AR": "Amérique du Sud",
    "CL": "Amérique du Sud",
    "ZA": "Afrique",
}


def build_region_revenue_df_from_imdb(
    imdb_business: Optional[Dict[str, Any]]
) -> Optional[pd.DataFrame]:
    """
    Version Python fidèle à ton JS :

    - Récupère titleBoxOffice.gross.regional
    - Ignore la région "Domestic"
    - Trie par total.amount décroissant
    - Garde les 20 premières régions
    - Agrège le reste dans une catégorie "Autre"
    """
    if not imdb_business:
        return None

    title_box_office = imdb_business.get("titleBoxOffice") or {}
    gross = title_box_office.get("gross") or {}
    regional = gross.get("regional") or []

    if not isinstance(regional, list) or len(regional) == 0:
        return None

    # Filtre "Domestic" comme dans ton JS
    filtered = [
        r
        for r in regional
        if (r.get("regionName") or r.get("region")) != "Domestic"
           and r.get("total")
    ]

    rows: List[Dict[str, Any]] = []

    for r in filtered:
        region_name = r.get("regionName") or r.get("region") or "Inconnu"

        total = r.get("total") or {}
        amount = total.get("amount")

        if amount is None:
            continue

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            continue

        rows.append({"region": region_name, "revenue": amount})

    if not rows:
        return None

    # Tri décroissant par revenu
    rows_sorted = sorted(rows, key=lambda x: x["revenue"], reverse=True)

    # Top 20
    top20 = rows_sorted[:20]
    others = rows_sorted[20:]

    # Somme pour "Autre"
    if others:
        other_total = sum(r["revenue"] for r in others)
        if other_total > 0:
            top20.append({"region": "Autre", "revenue": other_total})

    df = pd.DataFrame(top20)
    return df


def build_region_revenue_df_proxy_tmdb(details: Dict[str, Any]) -> pd.DataFrame:
    """
    Fallback si IMDb ne fournit rien : proxy basé sur les pays de production TMDB.
    """
    revenue = details.get("revenue") or 0
    prod_countries = details.get("production_countries") or []

    if not prod_countries:
        return pd.DataFrame(
            [{"region": "Inconnu", "revenue": revenue if revenue > 0 else 1}]
        )

    regions: List[str] = []
    for c in prod_countries:
        code = c.get("iso_3166_1")
        region = COUNTRY_TO_REGION.get(code, "Autre / Inconnu")
        regions.append(region)

    if revenue <= 0:
        df = (
            pd.DataFrame({"region": regions})
            .groupby("region")
            .size()
            .reset_index(name="revenue")
        )
        return df

    share = revenue / len(regions)
    df = (
        pd.DataFrame({"region": regions})
        .groupby("region")
        .size()
        .reset_index(name="n")
    )
    df["revenue"] = df["n"] * share
    df = df[["region", "revenue"]]

    return df


def build_region_revenue_df(
    details: Dict[str, Any],
    imdb_business: Optional[Dict[str, Any]],
) -> pd.DataFrame:
    """
    Essaie d'abord de construire les revenus par pays/région à partir d'IMDb.
    Si pas possible, fallback sur le proxy TMDB.
    """
    df_imdb = build_region_revenue_df_from_imdb(imdb_business)
    if df_imdb is not None and not df_imdb.empty:
        return df_imdb

    return build_region_revenue_df_proxy_tmdb(details)


# ========= Bar chart IMDb : répartition des notes 1 -> 10 =========

def build_imdb_votes_barchart(
    imdb_rating_data: Optional[Dict[str, Any]],
):
    """
    Affiche un bar chart (1 → 10) basé sur la vraie répartition IMDb
    quand l'histogramme existe :
      ratingsHistograms['IMDb Users'].histogram
    """
    _, _, histogram = parse_imdb_ratings(imdb_rating_data)

    if not isinstance(histogram, dict) or not histogram:
        return None

    # tri des notes : 1 → 10
    try:
        categories = sorted(histogram.keys(), key=lambda x: int(x))
    except Exception:
        return None

    rows = []
    for note in categories:
        try:
            value = int(histogram[note])
        except Exception:
            value = 0
        rows.append({"note": int(note), "votes": value})

    df = pd.DataFrame(rows)

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("note:O", title="Note IMDb (1 → 10)"),
            y=alt.Y("votes:Q", title="Nombre de votes"),
            tooltip=[
                alt.Tooltip("note:O", title="Note"),
                alt.Tooltip("votes:Q", title="Votes", format=","),
            ],
            color=alt.value("#ed2b12"),
        )
        .properties(height=350)
    )

    return chart


# ========= Top 5 acteurs / doubleurs =========

def build_top_cast_df(credits: Dict[str, Any], top_n: int = 5) -> pd.DataFrame:
    cast = credits.get("cast") or []
    if not cast:
        return pd.DataFrame(columns=["name", "popularity", "character"])

    sorted_cast = sorted(cast, key=lambda c: c.get("popularity", 0), reverse=True)[
        :top_n
    ]

    rows = []
    for person in sorted_cast:
        rows.append(
            {
                "name": person.get("name"),
                "popularity": person.get("popularity", 0.0),
                "character": person.get("character"),
            }
        )
    return pd.DataFrame(rows)


# ========= Mode : analyse d’un seul film =========

def render_single_movie_analysis():
    st.markdown("### 🎬 Analyse d’un film")
    st.caption(
        "Tape un titre, choisis le film dans la liste, "
        "puis on regarde popularité, budget, revenus et votes (TMDB + IMDb)."
    )

    # ------- Recherche dynamique -------
    with st.container():
        col_q, col_year = st.columns([4, 1.5])

        query = col_q.text_input(
            "Titre du film",
            placeholder="Ex : Inception, Parasite, Intouchables...",
            key="single_movie_query",
        )

        year_str = col_year.text_input("Année (optionnel)", placeholder="Ex : 2010")
        year: Optional[int] = None
        if year_str.strip():
            try:
                year = int(year_str.strip())
            except ValueError:
                st.warning("Année invalide, je l’ignore.")

    df_results = None
    if query and len(query.strip()) >= 2:
        with st.spinner("Recherche en cours sur TMDB..."):
            df_results = search_movies_df(
                query=query.strip(), year=year, language="fr-FR"
            )
        st.session_state.compare_search_results = df_results
    else:
        df_results = st.session_state.get("compare_search_results")

    if df_results is None or df_results.empty:
        st.info(
            "Commence à taper un titre (au moins 2 caractères) pour voir des résultats."
        )
        return

    # ------- Sélection du film -------
    st.markdown("#### 🔎 Résultats")

    def format_option(row_dict: Dict[str, Any]) -> str:
        y = row_dict.get("release_year")
        lang = (row_dict.get("original_language") or "").upper()
        title = row_dict.get("title") or "Titre inconnu"
        if y:
            return f"🎬 {title} ({y}) [{lang}]"
        return f"🎬 {title} [{lang}]"

    options = [format_option(row._asdict()) for row in df_results.itertuples()]

    selected_idx = st.selectbox(
        "Sélectionne le film à analyser",
        options=list(range(len(options))),
        format_func=lambda i: options[i],
        index=0,
        key="single_movie_select",
    )

    selected_row = df_results.iloc[selected_idx]
    movie_id = int(selected_row["id"])

    # ------- Récupération des détails -------
    tmdb = get_tmdb_client()
    try:
        imdb_client = get_imdb_client()
    except Exception:
        imdb_client = None  # on fera sans si pas de clé

    with st.spinner("Récupération des détails du film..."):
        details = tmdb.get_movie_details(movie_id)
        credits = tmdb.get_movie_credits(movie_id)

        imdb_id = details.get("imdb_id")
        imdb_rating_data: Optional[Dict[str, Any]] = None
        imdb_business: Optional[Dict[str, Any]] = None

        if imdb_client and imdb_id:
            try:
                imdb_rating_data = imdb_client.get_ratings(imdb_id)
            except Exception:
                imdb_rating_data = None

            try:
                imdb_business = imdb_client.get_business(imdb_id)
            except Exception:
                imdb_business = None

    # ------- Pré-calcul des métriques -------
    tmdb_vote = details.get("vote_average")
    tmdb_votes = details.get("vote_count")
    popularity = details.get("popularity")

    budget = details.get("budget") or 0
    revenue = details.get("revenue") or 0

    imdb_rating, imdb_rating_count, _ = parse_imdb_ratings(imdb_rating_data)

    # ------- Layout principal : 3 colonnes sur la même ligne -------
    col_left, col_mid, col_right = st.columns([2, 2.7, 2.8])

    # ----- COLONNE GAUCHE : affiche -----
    with col_left:
        poster_url = TMDBClient.build_poster_url(details.get("poster_path"), size="w342")
        if poster_url:
            st.image(poster_url, use_container_width=True)

    # ----- COLONNE MILIEU : infos film + indicateurs clés -----
    with col_mid:
        # Bloc infos film esthétique
        title = details.get("title") or selected_row.get("title")
        tagline = details.get("tagline") or ""
        release_date = details.get("release_date")
        runtime = details.get("runtime")
        lang = details.get("original_language")
        lang_display = lang.upper() if lang else None

        meta_badges: List[str] = []
        if release_date:
            meta_badges.append(f"📅 {release_date}")
        if runtime:
            meta_badges.append(f"⏱️ {runtime} min")
        if lang_display:
            meta_badges.append(f"🌍 {lang_display}")

        if meta_badges:
            badges_html = "".join(
                f'<span style="{BADGE_STYLE}">{badge}</span>'
                for badge in meta_badges
            )
        else:
            badges_html = ""

        info_html = f'''
        <div style="
            padding:0.85rem 1rem;
            border-radius:14px;
            background:linear-gradient(
                135deg,
                rgba(237,43,18,0.15),
                rgba(10,10,15,0.95)
            );
            border:1px solid rgba(237,43,18,0.4);
            box-shadow:0 18px 40px rgba(0,0,0,0.65);
            margin-bottom:0.9rem;
        ">
            <div style="font-size:1.1rem;font-weight:700;color:#f7f7f7;letter-spacing:0.03em;">
                {title or "Titre inconnu"}
            </div>
            <div style="font-size:0.9rem;color:#bbbbbb;font-style:italic;margin-top:0.2rem;margin-bottom:0.5rem;">
                {tagline}
            </div>
            <div style="display:flex;flex-wrap:wrap;align-items:center;">
                {badges_html}
            </div>
        </div>
        '''
        st.markdown(info_html, unsafe_allow_html=True)

        # Indicateurs clés
        st.markdown("##### 📈 Indicateurs clés")

        col_a, col_b = st.columns(2)
        col_c, col_d = st.columns(2)
        col_e, col_f = st.columns(2)

        with col_a:
            st.metric(
                "⭐ Note TMDB",
                f"{tmdb_vote:.1f}" if tmdb_vote is not None else "n/a",
            )
        with col_b:
            st.metric(
                "🗳️ Votes TMDB",
                f"{tmdb_votes:,}" if tmdb_votes is not None else "n/a",
            )

        with col_c:
            st.metric(
                "🔥 Popularité TMDB",
                f"{popularity:.1f}" if popularity is not None else "n/a",
            )
        with col_d:
            st.metric(
                "⭐ Note IMDb",
                f"{imdb_rating:.1f}" if imdb_rating is not None else "n/a",
            )

        with col_e:
            st.metric(
                "🗳️ Votes IMDb",
                f"{imdb_rating_count:,}"
                if imdb_rating_count is not None
                else "n/a",
            )
        with col_f:
            if budget:
                st.metric("💰 Budget", f"{budget:,.0f} $")
            else:
                st.metric("💰 Budget", "n/a")

        if revenue:
            st.metric("🎟️ Revenus mondiaux (TMDB)", f"{revenue:,.0f} $")

        st.caption(
            "Budget et revenus globaux : TMDB. "
            "Répartition détaillée & stats de votes : IMDb via RapidAPI."
        )

    # ----- COLONNE DROITE : les 3 graphiques -----
    with col_right:
        st.markdown("##### 📊 Visualisations")
        chart_mode = st.radio(
            "Vue",
            [
                "Répartition des notes IMDb",
                "Revenu par pays / région",
                "Top 5 acteurs/doubleurs",
            ],
            horizontal=True,
            key="single_movie_chart_mode",
        )

        # 1) Bar chart des notes IMDb
        if chart_mode == "Répartition des notes IMDb":
            chart = build_imdb_votes_barchart(imdb_rating_data)
            if chart is None:
                st.info(
                    "Impossible de récupérer la répartition détaillée des notes IMDb "
                    "pour ce film (l'API ne fournit pas l'histogramme 1→10)."
                )
            else:
                st.altair_chart(chart, use_container_width=True)
                st.caption(
                    "Répartition des notes IMDb (1 → 10). "
                    "Chaque barre représente le nombre de votes."
                )

        # 2) Revenu par pays / région (IMDb, puis fallback TMDB)
        elif chart_mode == "Revenu par pays / région":
            df_region = build_region_revenue_df(details, imdb_business)
            if df_region.empty:
                st.info("Impossible de déterminer les revenus par région pour ce film.")
            else:
                donut_chart = (
                    alt.Chart(df_region)
                    .mark_arc(innerRadius=60)
                    .encode(
                        theta=alt.Theta("revenue:Q", title="Revenu"),
                        color=alt.Color("region:N", title="Pays / Région"),
                        tooltip=[
                            alt.Tooltip("region:N", title="Pays / Région"),
                            alt.Tooltip("revenue:Q", title="Montant", format=","),
                        ],
                    )
                    .properties(height=350)
                )
                st.altair_chart(donut_chart, use_container_width=True)
                st.caption(
                    "Répartition des revenus par pays / région (top 20 + 'Autre'). "
                    "Basé sur les données box office IMDb quand disponibles, sinon proxy TMDB."
                )

        # 3) Top 5 acteurs / doubleurs
        else:
            df_cast = build_top_cast_df(credits, top_n=5)
            if df_cast.empty:
                st.info(
                    "Casting insuffisant pour afficher un top des acteurs/doubleurs."
                )
            else:
                chart_cast = (
                    alt.Chart(df_cast)
                    .mark_bar()
                    .encode(
                        x=alt.X("popularity:Q", title="Popularité TMDB"),
                        y=alt.Y("name:N", sort="-x", title="Acteur / Doubleur"),
                        tooltip=[
                            alt.Tooltip("name:N", title="Nom"),
                            alt.Tooltip("character:N", title="Personnage"),
                            alt.Tooltip(
                                "popularity:Q",
                                title="Popularité",
                                format=".1f",
                            ),
                        ],
                    )
                    .properties(height=350)
                )
                st.altair_chart(chart_cast, use_container_width=True)
                st.caption(
                    "Top 5 basé sur le score de popularité TMDB du casting."
                )

# ========= Mode : comparaison de deux films =========
# ========= Mode : comparaison de deux films =========
# ========= Mode : comparaison de deux films =========

def render_compare_two_movies():
    """
    Affiche une interface pour comparer deux films côte à côte.
    """
    st.markdown("### 🎬 Comparaison de deux films")
    st.caption("Sélectionne deux films et compare leurs statistiques, revenus, casting...")

    # ------- Recherche des deux films -------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎥 Film 1")
        query1 = st.text_input(
            "Titre du film 1",
            placeholder="Ex : Inception...",
            key="compare_movie_1_query",
        )
        year1_str = st.text_input("Année (optionnel)", placeholder="Ex : 2010", key="compare_movie_1_year")
        year1: Optional[int] = None
        if year1_str.strip():
            try:
                year1 = int(year1_str.strip())
            except ValueError:
                st.warning("Année invalide pour le film 1")

    with col2:
        st.markdown("#### 🎥 Film 2")
        query2 = st.text_input(
            "Titre du film 2",
            placeholder="Ex : Parasite...",
            key="compare_movie_2_query",
        )
        year2_str = st.text_input("Année (optionnel)", placeholder="Ex : 2019", key="compare_movie_2_year")
        year2: Optional[int] = None
        if year2_str.strip():
            try:
                year2 = int(year2_str.strip())
            except ValueError:
                st.warning("Année invalide pour le film 2")

    # ------- Recherche si au moins 2 caractères -------
    df_results1 = None
    df_results2 = None

    if query1 and len(query1.strip()) >= 2:
        with st.spinner("Recherche film 1 sur TMDB..."):
            df_results1 = search_movies_df(query=query1.strip(), year=year1, language="fr-FR")
        st.session_state.compare_1_results = df_results1
    else:
        df_results1 = st.session_state.get("compare_1_results")

    if query2 and len(query2.strip()) >= 2:
        with st.spinner("Recherche film 2 sur TMDB..."):
            df_results2 = search_movies_df(query=query2.strip(), year=year2, language="fr-FR")
        st.session_state.compare_2_results = df_results2
    else:
        df_results2 = st.session_state.get("compare_2_results")

    if df_results1 is None or df_results1.empty or df_results2 is None or df_results2.empty:
        st.info("Tape les titres (min. 2 caractères) pour voir les résultats de recherche.")
        return

    # ------- Sélection des deux films -------
    col1, col2 = st.columns(2)

    def format_option(row_dict: Dict[str, Any]) -> str:
        y = row_dict.get("release_year")
        lang = (row_dict.get("original_language") or "").upper()
        title = row_dict.get("title") or "Titre inconnu"
        if y:
            return f"🎬 {title} ({y}) [{lang}]"
        return f"🎬 {title} [{lang}]"

    with col1:
        options1 = [format_option(row._asdict()) for row in df_results1.itertuples()]
        selected_idx1 = st.selectbox(
            "Sélectionne film 1",
            options=list(range(len(options1))),
            format_func=lambda i: options1[i],
            index=0,
            key="compare_select_1",
        )
        selected_row1 = df_results1.iloc[selected_idx1]
        movie_id1 = int(selected_row1["id"])

    with col2:
        options2 = [format_option(row._asdict()) for row in df_results2.itertuples()]
        selected_idx2 = st.selectbox(
            "Sélectionne film 2",
            options=list(range(len(options2))),
            format_func=lambda i: options2[i],
            index=0,
            key="compare_select_2",
        )
        selected_row2 = df_results2.iloc[selected_idx2]
        movie_id2 = int(selected_row2["id"])

    # ------- Récupération des détails des deux films -------
    tmdb = get_tmdb_client()
    try:
        imdb_client = get_imdb_client()
    except Exception:
        imdb_client = None

    with st.spinner("Récupération des détails..."):
        details1 = tmdb.get_movie_details(movie_id1)
        credits1 = tmdb.get_movie_credits(movie_id1)
        details2 = tmdb.get_movie_details(movie_id2)
        credits2 = tmdb.get_movie_credits(movie_id2)

        imdb_id1 = details1.get("imdb_id")
        imdb_id2 = details2.get("imdb_id")

        imdb_rating_data1: Optional[Dict[str, Any]] = None
        imdb_business1: Optional[Dict[str, Any]] = None
        imdb_rating_data2: Optional[Dict[str, Any]] = None
        imdb_business2: Optional[Dict[str, Any]] = None

        if imdb_client:
            if imdb_id1:
                try:
                    imdb_rating_data1 = imdb_client.get_ratings(imdb_id1)
                    imdb_business1 = imdb_client.get_business(imdb_id1)
                except Exception:
                    pass

            if imdb_id2:
                try:
                    imdb_rating_data2 = imdb_client.get_ratings(imdb_id2)
                    imdb_business2 = imdb_client.get_business(imdb_id2)
                except Exception:
                    pass

    # ------- Pré-calcul des métriques -------
    def extract_movie_data(details, credits, imdb_rating_data):
        tmdb_vote = details.get("vote_average")
        tmdb_votes = details.get("vote_count")
        popularity = details.get("popularity")
        budget = details.get("budget") or 0
        revenue = details.get("revenue") or 0
        runtime = details.get("runtime") or 0
        release_date = details.get("release_date") or "N/A"
        title = details.get("title") or "Titre inconnu"
        poster_path = details.get("poster_path")
        
        imdb_rating, imdb_rating_count, _ = parse_imdb_ratings(imdb_rating_data)

        top_cast = build_top_cast_df(credits, top_n=3)

        return {
            "title": title,
            "poster_path": poster_path,
            "release_date": release_date,
            "runtime": runtime,
            "tmdb_vote": tmdb_vote,
            "tmdb_votes": tmdb_votes,
            "popularity": popularity,
            "budget": budget,
            "revenue": revenue,
            "imdb_rating": imdb_rating,
            "imdb_rating_count": imdb_rating_count,
            "top_cast": top_cast,
        }

    movie_data1 = extract_movie_data(details1, credits1, imdb_rating_data1)
    movie_data2 = extract_movie_data(details2, credits2, imdb_rating_data2)

    # ------- Affichage : les deux affiches en haut -------
    st.markdown("---")
    col_poster1, col_vs, col_poster2 = st.columns([1, 0.3, 1])

    with col_poster1:
        poster_url1 = TMDBClient.build_poster_url(movie_data1["poster_path"], size="w342")
        if poster_url1:
            st.image(poster_url1, width=700)

    with col_vs:
        st.markdown("<div style='margin-top:350px; margin-right:70px; display: flex; align-items: center; justify-content: center; height: 150%; font-size: 8.5rem; font-weight: bold; color: rgba(237, 43, 18, 0.8);'>⚔️</div>", unsafe_allow_html=True)

    with col_poster2:
        poster_url2 = TMDBClient.build_poster_url(movie_data2["poster_path"], size="w342")
        if poster_url2:
            st.image(poster_url2, width=700)

    st.markdown("---")

    # ------- Comparaison des métriques clés en tableau -------
    st.markdown("### 📊 Comparaison des statistiques")

    comparison_data = {
        "Métrique": [
            "Titre",
            "Date de sortie",
            "Durée (min)",
            "Note TMDB",
            "Votes TMDB",
            "Note IMDb",
            "Votes IMDb",
            "Popularité TMDB",
            "Budget",
            "Revenus mondiaux",
        ],
        movie_data1["title"]: [
            movie_data1["title"],
            movie_data1["release_date"],
            f"{movie_data1['runtime']}" if movie_data1["runtime"] else "N/A",
            f"{movie_data1['tmdb_vote']:.1f}" if movie_data1["tmdb_vote"] else "N/A",
            f"{movie_data1['tmdb_votes']:,}" if movie_data1["tmdb_votes"] else "N/A",
            f"{movie_data1['imdb_rating']:.1f}" if movie_data1["imdb_rating"] else "N/A",
            f"{movie_data1['imdb_rating_count']:,}" if movie_data1["imdb_rating_count"] else "N/A",
            f"{movie_data1['popularity']:.1f}" if movie_data1["popularity"] else "N/A",
            f"${movie_data1['budget']:,.0f}" if movie_data1["budget"] else "N/A",
            f"${movie_data1['revenue']:,.0f}" if movie_data1["revenue"] else "N/A",
        ],
        movie_data2["title"]: [
            movie_data2["title"],
            movie_data2["release_date"],
            f"{movie_data2['runtime']}" if movie_data2["runtime"] else "N/A",
            f"{movie_data2['tmdb_vote']:.1f}" if movie_data2["tmdb_vote"] else "N/A",
            f"{movie_data2['tmdb_votes']:,}" if movie_data2["tmdb_votes"] else "N/A",
            f"{movie_data2['imdb_rating']:.1f}" if movie_data2["imdb_rating"] else "N/A",
            f"{movie_data2['imdb_rating_count']:,}" if movie_data2["imdb_rating_count"] else "N/A",
            f"{movie_data2['popularity']:.1f}" if movie_data2["popularity"] else "N/A",
            f"${movie_data2['budget']:,.0f}" if movie_data2["budget"] else "N/A",
            f"${movie_data2['revenue']:,.0f}" if movie_data2["revenue"] else "N/A",
        ],
    }

    df_comparison = pd.DataFrame(comparison_data)
    
    # Style du tableau
    styled_df = df_comparison.style.applymap(
        lambda v: "background-color: rgba(237, 43, 18, 0.15);" if v and v != "Métrique" else "",
        subset=[movie_data1["title"]]
    ).applymap(
        lambda v: "background-color: rgba(100, 200, 255, 0.15);" if v and v != "Métrique" else "",
        subset=[movie_data2["title"]]
    )

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ------- Comparaison graphique des votes -------
    st.markdown("### 📈 Comparaison des évaluations")

    col_rating1, col_rating2 = st.columns(2)

    with col_rating1:
        st.markdown(f"#### {movie_data1['title']}")
        
        # Créer deux colonnes pour les métriques
        m1, m2 = st.columns(2)
        with m1:
            st.metric(
                "⭐ TMDB",
                f"{movie_data1['tmdb_vote']:.1f}" if movie_data1["tmdb_vote"] else "n/a",
                delta=f"{movie_data1['tmdb_votes']:,} votes" if movie_data1["tmdb_votes"] else None,
            )
        with m2:
            st.metric(
                "⭐ IMDb",
                f"{movie_data1['imdb_rating']:.1f}" if movie_data1["imdb_rating"] else "n/a",
                delta=f"{movie_data1['imdb_rating_count']:,} votes" if movie_data1["imdb_rating_count"] else None,
            )

        # Histogramme des notes IMDb
        chart1 = build_imdb_votes_barchart(imdb_rating_data1)
        if chart1 is not None:
            st.altair_chart(chart1, use_container_width=True)
        else:
            st.caption("📊 Histogramme IMDb non disponible")

    with col_rating2:
        st.markdown(f"#### {movie_data2['title']}")
        
        # Créer deux colonnes pour les métriques
        m1, m2 = st.columns(2)
        with m1:
            st.metric(
                "⭐ TMDB",
                f"{movie_data2['tmdb_vote']:.1f}" if movie_data2["tmdb_vote"] else "n/a",
                delta=f"{movie_data2['tmdb_votes']:,} votes" if movie_data2["tmdb_votes"] else None,
            )
        with m2:
            st.metric(
                "⭐ IMDb",
                f"{movie_data2['imdb_rating']:.1f}" if movie_data2["imdb_rating"] else "n/a",
                delta=f"{movie_data2['imdb_rating_count']:,} votes" if movie_data2["imdb_rating_count"] else None,
            )

        # Histogramme des notes IMDb
        chart2 = build_imdb_votes_barchart(imdb_rating_data2)
        if chart2 is not None:
            st.altair_chart(chart2, use_container_width=True)
        else:
            st.caption("📊 Histogramme IMDb non disponible")

    st.markdown("---")

    # ------- Comparaison financière -------
    st.markdown("### 💰 Comparaison financière")

    col_fin1, col_fin2 = st.columns(2)

    # Données pour le graphique de comparaison budgétaire
    financial_data = pd.DataFrame({
        "Film": [movie_data1["title"], movie_data2["title"]],
        "Budget": [movie_data1["budget"], movie_data2["budget"]],
        "Revenus": [movie_data1["revenue"], movie_data2["revenue"]],
    })

    # Graphique en barres groupées
    fin_chart_data = financial_data.melt(
        id_vars=["Film"], value_vars=["Budget", "Revenus"], 
        var_name="Type", value_name="Montant"
    )

    fin_chart = (
        alt.Chart(fin_chart_data)
        .mark_bar()
        .encode(
            x=alt.X("Film:N", title="Film"),
            y=alt.Y("Montant:Q", title="Montant ($)", axis=alt.Axis(format="$,.0f")),
            color=alt.Color("Type:N", scale=alt.Scale(scheme="set1")),
            tooltip=[
                alt.Tooltip("Film:N", title="Film"),
                alt.Tooltip("Type:N", title="Type"),
                alt.Tooltip("Montant:Q", title="Montant", format="$,.0f"),
            ],
        )
        .properties(height=300)
    )

    st.altair_chart(fin_chart, use_container_width=True)

    with col_fin1:
        st.metric(
            f"💰 Budget - {movie_data1['title']}",
            f"${movie_data1['budget']:,.0f}" if movie_data1["budget"] else "N/A",
        )
        st.metric(
            f"🎟️ Revenus - {movie_data1['title']}",
            f"${movie_data1['revenue']:,.0f}" if movie_data1["revenue"] else "N/A",
        )
        if movie_data1["revenue"] and movie_data1["budget"]:
            ratio1 = movie_data1["revenue"] / movie_data1["budget"]
            st.metric(
                f"📊 ROI - {movie_data1['title']}",
                f"{ratio1:.2f}x",
            )

    with col_fin2:
        st.metric(
            f"💰 Budget - {movie_data2['title']}",
            f"${movie_data2['budget']:,.0f}" if movie_data2["budget"] else "N/A",
        )
        st.metric(
            f"🎟️ Revenus - {movie_data2['title']}",
            f"${movie_data2['revenue']:,.0f}" if movie_data2["revenue"] else "N/A",
        )
        if movie_data2["revenue"] and movie_data2["budget"]:
            ratio2 = movie_data2["revenue"] / movie_data2["budget"]
            st.metric(
                f"📊 ROI - {movie_data2['title']}",
                f"{ratio2:.2f}x",
            )

    st.markdown("---")

    # ------- Comparaison du casting -------
    st.markdown("### 🎭 Comparaison du casting")

    col_cast1, col_cast2 = st.columns(2)

    # Préparer les données pour le bar chart comparatif
    cast_data = []
    
    for idx, row in movie_data1["top_cast"].iterrows():
        cast_data.append({
            "Acteur": row['name'],
            "Film": movie_data1['title'],
            "Popularité": row['popularity']
        })
    
    for idx, row in movie_data2["top_cast"].iterrows():
        cast_data.append({
            "Acteur": row['name'],
            "Film": movie_data2['title'],
            "Popularité": row['popularity']
        })

    if cast_data:
        df_cast_comparison = pd.DataFrame(cast_data)
        
        cast_chart = (
            alt.Chart(df_cast_comparison)
            .mark_bar()
            .encode(
                y=alt.Y("Acteur:N", title="Acteur/Doubleur", sort="-x"),
                x=alt.X("Popularité:Q", title="Popularité TMDB"),
                color=alt.Color("Film:N", title="Film", scale=alt.Scale(scheme="category10")),
                tooltip=[
                    alt.Tooltip("Acteur:N", title="Acteur"),
                    alt.Tooltip("Film:N", title="Film"),
                    alt.Tooltip("Popularité:Q", title="Popularité", format=".2f"),
                ],
            )
            .properties(height=300)
        )
        
        st.altair_chart(cast_chart, use_container_width=True)
    else:
        st.caption("📊 Données de casting insuffisantes pour la comparaison")

    st.markdown("---")

    # Affichage détaillé du casting
# ========= Mise à jour de la fonction principale =========
# Remplace la section "else" de render_compare_page() par :

def render_compare_page():
    st.markdown("## 📊 Comparaison & analyse de films")

    mode = st.radio(
        "Que veux-tu faire ?",
        ["Analyse d'un film", "Comparer deux films"],
        horizontal=True,
    )

    if mode == "Analyse d'un film":
        render_single_movie_analysis()
    else:
        render_compare_two_movies()