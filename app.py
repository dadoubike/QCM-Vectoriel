import datetime
import random
import time
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuration de la page
st.set_page_config(page_title="QCM Express - Mécanique", page_icon="⚡")

# Connexion à Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INITIALISATION DE LA SESSION ---
if "test_started" not in st.session_state:
    st.session_state.test_started = False
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# Génération aléatoire des vecteurs (une seule fois par session)
if "q1_vecs" not in st.session_state:
    # Question 1 : Produit scalaire u . v
    u = np.random.randint(-5, 6, size=3)
    v = np.random.randint(-5, 6, size=3)
    sol1 = int(np.dot(u, v))
    st.session_state.q1_vecs = (u, v, sol1)

if "q2_vecs" not in st.session_state:
    # Question 2 : Produit vectoriel u x v (composante Z)
    u2 = np.random.randint(-4, 5, size=2)
    v2 = np.random.randint(-4, 5, size=2)
    # (u_x * v_y) - (u_y * v_x)
    sol2 = int(u2[0] * v2[1] - u2[1] * v2[0])
    st.session_state.q2_vecs = (u2, v2, sol2)

# --- DÉROULEMENT DU TEST ---

st.title("⚡ Test Flash : Outils Vectoriels")

# Étape 1 : Inscription de l'étudiant
if not st.session_state.test_started:
    st.subheader("Identification")
    nom = st.text_input("Nom :")
    prenom = st.text_input("Prénom :")
    groupe = st.selectbox("Groupe :", ["G1", "G2", "G3", "G4"])

    if st.button("Lancer le test (Délai : 3 min)"):
        if nom.strip() and prenom.strip():
            st.session_state.nom = nom
            st.session_state.prenom = prenom
            st.session_state.groupe = groupe
            st.session_state.test_started = True
            st.session_state.start_time = time.time()
            st.rerun()
        else:
            st.warning("Veuillez renseigner votre nom et prénom.")

# Étape 2 : QCM et Timer
elif st.session_state.test_started and not st.session_state.submitted:
    # ⏱️ Gestion du Timer (3 minutes = 180s)
    DUREE_MAX = 180
    ecoule = time.time() - st.session_state.start_time
    restant = int(DUREE_MAX - ecoule)

    if restant <= 0:
        st.error("⏳ Temps écoulé ! Soumission automatique de vos réponses.")
        st.session_state.submitted = True
        st.rerun()

    # Affichage du chrono
    mins, secs = divmod(restant, 60)
    st.metric("Temps restant", f"{mins:02d}:{secs:02d}")

    st.write(
        f"**Candidat :** {st.session_state.prenom} {st.session_state.nom} ({st.session_state.groupe})"
    )
    st.divider()

    # Formulaire de réponse
    with st.form("quiz_form"):
        # QUESTION 1 : Produit Scalaire
        u, v, sol1 = st.session_state.q1_vecs
        st.subheader("Question 1 : Produit Scalaire")
        st.latex(
            rf"\vec{{u}} = \begin{{pmatrix}} {u[0]} \\ {u[1]} \\ {u[2]} \end{{pmatrix}}, \quad \vec{{v}} = \begin{{pmatrix}} {v[0]} \\ {v[1]} \\ {v[2]} \end{{pmatrix}}"
        )
        resp1 = st.number_input(
            "Calculez le produit scalaire u · v :", step=1, key="r1"
        )

        st.divider()

        # QUESTION 2 : Produit Vectoriel
        u2, v2, sol2 = st.session_state.q2_vecs
        st.subheader("Question 2 : Produit Vectoriel (Composante Z)")
        st.latex(
            rf"\vec{{u}} = \begin{{pmatrix}} {u2[0]} \\ {u2[1]} \\ 0 \end{{pmatrix}}, \quad \vec{{v}} = \begin{{pmatrix}} {v2[0]} \\ {v2[1]} \\ 0 \end{{pmatrix}}"
        )
        resp2 = st.number_input(
            "Calculez la composante suivant z du produit vectoriel (u ∧ v)_z :",
            step=1,
            key="r2",
        )

        submit_btn = st.form_submit_button("Envoyer mes réponses")

        if submit_btn:
            st.session_state.submitted = True
            st.session_state.resp1 = resp1
            st.session_state.resp2 = resp2
            st.rerun()

    # Rafraîchir la page chaque seconde pour le timer
    time.sleep(1)
    st.rerun()

# Étape 3 : Calcul de la note et Envoi Google Sheets
elif st.session_state.submitted:
    u, v, sol1 = st.session_state.q1_vecs
    u2, v2, sol2 = st.session_state.q2_vecs

    r1 = st.session_state.get("resp1", None)
    r2 = st.session_state.get("resp2", None)

    # Bareme sur 20
    note = 0
    if r1 == sol1:
        note += 10
    if r2 == sol2:
        note += 10

    st.success("✅ Vos réponses ont été transmises avec succès !")
    st.subheader(f"Votre Note : {note} / 20")

    # Enregistrement dans Google Sheets
    try:
        df_existant = conn.read(ttl=0)
        nouvelle_ligne = {
            "Horodatage": datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Nom": st.session_state.nom,
            "Prenom": st.session_state.prenom,
            "Groupe": st.session_state.groupe,
            "Note": note,
            "Q1_Reponse": r1,
            "Q1_Exact": sol1,
            "Q2_Reponse": r2,
            "Q2_Exact": sol2,
        }
        df_maj = pd.concat(
            [df_existant, pd.DataFrame([nouvelle_ligne])], ignore_index=True
        )
        conn.update(data=df_maj)
    except Exception as e:
        st.error(f"Erreur Google Sheets : {e}")

    st.info("Vous pouvez fermer cette fenêtre.")