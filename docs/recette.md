# Recette finale (étape 8)

Date : 17/10/2026 00:27 · tests passés par l'API REST (http://127.0.0.1:8000)

## 1. Routes de l'API

| Route | Résultat | Détail |
|---|---|---|
| `GET /` | ✅ | API en ligne (0.0 s) |
| `GET /stats` | ✅ | 30 documents, 11505 morceaux (0.6 s) |
| `GET /search` | ✅ | 3 passages avec leur source (0.0 s) |
| `GET /analyse` | ✅ | indicateurs calculés, 30 documents sur la carte sémantique (5.5 s) |

## 2. Interface web

- ✅ `http://localhost:8501` : en ligne

## 3. Recherche sémantique sur les questions de validation (top 5)

| # | Question | Bon document dans le top 5 | Réponse dans les passages | 1re source | Score |
|---|---|---|---|---|---|
| 1 | D'où le caféier est-il originaire ? | ✅ | ✅ | histoire-cafe.html | 0.89 |
| 2 | Quelles sont les deux espèces de café les plus cultivées ? | ✅ | ✅ | cafe.html | 0.88 |
| 3 | Quelle part de la production mondiale représente l'arabica ? | ✅ | ✅ | histoire-cafe.html | 0.88 |
| 4 | En quelle année l'Organisation internationale du café a-t-elle été créée ? | ✅ | ✅ | rapport-assemblee-accord-sur-le-cafe.pdf p.7 | 0.93 |
| 5 | Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ? | ✅ | ❌ | histoire-cafe.html | 0.89 |
| 6 | Quelles substances la torréfaction forme-t-elle dans le café ? | ✅ | ✅ | cafe-climat-et-sante.pdf p.3 | 0.91 |
| 7 | Quelle part du prix d'un paquet de café revient aux petits producteurs ? | ❌ | ❌ | cafe.html | 0.88 |
| 8 | De quelle région le café est-il originaire ? | ✅ | ✅ | cafe-et-changement-climatique.pdf p.3 | 0.89 |
| 9 | Qu'est-ce que le kopi luwak ? | ✅ | ✅ | kopi-luwak.txt | 0.93 |
| 10 | Quelle est la différence entre le café vert et le café torréfié ? | ✅ | ✅ | torrefaction.html | 0.89 |

**Bon document trouvé : 9/10 · réponse présente dans les passages : 8/10**

- ✅ Tous les passages venant d'un PDF ont un numéro de page.

## 4. Assistant RAG (POST /chat)

| # | Question | Réponse juste | Bon document cité | Durée |
|---|---|---|---|---|
| 1 | D'où le caféier est-il originaire ? | ✅ | ✅ | 59.9 s |
| 2 | Quelles sont les deux espèces de café les plus cultivées ? | ✅ | ✅ | 57.2 s |
| 3 | Quelle part de la production mondiale représente l'arabica ? | ❌ | ✅ | 64.9 s |
| 4 | En quelle année l'Organisation internationale du café a-t-elle été créée ? | ✅ | ✅ | 57.8 s |
| 5 | Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ? | ❌ | ✅ | 80.7 s |
| 6 | Quelles substances la torréfaction forme-t-elle dans le café ? | ✅ | ✅ | 68.9 s |
| 7 | Quelle part du prix d'un paquet de café revient aux petits producteurs ? | ❌ | ❌ | 65.8 s |
| 8 | De quelle région le café est-il originaire ? | ✅ | ✅ | 56.6 s |
| 9 | Qu'est-ce que le kopi luwak ? | ✅ | ✅ | 83.2 s |
| 10 | Quelle est la différence entre le café vert et le café torréfié ? | ✅ | ✅ | 100.5 s |

**Réponses justes : 7/10 · bon document cité : 9/10**

- ❌ Question hors sujet (« Qui a gagné la Coupe du monde de football en 2018 ? ») : « Je ne trouve aucune information pertinente dans le contexte fourni concernant la Coupe du monde de football en 2018. Le contexte se concentre sur l'hi »

### Réponses complètes

**1. D'où le caféier est-il originaire ?**

> Selon [4] (source : cafeier.html) et [5] (source : arabica.html), le caféier est originaire de l'Afrique de l'Est, notamment en Éthiopie, au Soudan du Sud (plateau de Boma) et au Kenya.

*Sources : histoire-cafe.html, filiere-cafe-en-afrique.pdf p.3, cafe-et-changement-climatique.pdf p.3, cafeier.html, arabica.html*

**2. Quelles sont les deux espèces de café les plus cultivées ?**

> Selon [2] (source : cafeier.html), les deux espèces de café les plus cultivées sont :

1. Coffea arabica
2. Coffea canephora (connu sous le nom de café robusta)

*Sources : cafe.html, cafeier.html, cafeier.html, histoire-cafe.html, arabica.html*

