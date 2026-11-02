"""
interface.py
Interface web (front-end) du WebCognitive Engine, faite avec Streamlit.

Deux vues, choisies dans la barre latérale :
  - 💬 Chat (étape 6)     : dialogue avec le moteur RAG, sources affichées sous chaque réponse
  - 📊 Analyse (étape 7)  : tableau de bord de graphiques (Plotly) sur le corpus

L'interface ne contient aucune intelligence : elle appelle l'API REST (FastAPI)
par des requêtes HTTP et affiche les résultats.
  - mode « Assistant »  -> POST /chat/stream (réponse du LLM local mot par mot + sources)
  - mode « Recherche »  -> GET  /search  (passages les plus proches, sans LLM, instantané)
  - vue « Analyse »     -> GET  /analyse (indicateurs statistiques)
  - barre latérale      -> GET  /  et  GET /stats (état de l'API et de la base)

Lancement (2 terminaux, depuis le dossier du projet) :
  1) .venv\\Scripts\\python.exe -m uvicorn api:app --app-dir src
  2) .venv\\Scripts\\python.exe -m streamlit run src\\interface.py
"""

import json

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"
DELAI_CHAT = 600      # le LLM sur CPU peut être lent
DELAI_COURT = 120     # la 1re recherche charge le modèle d'embedding
DELAI_ANALYSE = 300   # la 1re analyse lit tous les vecteurs de la base

COULEURS_FORMATS = {"pdf": "#c0392b", "html": "#2e86c1", "docx": "#8e44ad", "txt": "#27ae60"}
NOMS_LANGUES = {"fr": "Français", "en": "Anglais"}

EXEMPLES = [
    "Quel pays est le premier producteur mondial de café ?",
    "Quelle est la différence entre l'arabica et le robusta ?",
    "Qu'est-ce que la torréfaction ?",
    "Comment prépare-t-on un espresso ?",
]

st.set_page_config(page_title="WebCognitive – Café", page_icon="☕", layout="wide")


# ---------- appels à l'API ----------

def api_get(route, delai=DELAI_COURT, **params):
    r = requests.get(API_URL + route, params=params, timeout=delai)
    r.raise_for_status()
    return r.json()


def api_chat_en_direct(question, k, resultat):
    """Appelle POST /chat/stream et renvoie la réponse morceau par morceau (générateur).
    Les sources et la durée sont rangées dans le dictionnaire « resultat »."""
    r = requests.post(API_URL + "/chat/stream", json={"question": question, "k": k},
                      stream=True, timeout=DELAI_CHAT)
    if r.status_code == 503:
        raise RuntimeError("Ollama ne répond pas. Lance l'application Ollama puis réessaie.")
    r.raise_for_status()
    r.encoding = "utf-8"
    for ligne in r.iter_lines(decode_unicode=True):
        if not ligne:
            continue
        message = json.loads(ligne)
        if message["type"] == "texte":
            yield message["texte"]
        elif message["type"] == "sources":
            resultat["sources"] = message["sources"]
        elif message["type"] == "fin":
            resultat["infos"] = f"{message['modele_llm']} · {message['duree_totale_s']} s"
        elif message["type"] == "erreur":
            raise RuntimeError(message["message"])


def api_en_ligne():
    try:
        requests.get(API_URL + "/", timeout=3).raise_for_status()
        return True
    except requests.RequestException:
        return False


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
    vue = st.radio("Vue", ["💬 Chat", "📊 Analyse du corpus"], horizontal=True)


# =====================================================================
# VUE 1 : CHAT (étape 6)
# =====================================================================

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


def conversation_en_texte(historique):
    """Transforme la conversation en texte (Markdown) pour la télécharger."""
    lignes = ["# Conversation WebCognitive – Café", ""]
    for msg in historique:
        if msg["role"] == "user":
            lignes.append(f"## Question : {msg['texte']}")
        else:
            lignes.append(msg["texte"])
            if msg.get("infos"):
                lignes.append(f"*{msg['infos']}*")
            if msg.get("sources"):
                lignes.append("")
                lignes.append("**Sources :**")
                for s in msg["sources"]:
                    lignes.append(f"- {nom_source(s)} (similarité {s['score']:.2f})")
        lignes.append("")
    return "\n".join(lignes)


