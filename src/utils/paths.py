import os
import os

def get_project_root() -> str:
    """
    Remonte les dossiers jusqu'à trouver outputs/ et models/ → racine projet détectée
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))

    while True:
        required = ["outputs", "models", "src"]
        if all(os.path.isdir(os.path.join(current_dir, sub)) for sub in required):
            return current_dir

        parent = os.path.abspath(os.path.join(current_dir, ".."))
        if parent == current_dir:
            raise FileNotFoundError("❌ Impossible de localiser la racine du projet (outputs/, models/...)")
        current_dir = parent

