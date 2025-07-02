# tests/test_api.py
# Tests cloud déployé (azurewebsites.net)

import requests
import pytest

# URL de l'Azure Function déployée
BASE_URL = "https://p10arnaudrecommendcs.azurewebsites.net/api/getRecommendations"

def test_recommendations_valid_user():
    """
    Test avec un user_id valide (ex : 59021)
    """
    params = {"user_id": 59021}
    response = requests.get(BASE_URL, params=params)

    assert response.status_code == 200, "Statut HTTP inattendu"
    
    data = response.json()
    assert "recommendations" in data, "Clé 'recommendations' manquante dans la réponse"
    assert isinstance(data["recommendations"], list), "Les recommandations doivent être une liste"

def test_recommendations_missing_param():
    """
    Test sans le paramètre user_id
    """
    response = requests.get(BASE_URL)

    assert response.status_code == 400, "Le statut HTTP doit être 400 si user_id est absent"
    assert "Paramètre" in response.text or "user_id" in response.text, "Message d'erreur attendu"

def test_recommendations_invalid_user_id():
    """
    Test avec un user_id invalide (string au lieu d’un entier)
    """
    params = {"user_id": "foobar"}
    response = requests.get(BASE_URL, params=params)

    assert response.status_code == 500, "Statut attendu pour une erreur interne"
    assert "Erreur" in response.text or "Exception" in response.text, "Message d’erreur attendu"



# exécuter ce test avec pytest (dossier source) :
# pytest tests/test_api.py -v
