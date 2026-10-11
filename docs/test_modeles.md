# Comparaison de modèles d'embedding

*Date : 2026-10-11 19:50 — 30 documents — 10 questions de validation*

Rappel du premier test (`paraphrase-multilingual-MiniLM-L12-v2`) : voir `test_chunking.md`.

| Configuration | Nb de morceaux | Réponse en 1re position | Réponse dans le top 5 | Bon document dans le top 5 |
|---|---|---|---|---|
| multilingual-e5-small | 250/50 | sans limite | 23578 | 4/10 | 7/10 | 7/10 |
| multilingual-e5-small | 250/50 | max 2 par document | 23578 | 4/10 | 6/10 | 8/10 |
| multilingual-e5-small | 500/100 | sans limite | 11505 | 4/10 | 8/10 | 9/10 |
| multilingual-e5-small | 500/100 | max 2 par document | 11505 | 4/10 | 8/10 | 9/10 |

## Détail par question

### multilingual-e5-small | 250/50 | sans limite

| Question | Rang de la réponse | Document du 1er résultat |
|---|---|---|
| D'où le caféier est-il originaire ? | 1 | filiere-cafe-en-afrique.pdf |
| Quelles sont les deux espèces de café les plus cultivées ? | 2 | cafeier.html |
| Quelle part de la production mondiale représente l'arabica ? | 1 | rapport-senat-marche-du-cafe.pdf |
| En quelle année l'Organisation internationale du café a-t-elle été créée ? | 1 | rapport-assemblee-accord-sur-le-cafe.pdf |
| Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ? | non trouvée | histoire-cafe.html |
| Quelles substances la torréfaction forme-t-elle dans le café ? | non trouvée | cafe.html |
| Quelle part du prix d'un paquet de café revient aux petits producteurs ? | non trouvée | cafe.html |
| De quelle région le café est-il originaire ? | 2 | cafe-et-changement-climatique.pdf |
| Qu'est-ce que le kopi luwak ? | 1 | kopi-luwak.txt |
| Quelle est la différence entre le café vert et le café torréfié ? | 5 | cafe.html |

### multilingual-e5-small | 250/50 | max 2 par document

| Question | Rang de la réponse | Document du 1er résultat |
|---|---|---|
| D'où le caféier est-il originaire ? | 1 | filiere-cafe-en-afrique.pdf |
| Quelles sont les deux espèces de café les plus cultivées ? | 2 | cafeier.html |
| Quelle part de la production mondiale représente l'arabica ? | 1 | rapport-senat-marche-du-cafe.pdf |
| En quelle année l'Organisation internationale du café a-t-elle été créée ? | 1 | rapport-assemblee-accord-sur-le-cafe.pdf |
| Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ? | non trouvée | histoire-cafe.html |
| Quelles substances la torréfaction forme-t-elle dans le café ? | non trouvée | cafe.html |
| Quelle part du prix d'un paquet de café revient aux petits producteurs ? | non trouvée | cafe.html |
| De quelle région le café est-il originaire ? | 2 | cafe-et-changement-climatique.pdf |
| Qu'est-ce que le kopi luwak ? | 1 | kopi-luwak.txt |
| Quelle est la différence entre le café vert et le café torréfié ? | non trouvée | cafe.html |

### multilingual-e5-small | 500/100 | sans limite

| Question | Rang de la réponse | Document du 1er résultat |
|---|---|---|
| D'où le caféier est-il originaire ? | 2 | histoire-cafe.html |
| Quelles sont les deux espèces de café les plus cultivées ? | 2 | cafe.html |
| Quelle part de la production mondiale représente l'arabica ? | 5 | histoire-cafe.html |
| En quelle année l'Organisation internationale du café a-t-elle été créée ? | 1 | rapport-assemblee-accord-sur-le-cafe.pdf |
| Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ? | non trouvée | histoire-cafe.html |
| Quelles substances la torréfaction forme-t-elle dans le café ? | 1 | cafe-climat-et-sante.pdf |
| Quelle part du prix d'un paquet de café revient aux petits producteurs ? | non trouvée | cafe.html |
| De quelle région le café est-il originaire ? | 3 | cafe-et-changement-climatique.pdf |
| Qu'est-ce que le kopi luwak ? | 1 | kopi-luwak.txt |
| Quelle est la différence entre le café vert et le café torréfié ? | 1 | torrefaction.html |

### multilingual-e5-small | 500/100 | max 2 par document

| Question | Rang de la réponse | Document du 1er résultat |
|---|---|---|
| D'où le caféier est-il originaire ? | 2 | histoire-cafe.html |
| Quelles sont les deux espèces de café les plus cultivées ? | 2 | cafe.html |
| Quelle part de la production mondiale représente l'arabica ? | 5 | histoire-cafe.html |
| En quelle année l'Organisation internationale du café a-t-elle été créée ? | 1 | rapport-assemblee-accord-sur-le-cafe.pdf |
| Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ? | non trouvée | histoire-cafe.html |
| Quelles substances la torréfaction forme-t-elle dans le café ? | 1 | cafe-climat-et-sante.pdf |
| Quelle part du prix d'un paquet de café revient aux petits producteurs ? | non trouvée | cafe.html |
| De quelle région le café est-il originaire ? | 3 | cafe-et-changement-climatique.pdf |
| Qu'est-ce que le kopi luwak ? | 1 | kopi-luwak.txt |
| Quelle est la différence entre le café vert et le café torréfié ? | 1 | torrefaction.html |
