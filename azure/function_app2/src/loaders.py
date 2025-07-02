# azure/function_app/src/loaders.py

import os
import pickle
import numpy as np
import pandas as pd
import logging
from io import BytesIO
from surprise import dump
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# === Chargement du .env si l'app tourne localement (Streamlit, tests, etc.) ===
env_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "streamlit_app", ".env.prod")
load_dotenv(dotenv_path=env_file)

# === Racine du projet ===
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def _get_conn_str(connection_string: str = None) -> str:
    conn_str = (
        connection_string
        or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        or os.getenv("AZURE_CONN_STR")
        or os.getenv("AzureWebJobsAZURE_CONN_STR")
        or os.getenv("AzureWebJobsStorage")
    )

    if not conn_str:
        raise RuntimeError("Chaîne de connexion Azure introuvable dans les variables d'environnement.")
    return conn_str

def _get_blob_buffer(container_name: str, filename: str, conn_str: str) -> BytesIO:
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    blob_client = blob_service.get_blob_client(container=container_name, blob=filename)

    buffer = BytesIO()
    blob_client.download_blob().readinto(buffer)
    buffer.seek(0)
    return buffer

def load_metadata(source: str,
                  filename: str = "df_articles_light.parquet",
                  container_name: str = "artefacts-fresh",
                  connection_string: str = None) -> pd.DataFrame:
    if source == "local":
        meta_path = os.path.join(PROJECT_ROOT, "outputs", filename)
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Fichier local introuvable : {meta_path}")
        logging.info(f"[LOADER] Chargement local des métadonnées : {meta_path}")
        return pd.read_parquet(meta_path) if filename.endswith(".parquet") else pd.read_csv(meta_path)

    elif source == "azure":
        try:
            conn_str = _get_conn_str(connection_string)
            buffer = _get_blob_buffer(container_name, filename, conn_str)
            logging.info(f"[LOADER] Chargement Azure Blob des métadonnées : {filename}")
            return pd.read_parquet(buffer) if filename.endswith(".parquet") else pd.read_csv(buffer)
        except Exception as e:
            raise RuntimeError(f"Erreur chargement métadonnées Azure : {str(e)}")

    else:
        raise ValueError("Paramètre 'source' invalide. Utiliser 'local' ou 'azure'")

def load_df(source: str,
            filename: str = "df_light.parquet",
            container_name: str = "artefacts-fresh",
            connection_string: str = None) -> pd.DataFrame:
    if source == "local":
        path = os.path.join(PROJECT_ROOT, "outputs", filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Fichier df_light.parquet introuvable : {path}")
        logging.info(f"[LOADER] Chargement local du df : {path}")
        return pd.read_parquet(path)

    elif source == "azure":
        try:
            conn_str = _get_conn_str(connection_string)
            buffer = _get_blob_buffer(container_name, filename, conn_str)
            logging.info(f"[LOADER] Chargement Azure Blob du df : {filename}")
            return pd.read_parquet(buffer)
        except Exception as e:
            raise RuntimeError(f"Erreur chargement df_light.parquet Azure : {str(e)}")

    else:
        raise ValueError("Paramètre 'source' invalide. Utiliser 'local' ou 'azure'")

def load_embeddings(source: str,
                    filename: str = "articles_embeddings_compressed.npz",
                    container_name: str = "artefacts-fresh",
                    connection_string: str = None) -> np.ndarray:
    if source == "local":
        path = os.path.join(PROJECT_ROOT, "outputs", filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Embeddings non trouvés : {path}")
        logging.info(f"[LOADER] Chargement local des embeddings : {path}")
        return np.load(path)["embeddings"]

    elif source == "azure":
        try:
            conn_str = _get_conn_str(connection_string)
            buffer = _get_blob_buffer(container_name, filename, conn_str)
            logging.info(f"[LOADER] ✅ Chargement Azure Blob des embeddings : {filename}")
            return np.load(buffer)["embeddings"]
        except Exception as e:
            raise RuntimeError(f"Erreur chargement embeddings Azure : {str(e)}")

    else:
        raise ValueError("Paramètre 'source' invalide. Utiliser 'local' ou 'azure'")

def load_cf_model(source: str,
                  filename: str = "model_cf_light.pkl",
                  container_name: str = "artefacts-fresh",
                  connection_string: str = None):
    if source == "local":
        path = os.path.join(PROJECT_ROOT, "models", filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Modèle CF non trouvé : {path}")
        logging.info(f"[LOADER] Chargement local du modèle CF : {path}")
        _, model = dump.load(path)
        return model

    elif source == "azure":
        try:
            conn_str = _get_conn_str(connection_string)
            buffer = _get_blob_buffer(container_name, filename, conn_str)
            logging.info(f"[LOADER] Chargement Azure Blob du modèle CF : {filename}")
            model_obj = pickle.loads(buffer.read())

            # Détection dynamique du format
            if isinstance(model_obj, dict) and "algo" in model_obj:
                return model_obj["algo"]
            elif isinstance(model_obj, tuple) and len(model_obj) == 2:
                return model_obj[1]
            else:
                raise RuntimeError("Format inattendu pour le modèle CF chargé depuis Azure.")
        except Exception as e:
            raise RuntimeError(f"Erreur chargement modèle CF Azure : {str(e)}")

    else:
        raise ValueError("Paramètre 'source' invalide. Utiliser 'local' ou 'azure'")
