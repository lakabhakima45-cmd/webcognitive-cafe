"""
analyse.py
Étape 7 : analyse statistique du corpus et de la base vectorielle (module de dataviz).

Calcule les indicateurs affichés dans l'onglet « Analyse » de l'interface :
  1. Répartition des documents par format et par langue
  2. Taille des documents (nombre de mots)
  3. Répartition des morceaux (chunks) par format et distribution de leur taille
  4. Fréquence des mots-clés du café (variétés, torréfaction, boissons...)
  5. Pays producteurs les plus cités
  6. Thèmes abordés par chaque document (carte de chaleur)
  7. Mots les plus fréquents du corpus
  8. Carte sémantique : position des documents selon leur sens (vecteurs réduits en 2D)

Les points 1, 2, 4 à 7 viennent des documents nettoyés (data/processed).
Les points 3 et 8 viennent de la base vectorielle ChromaDB (data/chroma).

Utilisation :
    python src/analyse.py        -> affiche les indicateurs et écrit docs/analyse_corpus.md
L'API les expose sur GET /analyse.
"""

import json
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DOCS = RACINE / "data" / "processed"
DOSSIER_BASE = RACINE / "data" / "chroma"
NOM_COLLECTION = "corpus_cafe"
RAPPORT = RACINE / "docs" / "analyse_corpus.md"

# ---------- mots-clés du thème (formes françaises et anglaises, sans accents) ----------

MOTS_CLES = {
    "Arabica": ["arabica"],
    "Robusta": ["robusta"],
    "Caféier": ["cafeier", "coffea", "coffee tree"],
    "Plantation": ["plantation", "plantations", "planteur", "planteurs"],
    "Récolte": ["recolte", "recoltes", "cueillette", "harvest"],
    "Torréfaction": ["torrefaction", "torrefie", "torrefies", "torrefacteur", "roast", "roasting", "roasted"],
    "Mouture": ["mouture", "moudre", "moulin", "grinding", "grind"],
    "Fermentation": ["fermentation"],
    "Espresso": ["espresso", "espressos", "expresso"],
    "Cappuccino": ["cappuccino"],
    "Café filtre": ["filtre", "filter", "percolateur"],
    "Barista": ["barista", "baristas"],
    "Caféine": ["cafeine", "caffeine"],
    "Santé": ["sante", "health"],
    "Prix": ["prix", "price", "prices"],
    "Exportation": ["exportation", "exportations", "export", "exports"],
    "Commerce équitable": ["commerce equitable", "fair trade", "fairtrade", "max havelaar"],
    "Histoire": ["histoire", "history", "historique"],
    "Légende": ["legende", "legend"],
}

THEMES = {
    "Botanique": ["Arabica", "Robusta", "Caféier"],
    "Culture et récolte": ["Plantation", "Récolte"],
    "Transformation": ["Torréfaction", "Mouture", "Fermentation"],
    "Boissons": ["Espresso", "Cappuccino", "Café filtre", "Barista"],
    "Santé": ["Caféine", "Santé"],
    "Économie": ["Prix", "Exportation", "Commerce équitable"],
    "Histoire": ["Histoire", "Légende"],
}

PAYS = {
    "Brésil": ["bresil", "brazil", "brasil"],
    "Vietnam": ["vietnam", "viet nam"],
    "Colombie": ["colombie", "colombia"],
    "Éthiopie": ["ethiopie", "ethiopia", "abyssinie", "abyssinia"],
    "Indonésie": ["indonesie", "indonesia", "java", "sumatra"],
    "Yémen": ["yemen", "moka", "mocha"],
    "Kenya": ["kenya"],
    "Honduras": ["honduras"],
    "Guatemala": ["guatemala"],
    "Inde": ["inde", "india"],
    "Ouganda": ["ouganda", "uganda"],
    "Pérou": ["perou", "peru"],
    "Mexique": ["mexique", "mexico"],
    "Côte d'Ivoire": ["cote d'ivoire", "ivory coast"],
    "Jamaïque": ["jamaique", "jamaica"],
}

MOTS_VIDES = set("""
le la les un une des du de d l au aux et ou en dans sur sous par pour avec sans ce cet cette ces
son sa ses leur leurs qui que quoi dont ou est sont etait etaient ete etre avoir a ont avait
plus moins tres aussi bien comme mais donc car ni ne pas se si il ils elle elles on nous vous
je tu y lui eux meme tout tous toute toutes autre autres entre apres avant depuis lors fait
faire peut peuvent sont cela celle celui ceux celles ainsi alors encore deja selon chez vers
dont quand comment pendant notamment egalement environ partir plusieurs grande grand
the and of to in is that for with was on as by it be are this from at or an which have has
had were but not their they its his her he she been more one also can all into than other
some there would these such when only who what about out may them will most any made used
very much well each many those then like being over after first so we our two upon where
annee annees puis deux trois cours lorsque tandis chaque jusqu ensuite toujours souvent
year years time three
""".split())
MOTS_RETIRES = {"cafe", "cafes", "coffee", "coffees"}   # le mot du thème lui-même


