# Cahier des charges

**Projet :** WebCognitive Engine – Moteur de recherche sémantique et assistant conversationnel
**Cours :** Techniques Informatiques et Web – Master Technologies de l'Hypermédia, Université Paris 8
**Étudiante :** Hakima Lakab
**Version :** Étape 1 – Cadrage et corpus

---

## 1. Contexte

Aujourd'hui, la recherche d'information ne se fait plus seulement par mots-clés exacts : on cherche du sens. L'objectif de ce projet est de construire une application web capable de lire un ensemble de documents de formats différents et de répondre en langage naturel aux questions posées sur leur contenu, en indiquant toujours les sources utilisées.

L'application fonctionne entièrement en local, avec des outils libres et gratuits, sans service cloud payant.

## 2. Thème du corpus

**Le café, de la plante à la tasse.**

Le corpus couvre plusieurs aspects d'un même sujet :
- **botanique** : le caféier, les espèces (arabica, robusta) ;
- **histoire** : origine en Éthiopie, diffusion dans le monde arabe puis en Europe ;
- **économie** : production mondiale, pays producteurs, prix et commerce équitable ;
- **transformation** : torréfaction, décaféination, café soluble ;
- **consommation** : boissons (expresso, cappuccino, café turc…), méthodes de préparation, caféine et santé ;
- **environnement** : impact du changement climatique sur la culture du café.

J'ai choisi ce thème parce qu'il est concret, facile à comprendre et riche en sources ouvertes. Il contient aussi beaucoup de chiffres, de dates et de définitions, ce qui permet de tester précisément les réponses du moteur.

## 3. Le corpus

Le corpus contient **30 documents** en 4 formats.

| Format | Nombre | Sources |
|---|---|---|
| HTML | 10 | Articles de Wikipédia (fr) |
| PDF | 8 | Rapports du Sénat et de l'Assemblée nationale, Organisation internationale du café, CIRAD / Max Havelaar, Académie d'agriculture, document pédagogique |
| TXT | 7 | Livres du domaine public (Projet Gutenberg, en anglais) et articles Wikipédia en texte brut |
| DOCX | 5 | Articles Wikipédia convertis en documents Word |

### Inventaire des documents

**HTML** (`data/html/`)

| Fichier | Contenu |
|---|---|
| cafe.html | Présentation générale du café |
| histoire-cafe.html | Histoire du café, de l'Éthiopie à aujourd'hui |
| cafeier.html | Le caféier (genre Coffea) |
| arabica.html | L'espèce Coffea arabica |
| robusta.html | L'espèce Coffea canephora (robusta) |
| cafeine.html | La caféine |
| torrefaction.html | La torréfaction |
| expresso.html | L'expresso |
| cafe-soluble.html | Le café soluble |
| commerce-equitable.html | Le commerce équitable |

**PDF** (`data/pdf/`)

| Fichier | Contenu |
|---|---|
| rapport-senat-marche-du-cafe.pdf | Rapport du Sénat sur le marché international du café |
| rapport-assemblee-accord-sur-le-cafe.pdf | Rapport de l'Assemblée nationale sur l'accord international sur le café |
| filiere-cafe-en-afrique.pdf | Organisation internationale du café : la filière café en Afrique |
| cycles-de-production-du-cafe.pdf | Organisation internationale du café : les cycles de production |
| production-cafe-pays-non-membres.pdf | Organisation internationale du café : la production des pays non membres |
| cafe-et-changement-climatique.pdf | Filière café et enjeux environnementaux (rencontre scientifique, 2023) |
| cafe-climat-et-sante.pdf | Académie d'agriculture : production, climat et santé |
| le-cafe-grand-marche-mondial.pdf | Document pédagogique sur la filière café |

**TXT** (`data/txt/`)

| Fichier | Contenu |
|---|---|
| tout-sur-le-cafe-ukers-1922.txt | *All About Coffee*, W. H. Ukers, 1922 (anglais) |
| commerce-du-cafe-ukers.txt | *Coffee Merchandising*, W. H. Ukers (anglais) |
| cappuccino.txt | Le cappuccino |
| cafe-turc.txt | Le café turc |
| kopi-luwak.txt | Le kopi luwak |
| cafetiere-italienne.txt | La cafetière italienne |
| decafeination.txt | La décaféination |

**DOCX** (`data/docx/`)

