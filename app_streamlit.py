# app_streamlit.py

import os
import json
import streamlit as st
import requests
from dotenv import load_dotenv

# Chargement des variables d'environnement (.env.prod recommandé)
load_dotenv(dotenv_path=".env.prod")

AZURE_FUNCTION_URL = os.getenv("AZURE_FUNCTION_URL")
AZURE_FUNCTION_KEY = os.getenv("AZURE_FUNCTION_KEY")

# Interface Streamlit
st.title("Système de recommandation (Projet P10)")

# Saisie utilisateur
user_id = st.number_input("ID utilisateur :", min_value=1, step=1, value=59021)
mode = st.selectbox("Mode de recommandation :", ["auto", "cb", "cf"])
alpha = st.slider("Alpha (hybridation)", 0.0, 1.0, 0.5, 0.05)
top_n = st.slider("Nombre d'articles recommandés :", 1, 10, 5)

# Bouton de lancement
if st.button("Obtenir des recommandations"):

    # Construction de la requête
    headers = {
        "Content-Type": "application/json",
        "x-functions-key": AZURE_FUNCTION_KEY
    }

    payload = {
        "user_id": int(user_id),
        "mode": mode,
        "alpha": alpha,
        "top_n": top_n,
        "source": "azure"
    }

    try:
        # Requête POST à Azure Function
        response = requests.post(
            url=AZURE_FUNCTION_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )

        # Affichage de la réponse
        if response.status_code == 200:
            recommandations = response.json()
            st.success("Recommandations reçues !")
            for i, article_id in enumerate(recommandations, 1):
                st.write(f"{i}. Article ID : {article_id}")
        elif response.status_code == 401:
            st.error("Erreur 401 : Clé d’API absente ou invalide.")
        elif response.status_code == 500:
            st.error(f"Erreur 500 : problème côté Azure.\nDétails : {response.text}")
        else:
            st.warning(f"Réponse inattendue ({response.status_code}) : {response.text}")

    except Exception as e:
        st.error(f"Erreur lors de la requête : {str(e)}")
