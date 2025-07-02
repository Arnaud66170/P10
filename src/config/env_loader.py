# src/config/env_loader.py

import os
from dotenv import load_dotenv

def load_environment(env: str = None) -> dict:
    """
    Charge dynamiquement le fichier .env approprié (.env.dev ou .env.prod) 
    et expose les principales variables d'environnement du projet.

    Paramètres
    ----------
    env : str
        Nom de l’environnement à charger : "dev" ou "prod". Si None, lit depuis ENV.

    Retour
    ------
    dict
        Dictionnaire contenant les variables d'environnement clés.
    """
    if env is None:
        env = os.getenv("ENV", "dev")

    env = env.lower()
    env_filename = f".env.{env}"

    # Racine du projet = dossier contenant .env.*
    project_root = os.getcwd()
    dotenv_path = os.path.join(project_root, env_filename)

    if not os.path.exists(dotenv_path):
        raise FileNotFoundError(f"Fichier {env_filename} introuvable à : {dotenv_path}")

    load_dotenv(dotenv_path)

    print(f"✅ Environnement {env.upper()} chargé depuis : {dotenv_path}")

    # Retourne un sous-ensemble utile
    keys = [
        "ENV",
        "AZURE_FUNCTION_URL",
        "AZURE_FUNCTION_KEY",
        "AZURE_CONN_STR",
        "AzureWebJobsAZURE_CONN_STR",
        "AZURE_STORAGE_CONNECTION_STRING",
        "DATA_SOURCE",
        "DATA_PATH",
        "MODELS_PATH"
    ]

    return {key: os.getenv(key) for key in keys}

def check_env_vars(required_keys: list):
    missing = [k for k in required_keys if os.getenv(k) is None]
    if missing:
        print("❌ Variables manquantes :", ", ".join(missing))
    else:
        print("✅ Toutes les variables attendues sont présentes.")
