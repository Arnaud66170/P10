# streamlit_app/config.py
# Configuration pour Hugging Face Spaces

import os

# Variables d'environnement lues directement depuis HF Spaces
_raw_url = os.getenv("AZURE_FUNCTION_URL")
_key = os.getenv("AZURE_FUNCTION_KEY")

# Construction de l'URL complète avec la clé
if _raw_url and _key:
    AZURE_FUNCTION_URL = f"{_raw_url}?code={_key}"
else:
    # Fallback pour tests locaux
    AZURE_FUNCTION_URL = "https://p10recommandationfresh.azurewebsites.net/api/get_recommendations?code=p6zkcJClI6UkOKquY5LAX7-JxZGo9En1SWPlCI0oRV4bAzFuOAmhPQ=="

# Configuration source de données
VALID_SOURCES = ["azure"]
DEFAULT_DATA_SOURCE = "azure"

# Debug : impression de confirmation
print("[config.py] AZURE_FUNCTION_URL =", AZURE_FUNCTION_URL)
print("[config.py] Raw URL =", _raw_url)
print("[config.py] Key =", _key[:10] + "..." if _key else "None")