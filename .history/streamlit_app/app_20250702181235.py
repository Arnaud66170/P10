# streamlit_app/app.py

import streamlit as st
import pandas as pd
import json
import requests
from pathlib import Path

# === Imports internes (versions simplifiées pour HF Spaces) ===
from utils_streamlit import call_azure_function

# === Configuration interface ===
st.set_page_config(page_title="Recommandation MyContent", layout="wide")
st.title("Recommandation personnalisée d'articles")
st.sidebar.header("Paramètres de recommandation")

# === Configuration Azure (depuis secrets.toml) ===
try:
    AZURE_FUNCTION_URL = st.secrets["AZURE_FUNCTION_URL"]
    AZURE_FUNCTION_KEY = st.secrets["AZURE_FUNCTION_KEY"]
    st.sidebar.success("✅ Configuration Azure chargée")
except Exception as e:
    st.error(f"Erreur configuration Azure : {e}")
    st.stop()

# === Source des données ===
st.sidebar.info("Source : **Azure Blob Storage** ☁️")

# === Chargement des user_ids valides (version correcte) ===
@st.cache_data(ttl=3600)  # Cache pendant 1 heure
def load_user_ids_valid():
    """Charge les user_ids valides depuis outputs/user_ids_valid.json"""
    try:
        # Chemin vers le fichier JSON des vrais user_ids
        project_root = Path(__file__).parent.parent
        user_ids_path = project_root / "outputs" / "user_ids_valid.json"
        
        # Charger le fichier JSON
        with open(user_ids_path, 'r', encoding='utf-8') as f:
            user_ids = json.load(f)
        
        st.sidebar.success(f"✅ {len(user_ids)} utilisateurs valides chargés")
        return sorted(user_ids)  # Trier pour l'affichage
        
    except FileNotFoundError:
        st.sidebar.error(f"❌ Fichier user_ids_valid.json introuvable")
        # Fallback avec des user_ids testés et validés
        return [8, 59021, 96, 330, 397, 452, 1060, 1685]
    except Exception as e:
        st.sidebar.error(f"❌ Erreur chargement utilisateurs: {e}")
        return [8, 59021, 96, 330, 397, 452, 1060, 1685]

# === Chargement des métadonnées articles (version correcte) ===
@st.cache_data(ttl=3600)
def load_articles_metadata():
    """Charge les vraies métadonnées depuis outputs/df_articles_light.parquet"""
    try:
        # Chemin vers le fichier des métadonnées réelles
        project_root = Path(__file__).parent.parent
        articles_path = project_root / "outputs" / "df_articles_light.parquet"
        
        # Charger les vraies métadonnées
        df_articles = pd.read_parquet(articles_path)
        
        # Convertir en dictionnaire pour l'affichage
        articles_dict = {}
        for _, row in df_articles.iterrows():
            article_id = row['article_id']
            # Créer un dictionnaire avec toutes les métadonnées disponibles
            metadata = {}
            for col in df_articles.columns:
                if col != 'article_id':
                    metadata[col] = row[col]
            articles_dict[article_id] = metadata
        
        st.sidebar.success(f"✅ {len(articles_dict)} articles avec métadonnées")
        return articles_dict
        
    except FileNotFoundError:
        st.sidebar.error(f"❌ Fichier df_articles_light.parquet introuvable")
        return {}
    except Exception as e:
        st.sidebar.error(f"❌ Erreur chargement métadonnées: {e}")
        return {}

