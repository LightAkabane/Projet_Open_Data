import time
import streamlit as st
import streamlit.components.v1 as components
from analysis_page import render_analysis_page
from discovery_page import render_discovery_page
from compare_page import render_compare_page
from ml_page import render_ml_page

# =========================================================
# Config de la page
# =========================================================
st.set_page_config(
    page_title="Movies Things Dashboard",
    page_icon="🎬",
    layout="wide",
)

# =========================================================
# HTML de l'animation d'intro (inchangé)
# =========================================================
INTRO_ANIMATION_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
@font-face {
  font-family: "Benguiat ITC W01 Bold Cn";
  src: url("https://matteoperonidev.github.io/hosted-assets/Benguiat ITC W01 Bold Cn.ttf");
}

html, body, #root {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

body {
  background-color: black;
  display: flex;
  justify-content: center;
  align-items: center;
}

.container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

.intro-sf-title {
  font-family: "Benguiat ITC W01 Bold Cn";
  font-size: 100px;
  color: #1c0502;
  text-shadow: -0.05rem -0.05rem 1px #ed2b12, 0.05rem -0.05rem 1px #ed2b12,
    -0.05rem 0.05rem 1px #ed2b12, 0.05rem 0.05rem 1px #ed2b12, 0 0 15px #630100,
    0 0 20px #450100;
  letter-spacing: -2px;
  text-align: center;
  text-transform: uppercase;
  animation: title-fade-in 0.8s ease-in-out, title-scale-out 4s ease-in-out;
}

.intro-sf-title.outro {
  animation: title-fade-out 1s linear forwards,
    title-scale-in 2s ease-in forwards;
}

.intro-sf-title .first-letter {
  font-size: 150px;
  margin-top: -10px;
  animation: letter-left-to-right 3.5s linear;
}

.intro-sf-title .last-letter {
  font-size: 150px;
  margin-top: -10px;
  animation: letter-right-to-left 3.5s linear;
}

.intro-sf-title .t {
  font-size: 105%;
  margin-top: -5px;
  animation: letter-left-to-right 3s linear;
}

.intro-sf-title-bound {
  visibility: hidden;
  box-shadow: -0.05rem -0.05rem 2px #ed2b12, 0.05rem -0.05rem 2px #ed2b12,
    -0.05rem 0.05rem 2px #ed2b12, 0.05rem 0.05rem 2px #ed2b12;
  height: 5px;
}

.intro-sf-title-bound.visible {
  visibility: visible;
  animation: bound-fade-in 0.8s linear;
}

.intro-sf-title-bound.down {
  width: 100%;
  margin-top: 0.8rem;
}

.intro-sf-title-up {
  display: flex;
  justify-content: center;
}

.intro-sf-title-up .up-to-down-1 {
  animation: letter-up-to-down 2.5s linear;
}

.intro-sf-title-up .up-to-down-2 {
  animation: letter-up-to-down 3.5s linear;
}

.intro-sf-title-down {
  display: flex;
  justify-content: center;
  margin-top: -20px;
}

.intro-sf-title-down-wrapper {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: flex-start;
  gap: 10px;
  margin-top: -20px;
}

.intro-sf-title-down .down-to-up-1 {
  animation: letter-down-to-up 2.8s linear;
}

.intro-sf-title-down .down-to-up-2 {
  animation: letter-down-to-up 3.2s linear;
}

@keyframes title-fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes title-fade-out {
  from { opacity: 1; }
  to   { opacity: 0; }
}

@keyframes title-scale-in {
  to { transform: scale(10); }
}

@keyframes title-scale-out {
  from { transform: scale(3); }
  to   { transform: scale(1); }
}

@keyframes letter-down-to-up {
  from { transform: translateY(10rem); }
  to   { transform: translateY(0rem); }
}

@keyframes letter-up-to-down {
  from { transform: translateY(-10rem); }
  to   { transform: translateY(0rem); }
}

@keyframes letter-left-to-right {
  from { transform: translateX(-10rem); }
  to   { transform: translateX(0rem); }
}

@keyframes letter-right-to-left {
  from { transform: translateX(10rem); }
  to   { transform: translateX(0rem); }
}