def vue_chat():
    with st.sidebar:
        mode = st.radio("Mode", ["💬 Assistant (IA)", "🔎 Recherche rapide"])
        k = st.slider("Nombre de passages", 1, 10, 5)
        if st.button("🗑️ Effacer la conversation"):
            st.session_state.historique = []
            st.rerun()
        if st.session_state.get("historique"):
            st.download_button(
                "💾 Télécharger la conversation",
                data=conversation_en_texte(st.session_state.historique),
                file_name="conversation_cafe.md",
                mime="text/markdown",
            )
        st.divider()
        st.caption("Exemples de questions")
        for ex in EXEMPLES:
            if st.button(ex, use_container_width=True):
                st.session_state.question_exemple = ex

    if "historique" not in st.session_state:
        st.session_state.historique = []

    ia = mode.startswith("💬")
    st.header("Pose ta question sur le café")
    if ia:
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
    if not question:
        return

    st.session_state.historique.append({"role": "user", "texte": question})
    with st.chat_message("user", avatar="🙂"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="☕"):
        try:
            if ia:
                # la réponse s'affiche mot par mot, au fur et à mesure que Llama l'écrit
                resultat = {"sources": [], "infos": ""}
                with st.spinner("Recherche des passages puis rédaction de la réponse…"):
                    texte = st.write_stream(api_chat_en_direct(question, k, resultat))
                sources, infos = resultat["sources"], resultat["infos"]
            else:
                r = api_get("/search", q=question, k=k)
                sources = r["resultats"]
                for i, s in enumerate(sources, start=1):
                    s["numero"] = i
                texte = f"Voici les **{len(sources)} passages** les plus proches de ta question :"
                infos = "recherche sémantique (ChromaDB)"
                st.markdown(texte)
        except (requests.RequestException, RuntimeError) as e:
            texte, sources, infos = f"⚠️ Erreur : {e}", [], ""
            st.markdown(texte)

        if infos:
            st.caption(infos)
        afficher_sources(sources, "Sources" if ia else "Passages trouvés", ouvert=not ia)

    st.session_state.historique.append(
        {"role": "assistant", "texte": texte, "sources": sources, "infos": infos}
    )
    # on recharge la page pour que le bouton de téléchargement contienne la dernière réponse
    st.rerun()


# =====================================================================
# VUE 2 : ANALYSE DU CORPUS (étape 7)
# =====================================================================

def graphique(fig, hauteur=380):
    fig.update_layout(height=hauteur, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)


