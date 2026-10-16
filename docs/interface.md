# Étape 6 — Interface web (front-end)

**Outil :** Streamlit (bibliothèque Python libre). Fichier : `src/interface.py`.

## Comment ça marche

```
Navigateur (Streamlit, port 8501)  --requête HTTP-->  API FastAPI (port 8000)  -->  ChromaDB + Ollama
                                   <----- JSON -----
```

L'interface ne fait aucun calcul : elle appelle les routes de l'API et affiche les résultats.

| Partie de l'écran | Route de l'API appelée |
|---|---|
| Voyant « API connectée » | `GET /` |
| Nombre de documents et de morceaux | `GET /stats` |
| Mode **Assistant (IA)** | `POST /chat` |
| Mode **Recherche rapide** (sans IA) | `GET /search` |

## Ce que voit l'utilisateur

- Une zone de discussion : il tape sa question en bas, la réponse s'affiche comme dans un chat. L'historique reste affiché.
- Sous chaque réponse, un bloc **Sources** : nom du fichier, **numéro de page** pour les PDF, score de similarité et extrait du passage utilisé. On peut donc vérifier chaque réponse.
- Dans la barre de gauche : l'état de l'API, des questions d'exemple, le choix du nombre de passages (k) et un bouton pour effacer la conversation.
- Si Ollama est éteint, un message clair s'affiche à la place d'une erreur.

## Lancement (2 terminaux)

```powershell
# Terminal 1 : l'API
.venv\Scripts\python.exe -m uvicorn api:app --app-dir src

# Terminal 2 : l'interface (s'ouvre sur http://localhost:8501)
.venv\Scripts\python.exe -m streamlit run src\interface.py
```
