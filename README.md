# WebCognitive Engine – Corpus « Le café »

Projet individuel réalisé dans le cadre du cours **Techniques Informatiques et Web** (Master Technologies de l'Hypermédia, Université Paris 8, enseignant : N. Bouhai).

**Auteure :** Hakima Lakab

## Présentation

Application web qui transforme un corpus de 30 documents sur le café (PDF, HTML, Word, TXT) en :

- un **moteur de recherche sémantique** : on cherche par le sens, pas par mots exacts ;
- un **assistant conversationnel (RAG)** : il répond en langage naturel uniquement à partir des documents, et **cite ses sources** (fichier, page, extrait) ;
- un **tableau de bord (dataviz)** : des graphiques pour avoir une vue d'ensemble du corpus.

Tout fonctionne **en local**, avec des outils libres, sans service cloud payant.

## Thème et corpus

**Le café, de la plante à la tasse** : botanique, histoire, production et commerce, transformation, boissons, santé et environnement.

| Format | Documents | Morceaux indexés |
|---|---|---|
| HTML | 10 | 1 741 |
| PDF | 8 (117 pages) | 570 |
| DOCX | 5 | 172 |
| TXT | 7 | 9 022 |
| **Total** | **30** | **11 505** |

Environ 650 000 mots, principalement en français, avec deux livres anciens en anglais (Projet Gutenberg, W. H. Ukers, 1922). Les sources sont des rapports publics (Sénat, Assemblée nationale, Organisation internationale du café), des articles Wikipédia et des documents de vulgarisation.

## Architecture

```
Documents bruts (data/pdf, html, docx, txt)
   │  extraction.py + nettoyage.py                         (étape 2)
   ▼
Textes nettoyés en JSON (data/processed)
   │  chunking.py : morceaux de 500 caractères, chevauchement de 100   (étape 3)
   │  modèle d'embedding multilingual-e5-small (384 dimensions, en local)
   ▼
Base vectorielle ChromaDB (data/chroma)                   (étape 4)
   │  recherche par similarité cosinus (Top-K)
   ▼
Pipeline RAG : passages + prompt → Llama 3.2 via Ollama   (étape 5)
   ▼
API REST FastAPI : /index /stats /search /chat /analyse    (étapes 4, 5, 7)
   ▼  requêtes HTTP
Interface web Streamlit (étapes 6 et 7)
   ├── 💬 Chat : questions, réponses et sources (fichier + page)
   └── 📊 Analyse du corpus : 7 graphiques Plotly
```

L'interface ne fait aucun calcul : elle appelle l'API et affiche les résultats.

## Outils utilisés

| Besoin | Outil |
|---|---|
| Lecture des documents | pdfplumber, BeautifulSoup, python-docx |
| Nettoyage | expressions régulières (module `re`) |
| Embeddings | sentence-transformers, modèle `intfloat/multilingual-e5-small` |
| Base vectorielle | ChromaDB |
| API | FastAPI, Uvicorn |
| Modèle de langage local | Ollama, modèle `llama3.2:3b` |
| Interface web | Streamlit |
| Graphiques | Plotly, numpy, pandas |
| Versionnement | Git, GitHub |

## Organisation du projet

```
cafe/
├── data/
│   ├── pdf/ html/ docx/ txt/      documents du corpus
│   ├── processed/                 textes nettoyés (JSON)
│   └── chroma/                    base vectorielle (créée à l'installation, non versionnée)
├── docs/
│   ├── cahier_des_charges.md
│   ├── questions_validation.md    questions de l'étape 1
│   ├── test_chunking.md           test des tailles de morceaux
│   ├── test_modeles.md            comparaison des modèles d'embedding
│   ├── test_rag.md                test de l'assistant
│   ├── interface.md               étape 6
│   ├── dataviz.md                 étape 7
│   ├── analyse_corpus.md          indicateurs du corpus
│   └── recette.md                 tests finaux (étape 8)
├── src/
│   ├── extraction.py              lecture des 4 formats
│   ├── nettoyage.py               nettoyage et normalisation (regex)
│   ├── pipeline_ingestion.py      étape 2 : traitement de tout le corpus
│   ├── chunking.py                découpage avec chevauchement
│   ├── pipeline_vectorisation.py  étape 3 : vectorisation
│   ├── test_chunking.py           tests de taille de morceaux
│   ├── test_modeles.py            comparaison de modèles
│   ├── base_vectorielle.py        étape 4 : indexation et recherche dans ChromaDB
│   ├── rag.py                     étape 5 : assistant RAG
│   ├── api.py                     API REST FastAPI
│   ├── interface.py               étapes 6 et 7 : interface web Streamlit
│   ├── analyse.py                 étape 7 : statistiques pour la dataviz
│   └── recette.py                 étape 8 : tests globaux
├── requirements.txt
└── README.md
```

## Installation (Windows, PowerShell)

**Pré-requis :** [Python 3.12](https://www.python.org), [Git](https://git-scm.com) et [Ollama](https://ollama.com).

1. Récupérer le projet :
   ```powershell
   git clone https://github.com/lakabhakima45-cmd/webcognitive-cafe.git
   cd webcognitive-cafe
   ```
2. Créer l'environnement virtuel et installer les bibliothèques :
   ```powershell
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
3. Télécharger le modèle de langage (environ 2 Go, une seule fois) :
   ```powershell
   ollama pull llama3.2:3b
   ```
4. Préparer les données, une seule fois (environ 8 minutes) :
   ```powershell
   .venv\Scripts\python.exe src\pipeline_ingestion.py
   .venv\Scripts\python.exe src\base_vectorielle.py
   ```
   Cela peut aussi se faire par l'API : `POST /index?reextraire=true`.

## Lancement

Ollama doit être ouvert (il démarre en général tout seul avec Windows). Ensuite, il faut **deux terminaux** dans le dossier du projet :

```powershell
# Terminal 1 : l'API (documentation Swagger : http://127.0.0.1:8000/docs)
.venv\Scripts\python.exe -m uvicorn api:app --app-dir src

# Terminal 2 : l'interface web (s'ouvre sur http://localhost:8501)
.venv\Scripts\python.exe -m streamlit run src\interface.py
```

## Utilisation

- **💬 Chat**, mode *Assistant (IA)* : on pose une question, Llama répond en une à deux minutes. Sous la réponse, le bloc **Sources** montre le fichier, le numéro de page pour les PDF, le score de similarité et l'extrait utilisé.
- **💬 Chat**, mode *Recherche rapide* : on obtient tout de suite les passages les plus proches, sans IA.
- **📊 Analyse du corpus** : on voit les formats, la taille des documents et des morceaux, les mots-clés du café, les pays producteurs les plus cités, une carte de chaleur des thèmes par document, les mots fréquents et la carte sémantique des documents.

## Routes de l'API

| Route | Rôle |
|---|---|
| `GET /` | état de l'API |
| `POST /index` | indexe le corpus (lecture, découpage, vectorisation, enregistrement) et renvoie un rapport JSON |
| `GET /stats` | contenu de la base (morceaux par format et par langue) |
| `GET /search?q=...` | les passages les plus proches d'une question, avec leur source |
| `POST /chat` | réponse rédigée par le modèle local à partir des passages, avec les sources |
| `GET /analyse` | indicateurs statistiques pour le tableau de bord |

## Tests et résultats

**Choix du modèle et de la taille des morceaux** (étape 3, 10 questions de validation) :

| Configuration | Réponse dans le top 5 | Bon document trouvé |
|---|---|---|
| paraphrase-multilingual-MiniLM, morceaux de 250 | 4/10 | 6/10 |
| **multilingual-e5-small, morceaux de 500** | **8/10** | **9/10** |

**Recette finale** (étape 8). Le script `src/recette.py` teste toute la chaîne en passant par l'API ; le détail est dans [`docs/recette.md`](docs/recette.md).

| Test | Résultat |
|---|---|
| Routes de l'API (`/`, `/stats`, `/search`, `/analyse`) | ✅ 4/4 |
| Interface web en ligne | ✅ |
| Recherche : bon document dans le top 5 | 9/10 |
| Recherche : réponse présente dans les passages | 8/10 |
| Assistant : réponse juste | 7/10 |
| Assistant : bon document cité dans les sources | 9/10 |
| Question hors sujet (Coupe du monde 2018) : l'assistant refuse de répondre | ✅ (« Je ne trouve aucune information pertinente dans le contexte fourni… ») |
| Numéro de page affiché pour les passages PDF | ✅ |

Les 10 questions demandent un fait précis (un chiffre, une année, un nom). Le test compte une réponse comme juste seulement si le mot attendu y apparaît. Durée moyenne d'une réponse : environ 70 secondes.

Remarque : à la première exécution, la question hors sujet était notée ❌, car le test cherchait seulement la phrase exacte « Je ne sais pas ». L'IA avait pourtant bien refusé avec une autre phrase. Le test reconnaît maintenant les différentes façons de refuser.

Pour relancer les tests (avec l'API lancée) :

```powershell
.venv\Scripts\python.exe src\recette.py          # rapide, environ 1 minute
.venv\Scripts\python.exe src\recette.py --chat   # avec l'IA, environ 15 minutes
```

## Limites

- Le modèle Llama 3.2 (3 milliards de paramètres) est léger pour tourner sur un ordinateur portable. Il peut parfois mélanger deux informations proches, mais les sources affichées permettent de vérifier chaque réponse.
- Sans carte graphique, une réponse de l'assistant prend une à deux minutes.
- Une question dont la réponse est un chiffre noyé dans un long rapport (la part du prix qui revient aux petits producteurs) n'est pas toujours retrouvée par la recherche.

## Avancement

- [x] Étape 1 : cadrage, corpus, questions de validation, initialisation Git
- [x] Étape 2 : pipeline d'extraction et de nettoyage
- [x] Étape 3 : chunking, embeddings et tests d'optimisation
- [x] Étape 4 : base vectorielle ChromaDB et API d'indexation
- [x] Étape 5 : moteur de recherche sémantique et pipeline RAG
- [x] Étape 6 : interface web (Streamlit) avec traçabilité des sources
- [x] Étape 7 : module de dataviz (Plotly)
- [x] Étape 8 : recette, documentation et dépôt GitHub
