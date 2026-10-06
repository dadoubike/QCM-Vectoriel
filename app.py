import os

if os.path.exists("/etc/secrets/secrets.toml"):
    os.environ["STREAMLIT_SECRETS_FILE"] = "/etc/secrets/secrets.toml"

import datetime
import random
import time
import zoneinfo
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Correction des sauts de ligne pour la clé privée
if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
    if "private_key" in st.secrets["connections"]["gsheets"]:
        st.secrets["connections"]["gsheets"]["private_key"] = st.secrets["connections"]["gsheets"]["private_key"].replace("\\n", "\n")

conn = st.connection("gsheets", type=GSheetsConnection)


# Configuration de la page
st.set_page_config(page_title="QCM - Produits Vectoriels", page_icon="📐")

# --- EN-TÊTE AVEC LOGO ET AUTEUR (Unique) ---
col_logo, col_titre = st.columns([1, 4])

with col_logo:
    try:
        st.image("Logo-Saliege-Campus-HD-Transp-rouge.png", width=160)
    except Exception:
        pass

with col_titre:
    st.title("📐 QCM : Produits Vectoriels Progressifs")
    st.caption("✍️ conçu par **D. Peyrou**")

# CSS pour compacter les marges et optimiser l'affichage mobile
st.markdown(
    """
    <style>
    div[data-testid="stRadio"] > label {
        font-size: 0.85rem !important;
        font-weight: bold !important;
    }
    div[data-testid="stRadio"] > div {
        gap: 0.4rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

URL_GSHEET = "https://docs.google.com/spreadsheets/d/1HAsgs2g1zYVH7bxl_37MNU24nmEHMgcZVuQ2rRfIev8/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)



# Durée maximale du test (5 minutes = 300 secondes)
DUREE_MAX_SECONDES = 300

# Équivalences géométriques des axes
EQUIVALENCES_VECTEURS = {
    ("z", "0"): [("z", "0"), ("z", "1")],
    ("z", "1"): [("z", "0"), ("z", "1")],
    ("y", "1"): [("y", "1"), ("y", "2")],
    ("y", "2"): [("y", "1"), ("y", "2")],
    ("x", "2"): [("x", "2"), ("x", "3")],
    ("x", "3"): [("x", "2"), ("x", "3")],
}


def verifier_vecteur_egal(vec_user, ind_user, vec_sol, ind_sol):
    """Vérifie si la combinaison vecteur/indice choisie est identique ou géométriquement équivalente."""
    if vec_user == vec_sol and ind_user == ind_sol:
        return True
    equivalents = EQUIVALENCES_VECTEURS.get((vec_sol, ind_sol), [])
    return (vec_user, ind_user) in equivalents


def verifier_reponse_colonnes(reponse_eleve, solution_qcm):
    """
    Vérifie les choix de l'élève par rapport au dictionnaire solution.
    - Si trigo == "1", l'angle est ignoré (toujours valide).
    - Sinon, l'angle doit correspondre exactement à la solution.
    """
    signe_ok = reponse_eleve.get("signe") == solution_qcm.get("signe")
    trigo_ok = reponse_eleve.get("trigo") == solution_qcm.get("trigo")

    vecteur_ok = verifier_vecteur_egal(
        reponse_eleve.get("vecteur"),
        reponse_eleve.get("indice"),
        solution_qcm.get("vecteur"),
        solution_qcm.get("indice"),
    )

    if reponse_eleve.get("trigo") == "1":
        angle_ok = True
    else:
        angle_ok = reponse_eleve.get("angle") == solution_qcm.get("angle")

    return signe_ok and trigo_ok and vecteur_ok and angle_ok


# --- BANQUE DE QUESTIONS ---
BANQUE_QUESTIONS = {
    "A": [
        {
            "type": "colonnes",
            "enonce": r"\vec{x}_0 \wedge \vec{x}_1",
            "solution": {
                "signe": "+",
                "trigo": "sin",
                "angle": "α",
                "vecteur": "z",
                "indice": "0",
            },
            "description": "Niveau A (1/4) : Base 0 et 1",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{x}_1 \wedge \vec{x}_0",
            "solution": {
                "signe": "-",
                "trigo": "sin",
                "angle": "α",
                "vecteur": "z",
                "indice": "0",
            },
            "description": "Niveau A (1/4) : Base 0 et 1",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{y}_0 \wedge \vec{y}_1",
            "solution": {
                "signe": "+",
                "trigo": "sin",
                "angle": "α",
                "vecteur": "z",
                "indice": "0",
            },
            "description": "Niveau A (1/4) : Base 0 et 1",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{y}_1 \wedge \vec{y}_0",
            "solution": {
                "signe": "-",
                "trigo": "sin",
                "angle": "α",
                "vecteur": "z",
                "indice": "0",
            },
            "description": "Niveau A (1/4) : Base 0 et 1",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{x}_1 \wedge \vec{z}_0",
            "solution": {
                "signe": "-",
                "trigo": "1",
                "angle": "θ",
                "vecteur": "y",
                "indice": "1",
            },
            "description": "Niveau A (1/4) : Base 1 et 2",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{z}_1 \wedge \vec{z}_2",
            "solution": {
                "signe": "+",
                "trigo": "sin",
                "angle": "θ",
                "vecteur": "y",
                "indice": "1",
            },
            "description": "Niveau A (1/4) : Base 1 et 2",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{z}_2 \wedge \vec{z}_1",
            "solution": {
                "signe": "-",
                "trigo": "sin",
                "angle": "θ",
                "vecteur": "y",
                "indice": "1",
            },
            "description": "Niveau A (1/4) : Base 1 et 2",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{x}_1 \wedge \vec{x}_2",
            "solution": {
                "signe": "+",
                "trigo": "sin",
                "angle": "θ",
                "vecteur": "y",
                "indice": "1",
            },
            "description": "Niveau A (1/4) : Base 1 et 2",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{x}_2 \wedge \vec{x}_1",
            "solution": {
                "signe": "-",
                "trigo": "sin",
                "angle": "θ",
                "vecteur": "y",
                "indice": "1",
            },
            "description": "Niveau A (1/4) : Base 1 et 2",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{y}_1 \wedge \vec{x}_2",
            "solution": {
                "signe": "-",
                "trigo": "1",
                "angle": "θ",
                "vecteur": "z",
                "indice": "2",
            },
            "description": "Niveau A (1/4) : Base 1 et 2",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{y}_2 \wedge \vec{y}_3",
            "solution": {
                "signe": "+",
                "trigo": "sin",
                "angle": "β",
                "vecteur": "x",
                "indice": "2",
            },
            "description": "Niveau A (1/4) : Base 2 et 3",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{y}_3 \wedge \vec{y}_2",
            "solution": {
                "signe": "-",
                "trigo": "sin",
                "angle": "β",
                "vecteur": "x",
                "indice": "2",
            },
            "description": "Niveau A (1/4) : Base 2 et 3",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{z}_2 \wedge \vec{z}_3",
            "solution": {
                "signe": "+",
                "trigo": "sin",
                "angle": "β",
                "vecteur": "x",
                "indice": "2",
            },
            "description": "Niveau A (1/4) : Base 2 et 3",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{z}_3 \wedge \vec{z}_2",
            "solution": {
                "signe": "-",
                "trigo": "sin",
                "angle": "β",
                "vecteur": "x",
                "indice": "2",
            },
            "description": "Niveau A (1/4) : Base 2 et 3",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{y}_3 \wedge \vec{x}_2",
            "solution": {
                "signe": "-",
                "trigo": "1",
                "angle": "β",
                "vecteur": "z",
                "indice": "3",
            },
            "description": "Niveau A (1/4) : Base 2 et 3",
        },
    ],
    "B": [
        {
            "type": "colonnes",
            "enonce": r"\vec{x}_1 \wedge \vec{y}_0",
            "solution": {
                "signe": "+",
                "trigo": "cos",
                "angle": "α",
                "vecteur": "z",
                "indice": "0",
            },
            "description": "Niveau B (2/4) : Figure 0 et 1",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{x}_0 \wedge \vec{y}_1",
            "solution": {
                "signe": "+",
                "trigo": "cos",
                "angle": "α",
                "vecteur": "z",
                "indice": "0",
            },
            "description": "Niveau B (2/4) : Figure 0 et 1",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{y}_0 \wedge \vec{x}_1",
            "solution": {
                "signe": "-",
                "trigo": "cos",
                "angle": "α",
                "vecteur": "z",
                "indice": "0",
            },
            "description": "Niveau B (2/4) : Figure 0 et 1",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{y}_1 \wedge \vec{x}_0",
            "solution": {
                "signe": "+",
                "trigo": "cos",
                "angle": "α",
                "vecteur": "z",
                "indice": "0",
            },
            "description": "Niveau B (2/4) : Figure 0 et 1",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{z}_2 \wedge \vec{x}_1",
            "solution": {
                "signe": "+",
                "trigo": "cos",
                "angle": "θ",
                "vecteur": "y",
                "indice": "1",
            },
            "description": "Niveau B (2/4) : Base 2 et 1",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{z}_1 \wedge \vec{x}_2",
            "solution": {
                "signe": "+",
                "trigo": "cos",
                "angle": "θ",
                "vecteur": "y",
                "indice": "1",
            },
            "description": "Niveau B (2/4) : Base 1 et 2",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{x}_1 \wedge \vec{z}_2",
            "solution": {
                "signe": "-",
                "trigo": "cos",
                "angle": "θ",
                "vecteur": "y",
                "indice": "1",
            },
            "description": "Niveau B (2/4) : Base 1 et 2",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{x}_2 \wedge \vec{z}_1",
            "solution": {
                "signe": "-",
                "trigo": "cos",
                "angle": "θ",
                "vecteur": "y",
                "indice": "1",
            },
            "description": "Niveau B (2/4) : Base 2 et 1",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{y}_3 \wedge \vec{z}_2",
            "solution": {
                "signe": "+",
                "trigo": "cos",
                "angle": "β",
                "vecteur": "x",
                "indice": "2",
            },
            "description": "Niveau B (2/4) : Base 3 et 2",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{y}_2 \wedge \vec{z}_3",
            "solution": {
                "signe": "+",
                "trigo": "cos",
                "angle": "β",
                "vecteur": "x",
                "indice": "2",
            },
            "description": "Niveau B (2/4) : Base 2 et 3",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{z}_2 \wedge \vec{y}_3",
            "solution": {
                "signe": "-",
                "trigo": "cos",
                "angle": "β",
                "vecteur": "x",
                "indice": "2",
            },
            "description": "Niveau B (2/4) : Base 2 et 3",
        },
        {
            "type": "colonnes",
            "enonce": r"\vec{z}_3 \wedge \vec{y}_2",
            "solution": {
                "signe": "-",
                "trigo": "cos",
                "angle": "β",
                "vecteur": "x",
                "indice": "2",
            },
            "description": "Niveau B (2/4) : Base 3 et 2",
        },
    ],
    "C": [
        {
            "type": "qcm",
            "enonce": r"\vec{y}_3 \wedge \vec{z}_1",
            "propositions": [
                r"+\cos(\beta)\vec{x}_1 - \sin(\beta)\sin(\theta)\vec{y}_1",
                r"+\cos(\beta)\vec{x}_1 + \sin(\beta)\cos(\theta)\vec{y}_1",
                r"-\cos(\beta)\vec{x}_1 - \sin(\beta)\sin(\theta)\vec{y}_1",
                r"+\sin(\beta)\vec{x}_1",
            ],
            "correct_expressions": [
                r"+\cos(\beta)\vec{x}_1 - \sin(\beta)\sin(\theta)\vec{y}_1"
            ],
            "description": "Niveau C (3/4) : Fig 3 vers Fig 1",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{z}_3 \wedge \vec{z}_1",
            "propositions": [
                r"+\sin(\beta)\vec{x}_1 - \sin(\beta)\sin(\theta)\vec{y}_1",
                r"-\sin(\beta)\vec{x}_1 - \sin(\theta)\cos(\beta)\vec{y}_1",
                r"-\cos(\beta)\vec{x}_1 - \sin(\beta)\sin(\theta)\vec{y}_1",
                r"+\sin(\beta)\vec{x}_1",
            ],
            "correct_expressions": [
                r"-\sin(\beta)\vec{x}_1 - \sin(\theta)\cos(\beta)\vec{y}_1"
            ],
            "description": "Niveau C (3/4) : Fig 3 vers Fig 1",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{z}_1 \wedge \vec{y}_3",
            "propositions": [
                r"-\cos(\beta)\vec{x}_1 + \sin(\beta)\sin(\theta)\vec{y}_1",
                r"-\cos(\beta)\vec{x}_1 - \sin(\beta)\cos(\theta)\vec{y}_1",
                r"+\cos(\beta)\vec{x}_1 + \sin(\beta)\sin(\theta)\vec{y}_1",
                r"-\sin(\beta)\vec{x}_1",
            ],
            "correct_expressions": [
                r"-\cos(\beta)\vec{x}_1 + \sin(\beta)\sin(\theta)\vec{y}_1"
            ],
            "description": "Niveau C (3/4) : Fig 1 vers Fig 3",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{z}_1 \wedge \vec{z}_3",
            "propositions": [
                r"-\sin(\beta)\vec{x}_1 + \sin(\beta)\sin(\theta)\vec{y}_1",
                r"+\sin(\beta)\vec{x}_1 + \sin(\theta)\cos(\beta)\vec{y}_1",
                r"+\cos(\beta)\vec{x}_1 + \sin(\beta)\sin(\theta)\vec{y}_1",
                r"-\sin(\beta)\vec{x}_1",
            ],
            "correct_expressions": [
                r"+\sin(\beta)\vec{x}_1 + \sin(\theta)\cos(\beta)\vec{y}_1"
            ],
            "description": "Niveau C (3/4) : Fig 1 vers Fig 3",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{y}_3 \wedge \vec{x}_1",
            "propositions": [
                r"+\sin(\beta)\cos(\theta)\vec{y}_1 - \cos(\beta)\vec{z}_1",
                r"-\sin(\beta)\sin(\theta)\vec{x}_1 + \cos(\beta)\vec{z}_1",
                r"+\cos(\beta)\cos(\theta)\vec{y}_1 - \sin(\beta)\vec{z}_1",
                r"+\sin(\beta)\vec{y}_1",
            ],
            "correct_expressions": [
                r"+\sin(\beta)\cos(\theta)\vec{y}_1 - \cos(\beta)\vec{z}_1"
            ],
            "description": "Niveau C (3/4) : Fig 3 vers Fig 1",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{z}_3 \wedge \vec{x}_1",
            "propositions": [
                r"+\sin(\beta)\vec{x}_1 - \sin(\beta)\sin(\theta)\vec{y}_1",
                r"+\cos(\theta)\cos(\beta)\vec{y}_1 + \sin(\beta)\vec{z}_1",
                r"-\cos(\beta)\cos(\theta)\vec{y}_2 - \cos(\beta)\vec{z}_2",
                r"+\cos(\beta)\vec{x}_2",
            ],
            "correct_expressions": [
                r"+\cos(\theta)\cos(\beta)\vec{y}_1 + \sin(\beta)\vec{z}_1"
            ],
            "description": "Niveau C (3/4) : Fig 3 vers Fig 1",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{x}_1 \wedge \vec{y}_3",
            "propositions": [
                r"-\sin(\beta)\cos(\theta)\vec{y}_1 + \cos(\beta)\vec{z}_1",
                r"-\cos(\beta)\vec{y}_1 + \sin(\beta)\cos(\theta)\vec{y}_2",
                r"+\sin(\beta)\sin(\theta)\vec{y}_1 + \cos(\beta)\vec{z}_1",
                r"+\cos(\beta)\vec{z}_1",
            ],
            "correct_expressions": [
                r"-\sin(\beta)\cos(\theta)\vec{y}_1 + \cos(\beta)\vec{z}_1"
            ],
            "description": "Niveau C (3/4) : Fig 1 vers Fig 3",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{x}_1 \wedge \vec{z}_3",
            "propositions": [
                r"-\sin(\beta)\vec{x}_1 + \sin(\beta)\sin(\theta)\vec{y}_1",
                r"-\cos(\theta)\cos(\beta)\vec{y}_1 - \sin(\beta)\vec{z}_1",
                r"+\cos(\beta)\cos(\theta)\vec{y}_2 + \cos(\beta)\vec{z}_2",
                r"-\cos(\beta)\vec{x}_2",
            ],
            "correct_expressions": [
                r"-\cos(\theta)\cos(\beta)\vec{y}_1 - \sin(\beta)\vec{z}_1"
            ],
            "description": "Niveau C (3/4) : Fig 1 vers Fig 3",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{z}_2 \wedge \vec{x}_0",
            "propositions": [
                r"+\cos(\theta)\sin(\alpha)\vec{x}_1 + \cos(\theta)\cos(\alpha)\vec{y}_1 - \sin(\theta)\sin(\alpha)\vec{z}_1",
                r"+\cos(\theta)\vec{y}_0 - \sin(\theta)\sin(\alpha)\vec{z}_0",
                r"+\cos(\theta)\vec{y}_1 - \sin(\theta)\sin(\alpha)\vec{z}_1",
                r"+\cos(\theta)\sin(\alpha)\vec{z}_1",
            ],
            "correct_expressions": [
                r"+\cos(\theta)\sin(\alpha)\vec{x}_1 + \cos(\theta)\cos(\alpha)\vec{y}_1 - \sin(\theta)\sin(\alpha)\vec{z}_1",
                r"+\cos(\theta)\vec{y}_0 - \sin(\theta)\sin(\alpha)\vec{z}_0",
            ],
            "description": "Niveau C (3/4) : Fig 2 vers Fig 0",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{x}_0 \wedge \vec{z}_2",
            "propositions": [
                r"-\cos(\theta)\sin(\alpha)\vec{x}_1 - \cos(\theta)\cos(\alpha)\vec{y}_1 + \sin(\theta)\sin(\alpha)\vec{z}_1",
                r"-\cos(\theta)\vec{y}_0 + \sin(\theta)\sin(\alpha)\vec{z}_0",
                r"-\cos(\theta)\vec{y}_1 + \sin(\theta)\sin(\alpha)\vec{z}_1",
                r"-\cos(\theta)\sin(\alpha)\vec{z}_1",
            ],
            "correct_expressions": [
                r"-\cos(\theta)\sin(\alpha)\vec{x}_1 - \cos(\theta)\cos(\alpha)\vec{y}_1 + \sin(\theta)\sin(\alpha)\vec{z}_1",
                r"-\cos(\theta)\vec{y}_0 + \sin(\theta)\sin(\alpha)\vec{z}_0",
            ],
            "description": "Niveau C (3/4) : Fig 0 vers Fig 2",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{z}_2 \wedge \vec{y}_0",
            "propositions": [
                r"-\cos(\theta)\cos(\alpha)\vec{x}_1 + \cos(\theta)\sin(\alpha)\vec{y}_1 + \sin(\theta)\cos(\alpha)\vec{z}_1",
                r"-\cos(\theta)\vec{x}_0 + \sin(\theta)\cos(\alpha)\vec{z}_0",
                r"-\cos(\theta)\vec{x}_1 + \sin(\theta)\cos(\alpha)\vec{z}_1",
                r"+\sin(\theta)\cos(\alpha)\vec{z}_1",
            ],
            "correct_expressions": [
                r"-\cos(\theta)\cos(\alpha)\vec{x}_1 + \cos(\theta)\sin(\alpha)\vec{y}_1 + \sin(\theta)\cos(\alpha)\vec{z}_1",
                r"-\cos(\theta)\vec{x}_0 + \sin(\theta)\cos(\alpha)\vec{z}_0",
            ],
            "description": "Niveau C (3/4) : Fig 2 vers Fig 0",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{y}_0 \wedge \vec{z}_2",
            "propositions": [
                r"+\cos(\theta)\cos(\alpha)\vec{x}_1 - \cos(\theta)\sin(\alpha)\vec{y}_1 - \sin(\theta)\cos(\alpha)\vec{z}_1",
                r"+\cos(\theta)\vec{x}_0 - \sin(\theta)\cos(\alpha)\vec{z}_0",
                r"+\cos(\theta)\vec{x}_1 - \sin(\theta)\cos(\alpha)\vec{z}_1",
                r"-\sin(\theta)\cos(\alpha)\vec{z}_1",
            ],
            "correct_expressions": [
                r"+\cos(\theta)\cos(\alpha)\vec{x}_1 - \cos(\theta)\sin(\alpha)\vec{y}_1 - \sin(\theta)\cos(\alpha)\vec{z}_1",
                r"+\cos(\theta)\vec{x}_0 - \sin(\theta)\cos(\alpha)\vec{z}_0",
            ],
            "description": "Niveau C (3/4) : Fig 0 vers Fig 2",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{x}_2 \wedge \vec{x}_0",
            "propositions": [
                r"-\sin(\theta)\sin(\alpha)\vec{x}_1 - \sin(\theta)\cos(\alpha)\vec{y}_1 - \cos(\theta)\sin(\alpha)\vec{z}_1",
                r"-\sin(\theta)\vec{y}_0 - \cos(\theta)\sin(\alpha)\vec{z}_0",
                r"+\sin(\theta)\vec{y}_1 + \cos(\theta)\sin(\alpha)\vec{z}_1",
                r"+\sin(\theta)\sin(\alpha)\vec{x}_1 - \sin(\theta)\cos(\alpha)\vec{y}_1 - \cos(\theta)\sin(\alpha)\vec{z}_1",
            ],
            "correct_expressions": [
                r"-\sin(\theta)\sin(\alpha)\vec{x}_1 - \sin(\theta)\cos(\alpha)\vec{y}_1 - \cos(\theta)\sin(\alpha)\vec{z}_1",
                r"-\sin(\theta)\vec{y}_0 - \cos(\theta)\sin(\alpha)\vec{z}_0",
            ],
            "description": "Niveau C (3/4) : Fig 2 vers Fig 0",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{x}_0 \wedge \vec{x}_2",
            "propositions": [
                r"+\sin(\theta)\sin(\alpha)\vec{x}_1 + \sin(\theta)\cos(\alpha)\vec{y}_1 + \cos(\theta)\sin(\alpha)\vec{z}_1",
                r"+\sin(\theta)\vec{y}_0 + \cos(\theta)\sin(\alpha)\vec{z}_0",
                r"-\sin(\theta)\vec{y}_1 - \cos(\theta)\sin(\alpha)\vec{z}_1",
                r"-\sin(\theta)\sin(\alpha)\vec{x}_1 + \sin(\theta)\cos(\alpha)\vec{y}_1 + \cos(\theta)\sin(\alpha)\vec{z}_1",
            ],
            "correct_expressions": [
                r"+\sin(\theta)\sin(\alpha)\vec{x}_1 + \sin(\theta)\cos(\alpha)\vec{y}_1 + \cos(\theta)\sin(\alpha)\vec{z}_0",
                r"+\sin(\theta)\vec{y}_0 + \cos(\theta)\sin(\alpha)\vec{z}_0",
            ],
            "description": "Niveau C (3/4) : Fig 0 vers Fig 2",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{x}_2 \wedge \vec{y}_0",
            "propositions": [
                r"+\sin(\theta)\cos(\alpha)\vec{x}_1 - \sin(\theta)\sin(\alpha)\vec{y}_1 + \cos(\theta)\cos(\alpha)\vec{z}_1",
                r"+\sin(\theta)\vec{x}_0 + \cos(\theta)\cos(\alpha)\vec{z}_0",
                r"-\sin(\theta)\vec{x}_0 + \cos(\theta)\cos(\alpha)\vec{z}_0",
                r"-\cos(\theta)\cos(\alpha)\vec{z}_0",
            ],
            "correct_expressions": [
                r"+\sin(\theta)\cos(\alpha)\vec{x}_1 - \sin(\theta)\sin(\alpha)\vec{y}_1 + \cos(\theta)\cos(\alpha)\vec{z}_1",
                r"+\sin(\theta)\vec{x}_0 + \cos(\theta)\cos(\alpha)\vec{z}_0",
            ],
            "description": "Niveau C (3/4) : Fig 2 vers Fig 0",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{y}_0 \wedge \vec{x}_2",
            "propositions": [
                r"-\sin(\theta)\cos(\alpha)\vec{x}_1 + \sin(\theta)\sin(\alpha)\vec{y}_1 - \cos(\theta)\cos(\alpha)\vec{z}_1",
                r"-\sin(\theta)\vec{x}_0 - \cos(\theta)\cos(\alpha)\vec{z}_0",
                r"+\sin(\theta)\vec{x}_0 - \cos(\theta)\cos(\alpha)\vec{z}_0",
                r"+\cos(\theta)\cos(\alpha)\vec{z}_0",
            ],
            "correct_expressions": [
                r"-\sin(\theta)\cos(\alpha)\vec{x}_1 + \sin(\theta)\sin(\alpha)\vec{y}_1 - \cos(\theta)\cos(\alpha)\vec{z}_1",
                r"-\sin(\theta)\vec{x}_0 - \cos(\theta)\cos(\alpha)\vec{z}_0",
            ],
            "description": "Niveau C (3/4) : Fig 0 vers Fig 2",
        },
    ],
    "D": [
        {
            "type": "qcm",
            "enonce": r"\vec{y}_3 \wedge \vec{x}_1",
            "propositions": [
                r"-\cos(\beta)\vec{z}_1 + \sin(\beta)\cos(\theta)\vec{y}_1",
                r"+\cos(\beta)\vec{z}_1 - \sin(\beta)\sin(\theta)\vec{x}_1",
                r"-\sin(\beta)\vec{z}_1 + \cos(\beta)\cos(\theta)\vec{y}_1",
                r"+\sin(\beta)\vec{y}_1",
            ],
            "correct_expressions": [
                r"-\cos(\beta)\vec{z}_1 + \sin(\beta)\cos(\theta)\vec{y}_1"
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 3 / Fig 1)",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{x}_1 \wedge \vec{y}_3",
            "propositions": [
                r"+\cos(\beta)\vec{z}_1 - \sin(\beta)\cos(\theta)\vec{y}_1",
                r"-\cos(\beta)\vec{z}_1 + \sin(\beta)\sin(\theta)\vec{x}_1",
                r"+\sin(\beta)\vec{z}_1 - \cos(\beta)\cos(\theta)\vec{y}_1",
                r"-\sin(\beta)\vec{y}_1",
            ],
            "correct_expressions": [
                r"+\cos(\beta)\vec{z}_1 - \sin(\beta)\cos(\theta)\vec{y}_1"
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 1 / Fig 3)",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{y}_3 \wedge \vec{y}_1",
            "propositions": [
                r"-\sin(\beta)\cos(\theta)\vec{x}_1 + \sin(\beta)\sin(\theta)\vec{z}_1",
                r"+\sin(\beta)\cos(\theta)\vec{x}_1 - \sin(\beta)\sin(\theta)\vec{z}_1",
                r"-\cos(\beta)\cos(\theta)\vec{x}_1 + \sin(\beta)\sin(\theta)\vec{z}_1",
                r"-\sin(\beta)\vec{x}_2",
            ],
            "correct_expressions": [
                r"-\sin(\beta)\cos(\theta)\vec{x}_1 + \sin(\beta)\sin(\theta)\vec{z}_1",
                r"-\sin(\beta)\vec{x}_2",
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 3 / Fig 1)",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{y}_1 \wedge \vec{y}_3",
            "propositions": [
                r"+\sin(\beta)\cos(\theta)\vec{x}_1 - \sin(\beta)\sin(\theta)\vec{z}_1",
                r"-\sin(\beta)\cos(\theta)\vec{x}_1 + \sin(\beta)\sin(\theta)\vec{z}_1",
                r"+\cos(\beta)\cos(\theta)\vec{x}_1 - \sin(\beta)\sin(\theta)\vec{z}_1",
                r"+\sin(\beta)\vec{x}_2",
            ],
            "correct_expressions": [
                r"+\sin(\beta)\cos(\theta)\vec{x}_1 - \sin(\beta)\sin(\theta)\vec{z}_1",
                r"+\sin(\beta)\vec{x}_2",
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 1 / Fig 3)",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{z}_3 \wedge \vec{x}_1",
            "propositions": [
                r"+\cos(\beta)\cos(\theta)\vec{y}_1 + \sin(\beta)\vec{z}_1",
                r"-\cos(\beta)\cos(\theta)\vec{y}_1 - \sin(\beta)\vec{z}_1",
                r"+\sin(\beta)\cos(\theta)\vec{y}_1 + \cos(\beta)\vec{z}_1",
                r"+\sin(\beta)\vec{z}_1",
            ],
            "correct_expressions": [
                r"+\cos(\beta)\cos(\theta)\vec{y}_1 + \sin(\beta)\vec{z}_1"
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 3 / Fig 1)",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{x}_1 \wedge \vec{z}_3",
            "propositions": [
                r"-\cos(\beta)\cos(\theta)\vec{y}_1 - \sin(\beta)\vec{z}_1",
                r"+\cos(\beta)\cos(\theta)\vec{y}_1 + \sin(\beta)\vec{z}_1",
                r"-\sin(\beta)\cos(\theta)\vec{y}_1 - \cos(\beta)\vec{z}_1",
                r"-\sin(\beta)\vec{z}_1",
            ],
            "correct_expressions": [
                r"-\cos(\beta)\cos(\theta)\vec{y}_1 - \sin(\beta)\vec{z}_1"
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 1 / Fig 3)",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{z}_3 \wedge \vec{y}_1",
            "propositions": [
                r"-\cos(\beta)\cos(\theta)\vec{x}_1 + \cos(\beta)\sin(\theta)\vec{z}_1",
                r"+\cos(\beta)\cos(\theta)\vec{x}_1 - \cos(\beta)\sin(\theta)\vec{z}_1",
                r"-\sin(\beta)\cos(\theta)\vec{x}_1 + \cos(\beta)\sin(\theta)\vec{z}_1",
                r"-\cos(\beta)\vec{x}_2",
            ],
            "correct_expressions": [
                r"-\cos(\beta)\cos(\theta)\vec{x}_1 + \cos(\beta)\sin(\theta)\vec{z}_1",
                r"-\cos(\beta)\vec{x}_2",
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 3 / Fig 1)",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{y}_1 \wedge \vec{z}_3",
            "propositions": [
                r"+\cos(\beta)\cos(\theta)\vec{x}_1 - \cos(\beta)\sin(\theta)\vec{z}_1",
                r"-\cos(\beta)\cos(\theta)\vec{x}_1 + \cos(\beta)\sin(\theta)\vec{z}_1",
                r"+\sin(\beta)\cos(\theta)\vec{x}_1 - \cos(\beta)\sin(\theta)\vec{z}_1",
                r"+\cos(\beta)\vec{x}_2",
            ],
            "correct_expressions": [
                r"+\cos(\beta)\cos(\theta)\vec{x}_1 - \cos(\beta)\sin(\theta)\vec{z}_1",
                r"+\cos(\beta)\vec{x}_2",
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 1 / Fig 3)",
        },
    ],
}

NIVEAUX = ["A", "B", "C", "D"]

# --- BARÈME PROGRESSIF SUR 20 POINTS ---
BAREME = {
    "A": 2,
    "B": 4,
    "C": 6,
    "D": 8,
}

# --- INITIALISATION SESSION STATE ---
if "test_started" not in st.session_state:
    st.session_state.test_started = False
    st.session_state.step = 0
    st.session_state.reponses_enregistrees = {}
    st.session_state.show_popup = False
    st.session_state.review_mode = False
    st.session_state.test_finished = False
    st.session_state.is_editing = False

# --- FONCTION D'ENREGISTREMENT SÉCURISÉE ---
def sauvegarder_reponse_actuelle():
    """Sauvegarde le choix actuel de l'utilisateur pour la question en cours."""
    step = st.session_state.step
    q = st.session_state.questions_selectionnees[step]
    niveau_courant = NIVEAUX[step]

    if q["type"] == "colonnes":
        signe = st.session_state.get(f"signe_{step}", "+")
        trigo = st.session_state.get(f"trigo_{step}", "1")
        angle = st.session_state.get(f"angle_{step}", "α")
        vecteur = st.session_state.get(f"vec_{step}", "x")
        indice = st.session_state.get(f"ind_{step}", "0")

        choix_eleve = {
            "signe": signe,
            "trigo": trigo,
            "angle": angle,
            "vecteur": vecteur,
            "indice": indice,
        }
        exact = verifier_reponse_colonnes(choix_eleve, q["solution"])

        reponse_latex = (
            f"{signe} \\{trigo}({angle}) \\vec{{{vecteur}}}_{{{indice}}}"
            if trigo != "1"
            else f"{signe} \\vec{{{vecteur}}}_{{{indice}}}"
        )

        st.session_state.reponses_enregistrees[step] = {
            "niveau": niveau_courant,
            "enonce": q["enonce"],
            "reponse_display": reponse_latex,
            "reponse_sheet": (
                f"'{signe} {trigo}({angle}) {vecteur}_{indice}"
                if trigo != "1"
                else f"'{signe} {vecteur}_{indice}"
            ),
            "exact": exact,
            "choix_raw": choix_eleve,
        }
    else:
        choix_select = st.session_state.get(f"qcm_{step}", q["propositions_shuffled"][0])
        exact = choix_select in q["correct_expressions"]

        st.session_state.reponses_enregistrees[step] = {
            "niveau": niveau_courant,
            "enonce": q["enonce"],
            "reponse_display": choix_select,
            "reponse_sheet": f"'{choix_select}",
            "exact": exact,
        }

# --- 1. IDENTIFICATION ---
if not st.session_state.test_started:
    try:
# Un cache de 60s accélère l'affichage tout en capturant rapidement les modifications du Sheet
        df_eleves = conn.read(spreadsheet=URL_GSHEET, worksheet="Eleves", ttl=3600).fillna("")
        df_eleves["Classe"] = df_eleves["Classe"].astype(str).str.strip()
        df_eleves["Nom"] = df_eleves["Nom"].astype(str).str.strip()
        df_eleves["Prénom"] = df_eleves["Prénom"].astype(str).str.strip()
        df_eleves = df_eleves[df_eleves["Nom"] != ""]
    except Exception as e:
        st.error(f"Erreur de chargement de la liste des élèves : {e}")
        st.stop()

    st.subheader("Identification")

    col_classe, col_eleve = st.columns([1, 2])

    with col_classe:
        classes_disponibles = sorted(df_eleves["Classe"].unique().tolist())
        classe_choisie = st.selectbox(
            "Classe", classes_disponibles, key="select_classe"
        )

    with col_eleve:
        df_filtre = df_eleves[df_eleves["Classe"] == classe_choisie]
        liste_noms = (
            (df_filtre["Nom"] + " " + df_filtre["Prénom"]).str.strip().sort_values().tolist()
        )

        eleve_selectionne = st.selectbox(
            "Sélectionnez votre Nom et Prénom",
            ["-- Choisir dans la liste --"] + liste_noms,
            key=f"select_eleve_{classe_choisie}",
        )

    if st.button("Commencer l'évaluation", type="primary"):
        if eleve_selectionne != "-- Choisir dans la liste --":
            eleve_row = df_filtre[
                (df_filtre["Nom"] + " " + df_filtre["Prénom"]).str.strip()
                == eleve_selectionne
            ].iloc[0]

            st.session_state.nom = eleve_row["Nom"]
            st.session_state.prenom = eleve_row["Prénom"]
            st.session_state.classe = classe_choisie
            st.session_state.test_started = True
            st.session_state.show_popup = True
            st.session_state.start_time = time.time()

            q_list = []
            for niv in NIVEAUX:
                q_copy = dict(random.choice(BANQUE_QUESTIONS[niv]))
                if q_copy["type"] == "qcm":
                    props = list(q_copy["propositions"])
                    random.shuffle(props)
                    q_copy["propositions_shuffled"] = props
                q_list.append(q_copy)

            st.session_state.questions_selectionnees = q_list
            st.rerun()
        else:
            st.error(
                "⚠️ Veuillez sélectionner votre nom dans la liste avant de démarrer."
            )

# --- 2. ÉVALUATION PROGRESSIVE AVEC NAVIGATION FLUIDE ---
elif not st.session_state.test_finished and not st.session_state.review_mode:

    @st.fragment(run_every=1)
    def afficher_chronometre():
        temps_ecoule = time.time() - st.session_state.start_time
        temps_restant = int(DUREE_MAX_SECONDES - temps_ecoule)

        if temps_restant <= 0:
            st.error("⏳ **Temps écoulé !** Validation automatique du test.")
            st.session_state.review_mode = True
            st.rerun()

        minutes = temps_restant // 60
        secondes = temps_restant % 60
        color = "red" if temps_restant < 60 else "normal"

        st.metric(
            label="⏱ Temps restant",
            value=f"{minutes:02d}:{secondes:02d}",
            delta_color=color,
        )

    afficher_chronometre()

    if st.session_state.get("show_popup", False):
        st.info(
            "⏱ **Le test dure 5 minutes maximum.** Répondez puis relisez vos choix avant de valider !"
        )
        st.session_state.show_popup = False

    niveau_courant = NIVEAUX[st.session_state.step]
    q = st.session_state.questions_selectionnees[st.session_state.step]

    st.caption(
        f"Étudiant : **{st.session_state.nom} {st.session_state.prenom}**"
        f" ({st.session_state.classe})"
    )

    # --- BARRE DE NAVIGATION EN HAUT (AVEC SAUVEGARDE AUTOMATIQUE AU CLIC) ---
    cols_nav = st.columns([1, 1, 1, 1, 1.5])
    for idx, niv in enumerate(NIVEAUX):
        btn_label = f"Q{idx+1} ({niv})"
        if idx == st.session_state.step:
            cols_nav[idx].button(f"👉 {btn_label}", key=f"nav_{idx}", disabled=True)
        else:
            if cols_nav[idx].button(btn_label, key=f"nav_{idx}"):
                sauvegarder_reponse_actuelle()  # Sauvegarde auto de la question courante
                st.session_state.step = idx
                st.rerun()

    # Bouton rapide d'accès au récapitulatif
    with cols_nav[4]:
        if st.button("📋 Récapitulatif", key="go_review_top"):
            sauvegarder_reponse_actuelle()
            st.session_state.review_mode = True
            st.rerun()

    st.progress(
        (st.session_state.step + 1) / 4,
        text=f"Question {st.session_state.step + 1} / 4 — Niveau {niveau_courant}",
    )

    try:
        st.image(
            "3Figs_geom.png",
            use_container_width=True,
            caption="🔍 Cliquez sur 'Plein écran' pour agrandir les figures.",
        )
    except Exception:
        st.warning("Image '3Figs_geom.png' introuvable.")

    st.markdown("---")
    st.write(f"### {q['description']}")
    st.latex(f"{q['enonce']} = \dots")

    rep_prec = st.session_state.reponses_enregistrees.get(
        st.session_state.step, {}
    )

    if q["type"] == "colonnes":
        col_gauche, col_droite = st.columns(2)

        choix_prev = rep_prec.get("choix_raw", {})

        opts_signe = ["+", "-"]
        opts_trigo = ["1", "sin", "cos"]
        opts_angle = ["α", "θ", "β"]
        opts_vec = ["x", "y", "z", "0"]
        opts_ind = ["0", "1", "2", "3"]

        idx_signe = opts_signe.index(choix_prev.get("signe", "+")) if choix_prev.get("signe") in opts_signe else 0
        idx_trigo = opts_trigo.index(choix_prev.get("trigo", "1")) if choix_prev.get("trigo") in opts_trigo else 0
        idx_angle = opts_angle.index(choix_prev.get("angle", "α")) if choix_prev.get("angle") in opts_angle else 0
        idx_vec = opts_vec.index(choix_prev.get("vecteur", "x")) if choix_prev.get("vecteur") in opts_vec else 0
        idx_ind = opts_ind.index(choix_prev.get("indice", "0")) if choix_prev.get("indice") in opts_ind else 0

        with col_gauche:
            signe = st.radio(
                "Signe",
                opts_signe,
                horizontal=True,
                index=idx_signe,
                key=f"signe_{st.session_state.step}",
            )
            trigo = st.radio(
                "Trigo",
                opts_trigo,
                horizontal=True,
                index=idx_trigo,
                key=f"trigo_{st.session_state.step}",
            )
            angle = st.radio(
                "Angle",
                opts_angle,
                horizontal=True,
                index=idx_angle,
                key=f"angle_{st.session_state.step}",
            )

        with col_droite:
            vecteur = st.radio(
                "Vecteur",
                opts_vec,
                horizontal=True,
                index=idx_vec,
                key=f"vec_{st.session_state.step}",
            )
            indice = st.radio(
                "Indice",
                opts_ind,
                horizontal=True,
                index=idx_ind,
                key=f"ind_{st.session_state.step}",
            )

        trigo_str = "" if trigo == "1" else f"\\{trigo}"
        angle_str = "" if trigo == "1" else f"({angle})"
        vec_str = "0" if vecteur == "0" else f"\\vec{{{vecteur}}}_{{{indice}}}"
        formule_latex = f"{signe} {trigo_str}{angle_str} {vec_str}"

        st.markdown("---")
        st.write("**Aperçu de votre réponse :**")
        st.latex(f"{q['enonce']} = {formule_latex}")

    else:
        def_idx = 0
        if "reponse_display" in rep_prec:
            if rep_prec["reponse_display"] in q["propositions_shuffled"]:
                def_idx = q["propositions_shuffled"].index(
                    rep_prec["reponse_display"]
                )

        choix_select = st.radio(
            "Choisissez la bonne expression :",
            q["propositions_shuffled"],
            index=def_idx,
            format_func=lambda x: f"$${x}$$",
            key=f"qcm_{st.session_state.step}",
        )

    # --- BOUTONS D'ACTION INTELLIGENTS EN BAS ---
    st.markdown("---")
    
    # Texte dynamique du bouton selon si l'étudiant corrige depuis la page de récapitulatif
    if st.session_state.is_editing:
        btn_txt = "💾 Enregistrer & Revenir au récapitulatif 📋"
    elif st.session_state.step == 3:
        btn_txt = "Enregistrer & Réviser les réponses 📋"
    else:
        btn_txt = "Enregistrer & Question Suivante ➔"

    if st.button(btn_txt, type="primary"):
        sauvegarder_reponse_actuelle()

        if st.session_state.is_editing:
            st.session_state.is_editing = False
            st.session_state.review_mode = True
        elif st.session_state.step < 3:
            st.session_state.step += 1
        else:
            st.session_state.review_mode = True
            
        st.rerun()

# --- 3. PAGE DE RELECTURE ET MODIFICATION DIRECIIONNELLE ---
elif st.session_state.review_mode and not st.session_state.test_finished:
    st.subheader("📋 Récapitulatif de vos réponses")
    st.info(
        "Vérifiez vos réponses ci-dessous. Vous pouvez modifier une question puis revenir directement ici."
    )

    for idx in range(4):
        q = st.session_state.questions_selectionnees[idx]
        rep = st.session_state.reponses_enregistrees.get(idx, None)

        col_q, col_edit = st.columns([4, 1])

        with col_q:
            st.markdown(f"**Question {idx+1} (Niveau {NIVEAUX[idx]}) :**")
            if rep:
                st.latex(f"{rep['enonce']} = {rep['reponse_display']}")
            else:
                st.warning("Non répondue")

        with col_edit:
            if st.button("✏️ Modifier", key=f"edit_{idx}"):
                st.session_state.step = idx
                st.session_state.is_editing = True  # Mode modification activé
                st.session_state.review_mode = False
                st.rerun()

        st.markdown("---")

    col_val1, col_val2 = st.columns(2)
    with col_val1:
        if st.button("🚀 VALIDER DÉFINITIVEMENT LE TEST", type="primary"):
            st.session_state.test_finished = True
            st.session_state.end_time = time.time()
            st.rerun()

# --- 4. BILAN FINAL, GSHEETS ET CLASSEMENT ---
else:
    score_total = sum(
        BAREME[NIVEAUX[idx]]
        for idx in range(4)
        if st.session_state.reponses_enregistrees.get(idx, {}).get("exact", False)
    )

    if score_total >= 15:
        st.balloons()

    duree_totale_sec = int(st.session_state.end_time - st.session_state.start_time)
    duree_totale_sec = min(duree_totale_sec, DUREE_MAX_SECONDES)
    m_passe = duree_totale_sec // 60
    s_passe = duree_totale_sec % 60
    temps_passe_str = f"{m_passe:02d}:{s_passe:02d}"

    st.subheader(f"Test terminé ! Votre note : {score_total} / 20")
    st.info(f"⏱ Temps réalisé : **{temps_passe_str}**")
    st.markdown("---")

    for idx in range(4):
        resp = st.session_state.reponses_enregistrees.get(idx, {})
        symbole = "✅" if resp.get("exact", False) else "❌"
        st.write(f"**Question {idx+1} (Niveau {NIVEAUX[idx]}) : {symbole}**")
        st.latex(f"{resp.get('enonce', '')} = {resp.get('reponse_display', '')}")

    st.markdown("---")

    q1_val = st.session_state.reponses_enregistrees.get(0, {}).get(
        "reponse_sheet", "'Non répondu"
    )
    q2_val = st.session_state.reponses_enregistrees.get(1, {}).get(
        "reponse_sheet", "'Non répondu"
    )
    q3_val = st.session_state.reponses_enregistrees.get(2, {}).get(
        "reponse_sheet", "'Non répondu"
    )
    q4_val = st.session_state.reponses_enregistrees.get(3, {}).get(
        "reponse_sheet", "'Non répondu"
    )

    # SAUVEGARDE EN SESSIONS / SÉCURISÉE SANS RÉSULTATS ÉCRASÉS
    if "data_saved" not in st.session_state:
        st.session_state.data_saved = False

    if not st.session_state.data_saved:
        try:
            tz_paris = zoneinfo.ZoneInfo("Europe/Paris")
            horodatage_paris = datetime.datetime.now(tz_paris).strftime("%Y-%m-%d %H:%M:%S")

            nouvelle_ligne = {
                "Horodatage": horodatage_paris,
                "Temps_Passe": f"'{temps_passe_str}",
                "Nom": st.session_state.nom,
                "Prenom": st.session_state.prenom,
                "Classe": st.session_state.classe,
                "Note": score_total,
                "Q1_NivA": q1_val,
                "Q2_NivB": q2_val,
                "Q3_NivC": q3_val,
                "Q4_NivD": q4_val,
            }

            # Lecture directe (ttl=0) effectuée UNE SEULE FOIS lors de la soumission finale de l'élève
            df_existant = conn.read(spreadsheet=URL_GSHEET, worksheet="Réponses", ttl=0).fillna("")

            df_maj = pd.concat(
                [df_existant, pd.DataFrame([nouvelle_ligne])], ignore_index=True
            )

            conn.update(spreadsheet=URL_GSHEET, worksheet="Réponses", data=df_maj)
            
            st.session_state.data_saved = True
            st.session_state.df_leaderboard_cache = df_maj
            st.success("Vos résultats ont été enregistrés dans Google Sheets.")

        except Exception as e:
            st.error(f"Erreur lors de l'enregistrement dans Google Sheets : {e}")

    # AFFICHER LE CLASSEMENT DEPUIS LE CACHE D'ENREGISTREMENT
    if st.session_state.get("data_saved", False):
        try:
            st.subheader("🏆 Classement Général (Top Score & Vitesse)")

            df_leaderboard = st.session_state.df_leaderboard_cache.copy()
            df_leaderboard["Temps_Clean"] = (
                df_leaderboard["Temps_Passe"].astype(str).str.replace("'", "")
            )
            df_leaderboard["Note"] = pd.to_numeric(
                df_leaderboard["Note"], errors="coerce"
            )

            df_leaderboard = df_leaderboard.sort_values(
                by=["Note", "Temps_Clean"], ascending=[False, True]
            ).reset_index(drop=True)

            df_leaderboard.index = df_leaderboard.index + 1
            df_leaderboard.index.name = "Rang"

            df_display = df_leaderboard[
                ["Nom", "Prenom", "Classe", "Note", "Temps_Clean"]
            ].rename(columns={"Temps_Clean": "Temps"})

            st.dataframe(df_display, use_container_width=True)

        except Exception as e:
            st.error(f"Erreur d'affichage du classement : {e}")

    st.info("Vous pouvez fermer cette fenêtre.")