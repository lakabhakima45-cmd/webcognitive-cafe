# WebCognitive Engine – Corpus « Le café »

Projet individuel réalisé dans le cadre du cours **Techniques Informatiques et Web** (Master Technologies de l'Hypermédia, Université Paris 8).

**Auteure :** Hakima Lakab

## Présentation

Application qui transforme un corpus de documents sur le café (PDF, HTML, Word, TXT) en un **moteur de recherche sémantique** et un **assistant conversationnel (RAG)**. L'assistant répond aux questions en langage naturel en s'appuyant uniquement sur les documents du corpus, et il **cite ses sources** (fichier, page, extrait).

Tout fonctionne **en local**, avec des outils libres, sans service cloud payant.

## Thème et corpus

**Le café, de la plante à la tasse** : botanique, histoire, production et commerce, transformation, consommation et environnement.

| Format | Documents | Morceaux indexés |
|---|---|---|
| HTML | 10 | 1 741 |
| PDF | 8 | 570 |
| DOCX | 5 | 172 |
| TXT | 7 | 9 022 |
| **Total** | **30** | **11 505** |

Environ 650 000 mots, principalement en français, avec deux livres anciens en anglais (Projet Gutenberg).

## Architecture

```
Documents bruts (data/pdf, html, docx, txt)
   │  extraction.py + nettoyage.py        (étape 2)
   ▼
Textes nettoyés en JSON (data/processed)
   │  chunking.py : morceaux de 500 caractères, chevauchement de 100   (étape 3)
   │  modèle d'embedding multilingual-e5-small (384 dimensions, en local)
   ▼
Base vectorielle ChromaDB (data/chroma)   (étape 4)
   │  recherche par similarité cosinus (Top-K)
   ▼
Pipeline RAG : passages + prompt → Llama 3.2 via Ollama   (étape 5)
   ▼
API REST FastAPI : /index, /stats, /search, /chat
```

## Outils utilisés

| Besoin | Outil |
|---|---|
| Lecture des documents | pdfplumber, BeautifulSoup, python-docx |
| Nettoyage | expressions régulières (module `re`) |
| Embeddings | sentence-transformers, modèle `intfloat/multilingual-e5-small` |
| Base vectorielle | ChromaDB |
| API | FastAPI, Uvicorn |
| Modèle de langage local | Ollama, modèle `llama3.2:3b` |
| Versionnement | Git |

## Organisation du projet

```
cafe/
├── data/
│   ├── pdf/ html/ docx/ txt/   documents du corpus
│   └── processed/              textes nettoyés (JSON)
├── docs/
│   ├── cahier_des_charges.md
│   ├── questions_validation.md
│   ├── test_chunking.md        test des tailles de morceaux
│   ├── test_modeles.md         comparaison des modèles d'embedding
│   └── test_rag.md             test de l'assistant sur les questions de validation
├── src/
│   ├── extraction.py           lecture des 4 formats
│   ├── nettoyage.py            nettoyage et normalisation (regex)
│   ├── pipeline_ingestion.py   étape 2 : traitement de tout le corpus
│   ├── chunking.py             découpage avec chevauchement
│   ├── pipeline_vectorisation.py  étape 3 : vectorisation
│   ├── test_chunking.py        tests de taille de morceaux
│   ├── test_modeles.py         comparaison de modèles
│   ├── base_vectorielle.py     étape 4 : indexation et recherche dans ChromaDB
│   ├── rag.py                  étape 5 : assistant RAG
│   └── api.py                  API REST FastAPI
├── requirements.txt
└── README.md
```

## Installation et lancement

Pré-requis : Python 3.12 et [Ollama](https://ollama.com).

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
ollama pull llama3.2:3b
```

1. Lire et nettoyer les documents :
   ```
   .venv\Scripts\python.exe src\pipeline_ingestion.py
   ```
2. Remplir la base vectorielle (environ 8 minutes, une seule fois) :
   ```
   .venv\Scripts\python.exe src\base_vectorielle.py
   ```
3. Poser une question en ligne de commande :
   ```
   .venv\Scripts\python.exe src\rag.py "Qu'est-ce que le kopi luwak ?"
   ```
4. Lancer l'API, puis ouvrir http://127.0.0.1:8000/docs :
   ```
   .venv\Scripts\python.exe -m uvicorn api:app --app-dir src
   ```

## Routes de l'API

| Route | Rôle |
|---|---|
| `GET /` | état de l'API |
| `POST /index` | indexe le corpus (lecture, découpage, vectorisation, enregistrement) et renvoie un rapport JSON |
| `GET /stats` | contenu de la base (morceaux par format et par langue) |
| `GET /search?q=...` | les passages les plus proches d'une question, avec leur source |
| `POST /chat` | réponse rédigée par le modèle local à partir des passages, avec les sources |

## Résultats des tests

**Choix du modèle et de la taille des morceaux** (10 questions de validation) :

| Configuration | Réponse dans le top 5 | Bon document trouvé |
|---|---|---|
| paraphrase-multilingual-MiniLM, morceaux de 250 | 4/10 | 6/10 |
| **multilingual-e5-small, morceaux de 500** | **8/10** | **9/10** |

**Assistant RAG :** il répond en citant ses sources, et il refuse de répondre aux questions hors sujet (« Je ne sais pas ») au lieu d'inventer.

**Limite observée :** le modèle Llama 3.2 (3 milliards de paramètres) est léger mais peut parfois mélanger deux informations proches. Les sources affichées permettent de vérifier chaque réponse.

## Avancement

- [x] Étape 1 : cadrage, corpus, questions de validation, initialisation Git
- [x] Étape 2 : pipeline d'extraction et de nettoyage
- [x] Étape 3 : chunking, embeddings et tests d'optimisation
- [x] Étape 4 : base vectorielle ChromaDB et API d'indexation
- [x] Étape 5 : moteur de recherche sémantique et pipeline RAG
- [ ] Étape 6 : interface web
- [ ] Étape 7 : tableau de bord (dataviz)
- [ ] Étape 8 : validation finale et soutenance