@keyframes bound-fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}
</style>
</head>
<body>
  <div class="container">
    <h1 id="animation" class="intro-sf-title">
      <div class="intro-sf-title-bound"></div>
      <div class="intro-sf-title-up">
        <span class="first-letter">M</span>
        <span class="up-to-down-1">o</span>
        v
        <span class="up-to-down-2">i</span>
        e
        <span class="last-letter">s</span>
      </div>
      <div class="intro-sf-title-down-wrapper">
        <div class="intro-sf-title-bound down"></div>
        <div class="intro-sf-title-down">
          <span class="intro-sf-title t">T</span>
          <span class="down-to-up-1">h</span>
          ing
          <span class="down-to-up-2">s</span>
        </div>
        <div class="intro-sf-title-bound down"></div>
      </div>
    </h1>
  </div>

  <script>
    const animation = document.getElementById("animation");

    animation.addEventListener("animationend", (e) => {
      switch (e.animationName) {
        case "title-scale-out":
          [...document.getElementsByClassName("intro-sf-title-bound")].forEach(
            (element) => {
              element.classList.add("visible");
            }
          );
          break;
        case "bound-fade-in":
          setTimeout(() => {
            animation.classList.add("outro");
          }, 500);
          break;
        default:
          break;
      }
    });
  </script>
