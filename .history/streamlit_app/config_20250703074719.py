# streamlit_app/config.py
# Configuration pour Hugging Face Spaces - DEBUG SECRETS

import os

# Debug : affichage de TOUTES les variables d'environnement
print("[DEBUG] Variables d'environnement disponibles :")
for key, value in os.environ.items():
    if "AZURE" in key.upper():
        print(f"  {key} = {value[:20]}..." if len(value) > 20 else f"  {key} = {value}")

# Variables d'environnement lues directement depuis HF Spaces
_raw_url = os.getenv("AZURE_FUNCTION_URL")
_key = os.getenv("AZURE_FUNCTION_KEY")

print(f"[DEBUG] _raw_url = {_raw_url}")
print(f"[DEBUG] _key = {_key}")

# Construction de l'URL complète avec la clé
if _raw_url and _key:
    AZURE_FUNCTION_URL = f"{_raw_url}?code={_key}"
    print("[DEBUG] Variables trouvées - URL construite avec secrets")
else:
    # Fallback pour tests locaux - URL que tu as testée hier et qui MARCHE
    AZURE_FUNCTION_URL = "https://p10recommandationfresh.azurewebsites.net/api/get_recommendations?code=p6zkcJClI6UkOKquY5LAX7-JxZGo9En1SWPlCI0oRV4bAzFuOAmhPQ=="
    print("[DEBUG] Fallback utilisé - secrets non trouvés")

# Configuration source de données
VALID_SOURCES = ["azure"]
DEFAULT_DATA_SOURCE = "azure"

# Debug : impression de confirmation
print("[config.py] AZURE_FUNCTION_URL =", AZURE_FUNCTION_URL)