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
    
    # Vérification du vecteur et de l'indice avec équivalences
    vecteur_ok = verifier_vecteur_egal(
        reponse_eleve.get("vecteur"),
        reponse_eleve.get("indice"),
        solution_qcm.get("vecteur"),
        solution_qcm.get("indice")
    )

    # L'angle n'a d'importance que si une fonction trigo (sin/cos) est choisie
    if reponse_eleve.get("trigo") == "1":
        angle_ok = True
    else:
        angle_ok = reponse_eleve.get("angle") == solution_qcm.get("angle")

    return signe_ok and trigo_ok and vecteur_ok and angle_ok

# --- BANQUE DE QUESTIONS ---
BANQUE_QUESTIONS = {
    "A": [
#Figure 1 Sinus
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
   # Figure 2          
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
         # Figure 3
        
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
  # figure 1 cosinus type      
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
 # fig 2 cosinus type
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
 # fig 3 cosinus type
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
        # --- 1. Produits entre Fig 3 et Fig 1 ---
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

        # --- 2. Produits entre Base 2 et Base 0 ---
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
                r"+\sin(\theta)\sin(\alpha)\vec{x}_1 + \sin(\theta)\cos(\alpha)\vec{y}_1 + \cos(\theta)\sin(\alpha)\vec{z}_1",
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
        # --- 1. y3 ^ x1 et son opposé x1 ^ y3 ---
        {
            "type": "qcm",
            "enonce": r"\vec{y}_3 \wedge \vec{x}_1",
            "propositions": [
                (
                    r"-\cos(\beta)\vec{z}_1 +"
                    r" \sin(\beta)\cos(\theta)\vec{y}_1"
                ),
                (
                    r"+\cos(\beta)\vec{z}_1 -"
                    r" \sin(\beta)\sin(\theta)\vec{x}_1"
                ),
                (
                    r"-\sin(\beta)\vec{z}_1 +"
                    r" \cos(\beta)\cos(\theta)\vec{y}_1"
                ),
                r"+\sin(\beta)\vec{y}_1",
            ],
            "correct_expressions": [
                (
                    r"-\cos(\beta)\vec{z}_1 +"
                    r" \sin(\beta)\cos(\theta)\vec{y}_1"
                )
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 3 / Fig 1)",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{x}_1 \wedge \vec{y}_3",
            "propositions": [
                (
                    r"+\cos(\beta)\vec{z}_1 -"
                    r" \sin(\beta)\cos(\theta)\vec{y}_1"
                ),
                (
                    r"-\cos(\beta)\vec{z}_1 +"
                    r" \sin(\beta)\sin(\theta)\vec{x}_1"
                ),
                (
                    r"+\sin(\beta)\vec{z}_1 -"
                    r" \cos(\beta)\cos(\theta)\vec{y}_1"
                ),
                r"-\sin(\beta)\vec{y}_1",
            ],
            "correct_expressions": [
                (
                    r"+\cos(\beta)\vec{z}_1 -"
                    r" \sin(\beta)\cos(\theta)\vec{y}_1"
                )
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 1 / Fig 3)",
        },
        # --- 2. y3 ^ y1 et son opposé y1 ^ y3 ---
       {
            "type": "qcm",
            "enonce": r"\vec{y}_3 \wedge \vec{y}_1",
            "propositions": [
                (
                    r"-\sin(\beta)\cos(\theta)\vec{x}_1 +"
                    r" \sin(\beta)\sin(\theta)\vec{z}_1"
                ),
                (
                    r"+\sin(\beta)\cos(\theta)\vec{x}_1 -"
                    r" \sin(\beta)\sin(\theta)\vec{z}_1"
                ),
                (
                    r"-\cos(\beta)\cos(\theta)\vec{x}_1 +"
                    r" \sin(\beta)\sin(\theta)\vec{z}_1"
                ),
                r"-\sin(\beta)\vec{x}_2",
            ],
            "correct_expressions": [
                (
                    r"-\sin(\beta)\cos(\theta)\vec{x}_1 +"
                    r" \sin(\beta)\sin(\theta)\vec{z}_1"
                ),
                r"-\sin(\beta)\vec{x}_2",
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 3 / Fig 1)",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{y}_1 \wedge \vec{y}_3",
            "propositions": [
                (
                    r"+\sin(\beta)\cos(\theta)\vec{x}_1 -"
                    r" \sin(\beta)\sin(\theta)\vec{z}_1"
                ),
                (
                    r"-\sin(\beta)\cos(\theta)\vec{x}_1 +"
                    r" \sin(\beta)\sin(\theta)\vec{z}_1"
                ),
                (
                    r"+\cos(\beta)\cos(\theta)\vec{x}_1 -"
                    r" \sin(\beta)\sin(\theta)\vec{z}_1"
                ),
                r"+\sin(\beta)\vec{x}_2",
            ],
            "correct_expressions": [
                (
                    r"+\sin(\beta)\cos(\theta)\vec{x}_1 -"
                    r" \sin(\beta)\sin(\theta)\vec{z}_1"
                ),
                r"+\sin(\beta)\vec{x}_2",
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 1 / Fig 3)",
        },
        # --- 3. z3 ^ x1 et son opposé x1 ^ z3 ---
        {
            "type": "qcm",
            "enonce": r"\vec{z}_3 \wedge \vec{x}_1",
            "propositions": [
                (
                    r"+\cos(\beta)\cos(\theta)\vec{y}_1 +"
                    r" \sin(\beta)\vec{z}_1"
                ),
                (
                    r"-\cos(\beta)\cos(\theta)\vec{y}_1 -"
                    r" \sin(\beta)\vec{z}_1"
                ),
                (
                    r"+\sin(\beta)\cos(\theta)\vec{y}_1 +"
                    r" \cos(\beta)\vec{z}_1"
                ),
                r"+\sin(\beta)\vec{z}_1",
            ],
            "correct_expressions": [
                (
                    r"+\cos(\beta)\cos(\theta)\vec{y}_1 +"
                    r" \sin(\beta)\vec{z}_1"
                )
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 3 / Fig 1)",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{x}_1 \wedge \vec{z}_3",
            "propositions": [
                (
                    r"-\cos(\beta)\cos(\theta)\vec{y}_1 -"
                    r" \sin(\beta)\vec{z}_1"
                ),
                (
                    r"+\cos(\beta)\cos(\theta)\vec{y}_1 +"
                    r" \sin(\beta)\vec{z}_1"
                ),
                (
                    r"-\sin(\beta)\cos(\theta)\vec{y}_1 -"
                    r" \cos(\beta)\vec{z}_1"
                ),
                r"-\sin(\beta)\vec{z}_1",
            ],
            "correct_expressions": [
                (
                    r"-\cos(\beta)\cos(\theta)\vec{y}_1 -"
                    r" \sin(\beta)\vec{z}_1"
                )
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 1 / Fig 3)",
        },
        # --- 4. z3 ^ y1 et son opposé y1 ^ z3 ---
        {
            "type": "qcm",
            "enonce": r"\vec{z}_3 \wedge \vec{y}_1",
            "propositions": [
                (
                    r"-\cos(\beta)\cos(\theta)\vec{x}_1 +"
                    r" \cos(\beta)\sin(\theta)\vec{z}_1"
                ),
                (
                    r"+\cos(\beta)\cos(\theta)\vec{x}_1 -"
                    r" \cos(\beta)\sin(\theta)\vec{z}_1"
                ),
                (
                    r"-\sin(\beta)\cos(\theta)\vec{x}_1 +"
                    r" \cos(\beta)\sin(\theta)\vec{z}_1"
                ),
                r"-\cos(\beta)\vec{x}_2",
            ],
            "correct_expressions": [
                (
                    r"-\cos(\beta)\cos(\theta)\vec{x}_1 +"
                    r" \cos(\beta)\sin(\theta)\vec{z}_1"
                ),
                r"-\cos(\beta)\vec{x}_2",
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 3 / Fig 1)",
        },
        {
            "type": "qcm",
            "enonce": r"\vec{y}_1 \wedge \vec{z}_3",
            "propositions": [
                (
                    r"+\cos(\beta)\cos(\theta)\vec{x}_1 -"
                    r" \cos(\beta)\sin(\theta)\vec{z}_1"
                ),
                (
                    r"-\cos(\beta)\cos(\theta)\vec{x}_1 +"
                    r" \cos(\beta)\sin(\theta)\vec{z}_1"
                ),
                (
                    r"+\sin(\beta)\cos(\theta)\vec{x}_1 -"
                    r" \cos(\beta)\sin(\theta)\vec{z}_1"
                ),
                r"+\cos(\beta)\vec{x}_2",
            ],
            "correct_expressions": [
                (
                    r"+\cos(\beta)\cos(\theta)\vec{x}_1 -"
                    r" \cos(\beta)\sin(\theta)\vec{z}_1"
                ),
                r"+\cos(\beta)\vec{x}_2",
            ],
            "description": "Niveau D (4/4) : Produit complexe (Fig 1 / Fig 3)",
        },
    ],
}

