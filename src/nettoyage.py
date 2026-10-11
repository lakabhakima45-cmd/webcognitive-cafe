"""
nettoyage.py
Nettoyage et normalisation du texte extrait, avec des expressions régulières.

Étapes :
  1. correction des problèmes d'encodage (ex. "cafÃ©" -> "café")
  2. suppression des restes d'interface Wikipédia (menus, [modifier], notes [1])
  3. fusion des mots coupés en fin de ligne ("torré-\nfaction" -> "torréfaction")
  4. fusion des sauts de ligne au milieu des phrases (paragraphes propres)
  5. suppression des espaces multiples et des lignes vides en trop
"""

import re
import unicodedata


# ---------------------------------------------------------------------------
# 1. Encodage
# ---------------------------------------------------------------------------

MARQUEURS_MOJIBAKE = ("Ã©", "Ã¨", "Ã ", "Ãª", "Ã§", "Ã´", "â€™", "â€œ", "Â ")


def corriger_encodage(texte):
    """Corrige un texte UTF-8 mal décodé (accents remplacés par 'Ã©', 'â€™'...)."""
    if any(m in texte for m in MARQUEURS_MOJIBAKE):
        for encodage in ("cp1252", "latin-1"):
            try:
                return texte.encode(encodage).decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
    return texte


def normaliser_caracteres(texte):
    """Uniformise les caractères : forme Unicode NFC, espaces insécables,
    caractères invisibles, fins de ligne Windows."""
    texte = unicodedata.normalize("NFC", texte)
    texte = texte.replace("\r\n", "\n").replace("\r", "\n")
    texte = re.sub(r"[   \t]", " ", texte)          # espaces spéciaux
    texte = re.sub(r"[​‎‏﻿­]", "", texte)  # invisibles
    texte = texte.replace("\x0c", "\n")                              # saut de page
    return texte


# ---------------------------------------------------------------------------
# 2. Restes d'interface (pages copiées depuis Wikipédia)
# ---------------------------------------------------------------------------

LIGNES_INTERFACE = {
    "aller au contenu", "rechercher", "faire un don", "créer un compte", "se connecter", "sommaire",
    "masquer", "afficher", "début", "article", "discussion", "lire", "modifier",
    "modifier le code", "voir l’historique", "voir l'historique", "outils",
    "apparence", "taille du texte", "petite", "standard", "grande", "largeur",
    "large", "couleur (bêta)", "automatique", "clair", "sombre", "sommaire masquer",
    "apparence masquer", "aidez-nous à traduire !", "pages pour les contributeurs déconnectés",
    "en savoir plus", "contributions", "basculer la table des matières",
    "ajouter des liens", "ajouter un sujet", "imprimer / exporter",
    "télécharger comme pdf", "version imprimable", "dans d’autres projets",
    "élément wikidata", "menu principal", "navigation", "contribuer", "accueil",
    "portails thématiques", "article au hasard", "contact", "aide",
    "communauté", "modifications récentes", "pages liées", "suivi des pages liées",
    "téléverser un fichier", "pages spéciales", "lien permanent",
    "informations sur la page", "citer cette page", "obtenir l'url raccourcie",
}

# Pied de page Wikipédia : tout ce qui suit est supprimé
DEBUT_PIED_DE_PAGE = re.compile(
    r"^(La dernière modification de cette page a été faite|Politique de confidentialité)",
    re.M,
)

SECTIONS_DE_FIN = re.compile(
    r"^(Notes et références|Références|Notes|Voir aussi|Bibliographie|"
    r"Liens externes|Articles connexes|Annexes)\s*(\[.*\])?\s*$",
    re.M | re.I,
)


