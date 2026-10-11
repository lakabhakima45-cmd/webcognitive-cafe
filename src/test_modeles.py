"""
test_modeles.py
Suite de la phase d'optimisation de l'étape 3 : comparaison de modèles d'embedding.

Le premier test (test_chunking.py) a montré que :
  - les petits morceaux (250 caractères) donnent les meilleurs résultats ;
  - mais les scores restent faibles, car le modèle « paraphrase » est fait pour comparer
    deux phrases qui se ressemblent, pas pour relier une question à sa réponse ;
  - le gros livre anglais de 1922 (2/3 des morceaux) occupe souvent les premières places.

Ce test essaie donc :
  1. un modèle conçu pour la recherche question -> passage : multilingual-e5-small
  2. une règle de diversité : au maximum 2 morceaux par document dans le top 5

Lancement (depuis le dossier du projet) :
    python src/test_modeles.py
Le résultat est enregistré dans docs/test_modeles.md
"""

import time
from datetime import datetime

import numpy as np
from sentence_transformers import SentenceTransformer

from pipeline_vectorisation import RACINE, charger_documents, creer_chunks, prefixes, vectoriser
from test_chunking import K, QUESTIONS

MODELES = ["intfloat/multilingual-e5-small"]
CONFIGURATIONS = [(250, 50), (500, 100)]
MAX_PAR_DOCUMENT = 2


def top_k(scores, chunks, k, max_par_doc=None):
    """Indices des k morceaux les plus proches, avec éventuellement
    une limite de morceaux par document (diversité des sources)."""
    ordre = np.argsort(-scores)
    if not max_par_doc:
        return list(ordre[:k])
    choisis, compte = [], {}
    for i in ordre:
        doc = chunks[i]["doc_id"]
        if compte.get(doc, 0) < max_par_doc:
            choisis.append(i)
            compte[doc] = compte.get(doc, 0) + 1
        if len(choisis) == k:
            break
    return choisis


def evaluer(chunks, vecteurs, vecteurs_questions, max_par_doc=None):
    """Compte les questions dont la réponse est en 1re position / dans le top K."""
    top1 = topk = doc_ok = 0
    details = []
    for (question, doc_attendu, mots_cles), vq in zip(QUESTIONS, vecteurs_questions):
        scores = vecteurs @ vq
        top = top_k(scores, chunks, K, max_par_doc)
        rang = next((r for r, i in enumerate(top, 1)
                     if any(m in chunks[i]["texte"].lower() for m in mots_cles)), None)
        top1 += rang == 1
        topk += rang is not None
        doc_ok += any(doc_attendu in chunks[i]["fichier"] for i in top)
        details.append((question, rang, chunks[top[0]]["fichier"]))
    return top1, topk, doc_ok, details


def main():
    debut = time.time()
    documents = charger_documents()
    lignes_resultats = []
    tous_details = {}

    for nom in MODELES:
        print(f"\nChargement du modèle {nom}...")
        modele = SentenceTransformer(nom)
        p_question, p_passage = prefixes(nom)
        vq = vectoriser([q for q, _, _ in QUESTIONS], modele, p_question)

        for taille, chevauchement in CONFIGURATIONS:
            print(f"\n=== {nom} | taille {taille} / chevauchement {chevauchement} ===")
            chunks = creer_chunks(documents, taille, chevauchement)
            vecteurs = vectoriser([c["texte"] for c in chunks], modele, p_passage)
            for regle, max_doc in (("sans limite", None), (f"max {MAX_PAR_DOCUMENT} par document", MAX_PAR_DOCUMENT)):
                top1, topk, doc_ok, details = evaluer(chunks, vecteurs, vq, max_doc)
                config = f"{nom.split('/')[-1]} | {taille}/{chevauchement} | {regle}"
                lignes_resultats.append((config, len(chunks), top1, topk, doc_ok))
                tous_details[config] = details
                print(f"  {regle:28} -> 1re position : {top1}/10 | top {K} : {topk}/10 | bon document : {doc_ok}/10")

    # Rapport Markdown
    lignes = [
        "# Comparaison de modèles d'embedding",
        "",
        f"*Date : {datetime.now():%Y-%m-%d %H:%M} — {len(documents)} documents — 10 questions de validation*",
        "",
        "Rappel du premier test (`paraphrase-multilingual-MiniLM-L12-v2`) : voir `test_chunking.md`.",
        "",
        f"| Configuration | Nb de morceaux | Réponse en 1re position | Réponse dans le top {K} | Bon document dans le top {K} |",
        "|---|---|---|---|---|",
    ]
    for config, n, top1, topk, doc_ok in lignes_resultats:
        lignes.append(f"| {config} | {n} | {top1}/10 | {topk}/10 | {doc_ok}/10 |")
    lignes += ["", "## Détail par question", ""]
    for config, details in tous_details.items():
        lignes += [f"### {config}", "", "| Question | Rang de la réponse | Document du 1er résultat |", "|---|---|---|"]
        lignes += [f"| {q} | {r if r else 'non trouvée'} | {f} |" for q, r, f in details]
        lignes.append("")

    sortie = RACINE / "docs" / "test_modeles.md"
    sortie.write_text("\n".join(lignes), encoding="utf-8")
    print(f"\nRapport enregistré dans : {sortie}")
    print(f"Durée totale : {time.time() - debut:.0f} s")


if __name__ == "__main__":
    main()