NIVEAUX = ["A", "B", "C", "D"]

# --- BARÈME PROGRESSIF SUR 20 POINTS ---
BAREME = {
    "A": 2,  # Question niveau A = 2 points
    "B": 4,  # Question niveau B = 4 points
    "C": 6,  # Question niveau C = 6 points
    "D": 8   # Question niveau D = 8 points
}

# --- 1. IDENTIFICATION ---
if "test_started" not in st.session_state:
    st.session_state.test_started = False
    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.reponses_historique = []
    st.session_state.show_popup = False

if not st.session_state.test_started:
    try:
        # Chargement de la liste depuis Google Sheets
        df_eleves = conn.read(worksheet="Eleves", ttl=3600)
    except Exception as e:
        st.error(f"Erreur de chargement de la liste des élèves : {e}")
        st.stop()

    st.subheader("Identification")
    
    col_classe, col_eleve = st.columns([1, 2])
    
    with col_classe:
        classes_disponibles = sorted(df_eleves["Classe"].unique().tolist())
        # Utilisation de key pour conserver la classe sélectionnée dans le state
        classe_choisie = st.selectbox("Classe", classes_disponibles, key="select_classe")
    
    with col_eleve:
        # Filtrage dynamique des élèves en fonction de la classe sélectionnée
        df_filtre = df_eleves[df_eleves["Classe"] == classe_choisie]
        liste_noms = (df_filtre["Nom"] + " " + df_filtre["Prénom"]).sort_values().tolist()
        
        eleve_selectionne = st.selectbox(
            "Sélectionnez votre Nom et Prénom",
            ["-- Choisir dans la liste --"] + liste_noms,
            key=f"select_eleve_{classe_choisie}"  # La clef change quand la classe change pour réinitialiser proprement le champ
        )

    if st.button("Commencer l'évaluation", type="primary"):
        if eleve_selectionne != "-- Choisir dans la liste --":
            eleve_row = df_filtre[(df_filtre["Nom"] + " " + df_filtre["Prénom"]) == eleve_selectionne].iloc[0]
            
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
            st.error("⚠️ Veuillez sélectionner votre nom dans la liste avant de démarrer.")