# === Fonction d'affichage des recommandations (adaptée aux vraies données) ===
def display_recommendation_card(article_id, metadata, rank):
    """Affiche une carte de recommandation avec les vraies métadonnées"""
    with st.container():
        st.markdown(f"### 📄 Recommandation #{rank}")
        st.markdown(f"**Article ID**: {article_id}")
        
        if metadata:
            # Afficher les métadonnées disponibles de manière organisée
            col1, col2 = st.columns(2)
            
            with col1:
                for key, value in list(metadata.items())[:len(metadata)//2]:
                    # Formatage des noms de colonnes
                    display_key = key.replace('_', ' ').title()
                    st.write(f"**{display_key}**: {value}")
            
            with col2:
                for key, value in list(metadata.items())[len(metadata)//2:]:
                    # Formatage des noms de colonnes
                    display_key = key.replace('_', ' ').title()
                    st.write(f"**{display_key}**: {value}")
        else:
            st.write("*Métadonnées non disponibles*")
        
        st.markdown("---")

# Chargement des données
user_ids = load_user_ids_valid()
articles_metadata = load_articles_metadata()

# === Demo rapide ===
if st.sidebar.button("Demo live avec un user préchargé"):
    # Utilise le premier user_id de la liste (garanti valide)
    st.session_state.demo_user = user_ids[0] if user_ids else 59021

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
                    # Affichage des recommandations avec vraies métadonnées
                    st.write(f"**{len(recommendations)} articles recommandés :**")
                    
                    # Affichage en colonnes ou en expanders selon le nombre
                    if len(recommendations) <= 3:
                        # Affichage en colonnes pour 3 articles ou moins
                        cols = st.columns(len(recommendations))
                        for i, article_id in enumerate(recommendations):
                            with cols[i]:
                                st.markdown(f"### 📄 #{i+1}")
                                st.markdown(f"**Article {article_id}**")
                                
                                if article_id in articles_metadata:
                                    metadata = articles_metadata[article_id]
                                    # Afficher les métadonnées principales
                                    for key, value in metadata.items():
                                        display_key = key.replace('_', ' ').title()
                                        if len(str(value)) < 50:  # Valeurs courtes seulement
                                            st.caption(f"**{display_key}**: {value}")
                                else:
                                    st.caption("Métadonnées non disponibles")
                    else:
                        # Affichage en expanders pour plus de 3 articles
                        for i, article_id in enumerate(recommendations):
                            with st.expander(f"📄 Recommandation #{i+1} - Article {article_id}"):
                                if article_id in articles_metadata:
                                    metadata = articles_metadata[article_id]
                                    # Afficher toutes les métadonnées de manière organisée
                                    col1, col2 = st.columns(2)
                                    items = list(metadata.items())
                                    mid = len(items) // 2
                                    
                                    with col1:
                                        for key, value in items[:mid]:
                                            display_key = key.replace('_', ' ').title()
                                            st.write(f"**{display_key}**: {value}")
                                    
                                    with col2:
                                        for key, value in items[mid:]:
                                            display_key = key.replace('_', ' ').title()
                                            st.write(f"**{display_key}**: {value}")
                                else:
                                    st.write(f"**Article ID**: {article_id}")
                                    st.write("*Métadonnées non disponibles*")
                            
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
    
    # Utilisation d'articles réels de tes métadonnées
    if articles_metadata:
        available_articles = list(articles_metadata.keys())[:8]
        st.write(f"**Articles consultés récemment ({len(available_articles)}) :**")
        
        # Affichage en colonnes pour les articles consultés
        for i, article_id in enumerate(available_articles):
            if i % 4 == 0:
                cols = st.columns(4)
            
            col_idx = i % 4
            with cols[col_idx]:
                st.caption(f"📄 **{article_id}**")
                if article_id in articles_metadata:
                    metadata = articles_metadata[article_id]
                    # Afficher une métadonnée représentative
                    first_meta = list(metadata.items())[0]
                    st.caption(f"{first_meta[0]}: {first_meta[1]}")
                else:
                    st.caption("Données simulées")
    else:
        st.info("Métadonnées d'articles non disponibles pour l'historique")

# === Informations de debug ===
with st.expander("🔧 Informations techniques"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Utilisateurs valides", len(user_ids))
        st.metric("Articles en cache", len(articles_metadata))
        st.metric("Mode de fonctionnement", "Azure + Vraies données")
    
    with col2:
        st.write(f"**URL Function App :** {AZURE_FUNCTION_URL}")
        st.write(f"**Plateforme :** Hugging Face Spaces")
        st.write(f"**Utilisateur sélectionné :** {selected_user_id}")
    
    # Affichage des colonnes de métadonnées disponibles
    if articles_metadata:
        sample_article = next(iter(articles_metadata.values()))
        st.write(f"**Métadonnées disponibles:** {', '.join(sample_article.keys())}")
    
    # Test de connectivité
    if st.button("🧪 Tester la connectivité Azure Function"):
        with st.spinner("Test en cours..."):
            try:
                # Test avec le premier user_id valide
                test_user = user_ids[0] if user_ids else 59021
                url_with_key = f"{AZURE_FUNCTION_URL}?code={AZURE_FUNCTION_KEY}"
                payload = {
                    "user_id": test_user,
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
                        st.info(f"Article recommandé pour user {test_user}: {recommendations[0]}")
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
st.markdown("*Déployé sur Hugging Face Spaces avec vraies données*")

# === Instructions de lancement ===
# Pour lancer en local : streamlit run app.py
# Pour déployer : git push vers Hugging Face Spaces
# lien app en ligne : https://huggingface.co/spaces/arnaud66170/p10-recommendation-system