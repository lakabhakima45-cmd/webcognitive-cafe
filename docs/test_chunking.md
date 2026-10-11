# Test de la taille des morceaux (chunking)

*Date : 2026-10-11 18:43 — modèle : `paraphrase-multilingual-MiniLM-L12-v2` — 30 documents*

## Méthode

Le corpus est découpé avec plusieurs tailles de morceaux. Chaque morceau est transformé en vecteur, puis on pose les 10 questions de validation. Pour chaque question, on regarde les 5 morceaux les plus proches (similarité cosinus) et on vérifie s'ils contiennent la réponse attendue.

## Résultats

| Taille / chevauchement | Nb de morceaux | Longueur moyenne | Réponse en 1re position | Réponse dans le top 5 | Bon document dans le top 5 | Similarité moyenne | Durée |
|---|---|---|---|---|---|---|---|
| 250 / 50 | 23578 | 208 car. | 1/10 | 4/10 | 6/10 | 0.79 | 472 s |
| 500 / 100 | 11505 | 428 car. | 2/10 | 2/10 | 3/10 | 0.78 | 520 s |
| 1000 / 200 | 5193 | 914 car. | 2/10 | 3/10 | 3/10 | 0.78 | 321 s |

**Meilleure configuration : 250 / 50 caractères.**

## Détail par question

### 250 / 50

| Question | Rang de la réponse | Document du 1er résultat |
|---|---|---|
| D'où le caféier est-il originaire ? | non trouvée | tout-sur-le-cafe-ukers-1922.txt |
| Quelles sont les deux espèces de café les plus cultivées ? | 5 | tout-sur-le-cafe-ukers-1922.txt |
| Quelle part de la production mondiale représente l'arabica ? | 3 | histoire-cafe.html |
| En quelle année l'Organisation internationale du café a-t-elle été créée ? | 1 | rapport-assemblee-accord-sur-le-cafe.pdf |
| Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ? | non trouvée | histoire-cafe.html |
| Quelles substances la torréfaction forme-t-elle dans le café ? | non trouvée | cafe.html |
| Quelle part du prix d'un paquet de café revient aux petits producteurs ? | non trouvée | commerce-du-cafe-ukers.txt |
| De quelle région le café est-il originaire ? | non trouvée | histoire-cafe.html |
| Qu'est-ce que le kopi luwak ? | 5 | cafe.html |
| Quelle est la différence entre le café vert et le café torréfié ? | non trouvée | tout-sur-le-cafe-ukers-1922.txt |

### 500 / 100

| Question | Rang de la réponse | Document du 1er résultat |
|---|---|---|
| D'où le caféier est-il originaire ? | non trouvée | tout-sur-le-cafe-ukers-1922.txt |
| Quelles sont les deux espèces de café les plus cultivées ? | non trouvée | tout-sur-le-cafe-ukers-1922.txt |
| Quelle part de la production mondiale représente l'arabica ? | non trouvée | cycles-de-production-du-cafe.pdf |
| En quelle année l'Organisation internationale du café a-t-elle été créée ? | 1 | rapport-assemblee-accord-sur-le-cafe.pdf |
| Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ? | non trouvée | commerce-du-cafe-ukers.txt |
| Quelles substances la torréfaction forme-t-elle dans le café ? | non trouvée | cafe.html |
| Quelle part du prix d'un paquet de café revient aux petits producteurs ? | non trouvée | commerce-du-cafe-ukers.txt |
| De quelle région le café est-il originaire ? | non trouvée | commerce-du-cafe-ukers.txt |
| Qu'est-ce que le kopi luwak ? | 1 | kopi-luwak.txt |
| Quelle est la différence entre le café vert et le café torréfié ? | non trouvée | cafe.html |

### 1000 / 200

| Question | Rang de la réponse | Document du 1er résultat |
|---|---|---|
| D'où le caféier est-il originaire ? | non trouvée | tout-sur-le-cafe-ukers-1922.txt |
| Quelles sont les deux espèces de café les plus cultivées ? | non trouvée | tout-sur-le-cafe-ukers-1922.txt |
| Quelle part de la production mondiale représente l'arabica ? | non trouvée | production-cafe-pays-non-membres.pdf |
| En quelle année l'Organisation internationale du café a-t-elle été créée ? | 1 | rapport-assemblee-accord-sur-le-cafe.pdf |
| Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ? | 2 | commerce-du-cafe-ukers.txt |
| Quelles substances la torréfaction forme-t-elle dans le café ? | non trouvée | tout-sur-le-cafe-ukers-1922.txt |
| Quelle part du prix d'un paquet de café revient aux petits producteurs ? | non trouvée | tout-sur-le-cafe-ukers-1922.txt |
| De quelle région le café est-il originaire ? | non trouvée | tout-sur-le-cafe-ukers-1922.txt |
| Qu'est-ce que le kopi luwak ? | 1 | kopi-luwak.txt |
| Quelle est la différence entre le café vert et le café torréfié ? | non trouvée | commerce-du-cafe-ukers.txt |
