"""
recette.py
Étape 8 : recette (tests globaux) de toute l'application, en passant par l'API REST.

Vérifie toute la chaîne, comme le ferait un utilisateur :
  1. Les routes de l'API répondent         (GET /, /stats, /search, /analyse)
  2. L'interface web est en ligne           (http://localhost:8501)
  3. La recherche sémantique trouve le bon document pour les 10 questions de validation
     de l'étape 1, et les PDF ont bien un numéro de page
  4. (option --chat) L'assistant RAG répond juste et cite le bon document,
     et il répond « Je ne sais pas » à une question hors sujet

Le résultat est écrit dans docs/recette.md.

Utilisation (l'API doit être lancée dans un autre terminal) :
    python src/recette.py          -> tests rapides (environ 1 minute)
    python src/recette.py --chat   -> + réponses de l'IA (environ 15 minutes)
"""

import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

import requests

API_URL = "http://127.0.0.1:8000"
INTERFACE_URL = "http://localhost:8501"
RAPPORT = Path(__file__).resolve().parent.parent / "docs" / "recette.md"
K = 5

# Questions de validation de l'étape 1 (docs/questions_validation.md) :
# (question, document attendu, mots qui doivent apparaître dans la réponse)
QUESTIONS = [
    ("D'où le caféier est-il originaire ?", "cafeier", ["afrique", "asie"]),
    ("Quelles sont les deux espèces de café les plus cultivées ?", "cafeier", ["canephora", "robusta"]),
    ("Quelle part de la production mondiale représente l'arabica ?", "rapport-senat", ["trois-quarts", "trois quarts", "75"]),
    ("En quelle année l'Organisation internationale du café a-t-elle été créée ?", "rapport-assemblee", ["1963"]),
    ("Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ?", "filiere-cafe-en-afrique", ["27,2", "27.2"]),
    ("Quelles substances la torréfaction forme-t-elle dans le café ?", "cafe-climat-et-sante", ["acrylamide"]),
    ("Quelle part du prix d'un paquet de café revient aux petits producteurs ?", "le-cafe-grand-marche-mondial", ["10%", "10 %"]),
    ("De quelle région le café est-il originaire ?", "histoire-cafe", ["kaffa"]),
    ("Qu'est-ce que le kopi luwak ?", "kopi-luwak", ["civette"]),
    ("Quelle est la différence entre le café vert et le café torréfié ?", "torrefaction", ["grain vert", "vert"]),
]
HORS_SUJET = "Qui a gagné la Coupe du monde de football en 2018 ?"
# formulations par lesquelles l'IA refuse de répondre (elle ne dit pas toujours mot pour mot « Je ne sais pas »)
REFUS = ["je ne sais pas", "aucune information", "ne trouve pas", "ne trouve aucune",
         "pas dans les documents", "pas d'information", "ne contient pas", "ne mentionne pas"]

lignes = []


