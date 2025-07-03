# streamlit_app/app.py

import streamlit as st
import pandas as pd
import json
import requests
import os
from io import BytesIO

# === Configuration interface (DOIT ÊTRE EN PREMIER) ===
st.set_page_config(page_title="Recommandation MyContent", layout="wide")

# === DIAGNOSTIC - Variables d'environnement ===
st.write("**DEBUG - Variables d'environnement :**")
azure_vars = {k: v[:30] + "..." if len(v) > 30 else v for k, v in os.environ.items() if 'AZURE' in k.upper()}
st.write(azure_vars)
st.title("Recommandation personnalisée d'articles")
st.sidebar.header("Paramètres de recommandation")

# === Configuration Azure (lecture directe des secrets) ===
try:
    # Lecture directe des variables d'environnement HF Spaces
    AZURE_FUNCTION_URL = os.getenv("AZURE_FUNCTION_URL")
    AZURE_FUNCTION_KEY = os.getenv("AZURE_FUNCTION_KEY") 
    AZURE_CONN_STR = os.getenv("AZURE_CONN_STR")
    
    st.write("**DEBUG - Valeurs lues :**")
    st.write(f"AZURE_FUNCTION_URL: {AZURE_FUNCTION_URL}")
    st.write(f"AZURE_FUNCTION_KEY: {AZURE_FUNCTION_KEY[:10]}..." if AZURE_FUNCTION_KEY else "None")
    st.write(f"AZURE_CONN_STR: {'OK' if AZURE_CONN_STR else 'None'}")
    
    if not AZURE_FUNCTION_URL or not AZURE_FUNCTION_KEY:
        st.error("Configuration Azure Function manquante")
        # Construction manuelle de l'URL qui marche
        AZURE_FUNCTION_URL_COMPLETE = "https://p10recommandationfresh.azurewebsites.net/api/get_recommendations?code=p6zkcJClI6UkOKquY5LAX7-JxZGo9En1SWPlCI0oRV4bAzFuOAmhPQ=="
        st.warning("Utilisation de l'URL de fallback")
    else:
        # Construction de l'URL complète
        AZURE_FUNCTION_URL_COMPLETE = f"{AZURE_FUNCTION_URL}?code={AZURE_FUNCTION_KEY}"
        st.success("Configuration Azure chargée depuis les secrets")
    
    if not AZURE_CONN_STR:
        st.error("Connection string Azure Storage manquante")
        st.stop()
    
    st.sidebar.success("Configuration Azure chargée")
except Exception as e:
    st.error(f"Erreur configuration Azure : {e}")
    st.stop()

# === Source des données ===
st.sidebar.info("Source : **Azure Blob Storage**")

# === Chargement des user_ids depuis Azure Blob Storage ===
@st.cache_data(ttl=3600)
def load_user_ids_from_azure():
    """Charge les user_ids valides depuis Azure Blob Storage"""
    try:
        from azure.storage.blob import BlobServiceClient
        
        blob_service = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
        container_name = "artefacts-fresh"
        blob_name = "user_ids_valid.json"
        
        blob_client = blob_service.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        blob_data = blob_client.download_blob().readall()
        user_ids = json.loads(blob_data.decode('utf-8'))
        
        st.sidebar.success(f"{len(user_ids)} utilisateurs chargés depuis Azure")
        return sorted(user_ids)
        
    except Exception as e:
        st.sidebar.error(f"Erreur chargement user_ids depuis Azure: {e}")
        return [8, 59021, 96, 330, 397, 452, 1060, 1685, 1926, 1943]

# === Chargement des métadonnées depuis Azure Blob Storage ===
@st.cache_data(ttl=3600)
def load_articles_metadata_from_azure():
    """Charge les métadonnées articles depuis Azure Blob Storage"""
    try:
        from azure.storage.blob import BlobServiceClient
        
        blob_service = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
        container_name = "artefacts-fresh"
        blob_name = "df_articles_light.parquet"
        
        blob_client = blob_service.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        blob_data = blob_client.download_blob().readall()
        df_articles = pd.read_parquet(BytesIO(blob_data))
        
        articles_dict = {}
        for _, row in df_articles.iterrows():
            article_id = row['article_id']
            metadata = {}
            for col in df_articles.columns:
                if col != 'article_id' and col != 'embedding':
                    metadata[col] = row[col]
            articles_dict[article_id] = metadata
        
        st.sidebar.success(f"{len(articles_dict)} articles chargés depuis Azure")
        return articles_dict
        
    except Exception as e:
        st.sidebar.error(f"Erreur chargement métadonnées depuis Azure: {e}")
        return {}

# Chargement des données depuis Azure
user_ids = load_user_ids_from_azure()
articles_metadata = load_articles_metadata_from_azure()

# === Sidebar : Paramètres utilisateur ===
selected_user_id = st.sidebar.selectbox("Utilisateur :", options=user_ids, index=0)
mode = st.sidebar.radio("Méthode :", ["auto", "cbf", "cf", "hybrid"])
alpha = st.sidebar.slider("Pondération (alpha)", 0.0, 1.0, 0.7)
threshold = st.sidebar.slider("Seuil historique utilisateur", 1, 20, 5)
top_n = st.sidebar.slider("Nombre d'articles à recommander", 1, 10, 5)

