# tests/test_paths.py
import os
import sys
import pytest

# === AJOUT DE src/ AU PATH (configuration identique à test_loaders.py) ===
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# === IMPORTS APRES MISE A JOUR DE sys.path ===
from utils.paths import get_project_root

def test_get_project_root():
    """Test de la fonction get_project_root"""
    root = get_project_root()
    assert os.path.exists(os.path.join(root, "outputs")), "outputs/ manquant"
    assert os.path.exists(os.path.join(root, "models")), "models/ manquant"