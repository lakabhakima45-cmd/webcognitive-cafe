# WebCognitive Engine – Corpus « Le café »

Projet individuel réalisé dans le cadre du cours **Techniques Informatiques et Web** (Master Technologies de l'Hypermédia, Université Paris 8).

**Auteure :** Hakima Lakab

## Présentation

Application web qui transforme un ensemble de documents sur le café (PDF, HTML, Word, TXT) en un moteur de recherche sémantique et un assistant conversationnel, capable de répondre aux questions en citant ses sources.

L'application fonctionne entièrement en local, avec des outils libres.

## Thème du corpus

**Le café, de la plante à la tasse** : botanique, histoire, production et commerce, transformation, consommation et environnement.

Le corpus contient 30 documents :

| Format | Nombre |
|---|---|
| HTML | 10 |
| PDF | 8 |
| TXT | 7 |
| DOCX | 5 |

## Organisation du projet

```
cafe/
├── data/          documents du corpus (html, pdf, docx, txt)
├── docs/          cahier des charges et questions de validation
├── src/           code Python
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Avancement

- [x] Étape 1 : cadrage, corpus, questions de validation, initialisation Git
- [ ] Étape 2 : pipeline d'ingestion et de nettoyage
- [ ] Étape 3 : chunking et embeddings
- [ ] Étape 4 : base vectorielle et recherche sémantique
- [ ] Étape 5 : API REST (FastAPI)
- [ ] Étape 6 : RAG avec un modèle local (Ollama)
- [ ] Étape 7 : interface web et tableau de bord
- [ ] Étape 8 : tests, finitions et soutenance

## Documentation

- [Cahier des charges](docs/cahier_des_charges.md)
- [Questions de validation](docs/questions_validation.md)