# === Bouton de recommandation ===
if st.sidebar.button("Obtenir les recommandations"):
    with st.spinner("Appel de l'Azure Function..."):
        try:
            # Appel direct à l'Azure Function avec GET params
            params = {
                "user_id": int(selected_user_id),
                "mode": str(mode),
                "alpha": float(alpha),
                "threshold": int(threshold),
                "top_n": int(top_n),
                "source": "azure"
            }
            
            st.write(f"**URL utilisée :** {AZURE_FUNCTION_URL_COMPLETE}")
            
            response = requests.get(AZURE_FUNCTION_URL_COMPLETE, params=params, timeout=30)
            response.raise_for_status()
            
            # DEBUG INFO
            st.write("**DEBUG INFO:**")
            st.write(f"Status Code: {response.status_code}")
            st.write(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
            st.write(f"Response Length: {len(response.text)}")
            
            # Essayer le JSON
            if response.text.strip():
                try:
                    result = response.json()
                except json.JSONDecodeError as e:
                    st.error(f"JSON Error: {e}")
                    st.write("**Raw Response (premiers 1000 caractères):**")
                    st.code(response.text[:1000])
                    st.stop()
            else:
                st.error("Réponse vide de l'Azure Function")
                st.stop()
            
            # Gestion des recommandations
            recommendations = []
            
            if isinstance(result, dict) and "error" in result:
                st.error(f"Erreur Azure Function : {result['error']}")
                
            elif isinstance(result, list):
                recommendations = result
                st.success(f"Recommandations pour l'utilisateur {selected_user_id} :")
                
            elif isinstance(result, dict):
                if "recommendations" in result:
                    recommendations = result["recommendations"]
                    status = result.get("status", "SUCCESS")
                    if status == "SUCCESS":
                        st.success(f"Recommandations pour l'utilisateur {selected_user_id} :")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Mode", result.get('mode', mode))
                        with col2:
                            st.metric("Alpha", result.get('alpha', alpha))
                        with col3:
                            st.metric("Articles", len(recommendations))
                    else:
                        st.warning(f"Statut: {status}")
                        
                elif "body" in result and "recommendations" in result["body"]:
                    recommendations = result["body"]["recommendations"]
                    st.success(f"Recommandations pour l'utilisateur {selected_user_id} :")
                    
                else:
                    st.warning("Format de réponse Azure inattendu")
                    st.json(result)
                    
            else:
                st.error("Type de réponse Azure non géré")
                st.json(result)
            
            # Affichage des recommandations
            if recommendations:
                if len(recommendations) == 0:
                    st.info("Aucune recommandation trouvée pour cet utilisateur")
                else:
                    st.write(f"**{len(recommendations)} articles recommandés :**")
                    
                    for i, article_id in enumerate(recommendations):
                        with st.expander(f"Recommandation #{i+1} - Article {article_id}"):
                            if article_id in articles_metadata:
                                metadata = articles_metadata[article_id]
                                col1, col2 = st.columns(2)
                                items = list(metadata.items())
                                mid = len(items) // 2
                                
                                with col1:
                                    for key, value in items[:mid]:
                                        display_key = key.replace('_', ' ').title()
                                        if key == 'created_at_ts':
                                            import datetime
                                            date_obj = datetime.datetime.fromtimestamp(value/1000)
                                            value = date_obj.strftime('%d/%m/%Y %H:%M')
                                            display_key = "Date de création"
                                        st.write(f"**{display_key}**: {value}")
                                
                                with col2:
                                    for key, value in items[mid:]:
                                        display_key = key.replace('_', ' ').title()
                                        if key == 'created_at_ts':
                                            import datetime
                                            date_obj = datetime.datetime.fromtimestamp(value/1000)
                                            value = date_obj.strftime('%d/%m/%Y %H:%M')
                                            display_key = "Date de création"
                                        st.write(f"**{display_key}**: {value}")
                            else:
                                st.write(f"**Article ID**: {article_id}")
                                st.write("*Métadonnées non disponibles*")
                            
        except requests.exceptions.Timeout:
            st.error("Timeout lors de l'appel Azure Function")
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur réseau : {e}")
        except Exception as e:
            st.error(f"Erreur lors de l'appel Azure : {e}")

# === Footer ===
st.markdown("---")
st.markdown("**MyContent Recommendation System** - Azure Cloud")
st.markdown("*User IDs et métadonnées chargés depuis Azure Blob Storage*")

# === Instructions de lancement ===
# Variables d'environnement HF Spaces requises:
# - AZURE_FUNCTION_URL: URL de ton Azure Function
# - AZURE_FUNCTION_KEY: Clé d'accès Azure Function  
# - AZURE_CONN_STR: Connection string Azure Storage

# batch
# git add app.py
# git commit -m "Fix: replace return with st.stop() for Streamlit compatibility"
# git push huggingface main
# ou
# git add . && git commit -m "texte commit" && git push huggingface main