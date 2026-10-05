# Questions de validation du corpus

**Projet :** WebCognitive Engine – Étape 1 (Cadrage, corpus et stratégie d'ingestion)
**Thème du corpus :** Le café, de la plante à la tasse
**Étudiante :** Hakima Lakab

## Objectif

Avant de commencer le code, j'ai ouvert à la main plusieurs documents du corpus pour vérifier qu'ils contiennent des informations précises et exploitables. Pour chaque question, j'ai relevé la réponse, le passage exact du document et son emplacement.

Ces questions serviront plus tard à tester le moteur de recherche : l'application devra retrouver la bonne réponse et citer le bon document.

## Récapitulatif

| N° | Question | Document | Format | Type de réponse |
|---|---|---|---|---|
| 1 | Origine du caféier | cafeier.html | HTML | Lieu |
| 2 | Principales espèces cultivées | cafeier.html | HTML | Définition |
| 3 | Part de l'arabica dans la production | rapport-senat-marche-du-cafe.pdf | PDF | Chiffre |
| 4 | Création de l'Organisation internationale du café | rapport-assemblee-accord-sur-le-cafe.pdf | PDF | Date |
| 5 | Part de l'Afrique dans la production (années 1970) | filiere-cafe-en-afrique.pdf | PDF | Chiffre |
| 6 | Substances formées par la torréfaction | cafe-climat-et-sante.pdf | PDF | Explication |
| 7 | Part du prix pour les petits producteurs | le-cafe-grand-marche-mondial.pdf | PDF | Chiffre (tableau) |
| 8 | Région d'origine du café et premier café | histoire-cafe.html | HTML | Lieu et date |
| 9 | Le kopi luwak | kopi-luwak.txt | TXT | Définition et histoire |
| 10 | Café vert et café torréfié | torrefaction.html | HTML | Explication |

---

## Question 1 – D'où le caféier est-il originaire ?

- **Document :** `data/html/cafeier.html`
- **Emplacement :** introduction, 1er paragraphe
- **Réponse attendue :** des régions tropicales d'Afrique et d'Asie.
- **Passage du document :**
  > « Les Caféiers (Coffea L.) sont un genre de plantes à fleurs de la famille des Rubiacées, qui comprend plus de 130 espèces d'arbres ou d'arbustes originaires des régions tropicales d'Afrique ou d'Asie. »

## Question 2 – Quelles sont les deux espèces de café les plus cultivées ?

- **Document :** `data/html/cafeier.html`
- **Emplacement :** introduction, 2e paragraphe
- **Réponse attendue :** Coffea arabica et Coffea canephora (le robusta).
- **Passage du document :**
  > « Deux espèces sont plus particulièrement cultivées, Coffea arabica et Coffea canephora (et dans une moindre mesure Coffea liberica). »

## Question 3 – Quelle part de la production mondiale représente l'arabica ?

- **Document :** `data/pdf/rapport-senat-marche-du-cafe.pdf`
- **Emplacement :** partie I.A.1 « Un enjeu économique majeur », 2e paragraphe
- **Réponse attendue :** les trois quarts de la production mondiale.
- **Passage du document :**
  > « L'arabica représente les trois-quarts de la production mondiale qui s'établit à environ 110 millions de sacs par an. Le Brésil produit le tiers de la production mondiale avec 2,4 millions de tonnes, suivi du Vietnam, de la Colombie, de l'Indonésie et du Mexique. »

*Remarque : ce passage permet aussi de poser une question sur le premier pays producteur (le Brésil).*

## Question 4 – En quelle année l'Organisation internationale du café a-t-elle été créée ?

- **Document :** `data/pdf/rapport-assemblee-accord-sur-le-cafe.pdf`
- **Emplacement :** paragraphe sur la création de l'OIC
- **Réponse attendue :** en 1963.
- **Passage du document :**
  > « L'Organisation internationale du café a été créée en 1963 pour mettre en œuvre le premier accord international sur le café conclu en 1962 à New York sous les auspices des Nations unies. Cet accord, d'une durée de cinq ans, visait à stabiliser les cours du café. »

## Question 5 – Quelle était la part de l'Afrique dans la production mondiale dans les années 1970 ?

- **Document :** `data/pdf/filiere-cafe-en-afrique.pdf`
- **Emplacement :** section I.1.1 « Tendances passées et actuelles de la production »
- **Réponse attendue :** 27,2 %.
- **Passage du document :**
  > « La part de l'Afrique dans la production mondiale a donc diminué, passant de 27,2% dans les années 1970 à une moyenne de 16% dans les années 1990 et à 13,1% dans les années 2000. »

## Question 6 – Quelles substances la torréfaction forme-t-elle, et sont-elles dangereuses ?

- **Document :** `data/pdf/cafe-climat-et-sante.pdf`
- **Emplacement :** partie sur le café et la santé
- **Réponse attendue :** de l'acrylamide et du furane, mais en quantité trop faible pour affecter la santé.
- **Passage du document :**
  > « La torréfaction induit la formation d'acrylamide et de furane comme dans tous les aliments grillés. Toutefois, les concentrations présentes dans le café ne semblent pas suffisantes pour affecter la santé. »

## Question 7 – Quelle part du prix d'un paquet de café revient aux petits producteurs ?

- **Document :** `data/pdf/le-cafe-grand-marche-mondial.pdf`
- **Emplacement :** page 1, tableau « La filière café, du caféier au supermarché »
- **Réponse attendue :** 10 %.
- **Contenu du tableau :**

| Opération | Acteurs | Part du prix |
|---|---|---|
| Production, récolte | Petits producteurs, coopératives (45 pays du Sud) | 10 % |
| Préparation, exportation | 4 sociétés intermédiaires | 5 % |
| Importation, torréfaction, distribution | 5 grandes firmes (Nestlé, Kraft…) | 85 % |

*Remarque : cette réponse se trouve dans un tableau, ce qui permettra de vérifier si le pipeline d'ingestion lit correctement les tableaux des PDF.*

## Question 8 – De quelle région le café est-il originaire, et où a ouvert le premier café ?

- **Document :** `data/html/histoire-cafe.html`
- **Emplacement :** section « Moyen Âge », partie « Un essor dans tout le monde arabe, puis en Europe »
- **Réponse attendue :** de Kaffa, en Éthiopie ; le premier café, Kiva Han, a ouvert en 1475 à Constantinople.
- **Passage du document :**
  > « L'usage du café était très ancien en Abyssinie. Il est originaire de Kaffa, royaume de l'Éthiopie médiévale. […] Les arabes vendent leur café en Perse, Égypte, Afrique du Nord et en Turquie, où le premier café, Kiva Han, ouvre en 1475 à Constantinople. »

## Question 9 – Qu'est-ce que le kopi luwak et comment est-il apparu ?

- **Document :** `data/txt/kopi-luwak.txt`
- **Emplacement :** partie « Histoire »
- **Réponse attendue :** un café indonésien fait avec les grains rejetés dans les excréments de la civette ; il est apparu à Java et Sumatra pendant la colonisation néerlandaise.
- **Passage du document :**
  > « Au moment du Cultuurstelsel (1830—1870), ils interdirent aux fermiers indigènes et à leurs employés de cueillir le café pour leur usage personnel. Désireux de goûter néanmoins le fameux breuvage, ceux-ci découvrirent que certaines espèces de musang ou luwak (civette palmiste commune) consommaient les fruits des caféiers et rejetaient les graines dans leurs excréments. Ils consommèrent celles-ci nettoyées, grillées et moulues. »

## Question 10 – Quelle est la différence entre le café vert et le café torréfié ?

- **Document :** `data/html/torrefaction.html`
- **Emplacement :** section « Torréfaction du café », partie « Du grain vert aux teintes blondes, brunes ou noires »
- **Réponse attendue :** le grain vert n'a ni arôme ni saveur ; c'est la torréfaction qui révèle le goût du café.
- **Passage du document :**
  > « Le grain vert n'a aucun arôme ni saveur. Ce sont les Éthiopiens qui, au XIVe siècle, ont découvert fortuitement le processus de torréfaction du café permettant de révéler le goût et l'arôme des grains. »

---

## Bilan de l'audit

- Les réponses ont été trouvées dans **trois formats différents** (HTML, PDF et TXT), ce qui confirme que le corpus est varié et exploitable.
- Les questions couvrent plusieurs types d'informations : **chiffres, dates, lieux, définitions et explications**.
- Certaines réponses demandent de lire un **tableau** (question 7) ou de relier **deux phrases d'un même paragraphe** (question 8), ce qui sera utile pour tester la qualité du découpage du texte (chunking) et de la recherche.

**Problèmes repérés pendant l'audit et corrigés :**
- certains fichiers TXT contenaient le code HTML de la page au lieu du texte : ils ont été refaits ;
- deux fichiers Word ne correspondaient pas au thème (page vide ou mauvais article) : ils ont été remplacés.
