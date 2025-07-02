# azure\function_app\src\utils\paths.py

import os

def get_project_root() -> str:
    """
    Retourne le chemin racine du projet, sans exiger la présence de dossiers locaux.
    Utilisé uniquement pour la résolution des imports et chemins relatifs de scripts.
    """

    # Environnement Azure
    azure_root = "/home/site/wwwroot"
    if os.path.exists(azure_root):
        return azure_root

    # Fallback local si exécution en dev
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