def retirer_interface(texte):
    """Supprime les menus, liens [modifier], appels de notes et bas de page."""
    # bas de page
    m = DEBUT_PIED_DE_PAGE.search(texte)
    if m:
        texte = texte[: m.start()]

    # sections de fin (références, liens...) si elles sont dans la 2e moitié
    for m in SECTIONS_DE_FIN.finditer(texte):
        if m.start() > len(texte) * 0.4:
            texte = texte[: m.start()]
            break

    texte = re.sub(r"\[\s*modifier\s*(\|\s*modifier le code\s*)?\]", "", texte, flags=re.I)
    texte = re.sub(r"\[\s*(\d{1,3}|[a-z]|réf\.? nécessaire|Note \d+)\s*\]", "", texte, flags=re.I)
    texte = re.sub(r'HYPERLINK\s+"[^"]*"', "", texte)

    # Pages copiées-collées : le menu est en haut. On coupe tout ce qui précède
    # la dernière ligne de menu trouvée dans le haut du texte.
    toutes = texte.split("\n")
    limite = max(len(toutes) // 3, 60)
    derniere = max((i for i, l in enumerate(toutes[:limite])
                    if l.strip().lower() in LIGNES_INTERFACE), default=-1)
    if derniere >= 0:
        toutes = toutes[derniere + 1:]

    lignes = []
    for ligne in toutes:
        l = ligne.strip()
        if l.lower() in LIGNES_INTERFACE:
            continue
        if re.fullmatch(r"(Afficher / masquer la sous-section.*|\d+ langues?)", l):
            continue
        lignes.append(ligne)
    return "\n".join(lignes)


# ---------------------------------------------------------------------------
# 3-5. Mise en forme des paragraphes
# ---------------------------------------------------------------------------

FIN_DE_PHRASE = re.compile(r"[.!?:;»\"”)]$")
DEBUT_DE_LISTE = re.compile(r"^\s*([-•*–]|\d+[.)])\s+")


def reconstituer_paragraphes(texte):
    """Fusionne les lignes coupées au milieu d'une phrase."""
    # mot coupé par un tiret en fin de ligne : "torré-\nfaction"
    texte = re.sub(r"(\w)-\n(\w)", r"\1\2", texte)

    lignes = texte.split("\n")
    resultat = []
    for ligne in lignes:
        ligne = ligne.strip()
        if not ligne:
            resultat.append("")
            continue
        precedente = resultat[-1] if resultat else ""
        if (precedente
                and not FIN_DE_PHRASE.search(precedente)
                and not DEBUT_DE_LISTE.match(ligne)
                and re.match(r"[a-zàâçéèêëîïôûùüÿœ0-9(«,]", ligne)):
            resultat[-1] = precedente + " " + ligne   # même phrase : on recolle
        else:
            resultat.append(ligne)
    return "\n".join(resultat)


def compacter_espaces(texte):
    """Supprime les espaces multiples, les espaces avant la ponctuation simple
    et limite les lignes vides à une seule."""
    texte = re.sub(r"[ ]{2,}", " ", texte)
    texte = re.sub(r" +([,.])", r"\1", texte)
    texte = re.sub(r"\( +", "(", texte)
    texte = re.sub(r" +\)", ")", texte)
    texte = re.sub(r"^[ \W_]{1,3}$", "", texte, flags=re.M)  # lignes de symboles seuls
    texte = re.sub(r"\n{3,}", "\n\n", texte)
    return texte.strip()


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def nettoyer(texte):
    """Applique toutes les étapes de nettoyage dans l'ordre."""
    texte = corriger_encodage(texte)
    texte = normaliser_caracteres(texte)
    texte = retirer_interface(texte)
    texte = reconstituer_paragraphes(texte)
    texte = compacter_espaces(texte)
    return texte


# ---------------------------------------------------------------------------
# Détection simple de la langue (français / anglais)
# ---------------------------------------------------------------------------

MOTS_FR = {"le", "la", "les", "des", "est", "et", "une", "du", "dans", "que", "pour", "qui", "sur"}
MOTS_EN = {"the", "and", "of", "is", "in", "to", "that", "for", "with", "was", "on", "as", "by"}


def detecter_langue(texte):
    """Compte les mots outils les plus courants de chaque langue."""
    mots = re.findall(r"[a-zàâçéèêëîïôûùüÿœ]+", texte.lower()[:20000])
    fr = sum(m in MOTS_FR for m in mots)
    en = sum(m in MOTS_EN for m in mots)
    if fr == en == 0:
        return "inconnue"
    return "fr" if fr >= en else "en"
