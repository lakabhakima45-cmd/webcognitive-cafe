"""
interface.py
Étape 6 : interface web (front-end) du WebCognitive Engine, faite avec Streamlit.

L'interface ne contient aucune intelligence : elle appelle l'API REST (FastAPI)
par des requêtes HTTP et affiche les résultats.
  - mode « Assistant »  -> POST /chat   (réponse du LLM local + sources)
  - mode « Recherche »  -> GET  /search (passages les plus proches, sans LLM, instantané)
  - barre latérale      -> GET  /      et GET /stats (état de l'API et de la base)

Sous chaque réponse, on affiche les sources exactes : nom du fichier,
numéro de page (pour les PDF), score de similarité et extrait du passage.

Lancement (2 terminaux, depuis le dossier du projet) :
  1) .venv\\Scripts\\python.exe -m uvicorn api:app --app-dir src
  2) .venv\\Scripts\\python.exe -m streamlit run src\\interface.py
"""

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"
DELAI_CHAT = 600      # le LLM sur CPU peut être lent
DELAI_COURT = 120     # la 1re recherche charge le modèle d'embedding

EXEMPLES = [
    "Quel pays est le premier producteur mondial de café ?",
    "Quelle est la différence entre l'arabica et le robusta ?",
    "Qu'est-ce que la torréfaction ?",
    "Comment prépare-t-on un espresso ?",
]

st.set_page_config(page_title="WebCognitive – Café", page_icon="☕", layout="wide")


# ---------- appels à l'API ----------

def api_get(route, **params):
    r = requests.get(API_URL + route, params=params, timeout=DELAI_COURT)
    r.raise_for_status()
    return r.json()


def api_chat(question, k):
    r = requests.post(API_URL + "/chat", json={"question": question, "k": k}, timeout=DELAI_CHAT)
    if r.status_code == 503:
        raise RuntimeError("Ollama ne répond pas. Lance l'application Ollama puis réessaie.")
    r.raise_for_status()
    return r.json()


def api_en_ligne():
    try:
        requests.get(API_URL + "/", timeout=3).raise_for_status()
        return True
    except requests.RequestException:
        return False


# ---------- affichage des sources ----------

def nom_source(s):
    page = f" — page {s['page']}" if s.get("page") else ""
    return f"{s['fichier']}{page}"


def afficher_sources(sources, titre="Sources utilisées", ouvert=False):
    if not sources:
        return
    with st.expander(f"📄 {titre} ({len(sources)})", expanded=ouvert):
        for s in sources:
            numero = f"[{s['numero']}] " if "numero" in s else ""
            st.markdown(f"**{numero}{nom_source(s)}**  ·  similarité {s['score']:.2f}")
            if s.get("titre"):
                st.caption(s["titre"])
            extrait = s.get("extrait") or s.get("texte", "")[:300]
            st.markdown(f"> {extrait}…")


# ---------- barre latérale ----------

with st.sidebar:
    st.title("☕ WebCognitive")
    st.caption("Moteur de recherche sémantique sur le café — 100 % local")

    en_ligne = api_en_ligne()
    if en_ligne:
        st.success("API connectée")
        try:
            stats = api_get("/stats")
            col1, col2 = st.columns(2)
            col1.metric("Documents", stats.get("documents", "–"))
            col2.metric("Morceaux", stats.get("morceaux", "–"))
        except requests.RequestException:
            pass
    else:
        st.error("API hors ligne")
        st.code(".venv\\Scripts\\python.exe -m uvicorn api:app --app-dir src", language="powershell")

    st.divider()
    mode = st.radio("Mode", ["💬 Assistant (IA)", "🔎 Recherche rapide"])
    k = st.slider("Nombre de passages", 1, 10, 5)

    if st.button("🗑️ Effacer la conversation"):
        st.session_state.historique = []
        st.rerun()

    st.divider()
    st.caption("Exemples de questions")
    for ex in EXEMPLES:
        if st.button(ex, use_container_width=True):
            st.session_state.question_exemple = ex


# ---------- zone de dialogue ----------

if "historique" not in st.session_state:
    st.session_state.historique = []

st.header("Pose ta question sur le café")
if mode.startswith("💬"):
    st.caption("L'IA (Llama 3.2 en local) répond uniquement à partir des 30 documents du corpus "
               "et cite ses sources. Une réponse peut prendre une à deux minutes.")
else:
    st.caption("Affiche directement les passages les plus proches de ta question, sans IA. Instantané.")

# on réaffiche toute la conversation
for msg in st.session_state.historique:
    with st.chat_message(msg["role"], avatar="🙂" if msg["role"] == "user" else "☕"):
        st.markdown(msg["texte"])
        if msg.get("infos"):
            st.caption(msg["infos"])
        afficher_sources(msg.get("sources", []))

question = st.chat_input("Ex. : Quelle est l'origine du café ?", disabled=not en_ligne)
if not question and st.session_state.get("question_exemple"):
    question = st.session_state.pop("question_exemple")

if question:
    st.session_state.historique.append({"role": "user", "texte": question})
    with st.chat_message("user", avatar="🙂"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="☕"):
        try:
            if mode.startswith("💬"):
                with st.spinner("Recherche des passages puis rédaction de la réponse…"):
                    r = api_chat(question, k)
                texte = r["reponse"]
                sources = r["sources"]
                infos = f"{r['modele_llm']} · {r['duree_totale_s']} s"
            else:
                r = api_get("/search", q=question, k=k)
                sources = r["resultats"]
                texte = f"Voici les **{len(sources)} passages** les plus proches de ta question :"
                for i, s in enumerate(sources, start=1):
                    s["numero"] = i
                infos = "recherche sémantique (ChromaDB)"
        except (requests.RequestException, RuntimeError) as e:
            texte, sources, infos = f"⚠️ Erreur : {e}", [], ""

        st.markdown(texte)
        if infos:
            st.caption(infos)
        afficher_sources(sources, "Sources" if mode.startswith("💬") else "Passages trouvés",
                         ouvert=not mode.startswith("💬"))

    st.session_state.historique.append(
        {"role": "assistant", "texte": texte, "sources": sources, "infos": infos}
    )
