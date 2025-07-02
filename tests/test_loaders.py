import os
import sys
import pytest
import numpy as np
from dotenv import load_dotenv

# === AJOUT DE src/ AU PATH (important pour les imports internes) ===
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# === IMPORTS APRES MISE A JOUR DE sys.path ===
from loaders import load_df, load_embeddings, load_cf_model
from wrappers import get_recommendations_from_user

# === CHARGEMENT DU .env SI DISPONIBLE ===
dotenv_path = os.path.join(project_root, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

AZURE_CONN_STR = os.getenv("AZURE_CONN_STR")


def test_load_df_local():
    df = load_df(source="local")
    assert df.shape[0] > 0, "df.parquet vide ou non trouvé"
    assert "user_id" in df.columns, "Colonne user_id absente"


def test_load_embeddings_local():
    embeddings = load_embeddings(source="local")
    assert isinstance(embeddings, np.ndarray), "Format embeddings incorrect"
    assert embeddings.shape[0] > 0, "Embeddings vides"


def test_load_cf_model_local():
    model = load_cf_model(source="local")
    assert hasattr(model, "predict"), "Modèle CF invalide"


@pytest.mark.skipif(AZURE_CONN_STR is None, reason="Chaîne Azure manquante")
def test_load_df_azure():
    df = load_df(source="azure", connection_string=AZURE_CONN_STR)
    assert df.shape[0] > 0, "df.parquet vide depuis Azure"
    assert "user_id" in df.columns, "Colonne user_id absente dans Azure"


@pytest.mark.skipif(AZURE_CONN_STR is None, reason="Chaîne Azure manquante")
def test_load_embeddings_azure():
    embeddings = load_embeddings(source="azure", connection_string=AZURE_CONN_STR)
    assert isinstance(embeddings, np.ndarray), "Format embeddings incorrect (Azure)"
    assert embeddings.shape[0] > 0, "Embeddings Azure vides"


@pytest.mark.skipif(AZURE_CONN_STR is None, reason="Chaîne Azure manquante")
def test_load_cf_model_azure():
    model = load_cf_model(source="azure", filename="model_cf_light.pkl", connection_string=AZURE_CONN_STR)
    assert hasattr(model, "predict"), "Modèle CF Azure invalide"


def test_get_recommendations_local():
    recommendations = get_recommendations_from_user(user_id=8, source="local")
    assert isinstance(recommendations, list), "Résultat non listé"
    assert len(recommendations) > 0, "Aucune recommandation"
    assert isinstance(recommendations[0], int), "Les IDs doivent être entiers"


@pytest.mark.skipif(AZURE_CONN_STR is None, reason="Chaîne Azure manquante")
def test_get_recommendations_azure():
    recommendations = get_recommendations_from_user(user_id=8, source="azure", connection_string=AZURE_CONN_STR)
    assert isinstance(recommendations, list), "Résultat non listé (Azure)"
    assert len(recommendations) > 0, "Aucune reco depuis Azure"
    assert isinstance(recommendations[0], int), "Les IDs doivent être entiers (Azure)"