# ---------- outils ----------

def sans_accents(texte):
    """« Torréfaction » -> « torrefaction » : on compare les mots sans accents ni majuscules."""
    texte = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn").replace("’", "'")


def motif(variantes):
    """Expression régulière qui trouve une des variantes comme mot entier."""
    return re.compile(r"\b(?:" + "|".join(re.escape(v) for v in variantes) + r")\b")


MOTIFS_MOTS_CLES = {nom: motif(v) for nom, v in MOTS_CLES.items()}
MOTIFS_PAYS = {nom: motif(v) for nom, v in PAYS.items()}


def charger_corpus():
    """Charge les documents nettoyés de l'étape 2."""
    docs = []
    for f in sorted(DOSSIER_DOCS.glob("doc_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        d["texte_simple"] = sans_accents(d.get("texte", ""))
        docs.append(d)
    return docs


def nom_court(fichier, n=28):
    return fichier if len(fichier) <= n else fichier[: n - 1] + "…"


# ---------- indicateurs sur les documents ----------

def indicateurs_documents(docs):
    return {
        "nb_documents": len(docs),
        "nb_mots": sum(d.get("nb_mots", 0) for d in docs),
        "nb_pages_pdf": sum(d.get("nb_pages") or 0 for d in docs if d["format"] == "pdf"),
        "par_format": dict(Counter(d["format"] for d in docs)),
        "par_langue": dict(Counter(d.get("langue", "?") for d in docs)),
        "documents": sorted(
            ({"fichier": d["fichier"], "titre": d.get("titre", ""), "format": d["format"],
              "langue": d.get("langue", "?"), "nb_mots": d.get("nb_mots", 0)} for d in docs),
            key=lambda x: x["nb_mots"], reverse=True),
    }


def compter(docs, motifs):
    """Pour chaque mot-clé : nombre total d'occurrences et nombre de documents qui le citent."""
    resultat = []
    for nom, m in motifs.items():
        par_doc = {d["fichier"]: len(m.findall(d["texte_simple"])) for d in docs}
        resultat.append({
            "nom": nom,
            "occurrences": sum(par_doc.values()),
            "nb_documents": sum(1 for n in par_doc.values() if n),
            "par_document": par_doc,
        })
    return sorted(resultat, key=lambda x: x["occurrences"], reverse=True)


def themes_par_document(docs, mots_cles):
    """Carte de chaleur : pour chaque document, poids de chaque thème
    (occurrences pour 1 000 mots, pour comparer des documents de tailles différentes)."""
    par_nom = {m["nom"]: m["par_document"] for m in mots_cles}
    lignes = []
    for d in docs:
        mille_mots = max(d.get("nb_mots", 0), 1) / 1000
        valeurs = [round(sum(par_nom[k][d["fichier"]] for k in cles) / mille_mots, 2)
                   for cles in THEMES.values()]
        lignes.append({"fichier": d["fichier"], "valeurs": valeurs})
    return {"themes": list(THEMES), "documents": lignes}


def mots_frequents(docs, n=20):
    """Mots les plus fréquents des documents en français (sinon les gros livres anglais
    de 1922 écrasent tout le reste)."""
    compteur = Counter()
    for d in docs:
        if d.get("langue") != "fr":
            continue
        for mot in re.findall(r"[a-z]{4,}", d["texte_simple"]):
            if mot not in MOTS_VIDES and mot not in MOTS_RETIRES:
                compteur[mot] += 1
    return [{"mot": m, "occurrences": c} for m, c in compteur.most_common(n)]


# ---------- indicateurs sur la base vectorielle ----------

def lire_base(avec_vecteurs=True):
    import chromadb   # importé ici : seule cette partie a besoin de la base
    collection = chromadb.PersistentClient(path=str(DOSSIER_BASE)).get_collection(NOM_COLLECTION)
    include = ["metadatas", "embeddings"] if avec_vecteurs else ["metadatas"]
    return collection.get(include=include)


def indicateurs_morceaux(metas):
    tailles = [m.get("nb_caracteres", 0) for m in metas]
    par_doc = Counter(m["fichier"] for m in metas)
    return {
        "nb_morceaux": len(metas),
        "par_format": dict(Counter(m["format"] for m in metas)),
        "tailles": tailles,
        "taille_moyenne": round(float(np.mean(tailles)), 1) if tailles else 0,
        "taille_mediane": float(np.median(tailles)) if tailles else 0,
        "par_document": [{"fichier": f, "nb_morceaux": n} for f, n in par_doc.most_common()],
    }


def carte_semantique(metas, vecteurs):
    """Chaque document = moyenne des vecteurs de ses morceaux (384 nombres).
    On réduit ces 384 dimensions à 2 avec une ACP (analyse en composantes principales)
    pour les placer sur un graphique : deux documents proches parlent des mêmes sujets."""
    groupes = defaultdict(list)
    infos = {}
    for meta, v in zip(metas, vecteurs):
        groupes[meta["doc_id"]].append(v)
        infos[meta["doc_id"]] = meta
    ids = sorted(groupes)
    if len(ids) < 3:
        return {"points": [], "variance_expliquee": []}
    X = np.array([np.mean(groupes[i], axis=0) for i in ids])
    X = X / np.linalg.norm(X, axis=1, keepdims=True)
    X = X - X.mean(axis=0)
    _, s, vt = np.linalg.svd(X, full_matrices=False)
    coords = X @ vt[:2].T
    variance = (s ** 2) / (s ** 2).sum()
    return {
        "variance_expliquee": [round(float(v) * 100, 1) for v in variance[:2]],
        "points": [{"fichier": infos[i]["fichier"], "titre": infos[i]["titre"],
                    "format": infos[i]["format"], "nb_morceaux": len(groupes[i]),
                    "x": round(float(x), 4), "y": round(float(y), 4)}
                   for i, (x, y) in zip(ids, coords)],
    }


# ---------- analyse complète ----------

def analyser():
    debut = time.time()
    docs = charger_corpus()
    if not docs:
        raise RuntimeError("Aucun document dans data/processed : lancer d'abord pipeline_ingestion.py")
    mots_cles = compter(docs, MOTIFS_MOTS_CLES)
    resultat = {
        "documents": indicateurs_documents(docs),
        "mots_cles": mots_cles,
        "pays": [p for p in compter(docs, MOTIFS_PAYS) if p["occurrences"]],
        "themes": themes_par_document(docs, mots_cles),
        "mots_frequents": mots_frequents(docs),
    }
    resultat["morceaux"] = resultat["carte"] = None
    try:
        base = lire_base()
        resultat["morceaux"] = indicateurs_morceaux(base["metadatas"])
        resultat["carte"] = carte_semantique(base["metadatas"], base["embeddings"])
    except Exception as e:   # base absente : on garde les indicateurs sur les documents
        resultat["erreur_base"] = str(e)
    resultat["duree_s"] = round(time.time() - debut, 1)
    return resultat


def ecrire_rapport(r):
    d = r["documents"]
    lignes = [
        "# Analyse du corpus (étape 7)", "",
        f"- Documents : **{d['nb_documents']}** · mots : **{d['nb_mots']:,}** · pages PDF : **{d['nb_pages_pdf']}**".replace(",", " "),
    ]
    if r.get("morceaux"):
        m = r["morceaux"]
        lignes.append(f"- Morceaux dans ChromaDB : **{m['nb_morceaux']}** "
                      f"(taille moyenne {m['taille_moyenne']} caractères, médiane {m['taille_mediane']:.0f})")
    lignes += ["", "## Documents par format", "", "| Format | Documents |", "|---|---|"]
    lignes += [f"| {f} | {n} |" for f, n in sorted(d["par_format"].items())]
    if r.get("morceaux"):
        lignes += ["", "## Morceaux par format", "", "| Format | Morceaux |", "|---|---|"]
        lignes += [f"| {f} | {n} |" for f, n in sorted(r["morceaux"]["par_format"].items())]
    lignes += ["", "## Mots-clés du café", "", "| Mot-clé | Occurrences | Documents qui le citent |", "|---|---|---|"]
    lignes += [f"| {k['nom']} | {k['occurrences']} | {k['nb_documents']} |" for k in r["mots_cles"]]
    lignes += ["", "## Pays producteurs les plus cités", "", "| Pays | Occurrences | Documents |", "|---|---|---|"]
    lignes += [f"| {p['nom']} | {p['occurrences']} | {p['nb_documents']} |" for p in r["pays"]]
    lignes += ["", "## 20 mots les plus fréquents des documents en français (hors mots vides et « café »)", "",
               ", ".join(f"{m['mot']} ({m['occurrences']})" for m in r["mots_frequents"]), ""]
    RAPPORT.parent.mkdir(exist_ok=True)
    RAPPORT.write_text("\n".join(lignes), encoding="utf-8")


if __name__ == "__main__":
    r = analyser()
    d = r["documents"]
    print(f"Documents : {d['nb_documents']}  |  mots : {d['nb_mots']}  |  formats : {d['par_format']}")
    if r.get("morceaux"):
        print(f"Morceaux : {r['morceaux']['nb_morceaux']}  |  par format : {r['morceaux']['par_format']}")
        print(f"Carte sémantique : {len(r['carte']['points'])} documents placés "
              f"(variance expliquée {r['carte']['variance_expliquee']} %)")
    else:
        print("Base vectorielle non lue :", r.get("erreur_base"))
    print("Top mots-clés :", ", ".join(f"{k['nom']} {k['occurrences']}" for k in r["mots_cles"][:6]))
    print("Top pays :", ", ".join(f"{p['nom']} {p['occurrences']}" for p in r["pays"][:6]))
    print("Top mots :", ", ".join(m["mot"] for m in r["mots_frequents"][:10]))
    ecrire_rapport(r)
    print(f"\nRapport écrit : {RAPPORT.relative_to(RACINE)}  ({r['duree_s']} s)")
    sys.exit(0)
