import time
import streamlit as st
import streamlit.components.v1 as components

# =========================================================
# Config de la page
# =========================================================
st.set_page_config(
    page_title="Movies Things Dashboard",
    page_icon="🎬",
    layout="wide",
)

# =========================================================
# HTML de l'animation d'intro
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
  /* plus rapide : */
  animation: title-fade-in 0.8s ease-in-out, title-scale-out 4s ease-in-out;
}

.intro-sf-title.outro {
  /* plus rapide : */
  animation: title-fade-out 1s linear forwards,
    title-scale-in 2s ease-in forwards;
}

.intro-sf-title .first-letter {
  font-size: 150px;
  margin-top: -10px;
  /* plus rapide : */
  animation: letter-left-to-right 3.5s linear;
}

.intro-sf-title .last-letter {
  font-size: 150px;
  margin-top: -10px;
  /* plus rapide : */
  animation: letter-right-to-left 3.5s linear;
}

.intro-sf-title .t {
  font-size: 105%;
  margin-top: -5px;
  /* plus rapide : */
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
  /* plus rapide : */
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
  /* plus rapide : */
  animation: letter-up-to-down 2.5s linear;
}

.intro-sf-title-up .up-to-down-2 {
  /* plus rapide : */
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
  /* plus rapide : */
  animation: letter-down-to-up 2.8s linear;
}

.intro-sf-title-down .down-to-up-2 {
  /* plus rapide : */
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
          }, 500); // au lieu de 2000ms
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
# HTML du carrousel fullscreen (inchangé)
# =========================================================
FULLSCREEN_CAROUSEL_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
@font-face {
  font-family: "Benguiat ITC W01 Bold Cn";
  src: url("https://matteoperonidev.github.io/hosted-assets/Benguiat ITC W01 Bold Cn.ttf");
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #000;
}

.carousel-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.carousel-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-slides {
  width: 100%;
  height: 100%;
  display: flex;
  transition: transform 0.9s cubic-bezier(0.4, 0, 0.2, 1);
}

.carousel-slide {
  width: 100%;
  height: 100%;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6rem 14rem;
  text-align: center;
  background: radial-gradient(circle at 50% 40%, #1b0504 0%, #050101 80%);
  position: relative;
  overflow: hidden;
}

.carousel-slide::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 50% 50%, rgba(237, 43, 18, 0.1) 0%, transparent 70%);
  animation: shimmer 8s infinite;
  pointer-events: none;
}

@keyframes shimmer {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(50px, 50px);
  }
}

.slide-content {
  position: relative;
  z-index: 2;
  animation: slideContentFadeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

@keyframes slideContentFadeIn {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.carousel-slide-icon {
  font-size: 8rem;
  margin-bottom: 0.5rem;
  animation: iconRotate 0.9s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes iconRotate {
  from {
    opacity: 0;
    transform: scale(0) rotate(-30deg);
  }
  to {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }
}

.carousel-slide-title {
  font-family: "Benguiat ITC W01 Bold Cn", serif;
  font-size: 4.5rem;
  text-transform: uppercase;
  letter-spacing: -3px;
  color: #ed2b12;
  text-shadow: 0 0 30px rgba(237, 43, 18, 0.7);
  margin-bottom: 0.5rem;
  animation: titleSlideIn 0.9s cubic-bezier(0.34, 1.56, 0.64, 1) 0.1s both;
}

@keyframes titleSlideIn {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* -------- Carrousel vertical intra-catégorie -------- */

.v-carousel {
  width: 100%;
  max-width: 900px;
  height: 260px;
  position: relative;
  overflow: hidden;
  margin-top: 1rem;
}

.v-nav input {
  display: none;
}

.v-slides {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.v-slide {
  flex: 0 0 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 0.5rem;
}

.v-slide-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #f5f5f5;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.v-slide-desc {
  font-size: 1.1rem;
  color: #ddd;
  line-height: 1.8;
}

/* Dots verticaux */
.v-dots {
  position: absolute;
  right: -40px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.v-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #555;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.v-dot:hover {
  transform: scale(1.2);
  background: #777;
}

/* Découverte : v-slide-1 */
#v1-1:checked ~ .v-slides { transform: translateY(0%); }
#v1-2:checked ~ .v-slides { transform: translateY(-100%); }
#v1-3:checked ~ .v-slides { transform: translateY(-200%); }

#v1-1:checked ~ .v-dots .v1-dot-1,
#v1-2:checked ~ .v-dots .v1-dot-2,
#v1-3:checked ~ .v-dots .v1-dot-3 {
  background: #ed2b12;
  box-shadow: 0 0 12px rgba(237, 43, 18, 0.8);
}

/* Data Analyse : v-slide-2 */
#v2-1:checked ~ .v-slides { transform: translateY(0%); }
#v2-2:checked ~ .v-slides { transform: translateY(-100%); }
#v2-3:checked ~ .v-slides { transform: translateY(-200%); }

#v2-1:checked ~ .v-dots .v2-dot-1,
#v2-2:checked ~ .v-dots .v2-dot-2,
#v2-3:checked ~ .v-dots .v2-dot-3 {
  background: #ed2b12;
  box-shadow: 0 0 12px rgba(237, 43, 18, 0.8);
}

/* Machine Learning : v-slide-3 */
#v3-1:checked ~ .v-slides { transform: translateY(0%); }
#v3-2:checked ~ .v-slides { transform: translateY(-100%); }
#v3-3:checked ~ .v-slides { transform: translateY(-200%); }

#v3-1:checked ~ .v-dots .v3-dot-1,
#v3-2:checked ~ .v-dots .v3-dot-2,
#v3-3:checked ~ .v-dots .v3-dot-3 {
  background: #ed2b12;
  box-shadow: 0 0 12px rgba(237, 43, 18, 0.8);
}

/* -------- Dots horizontaux inter-catégories -------- */
.carousel-dots {
  position: absolute;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 15px;
  z-index: 100;
}

.carousel-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #555;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 2px solid transparent;
}

