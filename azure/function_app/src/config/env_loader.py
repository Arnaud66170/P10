# azure/function_app/src/config/env_loader.py

import os
from dotenv import load_dotenv

# def load_environment(env: str = None):
#     """
#     Charge dynamiquement le fichier .env correspondant à l’environnement (dev ou prod).

#     Paramètres :
#     ------------
#     env : str
#         "dev" ou "prod". Si None, essaie de lire depuis la variable ENV système.

#     Retourne :
#     ----------
#     dict : Dictionnaire avec les variables d’environnement chargées
#     """
#     if env is None:
#         env = os.getenv("ENV", "dev")  # par défaut dev

#     # Détermine le chemin du fichier .env à charger
#     env_filename = f".env.{env.lower()}"
#     project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
#     dotenv_path = os.path.join(project_root, env_filename)

#     # Chargement du fichier .env
#     if not os.path.exists(dotenv_path):
#         raise FileNotFoundError(f"Fichier {env_filename} introuvable à : {dotenv_path}")

#     load_dotenv(dotenv_path)

#     print(f"✅ Environnement {env.upper()} chargé depuis : {dotenv_path}")
#     return {
#         key: os.getenv(key) for key in [
#             "ENV", "AZURE_FUNCTION_URL", "AZURE_CONN_STR", "DATA_SOURCE"
#         ]
#     }

import os
from dotenv import load_dotenv

def load_environment(env: str = None):
    """
    Charge dynamiquement le fichier .env correspondant à l’environnement (dev ou prod).
    Le .env est cherché dans le dossier parent du dossier azure/, c’est-à-dire 2-python/
    """
    if env is None:
        env = os.getenv("ENV", "dev")

    env_filename = f".env.{env.lower()}"

    # Chemin absolu depuis CE fichier → remonte vers le dossier 2-python
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    dotenv_path = os.path.join(base_dir, env_filename)

    if not os.path.exists(dotenv_path):
        raise FileNotFoundError(f"Fichier {env_filename} introuvable à : {dotenv_path}")

    load_dotenv(dotenv_path, override=True)
    print(f"✅ Environnement {env.upper()} chargé depuis : {dotenv_path}")

    return {
        key: os.getenv(key)
        for key in [
            "ENV", "AZURE_FUNCTION_URL", "AZURE_FUNCTION_KEY",
            "AZURE_CONN_STR", "AzureWebJobsAZURE_CONN_STR", "DATA_SOURCE"
        ]
    }