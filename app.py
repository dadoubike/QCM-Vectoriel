import datetime
import random
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuration de la page
st.set_page_config(page_title="QCM - Produit Vectoriel", page_icon="📐")

# Initialisation de la connexion Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📐 QCM : Produit Vectoriel & Figures de Changement de Base")

# --- 1. IDENTIFICATION ---
if "submitted" not in st.session_state:
    st.session_state.submitted = False

with st.form("form_identite"):
    st.subheader("Identification")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        nom = st.text_input("Nom").strip()
    with col_b:
        prenom = st.text_input("Prénom").strip()
    with col_c:
        groupe = st.selectbox("Groupe / Classe", ["CPGE 1", "CPGE 2", "Autre"])

    start_btn = st.form_submit_button("Commencer le test")
    if start_btn and nom and prenom:
        st.session_state.nom = nom
        st.session_state.prenom = prenom
        st.session_state.groupe = groupe
        st.session_state.test_started = True

# --- 2. GENERATION DE LA QUESTION ---
if st.session_state.get("test_started", False) and not st.session_state.submitted:

    st.info(f"Élève : **{st.session_state.nom} {st.session_state.prenom}** ({st.session_state.groupe})")

    # On fixe les paramètres du problème dans la session pour qu'ils ne changent pas lors des clics
    if "question_data" not in st.session_state:
        # Solution de l'exemple : z2 ^ y3 = + x3 sin(beta)
        st.session_state.question_data = {
            "enonce": r"\vec{z}_2 \wedge \vec{y}_3",
            "solution": {
                "signe": "+",
                "vecteur": "x",
                "indice": "3",
                "trigo": "sin",
                "angle": "β"
            }
        }

    q = st.session_state.question_data

    st.markdown("---")
    st.write("### Déterminez l'expression du produit vectoriel suivant :")
    st.latex(f"{q['enonce']} = \dots")

    # Image ou rappel des figures de projection si nécessaire
    # st.image("figure_changement_base.png")

    st.write("#### Sélectionnez les composants de la réponse :")

    # --- Saisie par colonnes (Radio buttons) ---
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        signe = st.radio("Signe", ["+", "-"], key="rad_signe")
    with c2:
        vecteur = st.radio("Vecteur", ["x", "y", "z", "0"], key="rad_vec")
    with c3:
        indice = st.radio("Indice", ["1", "2", "3", "4"], key="rad_ind")
    with c4:
        trigo = st.radio("Trigo", ["1", "sin", "cos"], key="rad_trigo")
    with c5:
        angle = st.radio("Angle", ["α", "β", "γ"], key="rad_angle")

    # Formattage LaTeX dynamique pour prévisualisation par l'élève
    if trigo == "1":
        trigo_str = ""
        angle_str = ""
    else:
        trigo_str = f"\\{trigo}"
        angle_str = f"({angle})"

    vec_str = f"\\vec{{{vecteur}}}_{{{indice}}}" if vecteur != "0" else "0"
    formule_latex = f"{signe} {vec_str} {trigo_str}{angle_str}"

    st.markdown("---")
    st.write("**Aperçu de votre réponse :**")
    st.latex(f"{q['enonce']} = {formule_latex}")

    # Bouton de validation
    if st.button("Envoyer la réponse", type="primary"):
        st.session_state.user_choice = {
            "signe": signe,
            "vecteur": vecteur,
            "indice": indice,
            "trigo": trigo,
            "angle": angle
        }
        st.session_state.formule_text = f"{signe} {vecteur}_{indice} {trigo}({angle})"
        st.session_state.submitted = True
        st.rerun()

# --- 3. CALCUL DE LA NOTE ET ENREGISTREMENT ---
elif st.session_state.submitted:

    q = st.session_state.question_data
    sol = q["solution"]
    user = st.session_state.user_choice

    # Vérification exacte des 5 composantes
    est_correct = (
        user["signe"] == sol["signe"] and
        user["vecteur"] == sol["vecteur"] and
        user["indice"] == sol["indice"] and
        user["trigo"] == sol["trigo"] and
        user["angle"] == sol["angle"]
    )

    note = 20 if est_correct else 0

    st.subheader(f"Votre Note : {note} / 20")
    if est_correct:
        st.success("✅ Bravo, votre réponse est exacte !")
    else:
        st.error(f"❌ Réponse incorrecte. La solution était : {sol['signe']} {sol['vecteur']}_{sol['indice']} {sol['trigo']}({sol['angle']})")

    # Enregistrement dans Google Sheets
    try:
        df_existant = conn.read(ttl=0)
        
        nouvelle_ligne = {
            "Horodatage": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Nom": st.session_state.nom,
            "Prenom": st.session_state.prenom,
            "Groupe": st.session_state.groupe,
            "Note": note,
            "Reponse_Eleve": st.session_state.formule_text,
            "Est_Exact": est_correct
        }

        df_maj = pd.concat([df_existant, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
        conn.update(data=df_maj)
        st.success(" Vos résultats ont été enregistrés avec succès dans Google Sheets.")
    except Exception as e:
        st.error(f"Erreur lors de la synchronisation avec Google Sheets : {e}")

    st.info("Vous pouvez fermer cette fenêtre.")