.carousel-dot:hover {
  transform: scale(1.3);
  background: #777;
}

.carousel-nav input[name="carousel-slide"] {
  display: none;
}

/* Slides horizontaux */
#slide-1:checked ~ .carousel-container .carousel-slides {
  transform: translateX(0%);
}
#slide-2:checked ~ .carousel-container .carousel-slides {
  transform: translateX(-100%);
}
#slide-3:checked ~ .carousel-container .carousel-slides {
  transform: translateX(-200%);
}

#slide-1:checked ~ .carousel-dots .dot-1,
#slide-2:checked ~ .carousel-dots .dot-2,
#slide-3:checked ~ .carousel-dots .dot-3 {
  background: #ed2b12;
  box-shadow: 0 0 20px rgba(237, 43, 18, 0.8);
  width: 32px;
  border-radius: 7px;
}
</style>
</head>
<body>
  <div class="carousel-wrapper">
    <div class="carousel-nav">
      <!-- Carrousel horizontal inter-catégories -->
      <input type="radio" name="carousel-slide" id="slide-1" checked />
      <input type="radio" name="carousel-slide" id="slide-2" />
      <input type="radio" name="carousel-slide" id="slide-3" />

      <div class="carousel-container">
        <div class="carousel-slides">
          <!-- Slide 1: Découverte -->
          <div class="carousel-slide">
            <div class="slide-content">
              <div class="carousel-slide-icon">👀</div>
              <div class="carousel-slide-title">Découverte</div>

              <div class="v-carousel">
                <div class="v-nav">
                  <input type="radio" name="v-slide-1" id="v1-1" checked />
                  <input type="radio" name="v-slide-1" id="v1-2" />
                  <input type="radio" name="v-slide-1" id="v1-3" />

                  <div class="v-slides">
                    <div class="v-slide">
                      <div class="v-slide-title">Vue d'ensemble</div>
                      <div class="v-slide-desc">
                        KPIs globaux sur ta base : nombre de films & séries, notes moyennes,
                        volumes par plateforme et progression dans le temps.
                      </div>
                    </div>
                    <div class="v-slide">
                      <div class="v-slide-title">Genres & ambiances</div>
                      <div class="v-slide-desc">
                        Répartition des genres, popularité, durées moyennes, pays d'origine…
                        de quoi sentir le mood de ta watchlist.
                      </div>
                    </div>
                    <div class="v-slide">
                      <div class="v-slide-title">Timeline cinéma</div>
                      <div class="v-slide-desc">
                        Exploration par années et décennies : périodes les plus représentées,
                        pics de visionnage et périodes creuses.
                      </div>
                    </div>
                  </div>

                  <div class="v-dots">
                    <label for="v1-1" class="v-dot v1-dot-1"></label>
                    <label for="v1-2" class="v-dot v1-dot-2"></label>
                    <label for="v1-3" class="v-dot v1-dot-3"></label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Slide 2: Data Analyse -->
          <div class="carousel-slide">
            <div class="slide-content">
              <div class="carousel-slide-icon">📊</div>
              <div class="carousel-slide-title">Data Analyse</div>

              <div class="v-carousel">
                <div class="v-nav">
                  <input type="radio" name="v-slide-2" id="v2-1" checked />
                  <input type="radio" name="v-slide-2" id="v2-2" />
                  <input type="radio" name="v-slide-2" id="v2-3" />

                  <div class="v-slides">
                    <div class="v-slide">
                      <div class="v-slide-title">Distributions & densités</div>
                      <div class="v-slide-desc">
                        Analyse des distributions de notes, durées, popularité, années de sortie
                        avec histogrammes, KDE et boxplots.
                      </div>
                    </div>
                    <div class="v-slide">
                      <div class="v-slide-title">Comparaisons croisées</div>
                      <div class="v-slide-desc">
                        Comparaisons entre plateformes, genres, réalisateurs ou pays pour détecter
                        tes zones de confort… et d'oubli.
                      </div>
                    </div>
                    <div class="v-slide">
                      <div class="v-slide-title">Corrélations & patterns</div>
                      <div class="v-slide-desc">
                        Matrices de corrélation, scatter plots et analyses multi-variables
                        pour comprendre ce qui influence vraiment tes notes.
                      </div>
                    </div>
                  </div>

                  <div class="v-dots">
                    <label for="v2-1" class="v-dot v2-dot-1"></label>
                    <label for="v2-2" class="v-dot v2-dot-2"></label>
                    <label for="v2-3" class="v-dot v2-dot-3"></label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Slide 3: Machine Learning -->
          <div class="carousel-slide">
            <div class="slide-content">
              <div class="carousel-slide-icon">🤖</div>
              <div class="carousel-slide-title">Machine Learning</div>

              <div class="v-carousel">
                <div class="v-nav">
                  <input type="radio" name="v-slide-3" id="v3-1" checked />
                  <input type="radio" name="v-slide-3" id="v3-2" />
                  <input type="radio" name="v-slide-3" id="v3-3" />

                  <div class="v-slides">
                    <div class="v-slide">
                      <div class="v-slide-title">Recommandations personnalisées</div>
                      <div class="v-slide-desc">
                        Systèmes de recommandation basés sur tes notes, genres favoris et similarité
                        entre œuvres (collaboratif & contenu).
                      </div>
                    </div>
                    <div class="v-slide">
                      <div class="v-slide-title">Prédiction de notes</div>
                      <div class="v-slide-desc">
                        Modèles supervisés pour estimer la note que tu donnerais à un film
                        avant même de l'avoir vu.
                      </div>
                    </div>
                    <div class="v-slide">
                      <div class="v-slide-title">Clustering de goûts</div>
                      <div class="v-slide-desc">
                        Segmentation de tes préférences en clusters : périodes, genres, moods,
                        réalisateurs… pour comprendre tes phases.
                      </div>
                    </div>
                  </div>

                  <div class="v-dots">
                    <label for="v3-1" class="v-dot v3-dot-1"></label>
                    <label for="v3-2" class="v-dot v3-dot-2"></label>
                    <label for="v3-3" class="v-dot v3-dot-3"></label>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- Dots horizontaux -->
      <div class="carousel-dots">
        <label for="slide-1" class="carousel-dot dot-1"></label>
        <label for="slide-2" class="carousel-dot dot-2"></label>
        <label for="slide-3" class="carousel-dot dot-3"></label>
      </div>
    </div>
  </div>

  <script>
    document.addEventListener('keydown', (e) => {
      // Carrousel horizontal
      const slides = document.querySelectorAll('input[name="carousel-slide"]');
      let currentIndex = 0;
      for (let i = 0; i < slides.length; i++) {
        if (slides[i].checked) {
          currentIndex = i;
          break;
        }
      }
      
      if (e.key === 'ArrowRight') {
        slides[(currentIndex + 1) % slides.length].checked = true;
        return;
      } else if (e.key === 'ArrowLeft') {
        slides[(currentIndex - 1 + slides.length) % slides.length].checked = true;
        return;
      }

      // Carrousels verticaux (intra-catégorie)
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        const currentSlideId = slides[currentIndex].id; // slide-1 / slide-2 / slide-3
        const vName = 'v-' + currentSlideId; // v-slide-1 etc.
        const vRadios = document.querySelectorAll('input[name="' + vName + '"]');
        if (!vRadios.length) return;

        let vIndex = 0;
        for (let i = 0; i < vRadios.length; i++) {
          if (vRadios[i].checked) {
            vIndex = i;
            break;
          }
        }

        if (e.key === 'ArrowDown') {
          vRadios[(vIndex + 1) % vRadios.length].checked = true;
        } else if (e.key === 'ArrowUp') {
          vRadios[(vIndex - 1 + vRadios.length) % vRadios.length].checked = true;
        }
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
        padding: 0 !important;
        margin: 0 !important;
    }

    iframe {
        border: none !important;
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
# Carrousel fullscreen
# =========================================================
def show_fullscreen_carousel():
    components.html(FULLSCREEN_CAROUSEL_HTML, height=900, scrolling=False)

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
    time.sleep(8)  # <= plus cohérent avec la durée réelle de l'animation
    st.session_state.show_dashboard = True
    st.rerun()
else:
    show_fullscreen_carousel()