| Fichier | Contenu |
|---|---|
| barista.docx | Le métier de barista |
| nespresso.docx | La marque Nespresso |
| cafe-liegeois.docx | Le café liégeois |
| cafe-au-lait.docx | Le café au lait |
| starbucks.docx | L'entreprise Starbucks |

### Langues

Le corpus est principalement en **français**, avec deux livres en **anglais**. Il faudra donc choisir un modèle d'embeddings multilingue pour que les recherches en français trouvent aussi les passages en anglais.

### Licences

- Wikipédia : licence CC BY-SA ;
- Projet Gutenberg : domaine public ;
- rapports publics (Sénat, Assemblée nationale) : documents publics librement consultables ;
- autres PDF : documents publiés en accès libre par leurs organismes.

Le corpus est utilisé uniquement dans un cadre pédagogique.

## 4. Utilisateurs visés

- étudiants ou curieux qui veulent apprendre sur le café ;
- personnes qui travaillent dans le secteur (barista, torréfacteur, commerce) et cherchent une information précise ;
- l'enseignant, pour évaluer la qualité des réponses du moteur.

## 5. Fonctionnalités attendues

### 5.1 Ingestion des documents
- lire automatiquement les fichiers PDF, HTML, DOCX et TXT ;
- extraire le texte et le nettoyer (menus de Wikipédia, en-têtes, espaces en trop, caractères spéciaux) ;
- conserver les informations sur chaque document : titre, format, source, langue.

### 5.2 Vectorisation
- découper les textes en morceaux (chunks) de taille adaptée ;
- transformer chaque morceau en vecteur (embedding) ;
- stocker les vecteurs dans une base de données vectorielle.

### 5.3 Recherche sémantique
- poser une question en langage naturel ;
- retrouver les passages les plus proches par le sens, même sans les mots exacts.

### 5.4 Assistant conversationnel (RAG)
- générer une réponse avec un modèle de langage local, à partir des passages trouvés ;
- **toujours citer les sources** (nom du document et passage) ;
- répondre « je ne sais pas » si l'information n'est pas dans le corpus, pour éviter les hallucinations.

### 5.5 Interface web et visualisation
- une page pour poser des questions et lire les réponses avec leurs sources ;
- un tableau de bord sur le corpus, par exemple : nombre de documents par format, mots les plus fréquents, répartition des thèmes, frise chronologique des dates citées.

## 6. Contraintes techniques

| Besoin | Outil prévu |
|---|---|
| Langage | Python |
| Lecture des fichiers | pypdf ou PyMuPDF (PDF), BeautifulSoup (HTML), python-docx (Word) |
| Embeddings | Sentence-Transformers (modèle multilingue, Hugging Face) |
| Base vectorielle | ChromaDB (ou FAISS) |
| API | FastAPI |
| Modèle de langage local | Ollama |
| Interface | Streamlit ou page web (HTML/CSS/JavaScript) |
| Visualisation | Plotly |
| Versionnement | Git et GitHub |

Contraintes générales :
- fonctionnement **100 % local** ;
- outils **libres et gratuits** uniquement ;
- code organisé, commenté et versionné avec Git ;
- environnement Python isolé (environnement virtuel).

## 7. Organisation du projet

```
cafe/
├── data/
│   ├── html/      documents HTML
│   ├── pdf/       documents PDF
│   ├── docx/      documents Word
│   └── txt/       documents texte
├── docs/
│   ├── cahier_des_charges.md
│   └── questions_validation.md
├── src/           code Python (à partir de l'étape 2)
├── .gitignore
├── README.md
└── requirements.txt
```

## 8. Validation

Pour vérifier la qualité du moteur, j'ai préparé **10 questions de validation** (fichier `docs/questions_validation.md`). Leurs réponses se trouvent dans des documents précis du corpus, en HTML, PDF et TXT.

Le moteur sera considéré comme réussi s'il :
- trouve la bonne réponse ;
- cite le bon document ;
- ne donne pas d'information inventée.

## 9. Planning prévisionnel

| Étape | Contenu |
|---|---|
| 1 | Cadrage, constitution du corpus, questions de validation, Git |
| 2 | Pipeline d'ingestion et de nettoyage |
| 3 | Découpage (chunking) et embeddings |
| 4 | Base vectorielle et recherche sémantique |
| 5 | API REST avec FastAPI |
| 6 | Intégration du modèle local (RAG) avec citation des sources |
| 7 | Interface web et tableau de bord |
| 8 | Tests, finitions et soutenance |
