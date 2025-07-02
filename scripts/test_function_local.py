# tests/test_function_local.py

import requests

url = "http://localhost:7071/api/getRecommendations"
params = {
    "user_id": 59021,
    "mode": "auto",
    "alpha": 0.5,
    "threshold": 5,
    "top_n": 5
}

response = requests.get(url, params=params)

print("Status:", response.status_code)
print("Réponse JSON :")
print(response.json())
