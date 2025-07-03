# streamlit_app/app.py

import streamlit as st
import pandas as pd
import json
import requests

# === Imports internes (versions simplifiées pour HF Spaces) ===
from utils_streamlit import call_azure_function

# === Configuration interface ===
st.set_page_config(page_title="Recommandation MyContent", layout="wide")
st.title("Recommandation personnalisée d'articles")
st.sidebar.header("Paramètres de recommandation")

# === Demo rapide ===
if st.sidebar.button("Demo live avec un user préchargé"):
    st.session_state.demo_user = 8  # Utilise un user_id qu'on sait valide

# === Configuration Azure (depuis secrets.toml) ===
try:
    AZURE_FUNCTION_URL = st.secrets["AZURE_FUNCTION_URL"]
    AZURE_FUNCTION_KEY = st.secrets["AZURE_FUNCTION_KEY"]
    st.sidebar.success("✅ Configuration Azure chargée")
except Exception as e:
    st.error(f"❌ Erreur configuration Azure : {e}")
    st.stop()

# === Source des données ===
st.sidebar.info("Source : **Azure Blob Storage** ☁️")

# === Chargement des user_ids valides (version simplifiée) ===
@st.cache_data(ttl=3600)  # Cache pendant 1 heure
def load_user_ids_valid():
    """Charge les user_ids valides - version simplifiée pour HF Spaces"""
    try:
        # Liste de user_ids valides pré-définie (basée sur tes tests)
        user_ids = [8, 96, 330, 397, 452, 1060, 1685, 1926, 1943, 2186, 
                   2347, 2446, 2664, 2798, 3019, 3147, 3289, 3456, 3621, 3784,
                   3952, 4123, 4298, 4467, 4634, 4809, 4981, 5156, 5328, 5503]
        st.sidebar.success(f"✅ {len(user_ids)} utilisateurs disponibles")
        return user_ids
        
    except Exception as e:
        st.sidebar.error(f"❌ Erreur chargement utilisateurs: {e}")
        # Valeurs par défaut minimales
        return [8, 96, 330, 397, 452]

# === Chargement des métadonnées articles (version simplifiée) ===
@st.cache_data(ttl=3600)
def load_articles_metadata():
    """Simulation des métadonnées d'articles pour l'affichage"""
    # Données de démonstration pour l'affichage des recommandations
    articles_demo = {
        233842: {"title": "Article IA et Machine Learning", "category_id": "tech", "words_count": 1250, "publisher_id": "TechMag"},
        141128: {"title": "Guide Data Science 2025", "category_id": "data", "words_count": 890, "publisher_id": "DataWorld"},
        203218: {"title": "Tendances Cloud Computing", "category_id": "cloud", "words_count": 1450, "publisher_id": "CloudTech"},
        63304: {"title": "Sécurité Cybersécurité", "category_id": "security", "words_count": 980, "publisher_id": "SecuInfo"},
        160152: {"title": "Innovation Blockchain", "category_id": "blockchain", "words_count": 1120, "publisher_id": "CryptoNews"}
    }
    return articles_demo

# Chargement des données
user_ids = load_user_ids_valid()
articles_metadata = load_articles_metadata()

# === Sidebar : Paramètres utilisateur ===
selected_user_id = st.sidebar.selectbox(
    "Utilisateur :", 
    options=user_ids, 
    index=0 if "demo_user" not in st.session_state else (
        user_ids.index(st.session_state.demo_user) if st.session_state.demo_user in user_ids else 0
    )
)

mode = st.sidebar.radio("Méthode :", ["auto", "cbf", "cf", "hybrid"])
alpha = st.sidebar.slider("Pondération (alpha)", 0.0, 1.0, 0.7)  # Valeur par défaut cohérente avec Azure Function
threshold = st.sidebar.slider("Seuil historique utilisateur", 1, 20, 5)
top_n = st.sidebar.slider("Nombre d'articles à recommander", 1, 10, 5)

