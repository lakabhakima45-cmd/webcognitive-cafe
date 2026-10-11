"""
pipeline_vectorisation.py
Étape 3 du projet WebCognitive Engine : chunking et vectorisation locale.

  1. lit les documents nettoyés de data/processed/ (résultat de l'étape 2)
  2. découpe chaque texte en morceaux avec chevauchement      -> chunking.py
  3. transforme chaque morceau en vecteur avec un modèle
     d'embedding open-source exécuté en local (sentence-transformers)
  4. enregistre les vecteurs et les morceaux dans data/vectors/

Lancement (depuis le dossier du projet) :
    python src/pipeline_vectorisation.py

Au premier lancement, le modèle est téléchargé depuis Hugging Face (une seule fois).
Ensuite, tout fonctionne en local, sans connexion.
"""

import json
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from chunking import decouper

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_ENTREE = RACINE / "data" / "processed"
DOSSIER_SORTIE = RACINE / "data" / "vectors"

# --- Paramètres (choisis après les tests de test_chunking.py) ---
TAILLE_CHUNK = 500        # nombre de caractères maximum par morceau (environ)
CHEVAUCHEMENT = 100       # caractères repris du morceau précédent
# Modèle multilingue : le corpus contient du français ET de l'anglais.
# Il produit des vecteurs de 384 dimensions, comme all-MiniLM-L6-v2,
# mais il comprend aussi le français (all-MiniLM-L6-v2 est entraîné surtout sur l'anglais).
MODELE = "paraphrase-multilingual-MiniLM-L12-v2"


def charger_documents():
    """Charge les documents nettoyés produits par l'étape 2."""
    fichiers = sorted(DOSSIER_ENTREE.glob("doc_*.json"))
    return [json.loads(f.read_text(encoding="utf-8")) for f in fichiers]


def creer_chunks(documents, taille=TAILLE_CHUNK, chevauchement=CHEVAUCHEMENT):
    """Découpe tous les documents et garde, pour chaque morceau, la trace de sa source."""
    chunks = []
    for doc in documents:
        # PDF : on découpe page par page pour connaître le numéro de page de chaque morceau
        sections = ([(p["page"], p["texte"]) for p in doc["pages"]] if doc.get("pages")
                    else [(None, doc["texte"])])
        position = 0
        for page, texte_section in sections:
            for texte in decouper(texte_section, taille, chevauchement):
                chunks.append({
                    "chunk_id": f"{doc['id']}_c{position:04d}",
                    "doc_id": doc["id"],
                    "fichier": doc["fichier"],
                    "titre": doc["titre"],
                    "format": doc["format"],
                    "langue": doc["langue"],
                    "page": page,
                    "position": position,
                    "nb_caracteres": len(texte),
                    "texte": texte,
                })
                position += 1
    return chunks


def vectoriser(textes, modele):
    """Transforme une liste de textes en une matrice de vecteurs (une ligne par texte).
    Les vecteurs sont normalisés : la similarité cosinus devient un simple produit scalaire."""
    return modele.encode(
        textes,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype(np.float32)


def rechercher(question, modele, vecteurs, chunks, k=3):
    """Petite démonstration : trouve les morceaux les plus proches d'une question."""
    v = vectoriser([question], modele)[0]
    scores = vecteurs @ v                       # similarité cosinus avec tous les morceaux
    meilleurs = np.argsort(-scores)[:k]
    return [(float(scores[i]), chunks[i]) for i in meilleurs]


def main():
    debut = time.time()
    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

    # 1. Documents nettoyés
    documents = charger_documents()
    if not documents:
        print("Aucun document dans data/processed : lance d'abord src/pipeline_ingestion.py")
        return
    print(f"{len(documents)} documents chargés")

    # 2. Chunking
    chunks = creer_chunks(documents)
    longueurs = [c["nb_caracteres"] for c in chunks]
    print(f"{len(chunks)} morceaux créés (taille {TAILLE_CHUNK}, chevauchement {CHEVAUCHEMENT})")
    print(f"  longueur moyenne : {np.mean(longueurs):.0f} caractères "
          f"(min {min(longueurs)}, max {max(longueurs)})")

    # 3. Vectorisation locale
    print(f"\nChargement du modèle {MODELE}...")
    modele = SentenceTransformer(MODELE)
    print("Vectorisation des morceaux (peut prendre quelques minutes)...")
    vecteurs = vectoriser([c["texte"] for c in chunks], modele)
    print(f"Matrice de vecteurs : {vecteurs.shape[0]} morceaux x {vecteurs.shape[1]} dimensions")

    # 4. Enregistrement
    np.save(DOSSIER_SORTIE / "embeddings.npy", vecteurs)
    (DOSSIER_SORTIE / "chunks.json").write_text(
        json.dumps(chunks, ensure_ascii=False, indent=1), encoding="utf-8")
    infos = {
        "modele": MODELE,
        "dimensions": int(vecteurs.shape[1]),
        "nb_chunks": len(chunks),
        "nb_documents": len(documents),
        "taille_chunk": TAILLE_CHUNK,
        "chevauchement": CHEVAUCHEMENT,
        "chunks_par_format": dict(Counter(c["format"] for c in chunks)),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "duree_secondes": round(time.time() - debut, 1),
    }
    (DOSSIER_SORTIE / "infos.json").write_text(
        json.dumps(infos, ensure_ascii=False, indent=2), encoding="utf-8")

    # Démonstration 1 : une phrase devient une liste de nombres
    phrase = "Le Brésil est le premier producteur mondial de café."
    v = vectoriser([phrase], modele)[0]
    print(f"\nExemple : « {phrase} »")
    print(f"  -> vecteur de {len(v)} nombres : [{', '.join(f'{x:.3f}' for x in v[:5])}, ...]")

    # Démonstration 2 : recherche par le sens
    question = "Quel pays produit le plus de café ?"
    print(f"\nTest de recherche : « {question} »")
    for score, c in rechercher(question, modele, vecteurs, chunks):
        print(f"  {score:.2f} | {c['fichier']} | {c['texte'][:110]}...")

    print(f"\nRésultats enregistrés dans : {DOSSIER_SORTIE}")
    print(f"Durée totale : {time.time() - debut:.0f} s")


if __name__ == "__main__":
    main()
