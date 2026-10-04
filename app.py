import datetime
import random
import time
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuration de la page
st.set_page_config(page_title="QCM - Produits Vectoriels", page_icon="📐")

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
    ],
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
}

NIVEAUX = ["A", "B", "C", "D"]

# --- 1. IDENTIFICATION ---
if "test_started" not in st.session_state:
    st.session_state.test_started = False
    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.reponses_historique = []
    st.session_state.show_popup = False

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

# --- 2. EVALUATION PROGRESSIVE AVEC CHRONOMÈTRE NATIVE EN ARRIÈRE-PLAN ---
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
            label="⏱️ Temps restant",
            value=f"{minutes:02d}:{secondes:02d}",
            delta_color=color,
        )

    afficher_chronometre()

    if st.session_state.get("show_popup", False):
        st.info("⏱️ **Le test dure 5 minutes maximum.** Répondez le plus rapidement possible !")
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
            signe = st.radio("Signe", ["+", "-"], key=f"signe_{st.session_state.step}")
        with c2:
            trigo = st.radio("Trigo", ["1", "sin", "cos"], key=f"trigo_{st.session_state.step}")
        with c3:
            angle = st.radio("Angle", ["α", "θ", "β"], key=f"angle_{st.session_state.step}")
        with c4:
            vecteur = st.radio("Vecteur", ["x", "y", "z", "0"], key=f"vec_{st.session_state.step}")
        with c5:
            indice = st.radio("Indice", ["0", "1", "2", "3"], key=f"ind_{st.session_state.step}")

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
                st.session_state.score += 5

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

    # Affichage des corrections
    for idx, resp in enumerate(st.session_state.reponses_historique):
        symbole = "✅" if resp["exact"] else "❌"
        st.write(f"**Question {idx+1} (Niveau {resp['niveau']}) : {symbole}**")
        st.latex(f"{resp['enonce']} = {resp['reponse_display']}")

    st.markdown("---")

    q_ans = len(st.session_state.reponses_historique)
    q1_val = st.session_state.reponses_historique[0]["reponse_sheet"] if q_ans > 0 else "'Non répondu"
    q2_val = st.session_state.reponses_historique[1]["reponse_sheet"] if q_ans > 1 else "'Non répondu"
    q3_val = st.session_state.reponses_historique[2]["reponse_sheet"] if q_ans > 3 else "'Non répondu"
    q4_val = st.session_state.reponses_historique[3]["reponse_sheet"] if q_ans > 3 else "'Non répondu"

    # Enregistrement + Affichage du classement
    try:
        df_existant = conn.read(ttl=0)
        
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
        
        df_maj = pd.concat(
            [df_existant, pd.DataFrame([nouvelle_ligne])], ignore_index=True
        )
        conn.update(data=df_maj)
        st.success(" Vos résultats ont été enregistrés dans Google Sheets.")

        # --- GENERATION DU CLASSEMENT (LEADERBOARD) ---
        st.subheader("🏆 Classement Général (Top Score & Vitesse)")

        # Nettoyage et formatage du DataFrame pour le tri
        df_leaderboard = df_maj.copy()
        
        # Nettoyage de la colonne Temps_Passe pour le tri
        df_leaderboard["Temps_Clean"] = df_leaderboard["Temps_Passe"].astype(str).str.replace("'", "")
        df_leaderboard["Note"] = pd.to_numeric(df_leaderboard["Note"], errors="coerce")

        # Tri : Note décroissante, puis Temps croissant
        df_leaderboard = df_leaderboard.sort_values(
            by=["Note", "Temps_Clean"], ascending=[False, True]
        ).reset_index(drop=True)

        # Ajout du rang (1, 2, 3...)
        df_leaderboard.index = df_leaderboard.index + 1
        df_leaderboard.index.name = "Rang"

        # Sélection des colonnes à afficher
        df_display = df_leaderboard[["Nom", "Prenom", "Classe", "Note", "Temps_Clean"]].rename(
            columns={"Temps_Clean": "Temps"}
        )

        st.dataframe(df_display, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur lors du calcul du classement / Google Sheets : {e}")

    st.info("Vous pouvez fermer cette fenêtre.")