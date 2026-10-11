"""
rag.py
Étape 5 : moteur de recherche sémantique + pipeline RAG (Retrieval-Augmented Generation) en local.

Fonctionnement pour une question :
  1. Recherche (Retrieval) : la question est transformée en vecteur, puis on récupère
     les K morceaux les plus proches dans ChromaDB (similarité cosinus) -> base_vectorielle.py
  2. Augmentation : ces morceaux sont insérés dans un prompt, avec leur source
  3. Génération : un modèle de langage local (Llama 3.2 via Ollama) rédige la réponse
     UNIQUEMENT à partir de ces passages, et cite ses sources [1], [2]...
     S'il ne trouve pas la réponse, il doit dire qu'il ne sait pas (pas d'invention).

Pré-requis : Ollama installé et lancé, avec le modèle téléchargé :
    ollama pull llama3.2:3b

Utilisation (depuis le dossier du projet) :
    python src/rag.py "Quel pays produit le plus de café ?"
    python src/rag.py --test        -> pose les 10 questions de validation (docs/test_rag.md)
"""

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

import base_vectorielle

OLLAMA_URL = "http://localhost:11434/api/chat"
MODELE_LLM = "llama3.2:3b"
K = 5                      # nombre de passages donnés au modèle
TEMPERATURE = 0.1          # faible : réponses factuelles, peu « créatives »

PROMPT_SYSTEME = """Tu es un assistant spécialisé sur le café.
À partir UNIQUEMENT du contexte textuel fourni ci-dessous, réponds précisément à la question de l'utilisateur.
Règles :
- Utilise les informations du contexte même si elles sont formulées autrement que dans la question.
- Ne réponds « Je ne sais pas : cette information n'est pas dans les documents du corpus. » que si le contexte ne contient vraiment aucune information utile.
- N'invente rien et n'utilise pas tes connaissances personnelles.
- Cite les passages utilisés avec leur numéro entre crochets, par exemple [1] ou [2][3].
- Réponds toujours en français, en quelques phrases claires, même si un passage est en anglais."""


class OllamaIndisponible(Exception):
    """Ollama n'est pas lancé ou le modèle n'est pas installé."""


def elargir(passages):
    """Ajoute à chaque passage le morceau qui le précède et celui qui le suit dans le même document.
    Évite qu'une information soit coupée entre deux morceaux
    (ex. le nom du pays dans un morceau, le chiffre dans le suivant)."""
    collection = base_vectorielle.ouvrir_collection()
    for p in passages:
        doc_id, position = p["chunk_id"].rsplit("_c", 1)
        position = int(position)
        voisins = [f"{doc_id}_c{position - 1:04d}", f"{doc_id}_c{position + 1:04d}"]
        trouves = collection.get(ids=voisins, include=["documents"])
        textes = dict(zip(trouves["ids"], trouves["documents"]))
        p["texte_elargi"] = " ".join(t for t in (textes.get(voisins[0]), p["texte"], textes.get(voisins[1])) if t)
    return passages


def construire_contexte(passages):
    """Numérote les passages et indique leur source pour la traçabilité."""
    blocs = []
    for i, p in enumerate(passages, start=1):
        source = p["fichier"] + (f", page {p['page']}" if p.get("page") else "")
        blocs.append(f"[{i}] (source : {source})\n{p.get('texte_elargi', p['texte'])}")
    return "\n\n".join(blocs)


def appeler_llm(question, contexte):
    """Envoie le prompt au modèle local via l'API d'Ollama."""
    message_utilisateur = f"Contexte :\n{contexte}\n\nQuestion : {question}"
    donnees = json.dumps({
        "model": MODELE_LLM,
        "messages": [
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "user", "content": message_utilisateur},
        ],
        "stream": False,
        "options": {"temperature": TEMPERATURE, "num_ctx": 8192},
    }).encode("utf-8")
    requete = urllib.request.Request(OLLAMA_URL, data=donnees,
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(requete, timeout=300) as reponse:
            resultat = json.loads(reponse.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise OllamaIndisponible(f"Erreur Ollama ({e.code}) : {detail}. "
                                 f"Le modèle est-il installé ? -> ollama pull {MODELE_LLM}")
    except urllib.error.URLError:
        raise OllamaIndisponible("Ollama ne répond pas. Vérifie qu'il est lancé "
                                 "(icône Ollama près de l'horloge, ou commande : ollama serve).")
    return resultat["message"]["content"].strip()


def repondre(question, k=K):
    """Pipeline RAG complet : recherche des passages, puis génération de la réponse."""
    debut = time.time()
    passages = elargir(base_vectorielle.rechercher(question, k=k))
    t_recherche = time.time() - debut

    reponse = appeler_llm(question, construire_contexte(passages))

    return {
        "question": question,
        "reponse": reponse,
        "sources": [
            {
                "numero": i,
                "fichier": p["fichier"],
                "titre": p["titre"],
                "page": p.get("page"),
                "score": p["score"],
                "extrait": p["texte"][:300],
            }
            for i, p in enumerate(passages, start=1)
        ],
        "modele_llm": MODELE_LLM,
        "duree_recherche_s": round(t_recherche, 2),
        "duree_totale_s": round(time.time() - debut, 1),
    }


def afficher(resultat):
    print(f"\nQuestion : {resultat['question']}\n")
    print(f"Réponse : {resultat['reponse']}\n")
    print("Sources :")
    for s in resultat["sources"]:
        page = f", page {s['page']}" if s["page"] else ""
        print(f"  [{s['numero']}] {s['fichier']}{page} (similarité {s['score']:.2f})")
    print(f"\n(recherche : {resultat['duree_recherche_s']} s, total : {resultat['duree_totale_s']} s)")


def tester():
    """Pose les 10 questions de validation + 2 questions hors sujet (le modèle doit dire qu'il ne sait pas)."""
    from test_chunking import QUESTIONS
    questions = [q for q, _, _ in QUESTIONS] + [
        "Qui a gagné la Coupe du monde de football en 2018 ?",
        "Quelle est la capitale de l'Australie ?",
    ]
    lignes = [
        "# Test du pipeline RAG",
        "",
        f"*Date : {datetime.now():%Y-%m-%d %H:%M} — modèle : `{MODELE_LLM}` — {K} passages par question*",
        "",
        "Les 10 premières questions sont les questions de validation. Les 2 dernières sont hors sujet : "
        "le modèle doit répondre qu'il ne sait pas.",
        "",
    ]
    for n, question in enumerate(questions, start=1):
        print(f"\n===== Question {n}/{len(questions)} =====")
        r = repondre(question)
        afficher(r)
        sources = ", ".join(f"[{s['numero']}] {s['fichier']}" + (f" p.{s['page']}" if s["page"] else "")
                            for s in r["sources"])
        lignes += [f"## {n}. {question}", "", r["reponse"], "", f"*Sources : {sources}*",
                   f"*Durée : {r['duree_totale_s']} s*", ""]
    sortie = base_vectorielle.RACINE / "docs" / "test_rag.md"
    sortie.write_text("\n".join(lignes), encoding="utf-8")
    print(f"\nRapport enregistré dans : {sortie}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        tester()
    else:
        q = " ".join(sys.argv[1:]) or "Quel pays est le premier producteur mondial de café ?"
        afficher(repondre(q))