# --- 2. EVALUATION PROGRESSIVE AVEC CHRONOMÈTRE NATIVE ---
elif st.session_state.step < 4:

    @st.fragment(run_every=1)
    def afficher_chronometre():
        temps_ecoule = time.time() - st.session_state.start_time
        temps_restant = int(DUREE_MAX_SECONDES - temps_ecoule)

        if temps_restant <= 0:
            st.error("⏳ **Temps écoulé !** Le test est terminé.")
            st.session_state.step = 4
            st.session_state.end_time = time.time()
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
        st.info("⏱️️ **Le test dure 5 minutes maximum.** Répondez le plus rapidement possible !")
        st.session_state.show_popup = False

    niveau_courant = NIVEAUX[st.session_state.step]
    q = st.session_state.questions_selectionnees[st.session_state.step]

    st.caption(
        f"Étudiant : **{st.session_state.nom} {st.session_state.prenom}**"
        f" ({st.session_state.classe})"
    )
    st.progress(
        (st.session_state.step) / 4,
        text=f"Question {st.session_state.step + 1} / 4 — Niveau {niveau_courant}",
    )

    # --- IMAGE AVEC OPTION ZOOM PLEIN ÉCRAN ---
    try:
        st.image(
            "3Figs_geom.png",
            use_container_width=True,
            caption="🔍 Appuyez sur l'icône 'Plein écran' en haut à droite de l'image pour l'agrandir.",
        )
    except Exception:
        st.warning("Image '3Figs_geom.png' introuvable.")

    st.markdown("---")
    st.write(f"### {q['description']}")
    st.latex(f"{q['enonce']} = \dots")

    # --- CAS 1 : INTERFACE 2 COLONNES (Niveaux A & B) ---
    if q["type"] == "colonnes":
        col_gauche, col_droite = st.columns(2)

        with col_gauche:
            signe = st.radio(
                "Signe",
                ["+", "-"],
                horizontal=True,
                key=f"signe_{st.session_state.step}",
            )
            trigo = st.radio(
                "Trigo",
                ["1", "sin", "cos"],
                horizontal=True,
                key=f"trigo_{st.session_state.step}",
            )
            angle = st.radio(
                "Angle",
                ["α", "θ", "β"],
                horizontal=True,
                key=f"angle_{st.session_state.step}",
            )

        with col_droite:
            vecteur = st.radio(
                "Vecteur",
                ["x", "y", "z", "0"],
                horizontal=True,
                key=f"vec_{st.session_state.step}",
            )
            indice = st.radio(
                "Indice",
                ["0", "1", "2", "3"],
                horizontal=True,
                key=f"ind_{st.session_state.step}",
            )

        trigo_str = "" if trigo == "1" else f"\\{trigo}"
        angle_str = "" if trigo == "1" else f"({angle})"
        vec_str = "0" if vecteur == "0" else f"\\vec{{{vecteur}}}_{{{indice}}}"
        formule_latex = f"{signe} {trigo_str}{angle_str} {vec_str}"

        st.markdown("---")
        st.write("**Aperçu de votre réponse :**")
        st.latex(f"{q['enonce']} = {formule_latex}")

        if st.button("Valider cette question ➔", type="primary"):
            sol = q["solution"]

            choix_eleve = {
                "signe": signe,
                "trigo": trigo,
                "angle": angle,
                "vecteur": vecteur,
                "indice": indice
            }

            # Validation utilisant la tolérance sur l'angle quand trigo == "1"
            exact = verifier_reponse_colonnes(choix_eleve, sol)

            if exact:
                st.session_state.score += BAREME.get(niveau_courant, 0)

            reponse_latex = (
                f"{signe} \\{trigo}({angle}) \\vec{{{vecteur}}}_{{{indice}}}"
                if trigo != "1"
                else f"{signe} \\vec{{{vecteur}}}_{{{indice}}}"
            )

            st.session_state.reponses_historique.append({
                "niveau": niveau_courant,
                "enonce": q["enonce"],
                "reponse_display": reponse_latex,
                "reponse_sheet": (
                    f"'{signe} {trigo}({angle}) {vecteur}_{indice}"
                    if trigo != "1"
                    else f"'{signe} {vecteur}_{indice}"
                ),
                "exact": exact,
            })
            st.session_state.step += 1
            if st.session_state.step == 4:
                st.session_state.end_time = time.time()
            st.rerun()

    # --- CAS 2 : CHOIX MULTIPLES / QCM (Niveaux C & D) ---
    else:
        choix_select = st.radio(
            "Choisissez la bonne expression :",
            q["propositions_shuffled"],
            format_func=lambda x: f"$${x}$$",
            key=f"qcm_{st.session_state.step}",
        )

        if st.button("Valider cette question ➔", type="primary"):
            exact = choix_select in q["correct_expressions"]
            if exact:
                st.session_state.score += BAREME.get(niveau_courant, 0)

            st.session_state.reponses_historique.append({
                "niveau": niveau_courant,
                "enonce": q["enonce"],
                "reponse_display": choix_select,
                "reponse_sheet": f"'{choix_select}",
                "exact": exact,
            })
            st.session_state.step += 1
            if st.session_state.step == 4:
                st.session_state.end_time = time.time()
            st.rerun()

