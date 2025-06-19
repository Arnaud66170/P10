# streamlit_app/app.py

import streamlit as st
import requests
import pandas as pd
import os
import sys

# Chargement df_articles depuis outputs
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(project_root, "src"))

from data_preprocessing import load_metadata  # Charge automatiquement CSV ou Parquet

# Chargement des métadonnées articles
df_articles = load_metadata(os.path.join(project_root, "outputs", "df_articles.parquet"))

# Titre de l'app
st.title("📰 Recommandation d'articles personnalisée")

# Affiche les colonnes disponibles pour debug rapide
if st.sidebar.checkbox("Afficher les colonnes disponibles dans df_articles"):
    st.sidebar.write(df_articles.columns.tolist())

# Saisie de l'ID utilisateur
user_id = st.number_input("Identifiant utilisateur :", min_value=0, value=59021)

# Choix du mode
mode = st.selectbox("Méthode de recommandation :", options=["auto", "cbf", "cf"])
alpha = st.slider("Pondération (alpha) hybride", 0.0, 1.0, 0.5)
threshold = st.slider("Seuil historique utilisateur", 1, 20, 5)
top_n = st.slider("Nombre d'articles à recommander :", 1, 10, 5)

# URL Azure Function (à adapter pour la prod)
url = "http://localhost:7071/api/getRecommendations"

if st.button("Obtenir des recommandations"):
    with st.spinner("Chargement des recommandations..."):
        params = {
            "user_id": user_id,
            "mode": mode,
            "alpha": alpha,
            "threshold": threshold,
            "top_n": top_n
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # force erreur si 4xx/5xx
            data = response.json()
            reco_ids = data.get("recommendations", [])

            if len(reco_ids) == 0:
                st.warning("Aucune recommandation retournée.")
            else:
                # Affichage dynamique avec fallback si certaines colonnes sont manquantes
                columns_to_show = ["article_id", "title", "category_id", "publisher_id"]
                valid_columns = [col for col in columns_to_show if col in df_articles.columns]
                reco_df = df_articles[df_articles["article_id"].isin(reco_ids)]

                st.subheader("📌 Articles recommandés :")
                st.dataframe(reco_df[valid_columns] if valid_columns else reco_df)

        except Exception as e:
            st.error(f"Erreur API : {str(e)}")

# Lancement local :
# cd streamlit_app
# streamlit run app.py