# === Bouton de recommandation ===
if st.sidebar.button("🚀 Obtenir les recommandations"):
    with st.spinner("Appel de l'Azure Function..."):
        try:
            # Construction de l'URL complète avec la clé
            url_with_key = f"{AZURE_FUNCTION_URL}?code={AZURE_FUNCTION_KEY}"
            
            # Appel direct à l'Azure Function
            payload = {
                "user_id": int(selected_user_id),
                "mode": str(mode),
                "alpha": float(alpha),
                "threshold": int(threshold),
                "top_n": int(top_n),
                "source": "azure"
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url_with_key, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Gestion robuste des différents formats de réponse
            recommendations = []
            
            if isinstance(result, dict) and "error" in result:
                st.error(f"❌ Erreur Azure Function : {result['error']}")
                
            elif isinstance(result, list):
                recommendations = result
                st.success(f"✅ Recommandations pour l'utilisateur {selected_user_id} :")
                
            elif isinstance(result, dict):
                if "recommendations" in result:
                    recommendations = result["recommendations"]
                    status = result.get("status", "SUCCESS")
                    if status == "SUCCESS":
                        st.success(f"✅ Recommandations pour l'utilisateur {selected_user_id} :")
                        # Affichage des métriques de performance
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Mode", result.get('mode', mode))
                        with col2:
                            st.metric("Alpha", result.get('alpha', alpha))
                        with col3:
                            st.metric("Articles", len(recommendations))
                    else:
                        st.warning(f"⚠️ Statut: {status}")
                        
                elif "body" in result and "recommendations" in result["body"]:
                    recommendations = result["body"]["recommendations"]
                    st.success(f"✅ Recommandations pour l'utilisateur {selected_user_id} :")
                    
                else:
                    st.warning("⚠️ Format de réponse Azure inattendu")
                    st.json(result)
                    
            else:
                st.error("❌ Type de réponse Azure non géré")
                st.json(result)
            
            # Affichage des recommandations si on en a
            if recommendations:
                if len(recommendations) == 0:
                    st.info("ℹ️ Aucune recommandation trouvée pour cet utilisateur")
                else:
                    # Affichage des recommandations avec détails
                    st.write(f"**{len(recommendations)} articles recommandés :**")
                    
                    # Création de colonnes pour un affichage plus élégant
                    cols = st.columns(min(len(recommendations), 3))
                    
                    for i, article_id in enumerate(recommendations):
                        col_idx = i % len(cols)
                        with cols[col_idx]:
                            # Utilisation des métadonnées si disponibles
                            if article_id in articles_metadata:
                                article_data = articles_metadata[article_id]
                                title = article_data.get("title", f"Article {article_id}")
                                category = article_data.get("category_id", "Non spécifié")
                                words_count = article_data.get("words_count", "N/A")
                                publisher = article_data.get("publisher_id", "N/A")
                                
                                st.metric(
                                    label=f"#{i+1}",
                                    value=f"Article {article_id}",
                                    delta=f"Cat: {category}"
                                )
                                st.caption(f"📖 {words_count} mots | 🏢 {publisher}")
                                st.caption(f"📄 {title}")
                            else:
                                st.metric(
                                    label=f"#{i+1}",
                                    value=f"Article {article_id}",
                                    delta="Métadonnées non disponibles"
                                )
                            
        except requests.exceptions.Timeout:
            st.error("❌ Timeout lors de l'appel Azure Function")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Erreur réseau : {e}")
        except Exception as e:
            st.error(f"❌ Erreur lors de l'appel Azure : {e}")

# === Simulation affichage historique utilisateur ===
if st.checkbox("📊 Afficher l'historique utilisateur (simulation)"):
    st.subheader(f"Simulation historique de l'utilisateur {selected_user_id}")
    
    # Simulation de données d'historique
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre de clics", 45)
    with col2:
        st.metric("Articles uniques", 32)
    with col3:
        st.metric("Sessions", 8)
    
    # Simulation d'articles consultés
    simulated_articles = [233842, 141128, 203218, 63304, 160152, 178901, 192834, 205671]
    st.write(f"**Articles consultés récemment ({len(simulated_articles)}) :**")
    
    # Affichage en colonnes pour les articles consultés
    for i, article_id in enumerate(simulated_articles[:8]):
        if i % 4 == 0:
            cols = st.columns(4)
        
        col_idx = i % 4
        with cols[col_idx]:
            if article_id in articles_metadata:
                article_data = articles_metadata[article_id]
                title = article_data.get("title", f"Article {article_id}")
                category = article_data.get("category_id", "N/A")
                st.caption(f"📄 **{article_id}**")
                st.caption(f"Cat: {category}")
            else:
                st.caption(f"📄 **{article_id}**")
                st.caption("Données simulées")

# === Informations de debug ===
with st.expander("🔧 Informations techniques"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Utilisateurs valides", len(user_ids))
        st.metric("Articles en cache", len(articles_metadata))
        st.metric("Mode de fonctionnement", "Azure + Simulation")
    
    with col2:
        st.write(f"**URL Function App :** {AZURE_FUNCTION_URL}")
        st.write(f"**Plateforme :** Hugging Face Spaces")
        st.write(f"**Utilisateur sélectionné :** {selected_user_id}")
    
    # Test de connectivité
    if st.button("🧪 Tester la connectivité Azure Function"):
        with st.spinner("Test en cours..."):
            try:
                # Test avec user_id 8 (connu pour fonctionner)
                url_with_key = f"{AZURE_FUNCTION_URL}?code={AZURE_FUNCTION_KEY}"
                payload = {
                    "user_id": 8,
                    "mode": "auto",
                    "top_n": 1,
                    "source": "azure"
                }
                headers = {"Content-Type": "application/json"}
                
                response = requests.post(url_with_key, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                test_result = response.json()
                
                if isinstance(test_result, dict) and "recommendations" in test_result:
                    recommendations = test_result["recommendations"]
                    if len(recommendations) > 0:
                        st.success("✅ Azure Function accessible et fonctionnelle")
                        st.info(f"Article recommandé: {recommendations[0]}")
                    else:
                        st.warning("⚠️ Azure Function répond mais aucune recommandation")
                else:
                    st.warning("⚠️ Azure Function accessible mais format inattendu")
                    st.json(test_result)
                    
            except Exception as e:
                st.error(f"❌ Erreur de connectivité: {e}")

# === Footer ===
st.markdown("---")
st.markdown("**MyContent Recommendation System** - Powered by Azure Functions ☁️")
st.markdown("*Déployé sur Hugging Face Spaces avec Docker*")

# === Instructions de lancement ===
# Pour lancer en local : streamlit run app.py
# Pour déployer : git push vers Hugging Face Spaces
# lien app en ligne : https://huggingface.co/spaces/arnaud66170/p10-recommendation-system