import datetime
import random
import time
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuration de la page
st.set_page_config(page_title="QCM - Produits Vectoriels", page_icon="📐")

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

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📐 QCM : Produits Vectoriels Progressifs")

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
            "description": "Niveau C (3/4