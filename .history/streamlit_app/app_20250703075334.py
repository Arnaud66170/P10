# streamlit_app/app.py
# FIX URGENT - URL hardcodée

import streamlit as st
import requests
import json

# URL hardcodée qui MARCHE (testée hier)
AZURE_FUNCTION_URL_HARDCODE = "https://p10recommandationfresh.azurewebsites.net/api/get_recommendations?code=p6zkcJClI6UkOKquY5LAX7-JxZGo9En1SWPlCI0oRV4bAzFuOAmhPQ=="

st.title("Recommandation personnalisée d'articles")

# Interface utilisateur (garde ton code existant)
user_id = st.selectbox("Utilisateur :", [8, 96, 330, 397])  # Users valides
mode = st.selectbox("Méthode :", ["auto", "cbf", "cf", "hybrid"])
top_n = st.slider("Nombre d'articles à recommander :", 1, 10, 5)
alpha = st.slider("Pondération (alpha) :", 0.0, 1.0, 0.7)

if st.button("Obtenir les recommandations"):
    st.write("Appel de l'Azure Function...")
    
    # Paramètres de la requête
    params = {
        "user_id": user_id,
        "mode": mode,
        "top_n": top_n,
        "alpha": alpha
    }
    
    try:
        # Appel avec URL hardcodée
        response = requests.get(AZURE_FUNCTION_URL_HARDCODE, params=params, timeout=30)
        
        # Debug info
        st.write("**DEBUG INFO:**")
        st.write(f"Status Code: {response.status_code}")
        st.write(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        st.write(f"Response Length: {len(response.text)}")
        
        if response.status_code == 200:
            if "application/json" in response.headers.get('content-type', ''):
                data = response.json()
                st.success("Recommandations générées !")
                st.write("**Recommandations :**", data.get("recommendations", []))
            else:
                st.error("Réponse HTML au lieu de JSON")
                st.write("**Raw Response (premiers 1000 caractères):**")
                st.code(response.text[:1000])
        else:
            st.error(f"Erreur HTTP {response.status_code}")
            st.write(response.text)
            
    except Exception as e:
        st.error(f"Erreur lors de l'appel : {str(e)}")

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