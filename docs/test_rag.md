# Test du pipeline RAG

*Date : 2026-10-12 03:49 — modèle : `llama3.2:3b` — 5 passages par question*

Les 10 premières questions sont les questions de validation. Les 2 dernières sont hors sujet : le modèle doit répondre qu'il ne sait pas.

## 1. D'où le caféier est-il originaire ?

Selon [4] (source : cafeier.html) et [5] (source : arabica.html), le caféier est originaire de l'Afrique de l'Est, notamment en Éthiopie, au Soudan du Sud (plateau de Boma) et au Kenya.

*Sources : [1] histoire-cafe.html, [2] filiere-cafe-en-afrique.pdf p.3, [3] cafe-et-changement-climatique.pdf p.3, [4] cafeier.html, [5] arabica.html*
*Durée : 69.2 s*

## 2. Quelles sont les deux espèces de café les plus cultivées ?

Selon [2] (source : cafeier.html), les deux espèces de café les plus cultivées sont :

1. Coffea arabica
2. Coffea canephora (connu sous le nom de café robusta)

*Sources : [1] cafe.html, [2] cafeier.html, [3] cafeier.html, [4] histoire-cafe.html, [5] arabica.html*
*Durée : 48.2 s*

## 3. Quelle part de la production mondiale représente l'arabica ?

Selon le contexte fourni, l'arabica représente environ 85 % de la production mondiale de café, soit environ 110 millions de sacs par an.

*Sources : [1] histoire-cafe.html, [2] histoire-cafe.html, [3] arabica.html, [4] robusta.html, [5] rapport-senat-marche-du-cafe.pdf p.3*
*Durée : 55.0 s*

## 4. En quelle année l'Organisation internationale du café a-t-elle été créée ?

L'Organisation internationale du café a été créée en 1963.

*Sources : [1] rapport-assemblee-accord-sur-le-cafe.pdf p.7, [2] rapport-senat-marche-du-cafe.pdf p.8, [3] rapport-assemblee-accord-sur-le-cafe.pdf p.7, [4] histoire-cafe.html, [5] histoire-cafe.html*
*Durée : 51.9 s*

## 5. Quelle était la part de l'Afrique dans la production mondiale de café dans les années 1970 ?

Selon le document [2] (source : filiere-cafe-en-afrique.pdf, page 11), en 1970, les trois premiers pays exportateurs africains étaient l'Ouganda, l'Éthiopie et la Côte d'Ivoire, avec des parts respectives de 4,9%, 2,4% et 7,1% de la production mondiale de café. Cependant, pour connaître la part de l'Afrique dans la production mondiale de café dans les années 1970, il faut considérer la part totale des pays africains. 

Selon le document [4] (source : filiere-cafe-en-afrique.pdf, page 5), en 1970, les pays africains représentaient 4,9% de la production mondiale de café, et en 1974, cette part était de 5%. 

Il est donc possible de conclure que la part de l'Afrique dans la production mondiale de café dans les années 1970 était de l'ordre de 5%.

*Sources : [1] histoire-cafe.html, [2] filiere-cafe-en-afrique.pdf p.11, [3] histoire-cafe.html, [4] filiere-cafe-en-afrique.pdf p.5, [5] production-cafe-pays-non-membres.pdf p.3*
*Durée : 77.3 s*

## 6. Quelles substances la torréfaction forme-t-elle dans le café ?

Selon les sources [3] et [5], la torréfaction du café forme plusieurs substances, notamment :

* L'acrylamide, une substance potentiellement cancérigène chez l'humain.
* Des furanes polycondensés, qui constituent un arôme complexe se développant à partir d'alcools, de phénols, d'aldéhydes, de dérivés furaniques et pyrroliques, carbures, thiophènes, etc.
* Des composés aromatiques volatils, dont 42 sont de nature phénoliques, qui proviennent principalement de la dégradation thermique des acides chlorogéniques et de la lignine.

Il est important de noter que les concentrations de ces substances peuvent varier en fonction du degré de torréfaction et de la méthode de torréfaction utilisée.

*Sources : [1] cafe-climat-et-sante.pdf p.3, [2] cafe.html, [3] torrefaction.html, [4] torrefaction.html, [5] cafe.html*
*Durée : 68.6 s*

## 7. Quelle part du prix d'un paquet de café revient aux petits producteurs ?

Selon Oxfam, les producteurs de café ne reçoivent qu'environ 6 % de la valeur d'un paquet de café vendu dans les supermarchés et les épiceries [4].

*Sources : [1] cafe.html, [2] cafe-et-changement-climatique.pdf p.7, [3] rapport-senat-marche-du-cafe.pdf p.12, [4] rapport-senat-marche-du-cafe.pdf p.12, [5] filiere-cafe-en-afrique.pdf p.28*
*Durée : 65.8 s*

## 8. De quelle région le café est-il originaire ?

Selon [3] (source : histoire-cafe.html), le café est originaire de la province de Kaffa, en Éthiopie.

*Sources : [1] cafe-et-changement-climatique.pdf p.3, [2] cafe.html, [3] histoire-cafe.html, [4] cafe.html, [5] histoire-cafe.html*
*Durée : 53.7 s*

## 9. Qu'est-ce que le kopi luwak ?

Le kopi luwak est un type de café récolté dans les excréments d'une civette asiatique, le luwak (Paradoxurus musanga), du fait d'une digestion quasi inexistante. La civette consomme en effet les cerises du caféier, digérant leur pulpe mais pas leur noyau, qui se retrouve dans ses excréments. Le café luwak est connu pour sa saveur unique et ses arômes bénéfiques, résultant de la transformation des sucs gastriques du luwak. [1]

*Sources : [1] kopi-luwak.txt, [2] kopi-luwak.txt, [3] histoire-cafe.html, [4] cafe.html, [5] cafeier.html*
*Durée : 58.3 s*

## 10. Quelle est la différence entre le café vert et le café torréfié ?

Selon les informations fournies, le principal différend entre le café vert et le café torréfié réside dans leur contenu en termes de nutriments et de saveurs. 

Le café vert, issu du grain de café vert, n'a aucun arôme ni saveur, et est riche en saccharose et en trigonelline. Il contient également plus de caféine que le café torréfié. 

Le café torréfié, quant à lui, contient moins de caféine et plus de saccharose et de trigonelline que le café vert. De plus, la torréfaction du café peut détruire certains nutriments, tels que les acides chlorogéniques, qui constituent des composés phénoliques du café.

*Sources : [1] torrefaction.html, [2] cafe.html, [3] torrefaction.html, [4] cafe.html, [5] kopi-luwak.txt*
*Durée : 69.4 s*

## 11. Qui a gagné la Coupe du monde de football en 2018 ?

Je ne trouve aucune information dans le contexte fourni qui pourrait m'aider à répondre à cette question. Le contexte est principalement consacré à l'histoire du café, aux productions et aux exportations de café, ainsi qu'à la filière du café en Afrique. Il n'y a aucune mention de la Coupe du monde de football ou de tout événement sportif similaire.

*Sources : [1] histoire-cafe.html, [2] cafe.html, [3] histoire-cafe.html, [4] filiere-cafe-en-afrique.pdf p.30, [5] cycles-de-production-du-cafe.pdf p.2*
*Durée : 102.2 s*

## 12. Quelle est la capitale de l'Australie ?

Je n'ai pas trouvé d'information sur la capitale de l'Australie dans le contexte fourni.

*Sources : [1] kopi-luwak.txt, [2] kopi-luwak.txt, [3] histoire-cafe.html, [4] starbucks.docx, [5] histoire-cafe.html*
*Durée : 60.6 s*
