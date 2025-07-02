# tests/test_call_function.py

import requests

# URL locale de l'Azure Function
url = "http://localhost:7071/api/getRecommendations"

# Paramètres de requête simulée
params = {
    "user_id": 59021,
    "mode": "auto",
    "alpha": 0.5,
    "threshold": 5,
    "top_n": 5
}

# Envoi de la requête GET
response = requests.get(url, params=params)

# Affichage du résultat
print("Statut HTTP :", response.status_code)
print("Réponse JSON :", response.json())

# Exécution du script depuis le terminal (racine projet) :
# python tests/test_call_function.py
