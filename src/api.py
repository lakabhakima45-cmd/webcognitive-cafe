"""
api.py
Étape 4 : API REST (FastAPI) pour administrer l'indexation du corpus.

Routes :
  GET  /         -> état de l'API
  POST /index    -> lance tout le pipeline : (extraction) -> découpage -> vectorisation
                    -> enregistrement par lots dans ChromaDB, puis renvoie un rapport JSON
  GET  /stats    -> contenu de la base vectorielle
  GET  /search   -> recherche sémantique simple (testée ici, développée à l'étape 5)

Lancement (depuis le dossier du projet) :
    python -m uvicorn api:app --app-dir src --reload
Documentation interactive (Swagger) : http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query

import base_vectorielle
import pipeline_ingestion

app = FastAPI(
    title="WebCognitive Engine – Corpus café",
    description="API d'indexation et de recherche sémantique sur un corpus de 30 documents sur le café.",
    version="0.4.0",
)


@app.get("/")
def accueil():
    """Vérifie que l'API fonctionne."""
    return {
        "application": "WebCognitive Engine",
        "corpus": "Le café, de la plante à la tasse",
        "statut": "en ligne",
        "documentation": "/docs",
    }


@app.post("/index")
def indexer(
    reextraire: bool = Query(False, description="Relire et nettoyer d'abord les fichiers bruts (étape 2)"),
    reinitialiser: bool = Query(False, description="Vider la base et tout réindexer"),
):
    """Indexe tout le corpus dans la base vectorielle et renvoie un rapport.
    Seuls les nouveaux morceaux sont vectorisés, sauf si reinitialiser=true."""
    try:
        if reextraire:
            pipeline_ingestion.main()
        rapport = base_vectorielle.indexer(reinitialiser=reinitialiser, afficher=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    rapport["reextraction"] = reextraire
    return rapport


@app.get("/stats")
def stats():
    """Nombre de morceaux et de documents dans la base, par format et par langue."""
    return base_vectorielle.statistiques()


@app.get("/search")
def search(
    q: str = Query(..., min_length=3, description="Question en langage naturel"),
    k: int = Query(5, ge=1, le=20, description="Nombre de passages à renvoyer"),
    format: str | None = Query(None, description="Filtrer par format : pdf, html, docx ou txt"),
    langue: str | None = Query(None, description="Filtrer par langue : fr ou en"),
):
    """Renvoie les passages les plus proches de la question, avec leur source."""
    resultats = base_vectorielle.rechercher(q, k=k, format=format, langue=langue)
    return {"question": q, "nb_resultats": len(resultats), "resultats": resultats}