def vue_analyse():
    st.header("📊 Analyse du corpus")
    st.caption("Vue d'ensemble des 30 documents sur le café et de la base vectorielle. "
               "Les graphiques sont interactifs : survole-les pour voir les valeurs.")

    if not en_ligne:
        st.warning("Démarre d'abord l'API pour voir les graphiques.")
        return

    rafraichir = st.sidebar.button("🔄 Recalculer l'analyse")
    try:
        with st.spinner("Calcul des indicateurs… (la première fois peut prendre une minute)"):
            a = api_get("/analyse", delai=DELAI_ANALYSE, rafraichir=str(rafraichir).lower())
    except requests.RequestException as e:
        st.error(f"Erreur : {e}")
        return

    docs, morceaux, carte = a["documents"], a.get("morceaux"), a.get("carte")

    # --- chiffres clés ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Documents", docs["nb_documents"])
    c2.metric("Mots", f"{docs['nb_mots']:,}".replace(",", " "))
    c3.metric("Pages PDF", docs["nb_pages_pdf"])
    c4.metric("Morceaux indexés", f"{morceaux['nb_morceaux']:,}".replace(",", " ") if morceaux else "–")
    if a.get("erreur_base"):
        st.info(f"Base vectorielle non lue : {a['erreur_base']}")

    # --- 1. formats ---
    st.subheader("1. Formats des documents")
    g, d = st.columns(2)
    with g:
        df = pd.DataFrame(docs["par_format"].items(), columns=["format", "documents"])
        graphique(px.pie(df, names="format", values="documents", hole=0.45, color="format",
                         color_discrete_map=COULEURS_FORMATS, title="Nombre de documents par format"))
    with d:
        if morceaux:
            df2 = pd.DataFrame(morceaux["par_format"].items(), columns=["format", "morceaux"])
            graphique(px.pie(df2, names="format", values="morceaux", hole=0.45, color="format",
                             color_discrete_map=COULEURS_FORMATS, title="Nombre de morceaux par format"))
    if morceaux:
        part_doc = docs["par_format"].get("pdf", 0) / docs["nb_documents"] * 100
        part_morc = morceaux["par_format"].get("pdf", 0) / morceaux["nb_morceaux"] * 100
        st.caption(f"Les PDF représentent {part_doc:.0f} % des documents mais {part_morc:.0f} % "
                   "des morceaux.")

    # --- 2. taille des documents ---
    st.subheader("2. Taille des documents")
    df = pd.DataFrame(docs["documents"])
    fig = px.bar(df.sort_values("nb_mots"), x="nb_mots", y="fichier", color="format", orientation="h",
                 color_discrete_map=COULEURS_FORMATS, log_x=True, hover_data=["titre", "langue"],
                 labels={"nb_mots": "nombre de mots (échelle logarithmique)", "fichier": ""},
                 title="Nombre de mots par document")
    graphique(fig, hauteur=750)

    # --- 3. morceaux ---
    if morceaux:
        st.subheader("3. Les morceaux de texte (chunks) dans ChromaDB")
        g, d = st.columns([2, 1])
        with g:
            fig = px.histogram(x=morceaux["tailles"], nbins=40, title="Distribution de la taille des morceaux",
                               labels={"x": "taille du morceau (caractères)"})
            fig.update_layout(yaxis_title="nombre de morceaux", showlegend=False)
            graphique(fig)
            st.caption(f"Taille moyenne : {morceaux['taille_moyenne']:.0f} caractères · "
                       f"médiane : {morceaux['taille_mediane']:.0f} (réglage choisi : 500 avec 100 de chevauchement).")
        with d:
            df = pd.DataFrame(docs["par_langue"].items(), columns=["langue", "documents"])
            df["langue"] = df["langue"].map(lambda x: NOMS_LANGUES.get(x, x))
            graphique(px.pie(df, names="langue", values="documents", hole=0.45, title="Langue des documents"))

    # --- 4. mots-clés et pays ---
    st.subheader("4. Les sujets du café dans le corpus")
    g, d = st.columns(2)
    with g:
        df = pd.DataFrame(a["mots_cles"])
        fig = px.bar(df.sort_values("occurrences"), x="occurrences", y="nom", orientation="h",
                     color="nb_documents", color_continuous_scale="YlOrBr",
                     labels={"nom": "", "nb_documents": "documents"},
                     title="Fréquence des mots-clés du café")
        graphique(fig, hauteur=560)
    with d:
        df = pd.DataFrame(a["pays"])
        if not df.empty:
            fig = px.bar(df.sort_values("occurrences"), x="occurrences", y="nom", orientation="h",
                         color="nb_documents", color_continuous_scale="YlOrBr",
                         labels={"nom": "", "nb_documents": "documents"},
                         title="Pays producteurs les plus cités")
            graphique(fig, hauteur=560)
    st.caption("La couleur indique dans combien de documents le mot apparaît.")

    # --- 5. thèmes par document ---
    st.subheader("5. Quels thèmes dans quel document ?")
    t = a["themes"]
    z = [ligne["valeurs"] for ligne in t["documents"]]
    noms = [ligne["fichier"] for ligne in t["documents"]]
    fig = px.imshow(z, x=t["themes"], y=noms, aspect="auto", color_continuous_scale="YlOrBr",
                    labels={"color": "pour 1 000 mots"}, title="Poids de chaque thème par document")
    graphique(fig, hauteur=800)
    st.caption("Plus la case est foncée, plus le document parle de ce thème "
               "(mots-clés pour 1 000 mots, pour comparer des documents de tailles différentes).")

    # --- 6. mots fréquents ---
    st.subheader("6. Mots les plus fréquents")
    df = pd.DataFrame(a["mots_frequents"])
    fig = px.bar(df, x="mot", y="occurrences", title="20 mots les plus fréquents des documents en français (sans les mots vides ni « café »)",
                 color_discrete_sequence=["#8d5524"])
    graphique(fig)

    # --- 7. carte sémantique ---
    if carte and carte["points"]:
        st.subheader("7. Carte sémantique des documents")
        df = pd.DataFrame(carte["points"])
        fig = px.scatter(df, x="x", y="y", color="format", size="nb_morceaux", size_max=35,
                         hover_name="fichier", hover_data={"titre": True, "x": False, "y": False},
                         color_discrete_map=COULEURS_FORMATS, title="Documents placés selon leur sens")
        fig.update_xaxes(showticklabels=False, title="")
        fig.update_yaxes(showticklabels=False, title="")
        graphique(fig, hauteur=550)
        st.caption("Chaque point est un document (moyenne des vecteurs de ses morceaux), réduit de 384 "
                   "à 2 dimensions avec une ACP. Deux points proches = deux documents qui parlent des "
                   "mêmes sujets. La taille du point = nombre de morceaux.")


# ---------- choix de la vue ----------

if vue.startswith("💬"):
    vue_chat()
else:
    vue_analyse()
