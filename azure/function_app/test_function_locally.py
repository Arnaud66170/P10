# azure/function_app/test_function_locally.py

import requests
import os
import argparse
from dotenv import load_dotenv


def load_env(env_choice: str):
    """
    Charge le bon fichier .env selon l'argument --env
    """
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    env_files = {
        "dev": os.path.join(root_path, ".env.dev"),
        "prod": os.path.join(root_path, ".env.prod")
    }

    env_path = env_files.get(env_choice)

    if env_path and os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        print(f"✅ {os.path.basename(env_path)} chargé.")
    else:
        print(f"❌ Fichier {env_choice} introuvable.")
        exit(1)


def main():
    # ===== Arguments CLI =====
    parser = argparse.ArgumentParser(description="Test de l'Azure Function localement ou en ligne")
    parser.add_argument("--env", type=str, default="dev", choices=["dev", "prod"],
                        help="Environnement à utiliser : dev ou prod")
    args = parser.parse_args()

    # ===== Chargement de l'environnement =====
    load_env(args.env)

    # ===== Paramètres d’appel à l’API Azure Function =====
    base_url = os.getenv("AZURE_FUNCTION_URL", "http://localhost:7071/api/getRecommendations")

    params = {
        "user_id": 307698,
        "mode": "auto",
        "alpha": 0.5,
        "threshold": 5,
        "top_n": 5,
        "source": os.getenv("DATA_SOURCE", "local")  # Pour forcer source correct
    }

    try:
        response = requests.get(base_url, params=params)
        print(f"\n📤 Requête envoyée à : {response.url}")
        print(f"✅ Statut HTTP : {response.status_code}")
        print("📦 Réponse :")
        print(response.json())
    except Exception as e:
        print(f"❌ Erreur pendant l’appel : {e}")


if __name__ == "__main__":
    main()

# Exécute le script
# cd azure/function_app pour les 2
# 1 - dabord lancer :
# func start

# 2 - puis exécuter ce script pour tester la fonction, dans un autre terminal :
# en local (.env.dev) :

# python azure/function_app/test_function_locally.py --env dev

# en production (.env.prod) :
# python azure/function_app/test_function_locally.py --env prod
