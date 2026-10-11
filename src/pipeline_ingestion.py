"""
pipeline_ingestion.py
Étape 2 du projet WebCognitive Engine : pipeline de parsing et de prétraitement.

Pour chaque document de data/ (pdf, html, docx, txt) :
  1. extraction du texte brut           -> extraction.py
  2. nettoyage et normalisation (regex) -> nettoyage.py
  3. export en JSON avec ses métadonnées -> data/processed/

Lancement (depuis le dossier du projet) :
    python src/pipeline_ingestion.py
"""

import json
import time
from datetime import datetime
from pathlib import Path

from extraction import extraire
from nettoyage import detecter_langue, nettoyer

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DATA = RACINE / "data"
DOSSIER_SORTIE = DOSSIER_DATA / "processed"
FORMATS = ["pdf", "html", "docx", "txt"]

# En dessous de ce nombre de caractères, le document est signalé comme suspect
SEUIL_TEXTE_COURT = 500


def lister_documents():
    """Renvoie la liste des fichiers du corpus, rangés par format."""
    documents = []
    for fmt in FORMATS:
        dossier = DOSSIER_DATA / fmt
        if dossier.exists():
            documents += sorted(p for p in dossier.iterdir() if p.is_file())
    return documents


def traiter_document(chemin, numero):
    """Extrait, nettoie et décrit un document. Renvoie un dictionnaire."""
    brut = extraire(chemin)
    pages = None
    if brut.get("pages"):
        # PDF : chaque page est nettoyée à part pour garder son numéro
        pages = [{"page": i, "texte": nettoyer(t, page_web=False)}
                 for i, t in enumerate(brut["pages"], start=1)]
        texte = "\n\n".join(p["texte"] for p in pages if p["texte"])
    else:
        texte = nettoyer(brut["texte"])
    infos_fichier = chemin.stat()

    document = {
        "id": f"doc_{numero:03d}",
        "fichier": chemin.name,
        "chemin": chemin.relative_to(RACINE).as_posix(),
        "format": chemin.suffix.lower().lstrip("."),
        "titre": brut["titre"] or chemin.stem.replace("-", " ").replace("_", " ").capitalize(),
        "langue": detecter_langue(texte),
        "date_fichier": datetime.fromtimestamp(infos_fichier.st_mtime).strftime("%Y-%m-%d"),
        "date_extraction": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "nb_pages": brut["nb_pages"],
        "taille_brute": len(brut["texte"]),
        "nb_caracteres": len(texte),
        "nb_mots": len(texte.split()),
        "texte": texte,
    }
    if pages:
        document["pages"] = pages
    return document


def main():
    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    documents = lister_documents()
    print(f"{len(documents)} documents trouvés dans {DOSSIER_DATA}\n")

    index, erreurs, alertes = [], [], []
    debut = time.time()

    for numero, chemin in enumerate(documents, start=1):
        try:
            doc = traiter_document(chemin, numero)
        except Exception as e:  # un fichier abîmé ne doit pas bloquer tout le corpus
            erreurs.append((chemin.name, str(e)))
            print(f"  [ERREUR] {chemin.name} : {e}")
            continue

        sortie = DOSSIER_SORTIE / f"{doc['id']}_{chemin.stem}.json"
        sortie.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

        # l'index garde les métadonnées sans le texte complet
        index.append({k: v for k, v in doc.items() if k not in ("texte", "pages")} | {"sortie": sortie.name})

        etat = "OK"
        if doc["nb_caracteres"] < SEUIL_TEXTE_COURT:
            etat = "COURT"
            alertes.append(chemin.name)
        print(f"  [{etat:5}] {doc['format']:4} | {doc['nb_mots']:>7} mots | {doc['langue']} | {chemin.name}")

    (DOSSIER_SORTIE / "corpus_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    # Bilan
    print("\n----- Bilan -----")
    print(f"Documents traités : {len(index)} / {len(documents)}")
    for fmt in FORMATS:
        n = sum(d["format"] == fmt for d in index)
        print(f"  {fmt:4} : {n}")
    print(f"Mots au total     : {sum(d['nb_mots'] for d in index):,}".replace(",", " "))
    reduction = 1 - sum(d["nb_caracteres"] for d in index) / max(1, sum(d["taille_brute"] for d in index))
    print(f"Texte retiré au nettoyage : {reduction:.0%}")
    print(f"Durée : {time.time() - debut:.1f} s")
    if alertes:
        print(f"\nTextes très courts (à vérifier) : {', '.join(alertes)}")
    if erreurs:
        print(f"\nFichiers en erreur : {', '.join(n for n, _ in erreurs)}")
    print(f"\nRésultats enregistrés dans : {DOSSIER_SORTIE}")


if __name__ == "__main__":
    main()
