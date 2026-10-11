"""
base_vectorielle.py
Étape 4 : stockage durable des vecteurs dans une base de données vectorielle locale (ChromaDB).

Pour chaque morceau de texte, la base enregistre ensemble :
  - le vecteur (384 nombres)
  - le texte original du morceau
  - ses métadonnées : fichier source, titre, format, langue, numéro de page, position
  - un identifiant unique (ex. doc_008_c0012)
Cela permet de toujours savoir d'où vient un passage (traçabilité).

La base est enregistrée sur le disque dans data/chroma/ : elle reste disponible
après l'arrêt du programme, il n'est pas nécessaire de tout recalculer.

Utilisation en ligne de commande (depuis le dossier du projet) :
    python src/base_vectorielle.py              -> indexe les nouveaux morceaux
    python src/base_vectorielle.py --reset      -> vide la base et réindexe tout
"""

import sys
import time
from collections import Counter
from datetime import datetime

import chromadb
from sentence_transformers import SentenceTransformer

from pipeline_vectorisation import (CHEVAUCHEMENT, MODELE, RACINE, TAILLE_CHUNK,
                                    charger_documents, creer_chunks, prefixes, vectoriser)

DOSSIER_BASE = RACINE / "data" / "chroma"
NOM_COLLECTION = "corpus_cafe"
TAILLE_LOT = 500   # nombre de morceaux vectorisés et enregistrés à la fois

_modele = None


def charger_modele():
    """Charge le modèle d'embedding une seule fois (il est long à charger)."""
    global _modele
    if _modele is None:
        _modele = SentenceTransformer(MODELE)
    return _modele


def ouvrir_collection(reinitialiser=False):
    """Ouvre (ou crée) la collection ChromaDB enregistrée sur le disque."""
    client = chromadb.PersistentClient(path=str(DOSSIER_BASE))
    if reinitialiser:
        try:
            client.delete_collection(NOM_COLLECTION)
        except Exception:
            pass  # la collection n'existait pas encore
    return client.get_or_create_collection(
        name=NOM_COLLECTION,
        metadata={"hnsw:space": "cosine", "modele": MODELE},  # distance cosinus
    )


def metadonnees(chunk):
    """Métadonnées enregistrées avec chaque morceau (ChromaDB n'accepte pas les valeurs vides)."""
    meta = {
        "doc_id": chunk["doc_id"],
        "fichier": chunk["fichier"],
        "titre": chunk["titre"],
        "format": chunk["format"],
        "langue": chunk["langue"],
        "position": chunk["position"],
        "nb_caracteres": chunk["nb_caracteres"],
    }
    if chunk.get("page") is not None:
        meta["page"] = chunk["page"]
    return meta


def indexer(reinitialiser=False, afficher=True):
    """Pipeline complet d'indexation :
    documents nettoyés -> découpage -> vectorisation -> enregistrement par lots.
    Seuls les morceaux absents de la base sont calculés (sauf si reinitialiser=True).
    Renvoie un rapport sous forme de dictionnaire (utilisé par l'API)."""
    debut = time.time()
    documents = charger_documents()
    if not documents:
        raise RuntimeError("Aucun document dans data/processed : lancer d'abord pipeline_ingestion.py")

    chunks = creer_chunks(documents, TAILLE_CHUNK, CHEVAUCHEMENT)
    collection = ouvrir_collection(reinitialiser)

    deja_presents = set(collection.get(include=[])["ids"]) if collection.count() else set()
    nouveaux = [c for c in chunks if c["chunk_id"] not in deja_presents]

    if afficher:
        print(f"{len(documents)} documents | {len(chunks)} morceaux | "
              f"{len(deja_presents)} déjà dans la base | {len(nouveaux)} à indexer")

    if nouveaux:
        modele = charger_modele()
        prefixe_passage = prefixes(MODELE)[1]
        for i in range(0, len(nouveaux), TAILLE_LOT):
            lot = nouveaux[i:i + TAILLE_LOT]
            vecteurs = vectoriser([c["texte"] for c in lot], modele, prefixe_passage)
            collection.add(
                ids=[c["chunk_id"] for c in lot],
                embeddings=vecteurs.tolist(),
                documents=[c["texte"] for c in lot],
                metadatas=[metadonnees(c) for c in lot],
            )
            if afficher:
                print(f"  lot {i // TAILLE_LOT + 1} / {-(-len(nouveaux) // TAILLE_LOT)} enregistré "
                      f"({min(i + TAILLE_LOT, len(nouveaux))}/{len(nouveaux)})")

    rapport = {
        "statut": "ok",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modele": MODELE,
        "taille_chunk": TAILLE_CHUNK,
        "chevauchement": CHEVAUCHEMENT,
        "documents": len(documents),
        "morceaux_total": len(chunks),
        "morceaux_ajoutes": len(nouveaux),
        "morceaux_dans_la_base": collection.count(),
        "morceaux_par_format": dict(Counter(c["format"] for c in chunks)),
        "duree_secondes": round(time.time() - debut, 1),
    }
    return rapport


def rechercher(question, k=5, max_par_document=2, format=None, langue=None):
    """Recherche les k morceaux les plus proches d'une question (similarité cosinus).
    max_par_document limite la place d'un seul document dans les résultats
    (évite que le gros livre de 1922 occupe toutes les places)."""
    modele = charger_modele()
    collection = ouvrir_collection()
    vq = vectoriser([question], modele, prefixes(MODELE)[0])[0]

    filtres = {cle: val for cle, val in (("format", format), ("langue", langue)) if val}
    if len(filtres) > 1:
        filtre = {"$and": [{cle: val} for cle, val in filtres.items()]}
    else:
        filtre = filtres or None

    brut = collection.query(
        query_embeddings=[vq.tolist()],
        n_results=min(k * 6, max(collection.count(), 1)),  # on en prend plus, puis on filtre
        where=filtre,
        include=["documents", "metadatas", "distances"],
    )

    resultats, par_doc = [], Counter()
    for id_, texte, meta, distance in zip(brut["ids"][0], brut["documents"][0],
                                          brut["metadatas"][0], brut["distances"][0]):
        if max_par_document and par_doc[meta["doc_id"]] >= max_par_document:
            continue
        par_doc[meta["doc_id"]] += 1
        resultats.append({
            "chunk_id": id_,
            "score": round(1 - distance, 4),   # distance cosinus -> similarité
            "fichier": meta["fichier"],
            "titre": meta["titre"],
            "format": meta["format"],
            "page": meta.get("page"),
            "texte": texte,
        })
        if len(resultats) == k:
            break
    return resultats


def statistiques():
    """Contenu actuel de la base."""
    collection = ouvrir_collection()
    total = collection.count()
    metas = collection.get(include=["metadatas"])["metadatas"] if total else []
    return {
        "collection": NOM_COLLECTION,
        "modele": MODELE,
        "morceaux": total,
        "documents": len({m["doc_id"] for m in metas}),
        "morceaux_par_format": dict(Counter(m["format"] for m in metas)),
        "morceaux_par_langue": dict(Counter(m["langue"] for m in metas)),
    }


if __name__ == "__main__":
    rapport = indexer(reinitialiser="--reset" in sys.argv)
    print("\n----- Rapport d'indexation -----")
    for cle, valeur in rapport.items():
        print(f"  {cle} : {valeur}")

    question = "Quel pays est le premier producteur mondial de café ?"
    print(f"\nTest de recherche : « {question} »")
    for r in rechercher(question, k=3):
        page = f" p.{r['page']}" if r["page"] else ""
        print(f"  {r['score']:.2f} | {r['fichier']}{page} | {r['texte'][:100]}...")