**3. Quelle part de la production mondiale représente l'arabica ?**

> Selon le contexte fourni, l'arabica représente 85 % de la production mondiale de café, ce qui équivaut à environ 110 millions de sacs par an. [3]

*Sources : histoire-cafe.html, histoire-cafe.html, arabica.html, robusta.html, rapport-senat-marche-du-cafe.pdf p.3*

**4. En quelle année l'Organisation internationale du café a-t-elle été créée ?**

> L'Organisation internationale du café a été créée en 1963.

*Sources : rapport-assemblee-accord-sur-le-cafe.pdf p.7, rapport-senat-marche-du-cafe.pdf p.8, rapport-assemblee-accord-sur-le-cafe.pdf p.7, histoire-cafe.html, histoire-cafe.html*

**5. Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ?**

> Selon le document [2] (source : filiere-cafe-en-afrique.pdf, page 11), en 1970, les trois premiers pays exportateurs africains de café avaient des parts mondiales de 4,9%, 2,4% et 7,1% respectivement. Cependant, pour connaître la part de l'Afrique dans la production mondiale de café dans les années 1970, il faut considérer la production totale de l'Afrique. 

Selon le document [4] (source : filiere-cafe-en-afrique.pdf, page 5), en 1970, la production totale de l'Afrique était de 1,6 million de sacs. 

En 1970, la production mondiale de café était de 42,2 millions de sacs (selon le document [1] (source : histoire-cafe.html)). 

La part de l'Afrique dans la production mondiale de café en 1970 serait donc de 1,6 million de sacs / 42,2 millions de sacs = 3,8%.

*Sources : histoire-cafe.html, filiere-cafe-en-afrique.pdf p.11, histoire-cafe.html, filiere-cafe-en-afrique.pdf p.5, production-cafe-pays-non-membres.pdf p.3*

**6. Quelles substances la torréfaction forme-t-elle dans le café ?**

> Selon les sources [3] et [5], la torréfaction forme plusieurs substances dans le café, notamment :

* L'acrylamide, une substance potentiellement cancérigène chez l'humain.
* Des furanes polycondensés, qui contribuent à l'arôme complexe du café.
* Des alcools, des phénols, des aldéhydes, des dérivés furaniques (comme le kahwéol ou le cafestol) et pyrroliques, carbures, thiophènes, etc.

Il est également mentionné que la torréfaction peut dégrader les polysaccharides des grains verts d'arabica, notamment les arabinogalactanes et les mannanes.

*Sources : cafe-climat-et-sante.pdf p.3, cafe.html, torrefaction.html, torrefaction.html, cafe.html*

**7. Quelle part du prix d'un paquet de café revient aux petits producteurs ?**

> Selon le rapport du Sénat [4], les producteurs de café ne reçoivent qu'environ 6 % de la valeur d'un paquet de café vendu dans les supermarchés et les épiceries.

*Sources : cafe.html, cafe-et-changement-climatique.pdf p.7, rapport-senat-marche-du-cafe.pdf p.12, rapport-senat-marche-du-cafe.pdf p.12, filiere-cafe-en-afrique.pdf p.28*

**8. De quelle région le café est-il originaire ?**

> Selon [3] (source : histoire-cafe.html), le café est originaire de la province de Kaffa, en Éthiopie.

*Sources : cafe-et-changement-climatique.pdf p.3, cafe.html, histoire-cafe.html, cafe.html, histoire-cafe.html*

**9. Qu'est-ce que le kopi luwak ?**

> Le kopi luwak est un type de café récolté dans les excréments d'une civette asiatique, le luwak (Paradoxurus musanga), de la famille des viverridés. Les civettes consomment les cerises du caféier, digérant leur pulpe mais pas leur noyau, qui se retrouve dans ses excréments. Les sucs gastriques du luwak font subir une transformation bénéfique aux arômes des grains de café, ce qui donne au kopi luwak son caractère unique et son goût spécifique. [1]

*Sources : kopi-luwak.txt, kopi-luwak.txt, histoire-cafe.html, cafe.html, cafeier.html*

**10. Quelle est la différence entre le café vert et le café torréfié ?**

> Selon les informations fournies, le principal différend entre le café vert et le café torréfié réside dans leur contenu en termes de nutriments et de saveur. 

Le café vert, qui n'a pas subi de torréfaction, n'a pas d'arôme ni de saveur, contrairement au café torréfié qui a subi une torréfaction qui permet de révéler le goût et l'arôme des grains. 

En outre, selon une étude citée dans [4], le café vert contient plus de saccharose et de trigonelline, tandis que le café torréfié est plus riche en acides chlorogéniques et en caféine.

*Sources : torrefaction.html, cafe.html, torrefaction.html, cafe.html, kopi-luwak.txt*

*Durée totale de la recette : 14.1 min*
