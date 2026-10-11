"""
extraction.py
Lecture des documents du corpus selon leur format (PDF, HTML, DOCX, TXT).

Chaque fonction reçoit le chemin d'un fichier et renvoie un dictionnaire :
    {"texte": str, "titre": str ou None, "nb_pages": int ou None}
Le nettoyage fin du texte est fait ensuite dans nettoyage.py.
"""

import re
from collections import Counter
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup
from docx import Document


# Titres automatiques sans intérêt (métadonnées remplies par les logiciels)
TITRES_GENERIQUES = {"untitled", "sans titre", "document sans titre", "word document",
                     "document", "microsoft word", "titre"}


def titre_valide(titre):
    """Renvoie le titre des métadonnées s'il est utile, sinon None."""
    if not titre or not titre.strip():
        return None
    titre = titre.strip()
    if titre.lower() in TITRES_GENERIQUES or titre.lower().endswith((".doc", ".docx", ".pdf")):
        return None
    return titre


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

def _lignes_repetees(pages, nb_lignes=2, seuil=0.5):
    """Repère les en-têtes et pieds de page : lignes identiques qui reviennent
    en haut ou en bas de plus de la moitié des pages."""
    if len(pages) < 3:
        return set()
    compteur = Counter()
    for lignes in pages:
        bords = lignes[:nb_lignes] + lignes[-nb_lignes:]
        # on remplace les chiffres pour regrouper "Page 3", "Page 4"...
        for ligne in set(re.sub(r"\d+", "#", l.strip()) for l in bords if l.strip()):
            compteur[ligne] += 1
    return {ligne for ligne, n in compteur.items() if n / len(pages) >= seuil}


def lire_pdf(chemin):
    """Extrait le texte d'un PDF page par page en retirant les en-têtes,
    pieds de page et numéros de page isolés."""
    pages = []
    with pdfplumber.open(chemin) as pdf:
        for page in pdf.pages:
            texte = page.extract_text() or ""
            pages.append(texte.splitlines())
        titre = (pdf.metadata or {}).get("Title")

    repetees = _lignes_repetees(pages)
    pages_propres = []
    for lignes in pages:
        gardees = []
        for i, ligne in enumerate(lignes):
            l = ligne.strip()
            en_bord = i < 2 or i >= len(lignes) - 2   # 2 premières ou 2 dernières lignes
            if re.fullmatch(r"[-–—\s]*(page\s*)?\d{1,4}(\s*/\s*\d{1,4})?[-–—\s]*", l, re.I):
                continue  # numéro de page isolé : "12", "- 12 -", "Page 3/10"
            if en_bord and re.sub(r"\d+", "#", l) in repetees:
                continue  # en-tête ou pied de page répété
            gardees.append(ligne)
        pages_propres.append("\n".join(gardees))

    return {
        "texte": "\n\n".join(pages_propres),
        "titre": titre_valide(titre),
        "nb_pages": len(pages),
    }


# ---------------------------------------------------------------------------
# HTML (pages Wikipédia enregistrées)
# ---------------------------------------------------------------------------

# Éléments qui ne font pas partie du contenu principal
SELECTEURS_A_SUPPRIMER = [
    "script", "style", "noscript", "nav", "header", "footer", "form",
    ".mw-editsection",          # liens [modifier | modifier le code]
    "sup.reference",            # appels de notes [1], [2]...
    ".reference",
    ".references", ".reflist", ".mw-references-wrap",
    ".navbox", ".navbox-container", ".metadata", ".noprint",
    ".bandeau-container", ".bandeau-portail", ".homonymie",
    ".infobox", ".infobox_v2", ".infobox_v3",
    ".toc", "#toc", ".mw-jump-link", ".catlinks",
    "figure", ".thumb", ".gallery",
]

# Titres de sections de fin qu'on ne garde pas (bibliographie, liens...)
SECTIONS_DE_FIN = {
    "notes et références", "références", "notes", "voir aussi",
    "bibliographie", "liens externes", "articles connexes", "annexes",
}


def lire_html(chemin):
    """Isole le texte principal d'une page web en retirant menus,
    bandeaux, notes et code superflu."""
    html = Path(chemin).read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "lxml")

    titre = soup.title.get_text(strip=True) if soup.title else None
    if titre:
        titre = re.sub(r"\s*[—-]\s*Wikip[ée]dia\s*$", "", titre)

    # Contenu principal : celui de Wikipédia s'il existe, sinon le <body>
    contenu = (soup.select_one("#mw-content-text .mw-parser-output")
               or soup.select_one("#mw-content-text")
               or soup.find("main") or soup.body or soup)

    for selecteur in SELECTEURS_A_SUPPRIMER:
        for element in contenu.select(selecteur):
            element.decompose()

    # On parcourt les blocs dans l'ordre et on s'arrête aux sections de fin
    blocs = []
    for element in contenu.find_all(["h2", "h3", "h4", "p", "li", "dd", "blockquote", "table"]):
        if element.find_parent(["li", "table", "blockquote"]) is not None:
            continue  # déjà pris en compte par le bloc parent
        texte = re.sub(r"\s+", " ", element.get_text()).strip()
        if not texte:
            continue
        if element.name == "h2" and texte.lower() in SECTIONS_DE_FIN:
            break
        if element.name == "table":
            lignes = [" | ".join(re.sub(r"\s+", " ", c.get_text()).strip() for c in tr.find_all(["th", "td"]))
                      for tr in element.find_all("tr")]
            texte = "\n".join(l for l in lignes if l.strip(" |"))
        elif element.name in ("h2", "h3", "h4"):
            texte = "\n" + texte  # garde la structure en sections
        elif element.name == "li":
            texte = "- " + texte
        blocs.append(texte)

    return {"texte": "\n".join(blocs), "titre": titre, "nb_pages": None}


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------

def lire_docx(chemin):
    """Lit les paragraphes et les tableaux d'un document Word."""
    doc = Document(chemin)
    blocs = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for ligne in table.rows:
            cellules = [c.text.strip() for c in ligne.cells]
            if any(cellules):
                blocs.append(" | ".join(cellules))
    titre = titre_valide(doc.core_properties.title)
    return {"texte": "\n".join(blocs), "titre": titre, "nb_pages": None}


# ---------------------------------------------------------------------------
# TXT
# ---------------------------------------------------------------------------

def lire_txt(chemin):
    """Lit un fichier texte en essayant plusieurs encodages
    (le Bloc-notes peut enregistrer en UTF-8 ou en ANSI/Windows-1252)."""
    donnees = Path(chemin).read_bytes()
    for encodage in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            texte = donnees.decode(encodage)
            break
        except UnicodeDecodeError:
            continue

    # Livres du Projet Gutenberg : on garde seulement le texte du livre
    debut = re.search(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", texte, re.I)
    fin = re.search(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG", texte, re.I)
    if debut:
        texte = texte[debut.end(): fin.start() if fin else None]

    return {"texte": texte, "titre": None, "nb_pages": None}


# ---------------------------------------------------------------------------
# Aiguillage selon l'extension
# ---------------------------------------------------------------------------

LECTEURS = {
    ".pdf": lire_pdf,
    ".html": lire_html,
    ".htm": lire_html,
    ".docx": lire_docx,
    ".txt": lire_txt,
}


def extraire(chemin):
    """Choisit la bonne fonction de lecture selon l'extension du fichier."""
    extension = Path(chemin).suffix.lower()
    if extension not in LECTEURS:
        raise ValueError(f"Format non pris en charge : {extension}")
    return LECTEURS[extension](chemin)
