import time
import streamlit as st
import streamlit.components.v1 as components

from discovery_page import render_discovery_page

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
        background-color: #000000 !important;
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
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# =========================================================
# Intro
# =========================================================
def show_intro_animation():
    components.html(INTRO_ANIMATION_HTML, height=600, scrolling=False)

# =========================================================
# Carrousel Streamlit
# =========================================================
SLIDES = [
    {"key": "discovery", "label": "👀 Découverte", "subtitle": "Vue d'ensemble et films populaires"},
    {"key": "analysis", "label": "📊 Data Analyse", "subtitle": "Distributions, corrélations & co."},
    {"key": "ml", "label": "🤖 Machine Learning", "subtitle": "Recommandations & modèles de prédiction"},
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
    elif slide["key"] == "analysis":
        st.info("Section Data Analyse à implémenter (distributions, densités, corrélations…).")
    elif slide["key"] == "ml":
        st.info("Section Machine Learning à implémenter (reco, prédiction de notes, clustering…).")


# =========================================================
# Initialisation de l'état
# =========================================================
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

# =========================================================
# Logique principale
# =========================================================
inject_global_css()

if not st.session_state.show_dashboard:
    show_intro_animation()
    time.sleep(8)
    st.session_state.show_dashboard = True
    st.rerun()
else:
    render_streamlit_carousel()
