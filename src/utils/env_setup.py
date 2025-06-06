import sys
import subprocess
import os

def install_requirements(requirements_path="requirements.txt"):
    """
    Installe les packages listés dans requirements.txt depuis la racine du projet.
    Ce chemin est résolu dynamiquement peu importe où le script est appelé.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    req_full_path = os.path.join(project_root, requirements_path)

    if os.path.exists(req_full_path):
        print(f"📦 Installation des dépendances depuis {req_full_path} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_full_path])
    else:
        print(f"❌ Fichier {req_full_path} introuvable.")