# --- 3. BILAN, SYNCHRONISATION ET CLASSEMENT ---
else:
    note_finale = st.session_state.score
    if note_finale >= 15:
        st.balloons()

    if "end_time" not in st.session_state:
        st.session_state.end_time = time.time()

    duree_totale_sec = int(st.session_state.end_time - st.session_state.start_time)
    duree_totale_sec = min(duree_totale_sec, DUREE_MAX_SECONDES)
    m_passe = duree_totale_sec // 60
    s_passe = duree_totale_sec % 60
    temps_passe_str = f"{m_passe:02d}:{s_passe:02d}"

    st.subheader(f"Test terminé ! Votre note : {note_finale} / 20")
    st.info(f"⏱ Temps réalisé : **{temps_passe_str}**")
    st.markdown("---")

    for idx, resp in enumerate(st.session_state.reponses_historique):
        symbole = "✅" if resp["exact"] else "❌"
        st.write(f"**Question {idx+1} (Niveau {resp['niveau']}) : {symbole}**")
        st.latex(f"{resp['enonce']} = {resp['reponse_display']}")

    st.markdown("---")

    q_ans = len(st.session_state.reponses_historique)
    q1_val = st.session_state.reponses_historique[0]["reponse_sheet"] if q_ans > 0 else "'Non répondu"
    q2_val = st.session_state.reponses_historique[1]["reponse_sheet"] if q_ans > 1 else "'Non répondu"
    q3_val = st.session_state.reponses_historique[2]["reponse_sheet"] if q_ans > 2 else "'Non répondu"
    q4_val = st.session_state.reponses_historique[3]["reponse_sheet"] if q_ans > 3 else "'Non répondu"

    try:
        # Lire explicitement l'onglet des réponses
        df_existant = conn.read(worksheet="Réponses", ttl=0)

        nouvelle_ligne = {
            "Horodatage": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Temps_Passe": f"'{temps_passe_str}",
            "Nom": st.session_state.nom,
            "Prenom": st.session_state.prenom,
            "Classe": st.session_state.classe,
            "Note": note_finale,
            "Q1_NivA": q1_val,
            "Q2_NivB": q2_val,
            "Q3_NivC": q3_val,
            "Q4_NivD": q4_val,
        }

        df_maj = pd.concat([df_existant, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
        
        # Mettre à jour uniquement l'onglet des réponses
        conn.update(worksheet="Réponses", data=df_maj)
        st.success("Vos résultats ont été enregistrés dans Google Sheets.")
        

        # --- GENERATION DU CLASSEMENT (LEADERBOARD) ---
        st.subheader("🏆 Classement Général (Top Score & Vitesse)")

        df_leaderboard = df_maj.copy()

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
        st.error(f"Erreur lors du calcul du classement / Google Sheets : {e}")

    st.info("Vous pouvez fermer cette fenêtre.")