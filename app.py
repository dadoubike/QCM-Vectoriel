import datetime
import random
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuration de la page
st.set_page_config(page_title="QCM - Produits Vectoriels", page_icon="📐")

# Connection à Google Sheets (définie dans les Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📐 QCM : Produits Vectoriels Progressifs")

# --- BANQUE DE QUESTIONS PAR NIVEAU ---
BANQUE_QUESTIONS = {
    "A": [  # Niveau A : Débutant
        {
            "enonce": r"\vec{x}_0 \wedge \vec{x}_1",
            "solution": {"signe": "+", "vecteur": "z", "indice": "0", "trigo": "sin", "angle": "α"},
            "description": "Niveau A (1/4) : Base 0 et 1"
        },
        {
            "enonce": r"\vec{z}_2 \wedge \vec{z}_1",
            "solution": {"signe": "-", "vecteur": "y", "indice": "1", "trigo": "sin", "angle": "θ"},
            "description": "Niveau A (1/4) : Base 1 et 2"
        }
    ],
    "B": [  # Niveau B : Moyen
        {
            "enonce": r"\vec{x}_1 \wedge \vec{y}_0",
            "solution": {"signe": "+", "vecteur": "z", "indice": "0", "trigo": "cos", "angle": "α"},
            "description": "Niveau B (2/4) : Projection avec cosinus"
        },
        {
            "enonce": r"\vec{z}_2 \wedge \vec{y}_1",
            "solution": {"signe": "-", "vecteur": "x", "indice": "1", "trigo": "sin", "angle": "θ"},
            "description": "Niveau B (2/4) : Figure 2 vers 1"
        }
    ],
    "C": [  # Niveau C : Intrépide
        {
            "enonce": r"\vec{z}_2 \wedge \vec{x}_1",
            "solution": {"signe": "+", "vecteur": "y", "indice": "1", "trigo": "sin", "angle": "θ"},
            "description": "Niveau C (3/4) : Changement de base (Fig 2 / Fig 1)"
        },
        {
            "enonce": r"\vec{y}_3 \wedge \vec{z}_1",
            "solution": {"signe": "+", "vecteur": "x", "indice": "2", "trigo": "cos", "angle": "β"},
            "description": "Niveau C (3/4) : Fig 3 vers Fig 1"
        }
    ],
    "D": [  # Niveau D : Expert
        {
            "enonce": r"\vec{y}_3 \wedge \vec{x}_1",
            "solution": {"signe": "+", "vecteur": "z", "indice": "2", "trigo": "cos", "angle": "β"},
            "description": "Niveau D (4/4) : Produit vectoriel complexe (Fig 3 / Fig 1)"
        },
        {
            "enonce": r"\vec{z}_3 \wedge \vec{x}_0",
            "solution": {"signe": "-", "vecteur": "y", "indice": "0", "trigo": "sin", "angle": "α"},
            "description": "Niveau D (4/4) : Produit global (Fig 3 / Fig 0)"
        }
    ]
}

NIVEAUX = ["A", "B", "C", "D"]

# --- 1. IDENTIFICATION ---
if "test_started" not in st.session_state:
    st.session_state.test_started = False
    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.reponses_historique = []

if not st.session_state.test_started:
    with st.form("form_identite"):
        st.subheader("Identification")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            nom = st.text_input("Nom").strip()
        with col_b:
            prenom = st.text_input("Prénom").strip()
        with col_c:
            groupe = st.selectbox("Groupe", ["CPGE 1", "CPGE 2", "Autre"])

        if st.form_submit_button("Commencer l'évaluation"):
            if nom and prenom:
                st.session_state.nom = nom
                st.session_state.prenom = prenom
                st.session_state.groupe = groupe
                st.session_state.test_started = True
                
                # Sélection d'une question au hasard par niveau
                st.session_state.questions_selectionnees = [
                    random.choice(BANQUE_QUESTIONS[niv]) for niv in NIVEAUX
                ]
                st.rerun()

