# test_function_app.py

from src.config.env_loader import load_environment, check_env_vars 
import os
import requests

# Charger l'environnement "prod" depuis .env.prod (pas un chemin complet)
env_vars = load_environment("prod")
check_env_vars(list(env_vars.keys()))

# URL + clé
url = os.getenv("AZURE_FUNCTION_URL")
key = os.getenv("AZURE_FUNCTION_KEY")
full_url = f"{url}?code={key}"

# Requête
payload = {
    "user_id": 59021,
    "mode": "auto",
    "alpha": 0.5,
    "top_n": 5,
    "source": os.getenv("DATA_SOURCE", "azure")
}
headers = {"Content-Type": "application/json"}

res = requests.post(full_url, json=payload, headers=headers)

print("Status code:", res.status_code)

try:
    print(res.json())  # Essaye d'afficher le JSON s'il y en a
except Exception as e:
    print("⚠️ Réponse non JSON brute :")
    print(response.text)  # pour afficher même du HTML ou rien
    print("⚠️ Exception levée :", e)
    return None



# exécution du script :
# python test_function_app.py