def simple(texte):
    """Minuscules sans accents, pour comparer les noms de fichiers et les mots."""
    texte = unicodedata.normalize("NFD", (texte or "").lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


def ecrire(*nouvelles):
    """Ajoute des lignes au rapport et l'enregistre tout de suite (rien n'est perdu si ça coupe)."""
    lignes.extend(nouvelles)
    RAPPORT.write_text("\n".join(lignes) + "\n", encoding="utf-8")


def ok(condition):
    return "✅" if condition else "❌"


def tester_routes():
    print("1. Routes de l'API")
    ecrire("## 1. Routes de l'API", "", "| Route | Résultat | Détail |", "|---|---|---|")
    resultats = []

    def essai(nom, fonction):
        t0 = time.time()
        try:
            reussi, detail = fonction()
        except Exception as e:
            reussi, detail = False, f"erreur : {e}"
        detail += f" ({time.time() - t0:.1f} s)"
        print(f"   {ok(reussi)} {nom} : {detail}")
        ecrire(f"| `{nom}` | {ok(reussi)} | {detail} |")
        resultats.append(reussi)

    def accueil():
        r = requests.get(API_URL + "/", timeout=10).json()
        return r.get("statut") == "en ligne", "API en ligne"

    def stats():
        r = requests.get(API_URL + "/stats", timeout=60).json()
        return r["documents"] == 30 and r["morceaux"] > 0, f"{r['documents']} documents, {r['morceaux']} morceaux"

    def search():
        r = requests.get(API_URL + "/search", params={"q": "origine du café", "k": 3}, timeout=120).json()
        res = r["resultats"]
        return len(res) == 3 and all("fichier" in x for x in res), f"{len(res)} passages avec leur source"

    def analyse():
        r = requests.get(API_URL + "/analyse", params={"rafraichir": "true"}, timeout=300).json()
        nb_points = len((r.get("carte") or {}).get("points", []))
        reussi = r["documents"]["nb_documents"] == 30 and r.get("morceaux") and nb_points == 30
        return reussi, f"indicateurs calculés, {nb_points} documents sur la carte sémantique"

    essai("GET /", accueil)
    essai("GET /stats", stats)
    essai("GET /search", search)
    essai("GET /analyse", analyse)
    ecrire("")
    return all(resultats)


def tester_interface():
    print("2. Interface web")
    try:
        en_ligne = requests.get(INTERFACE_URL, timeout=5).status_code == 200
    except requests.RequestException:
        en_ligne = False
    detail = "en ligne" if en_ligne else "non lancée (lancer : python -m streamlit run src\\interface.py)"
    print(f"   {ok(en_ligne)} {INTERFACE_URL} : {detail}")
    ecrire("## 2. Interface web", "", f"- {ok(en_ligne)} `{INTERFACE_URL}` : {detail}", "")


def tester_recherche():
    print(f"3. Recherche sémantique (top {K}) sur les {len(QUESTIONS)} questions de validation")
    ecrire(f"## 3. Recherche sémantique sur les questions de validation (top {K})", "",
           "| # | Question | Bon document dans le top 5 | Réponse dans les passages | 1re source | Score |",
           "|---|---|---|---|---|---|")
    bons_docs = bonnes_reponses = 0
    pages_pdf_ok = True
    for n, (question, doc, mots) in enumerate(QUESTIONS, start=1):
        r = requests.get(API_URL + "/search", params={"q": question, "k": K}, timeout=120).json()
        res = r["resultats"]
        bon_doc = any(doc in simple(x["fichier"]) for x in res)
        reponse = any(any(m in simple(x["texte"]) for m in mots) for x in res)
        pages_pdf_ok &= all(x.get("page") for x in res if x["format"] == "pdf")
        bons_docs += bon_doc
        bonnes_reponses += reponse
        premier = res[0]
        source = premier["fichier"] + (f" p.{premier['page']}" if premier.get("page") else "")
        print(f"   {ok(bon_doc)} {ok(reponse)} {question}")
        ecrire(f"| {n} | {question} | {ok(bon_doc)} | {ok(reponse)} | {source} | {premier['score']:.2f} |")
    ecrire("", f"**Bon document trouvé : {bons_docs}/{len(QUESTIONS)} · "
               f"réponse présente dans les passages : {bonnes_reponses}/{len(QUESTIONS)}**", "",
           f"- {ok(pages_pdf_ok)} Tous les passages venant d'un PDF ont un numéro de page.", "")
    print(f"   -> bon document {bons_docs}/{len(QUESTIONS)}, réponse dans les passages {bonnes_reponses}/{len(QUESTIONS)}")
    return bons_docs, bonnes_reponses


def tester_chat():
    print(f"4. Assistant RAG (chaque réponse prend 1 à 2 minutes)")
    ecrire("## 4. Assistant RAG (POST /chat)", "",
           "| # | Question | Réponse juste | Bon document cité | Durée |", "|---|---|---|---|---|")
    justes = cites = 0
    details = []
    for n, (question, doc, mots) in enumerate(QUESTIONS, start=1):
        print(f"   [{n}/{len(QUESTIONS)}] {question}")
        try:
            r = requests.post(API_URL + "/chat", json={"question": question, "k": K}, timeout=900).json()
        except requests.RequestException as e:
            ecrire(f"| {n} | {question} | ❌ | ❌ | erreur : {e} |")
            continue
        juste = any(m in simple(r["reponse"]) for m in mots)
        cite = any(doc in simple(s["fichier"]) for s in r["sources"])
        justes += juste
        cites += cite
        print(f"       {ok(juste)} réponse  {ok(cite)} source  ({r['duree_totale_s']} s)")
        ecrire(f"| {n} | {question} | {ok(juste)} | {ok(cite)} | {r['duree_totale_s']} s |")
        sources = ", ".join(s["fichier"] + (f" p.{s['page']}" if s.get("page") else "") for s in r["sources"])
        details += [f"**{n}. {question}**", "", f"> {r['reponse']}", "", f"*Sources : {sources}*", ""]

    print(f"   [hors sujet] {HORS_SUJET}")
    r = requests.post(API_URL + "/chat", json={"question": HORS_SUJET, "k": K}, timeout=900).json()
    refus = any(m in simple(r["reponse"]) for m in REFUS)
    print(f"       {ok(refus)} l'IA refuse de répondre hors du corpus")
    ecrire("", f"**Réponses justes : {justes}/{len(QUESTIONS)} · bon document cité : {cites}/{len(QUESTIONS)}**", "",
           f"- {ok(refus)} Question hors sujet (« {HORS_SUJET} ») : « {r['reponse'][:150]} »", "",
           "### Réponses complètes", "", *details)
    return justes, cites, refus


def main():
    avec_chat = "--chat" in sys.argv
    debut = time.time()
    ecrire("# Recette finale (étape 8)", "",
           f"Date : {datetime.now():%d/%m/%Y %H:%M} · tests passés par l'API REST ({API_URL})", "")
    try:
        requests.get(API_URL + "/", timeout=5)
    except requests.RequestException:
        print("L'API ne répond pas. Lance-la d'abord dans un autre terminal :")
        print("   .venv\\Scripts\\python.exe -m uvicorn api:app --app-dir src")
        sys.exit(1)

    tester_routes()
    tester_interface()
    tester_recherche()
    if avec_chat:
        tester_chat()
    else:
        ecrire("## 4. Assistant RAG", "", "Non lancé dans cette exécution (ajouter `--chat`).", "")
    duree = time.time() - debut
    ecrire(f"*Durée totale de la recette : {duree / 60:.1f} min*")
    print(f"\nRapport écrit : docs/recette.md  ({duree / 60:.1f} min)")


if __name__ == "__main__":
    main()