# --- 2. EVALUATION PROGRESSIVE (4 QUESTIONS) ---
elif st.session_state.step < 4:

    niveau_courant = NIVEAUX[st.session_state.step]
    q = st.session_state.questions_selectionnees[st.session_state.step]

    st.caption(f"Étudiant : **{st.session_state.nom} {st.session_state.prenom}** ({st.session_state.groupe})")
    st.progress((st.session_state.step) / 4, text=f"Question {st.session_state.step + 1} / 4 — Niveau {niveau_courant}")

    # Image de référence
    try:
        st.image("3Figs_geom.png", use_container_width=True)
    except Exception:
        st.warning("Image '3Figs_geom.png' introuvable dans le dépôt GitHub.")

    st.markdown("---")
    st.write(f"### {q['description']}")
    st.latex(f"{q['enonce']} = \dots")

    # Choix en 5 colonnes
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        signe = st.radio("Signe", ["+", "-"], key=f"signe_{st.session_state.step}")
    with c2:
        vecteur = st.radio("Vecteur", ["x", "y", "z", "0"], key=f"vec_{st.session_state.step}")
    with c3:
        indice = st.radio("Indice", ["0", "1", "2", "3"], key=f"ind_{st.session_state.step}")
    with c4:
        trigo = st.radio("Trigo", ["1", "sin", "cos"], key=f"trigo_{st.session_state.step}")
    with c5:
        angle = st.radio("Angle", ["α", "β", "θ", "γ"], key=f"angle_{st.session_state.step}")

    # Prévisualisation LaTeX
    trigo_str = "" if trigo == "1" else f"\\{trigo}"
    angle_str = "" if trigo == "1" else f"({angle})"
    vec_str = "0" if vecteur == "0" else f"\\vec{{{vecteur}}}_{{{indice}}}"
    formule_latex = f"{signe} {vec_str} {trigo_str}{angle_str}"

    st.markdown("---")
    st.write("**Aperçu de votre réponse :**")
    st.latex(f"{q['enonce']} = {formule_latex}")

    if st.button("Valider cette question ➔", type="primary"):
        sol = q["solution"]
        exact = (
            signe == sol["signe"] and
            vecteur == sol["vecteur"] and
            indice == sol["indice"] and
            trigo == sol["trigo"] and
            angle == sol["angle"]
        )

        if exact:
            st.session_state.score += 5  # 5 points par question = 20/20

        st.session_state.reponses_historique.append({
            "niveau": niveau_courant,
            "reponse": f"{signe} {vecteur}_{indice} {trigo}({angle})",
            "exact": exact
        })

        st.session_state.step += 1
        st.rerun()

# --- 3. BILAN ET ENREGISTREMENT EN FIN DE TEST ---
else:
    note_finale = st.session_state.score
    if note_finale >= 15:
        st.balloons()

    st.subheader(f"Test terminé ! Votre note : {note_finale} / 20")

    # Résumé des résultats
    for idx, resp in enumerate(st.session_state.reponses_historique):
        symbole = "✅" if resp["exact"] else "❌"
        st.write(f"Question {idx+1} (Niveau {resp['niveau']}) : {symbole} Reponse : `{resp['reponse']}`")

    # Synchronisation Google Sheets
    try:
        df_existant = conn.read(ttl=0)
        
        nouvelle_ligne = {
            "Horodatage": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Nom": st.session_state.nom,
            "Prenom": st.session_state.prenom,
            "Groupe": st.session_state.groupe,
            "Note": note_finale,
            "Q1_NivA": st.session_state.reponses_historique[0]["reponse"],
            "Q2_NivB": st.session_state.reponses_historique[1]["reponse"],
            "Q3_NivC": st.session_state.reponses_historique[2]["reponse"],
            "Q4_NivD": st.session_state.reponses_historique[3]["reponse"],
        }
        
        df_maj = pd.concat([df_existant, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
        conn.update(data=df_maj)
        st.success(" Vos résultats ont été enregistrés avec succès dans Google Sheets.")
    except Exception as e:
        st.error(f"Erreur d'enregistrement Google Sheets : {e}")

    st.info("Vous pouvez fermer cette fenêtre.")