</body>
</html>
"""

# =========================================================
# CSS global
# =========================================================
def inject_global_css():
    css = """
    <style>
    @font-face {
      font-family: "Benguiat ITC W01 Bold Cn";
      src: url("https://matteoperonidev.github.io/hosted-assets/Benguiat ITC W01 Bold Cn.ttf");
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #000000 0%, #0a0a0f 50%, #1a0a05 100%);
        padding: 0 !important;
        margin: 0 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #050505;
    }
    
    [data-testid="stMainBlockContainer"] {
        padding: 1rem 2rem !important;
        margin: 0 !important;
    }

    .carousel-header {
        font-family: "Benguiat ITC W01 Bold Cn", sans-serif;
        font-size: 2.2rem;
        color: #ed2b12;
        text-shadow: 0 0 18px rgba(237, 43, 18, 0.6);
        letter-spacing: 2px;
        text-transform: uppercase;
    }
        /* ===== Bouton audio discret ===== */
    .audio-toggle {
        position: fixed;
        top: 18px;
        right: 22px;
        z-index: 9999;
        background: rgba(20,20,20,0.55);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.15);
        padding: 0.45rem 0.6rem;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.25s ease;
    }

    .audio-toggle:hover {
        background: rgba(237,43,18,0.35);
        border-color: rgba(237,43,18,0.6);
        transform: scale(1.03);
    }

    .audio-toggle span {
        font-size: 1.4rem;
        color: #f7f7f7;
    }

    .carousel-subtitle {
        color: #bbbbbb;
        font-size: 0.95rem;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.2rem 0.8rem;
        border-radius: 999px;
        background: #111111;
        border: 1px solid #333333;
        color: #dddddd;
        font-size: 0.85rem;
    }

    /* ===== Landing page améliorée ===== */

    .landing-root {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem 1.5rem;
        background: transparent;
        position: relative;
        overflow: hidden;
    }

    .landing-root::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, rgba(237, 43, 18, 0.15) 0%, transparent 70%);
        border-radius: 50%;
        filter: blur(80px);
        pointer-events: none;
    }

    .landing-root::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -15%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(100, 50, 150, 0.1) 0%, transparent 70%);
        border-radius: 50%;
        filter: blur(80px);
        pointer-events: none;
    }

    .landing-content {
        position: relative;
        z-index: 10;
        max-width: 900px;
        width: 100%;
        text-align: center;
    }

    .landing-title {
        font-family: "Benguiat ITC W01 Bold Cn", sans-serif;
        font-size: 4.5rem;
        letter-spacing: 0.35rem;
        text-transform: uppercase;
        background: linear-gradient(135deg, #ed2b12 0%, #ff6b4a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 30px rgba(237, 43, 18, 0.4);
        margin: 0 0 1.5rem 0;
        animation: fade-in-down 0.8s ease-out;
    }

    .landing-subtitle {
        color: #e8e8e8;
        font-size: 1.15rem;
        margin-bottom: 1rem;
        font-weight: 300;
        line-height: 1.6;
        animation: fade-in-down 0.8s ease-out 0.1s both;
    }

    .landing-tagline {
        color: #a0a0a0;
        font-size: 1rem;
        margin-bottom: 3rem;
        font-style: italic;
        animation: fade-in-down 0.8s ease-out 0.2s both;
    }

    .landing-features {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.5rem;
        margin: 3rem 0;
    }

    .feature-card {
        padding: 1.8rem 1.5rem;
        border-radius: 16px;
        background: rgba(15, 15, 20, 0.6);
        border: 1px solid rgba(237, 43, 18, 0.2);
        backdrop-filter: blur(10px);
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        animation: fade-in-up 0.8s ease-out forwards;
    }

    .feature-card:nth-child(1) {
        animation-delay: 0.3s;
    }

    .feature-card:nth-child(2) {
        animation-delay: 0.4s;
    }

    .feature-card:nth-child(3) {
        animation-delay: 0.5s;
    }

    .feature-card:hover {
        background: rgba(237, 43, 18, 0.1);
        border-color: rgba(237, 43, 18, 0.5);
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(237, 43, 18, 0.15);
    }

    .feature-emoji {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
        display: block;
    }

    .feature-title {
        color: #ed2b12;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        letter-spacing: 0.5px;
    }

    .feature-desc {
        color: #b0b0b0;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .landing-cta-container {
        margin-top: 2.5rem;
        animation: fade-in-up 0.8s ease-out 0.6s both;
    }

    .landing-cta {
        display: inline-block;
        padding: 1rem 2.5rem;
        border-radius: 50px;
        background: linear-gradient(135deg, #ed2b12 0%, #ff6b4a 100%);
        border: none;
        color: #ffffff;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        box-shadow: 0 10px 40px rgba(237, 43, 18, 0.3);
        text-decoration: none;
    }

    .landing-cta:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 60px rgba(237, 43, 18, 0.5);
        letter-spacing: 1.5px;
    }

    .landing-cta:active {
        transform: translateY(-1px);
    }

    .landing-footer {
        color: #666666;
        font-size: 0.85rem;
        margin-top: 2rem;
        animation: fade-in 0.8s ease-out 0.7s both;
    }

    @keyframes fade-in-down {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fade-in-up {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fade-in {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# =========================================================
# Intro
# =========================================================
def show_intro_animation():
    components.html(INTRO_ANIMATION_HTML, height=600, scrolling=False)

# =========================================================
# Player musique global (YouTube caché)
# =========================================================
def render_global_music_player():
    """
    Bouton audio (🔊 / 🔇) + player global invisible.
    """

    if not st.session_state.get("experience_started", False):
        return

    # État actuel
    is_on = st.session_state.get("bg_music_on", True)

    # Emoji selon l'état
    icon = "🔊" if is_on else "🔇"

    # Bouton HTML discret (haut droite)
    audio_html = f"""
        <div class="audio-toggle" onclick="fetch('/?toggle_audio', {{method:'POST'}}).then(() => window.location.reload());">
            <span>{icon}</span>
        </div>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

    # Player invisible (iframe)
    if is_on:
        components.html(
            """
            <div style="position:absolute; width:0; height:0; overflow:hidden;">
                <iframe 
                    width="0" height="0"
                    src="https://www.youtube.com/embed/-h-W1qLcTSA?autoplay=1&loop=1&playlist=-h-W1qLcTSA&controls=0"
                    frameborder="0"
                    allow="autoplay"
                ></iframe>
            </div>
            """,
            height=0,
        )

# =========================================================
# Landing page améliorée
# =========================================================
def show_landing_page():
    st.markdown(
        """
        <div class="landing-root">
          <div class="landing-content">
            <div class="landing-title">Movies Things</div>
            <div class="landing-subtitle">
              L'expérience ultime pour explorer, comparer et prédire le cinéma
            </div>
            <div class="landing-tagline">
              Plonge-toi dans les données et découvre les secrets du septième art
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Features grid
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown(
            """
            <div class="feature-card">
              <span class="feature-emoji">👀</span>
              <div class="feature-title">Découverte</div>
              <div class="feature-desc">Explore les sorties cinéma et films populaires</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with col2:
        st.markdown(
            """
            <div class="feature-card">
              <span class="feature-emoji">📊</span>
              <div class="feature-title">Comparaison</div>
              <div class="feature-desc">TMDB vs IMDb : analyse comparative avancée</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with col3:
        st.markdown(
            """
            <div class="feature-card">
              <span class="feature-emoji">🤖</span>
              <div class="feature-title">Prédictions</div>
              <div class="feature-desc">Modèles ML et recommandations d'Oscar</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Espacement
    st.markdown("<br>", unsafe_allow_html=True)

    # Bouton centré
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    with btn_col2:
        start = st.button(
            "🎬 Commencer l'expérience",
            use_container_width=True,
            type="primary",
        )

    # Footer
    st.markdown(
        """
        <div style="text-align: center; margin-top: 2rem;">
          <div class="landing-footer">
            ✨ Branche ton casque et laisse-toi guider par les données
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if start:
        st.session_state["experience_started"] = True
        st.session_state["show_dashboard"] = False
        st.session_state["bg_music_on"] = True
        st.rerun()

# =========================================================
# Carrousel Streamlit
# =========================================================
SLIDES = [
    {
        "key": "discovery",
        "label": "👀 Découverte",
        "subtitle": "Vue d'ensemble et films populaires",
    },
    {
        "key": "compare",
        "label": "📊 Comparaison IMDb / TMDB",
        "subtitle": "Comparer des films selon différents critères",
    },
    {
        "key": "analysis",
        "label": "📈 Data Analyse",
        "subtitle": "Genres, langues, temps, corrélations…",
    },
    {
        "key": "ml",
        "label": "🤖 Machine Learning",
        "subtitle": "Recommandations & modèles de prédiction",
    },
]


def render_streamlit_carousel():
    # État de la slide active
    if "current_slide" not in st.session_state:
        st.session_state.current_slide = 0

    slide = SLIDES[st.session_state.current_slide]

    # Navigation + header
    nav_col_left, nav_col_center, nav_col_right = st.columns([1, 6, 1])

    with nav_col_left:
        if st.button("⬅️ Précédent", use_container_width=True):
            st.session_state.current_slide = (st.session_state.current_slide - 1) % len(SLIDES)
            st.rerun()

    with nav_col_right:
        if st.button("Suivant ➡️", use_container_width=True):
            st.session_state.current_slide = (st.session_state.current_slide + 1) % len(SLIDES)
            st.rerun()

    with nav_col_center:
        st.markdown(f"<div class='carousel-header'>{slide['label']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='carousel-subtitle'>{slide['subtitle']}</div>",
            unsafe_allow_html=True,
        )
        # petites pastilles pour montrer la position
        pills = []
        for i, s in enumerate(SLIDES):
            if i == st.session_state.current_slide:
                pills.append(f"<span class='pill'><b>{s['label']}</b></span>")
            else:
                pills.append(f"<span class='pill' style='opacity:0.4;'>{s['label']}</span>")
        st.markdown(" ".join(pills), unsafe_allow_html=True)

    st.markdown("---")

    # Contenu de la slide
    if slide["key"] == "discovery":
        render_discovery_page()
    elif slide["key"] == "compare":
        render_compare_page()
    elif slide["key"] == "analysis":
        render_analysis_page()
    elif slide["key"] == "ml":
        render_ml_page()


# =========================================================
# Initialisation de l'état
# =========================================================
if "experience_started" not in st.session_state:
    st.session_state.experience_started = False

if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

# =========================================================
# Logique principale
# =========================================================
inject_global_css()
if st.query_params.get("toggle_audio") is not None:
    st.session_state["bg_music_on"] = not st.session_state.get("bg_music_on", True)
    st.query_params.clear()
    st.rerun()

# 1) Si l'expérience n'a pas commencé : landing page + bouton
if not st.session_state.experience_started:
    show_landing_page()

# 2) Une fois l'expérience lancée : musique globale + intro + dashboard
else:
    render_global_music_player()

    if not st.session_state.show_dashboard:
        show_intro_animation()
        time.sleep(8)
        st.session_state.show_dashboard = True
        st.rerun()
    else:
        render_streamlit_carousel()