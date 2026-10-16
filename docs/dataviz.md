# Étape 7 — Module de dataviz (analyse du corpus)

**Outils :** Plotly (graphiques interactifs) dans l'interface Streamlit, numpy pour les calculs.

## Comment ça marche

```
src/analyse.py  --calcule-->  GET /analyse (API)  --JSON-->  vue « 📊 Analyse du corpus » (Streamlit + Plotly)
   (documents nettoyés + base ChromaDB)
```

L'interface a maintenant deux vues (choix en haut de la barre latérale) :
- **💬 Chat** : la recherche précise d'informations (étape 6) ;
- **📊 Analyse du corpus** : la vue d'ensemble du corpus avec des graphiques.

## Les indicateurs

| # | Graphique | D'où viennent les données |
|---|---|---|
| 1 | Camemberts : documents par format et morceaux par format | documents + ChromaDB |
| 2 | Barres : nombre de mots par document | documents |
| 3 | Histogramme : taille des morceaux, et camembert des langues | ChromaDB + documents |
| 4 | Barres : fréquence des mots-clés du café et pays producteurs les plus cités | documents |
| 5 | Carte de chaleur : poids de 7 thèmes (botanique, culture, transformation, boissons, santé, économie, histoire) dans chaque document | documents |
| 6 | Barres : 20 mots les plus fréquents (sans les mots vides) | documents |
| 7 | Carte sémantique : chaque document placé selon son sens (vecteurs de 384 dimensions réduits à 2 par ACP) | ChromaDB |

Les mots-clés sont cherchés sans accents et en français et en anglais (ex. « torréfaction », « roast »).
Les thèmes sont comptés pour 1 000 mots, pour pouvoir comparer un petit document et un gros livre.

## Utilisation

```powershell
# rapport texte des indicateurs -> docs/analyse_corpus.md
.venv\Scripts\python.exe src\analyse.py
```

Dans l'interface : barre latérale → **📊 Analyse du corpus**.
