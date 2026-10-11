"""
chunking.py
Découpage des textes en morceaux (chunks) avec chevauchement.

Principe :
  - on découpe d'abord le texte en phrases, pour ne jamais couper une phrase
    au milieu (le sujet et le verbe restent dans le même morceau) ;
  - on regroupe les phrases jusqu'à atteindre la taille voulue (ex. 500 caractères) ;
  - le morceau suivant reprend la fin du précédent (chevauchement, ex. 100 caractères)
    pour garder la continuité du sens entre deux morceaux.
"""

import re

# Une fin de phrase : . ! ? … suivi d'un espace puis d'une majuscule, d'un chiffre ou d'un guillemet
FIN_DE_PHRASE = re.compile(r"(?<=[.!?…])\s+(?=[A-ZÀ-ÖØ-Ý0-9«\"“(])")


def decouper_en_phrases(texte):
    """Découpe un texte en phrases (les titres et lignes courtes restent à part)."""
    phrases = []
    for paragraphe in texte.split("\n"):
        paragraphe = paragraphe.strip()
        if paragraphe:
            phrases += [p.strip() for p in FIN_DE_PHRASE.split(paragraphe) if p.strip()]
    return phrases


def _couper_phrase_longue(phrase, taille, chevauchement):
    """Coupe une phrase plus longue que la taille maximale, mot par mot."""
    mots = phrase.split()
    morceaux, courant = [], []
    for mot in mots:
        if courant and len(" ".join(courant + [mot])) > taille:
            morceaux.append(" ".join(courant))
            # reprise des derniers mots pour le chevauchement
            reprise = []
            for m in reversed(courant):
                if len(" ".join([m] + reprise)) > chevauchement:
                    break
                reprise.insert(0, m)
            courant = reprise
        courant.append(mot)
    if courant:
        morceaux.append(" ".join(courant))
    return morceaux


def _fin_du_texte(texte, nb_caracteres):
    """Renvoie environ les nb_caracteres derniers caractères, sans couper un mot."""
    if len(texte) <= nb_caracteres:
        return texte
    fin = texte[-nb_caracteres:]
    # si une phrase commence dans cette zone, on reprend à partir du début de cette phrase
    m = re.search(r"[.!?…]\s+(?=[A-ZÀ-ÖØ-Ý0-9«\"“(])", fin)
    if m and len(fin) - m.end() >= nb_caracteres * 0.3:
        return fin[m.end():]
    espace = fin.find(" ")
    return fin[espace + 1:] if espace != -1 else fin


def decouper(texte, taille=500, chevauchement=100, taille_min=30):
    """Découpe un texte en morceaux d'environ `taille` caractères,
    avec `chevauchement` caractères repris d'un morceau à l'autre."""
    if chevauchement >= taille:
        raise ValueError("Le chevauchement doit être plus petit que la taille des morceaux.")

    morceaux = []
    courant = ""

    for phrase in decouper_en_phrases(texte):
        # cas rare : une seule phrase dépasse la taille maximale
        if len(phrase) > taille:
            if courant:
                morceaux.append(courant)
            parties = _couper_phrase_longue(phrase, taille, chevauchement)
            morceaux += parties[:-1]
            courant = parties[-1]
            continue

        if courant and len(courant) + 1 + len(phrase) > taille:
            morceaux.append(courant)
            # le nouveau morceau commence par la fin du précédent
            courant = _fin_du_texte(courant, chevauchement) if chevauchement else ""

        courant = f"{courant} {phrase}".strip()

    if courant:
        morceaux.append(courant)

    return [m for m in morceaux if len(m) >= taille_min]


if __name__ == "__main__":
    # Petit exemple pour voir le fonctionnement
    exemple = (
        "Le caféier est originaire d'Éthiopie. Sa culture se répand ensuite au Yémen. "
        "Le café est exporté par le port de Moka. Les Arabes vendent leur café en Perse, "
        "en Égypte et en Turquie, où le premier café ouvre en 1475 à Constantinople. "
        "La consommation prend alors son essor dans tout le monde arabe."
    )
    for i, m in enumerate(decouper(exemple, taille=150, chevauchement=40), 1):
        print(f"Morceau {i} ({len(m)} caractères) : {m}\n")
