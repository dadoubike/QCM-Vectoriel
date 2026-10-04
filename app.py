import datetime
import random
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuration de la page
st.set_page_config(page_title="QCM - Produits Vectoriels", page_icon="📐")

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📐 QCM : Produits Vectoriels Progressifs")

# Équivalences géométriques des axes (selon les figures de changement de base)
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
    ],
    "B": [
        # Cosinus de la première figure
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
        # Fin de la première figure en cosinus
        {
            "type": "colonnes",
            "enonce": r"\vec{z}_2 \wedge \vec{y}_1",
            "solution": {
                "signe": "-",
                "trigo": "1",
                "angle": "θ",
                "vecteur": "x",
                "indice": "2",
            },
            "description": "Niveau B (2/4) : Base 2 et 1",
        },
    ],  # <-- Virgule fermante de la liste "B" ajoutée ici
    "C": [
        {
            "type": "qcm",
            "enonce": r"\vec{z}_2 \wedge \vec{x}_1",
            "propositions": [
                r"+\cos(\theta)\vec{y}_1",
                r"+\cos(\theta)\vec{y}_2",
                r"-\cos(\theta)\vec{y}_1",
                r"+\sin(\theta)\vec{y}_1",
            ],
            "correct_expressions": [
                r"+\cos(\theta)\vec{y}_1",
                r"+\cos(\theta)\vec{y}_2",
            ],
            "description": "Niveau C (3/4) : Fig 2 vers Fig 1",
        },
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
    ],
    "D": [
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
        }
    ],
}  # <-- Accolade fermante du dictionnaire BANQUE_QUESTIONS ajoutée ici

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
            classe = st.selectbox("Classe", ["PCSI 1", "PCSI 2"])

        if st.form_submit_button("Commencer l'évaluation"):
            if nom and prenom:
                st.session_state.nom = nom
                st.session_state.prenom = prenom
                st.session_state.classe = classe
                st.session_state.test_started = True

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

# --- 2. EVALUATION PROGRESSIVE ---
elif st.session_state.step < 4:

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

    try:
        st.image("3Figs_geom.png", use_container_width=True)
    except Exception:
        st.warning("Image '3Figs_geom.png' introuvable.")

    st.markdown("---")
    st.write(f"### {q['description']}")
    st.latex(f"{q['enonce']} = \dots")

    # --- CAS 1 : INTERFACE 5 COLONNES (Niveaux A & B) ---
    if q["type"] == "colonnes":
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            signe = st.radio(
                "Signe", ["+", "-"], key=f"signe_{st.session_state.step}"
            )
        with c2:
            trigo = st.radio(
                "Trigo", ["1", "sin", "cos"], key=f"trigo_{st.session_state.step}"
            )
        with c3:
            angle = st.radio(
                "Angle", ["α", "θ", "β"], key=f"angle_{st.session_state.step}"
            )
        with c4:
            vecteur = st.radio(
                "Vecteur", ["x", "y", "z", "0"], key=f"vec_{st.session_state.step}"
            )
        with c5:
            indice = st.radio(
                "Indice", ["0", "1", "2", "3"], key=f"ind_{st.session_state.step}"
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

            vecteur_valide = verifier_vecteur_egal(
                vecteur, indice, sol["vecteur"], sol["indice"]
            )

            exact = (
                signe == sol["signe"]
                and trigo == sol["trigo"]
                and angle == sol["angle"]
                and vecteur_valide
            )

            if exact:
                st.session_state.score += 5

            # Représentation propre pour le bilan LaTeX
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
                st.session_state.score += 5

            st.session_state.reponses_historique.append({
                "niveau": niveau_courant,
                "enonce": q["enonce"],
                "reponse_display": choix_select,
                "reponse_sheet": f"'{choix_select}",
                "exact": exact,
            })
            st.session_state.step += 1
            st.rerun()

# --- 3. BILAN ET SYNCHRONISATION ---
else:
    note_finale = st.session_state.score
    if note_finale >= 15:
        st.balloons()

    st.subheader(f"Test terminé ! Votre note : {note_finale} / 20")
    st.markdown("---")

    for idx, resp in enumerate(st.session_state.reponses_historique):
        symbole = "✅" if resp["exact"] else "❌"
        st.write(f"**Question {idx+1} (Niveau {resp['niveau']}) : {symbole}**")
        st.latex(f"{resp['enonce']} = {resp['reponse_display']}")

    try:
        df_existant = conn.read(ttl=0)
        nouvelle_ligne = {
            "Horodatage": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Nom": st.session_state.nom,
            "Prenom": st.session_state.prenom,
            "Classe": st.session_state.classe,
            "Note": note_finale,
            "Q1_NivA": st.session_state.reponses_historique[0]["reponse_sheet"],
            "Q2_NivB": st.session_state.reponses_historique[1]["reponse_sheet"],
            "Q3_NivC": st.session_state.reponses_historique[2]["reponse_sheet"],
            "Q4_NivD": st.session_state.reponses_historique[3]["reponse_sheet"],
        }
        df_maj = pd.concat(
            [df_existant, pd.DataFrame([nouvelle_ligne])], ignore_index=True
        )
        conn.update(data=df_maj)
        st.success(" Vos résultats ont été enregistrés dans Google Sheets.")
    except Exception as e:
        st.error(f"Erreur Google Sheets : {e}")

    st.info("Vous pouvez fermer cette fenêtre.")