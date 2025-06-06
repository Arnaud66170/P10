import sys
import subprocess
import os

def install_requirements(requirements_path="../requirements.txt"):
    """
    Installe les packages listés dans requirements.txt via pip du venv actif.
    À appeler depuis un notebook ou script pour s'assurer que tout est prêt.
    """
    if os.path.exists(requirements_path):
        print(f"📦 Installation des dépendances depuis {requirements_path} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
    else:
        print(f"❌ Fichier {requirements_path} introuvable.")
