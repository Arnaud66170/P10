# tests/test_api_call.py
# Tests d'intégration de l'Azure Function locale (http://localhost:7071)

import requests

BASE_URL = "http://localhost:7071/api/getRecommendations"

def test_call_api_valid_user():
    """
    Test standard avec tous les paramètres valides
    """
    params = {
        "user_id": 59021,
        "mode": "auto",
        "alpha": 0.5,
        "threshold": 5,
        "top_n": 5
    }
    response = requests.get(BASE_URL, params=params)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert all(isinstance(x, int) for x in data["recommendations"])


def test_call_api_missing_user_id():
    """
    Test en cas de paramètre user_id manquant → doit renvoyer un 400
    """
    params = {
        "mode": "auto"
    }
    response = requests.get(BASE_URL, params=params)
    assert response.status_code == 400


def test_call_api_invalid_user_id():
    """
    Test avec un user_id non entier (ex : string)
    """
    params = {
        "user_id": "foobar",
        "mode": "auto"
    }
    response = requests.get(BASE_URL, params=params)
    assert response.status_code == 500


# Dabord lancer "func start" depuis le terminal (cd azure/function_app)
# ensuite exécuter ce test avec pytest dossier source) :
# pytest tests/test_api_call.py