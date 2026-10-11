"""
test_chunking.py
Phase de test et d'optimisation de l'étape 3 : quelle taille de morceaux choisir ?

On compare plusieurs tailles de chunks avec les 10 questions de validation
(docs/questions_validation.md). Pour chaque taille, on vérifie si la réponse
attendue se trouve dans les morceaux les plus proches de la question.

  - morceaux trop petits  -> manquent de contexte, la réponse est coupée
  - morceaux trop grands  -> contiennent du « bruit », le sens est dilué

Lancement (depuis le dossier du projet) :
    python src/test_chunking.py
Le résultat est enregistré dans docs/test_chunking.md
"""

import time
from datetime import datetime

import numpy as np
from sentence_transformers import SentenceTransformer

from pipeline_vectorisation import MODELE, RACINE, charger_documents, creer_chunks, vectoriser

# Tailles testées : (taille du morceau, chevauchement) en caractères
CONFIGURATIONS = [(250, 50), (500, 100), (1000, 200)]
K = 5  # nombre de morceaux regardés pour chaque question

# Les 10 questions de validation, le document où se trouve la réponse,
# et des mots-clés qui prouvent que le morceau contient la réponse
QUESTIONS = [
    ("D'où le caféier est-il originaire ?", "cafeier", ["afrique", "asie"]),
    ("Quelles sont les deux espèces de café les plus cultivées ?", "cafeier", ["canephora"]),
    ("Quelle part de la production mondiale représente l'arabica ?", "rapport-senat", ["trois-quarts", "trois quarts"]),
    ("En quelle année l'Organisation internationale du café a-t-elle été créée ?", "rapport-assemblee", ["1963"]),
    ("Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ?", "filiere-cafe-en-afrique", ["27,2"]),
    ("Quelles substances la torréfaction forme-t-elle dans le café ?", "cafe-climat-et-sante", ["acrylamide"]),
    ("Quelle part du prix d'un paquet de café revient aux petits producteurs ?", "le-cafe-grand-marche-mondial", ["10%", "10 %"]),
    ("De quelle région le café est-il originaire ?", "histoire-cafe", ["kaffa"]),
    ("Qu'est-ce que le kopi luwak ?", "kopi-luwak", ["civette"]),
    ("Quelle est la différence entre le café vert et le café torréfié ?", "torrefaction", ["grain vert"]),
]


def evaluer(chunks, vecteurs, vecteurs_questions):
    """Pour chaque question, regarde les K morceaux les plus proches."""
    resultats = []
    for (question, doc_attendu, mots_cles), vq in zip(QUESTIONS, vecteurs_questions):
        scores = vecteurs @ vq
        top = np.argsort(-scores)[:K]
        rang = None   # position du premier morceau contenant la réponse
        for r, i in enumerate(top, start=1):
            texte = chunks[i]["texte"].lower()
            if any(m in texte for m in mots_cles):
                rang = r
                break
        bon_doc = any(doc_attendu in chunks[i]["fichier"] for i in top)
        resultats.append({
            "question": question,
            "rang": rang,
            "bon_document": bon_doc,
            "score": float(scores[top[0]]),
            "source": chunks[top[0]]["fichier"],
        })
    return resultats


def main():
    debut = time.time()
    documents = charger_documents()
    print(f"Chargement du modèle {MODELE}...")
    modele = SentenceTransformer(MODELE)
    vecteurs_questions = vectoriser([q for q, _, _ in QUESTIONS], modele)

    bilan = []
    details = {}
    for taille, chevauchement in CONFIGURATIONS:
        print(f"\n=== Taille {taille} / chevauchement {chevauchement} ===")
        chunks = creer_chunks(documents, taille, chevauchement)
        t0 = time.time()
        vecteurs = vectoriser([c["texte"] for c in chunks], modele)
        duree = time.time() - t0
        res = evaluer(chunks, vecteurs, vecteurs_questions)
        top1 = sum(r["rang"] == 1 for r in res)
        topk = sum(r["rang"] is not None for r in res)
        doc_ok = sum(r["bon_document"] for r in res)
        bilan.append({
            "config": f"{taille} / {chevauchement}",
            "nb_chunks": len(chunks),
            "longueur_moy": np.mean([c["nb_caracteres"] for c in chunks]),
            "top1": top1, "topk": topk, "doc_ok": doc_ok,
            "score_moy": np.mean([r["score"] for r in res]),
            "duree": duree,
        })
        details[f"{taille} / {chevauchement}"] = res
        print(f"{len(chunks)} morceaux | réponse en 1re position : {top1}/10 | "
              f"dans le top {K} : {topk}/10 | bon document : {doc_ok}/10")

    # Choix : le plus de réponses trouvées dans le top K, puis en 1re position
    meilleure = max(bilan, key=lambda b: (b["topk"], b["top1"], b["doc_ok"]))

    # Rapport Markdown
    lignes = [
        "# Test de la taille des morceaux (chunking)",
        "",
        f"*Date : {datetime.now():%Y-%m-%d %H:%M} — modèle : `{MODELE}` — {len(documents)} documents*",
        "",
        "## Méthode",
        "",
        "Le corpus est découpé avec plusieurs tailles de morceaux. Chaque morceau est transformé en vecteur, "
        "puis on pose les 10 questions de validation. Pour chaque question, on regarde les "
        f"{K} morceaux les plus proches (similarité cosinus) et on vérifie s'ils contiennent la réponse attendue.",
        "",
        "## Résultats",
        "",
        f"| Taille / chevauchement | Nb de morceaux | Longueur moyenne | Réponse en 1re position | Réponse dans le top {K} | Bon document dans le top {K} | Similarité moyenne | Durée |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for b in bilan:
        lignes.append(
            f"| {b['config']} | {b['nb_chunks']} | {b['longueur_moy']:.0f} car. | {b['top1']}/10 | "
            f"{b['topk']}/10 | {b['doc_ok']}/10 | {b['score_moy']:.2f} | {b['duree']:.0f} s |")
    lignes += ["", f"**Meilleure configuration : {meilleure['config']} caractères.**", "",
               "## Détail par question", ""]
    for config, res in details.items():
        lignes += [f"### {config}", "", "| Question | Rang de la réponse | Document du 1er résultat |", "|---|---|---|"]
        for r in res:
            rang = r["rang"] if r["rang"] else "non trouvée"
            lignes.append(f"| {r['question']} | {rang} | {r['source']} |")
        lignes.append("")

    sortie = RACINE / "docs" / "test_chunking.md"
    sortie.write_text("\n".join(lignes), encoding="utf-8")
    print(f"\nMeilleure configuration : {meilleure['config']}")
    print(f"Rapport enregistré dans : {sortie}")
    print(f"Durée totale : {time.time() - debut:.0f} s")


if __name__ == "__main__":
    main()
