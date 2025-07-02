# src/loaders.py

import os
import pickle
import numpy as np
import pandas as pd
from io import BytesIO
from surprise import dump
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le .env
load_dotenv()


def load_metadata(source: str = "local",
                  filename: str = "df_articles.parquet",
                  container_name: str = "artefacts-fresh",
                  storage_account_url: str = "https://p10arnaudcs01.blob.core.windows.net/",
                  connection_string: str = None) -> pd.DataFrame:
    """
    Charge les mtadonnes articles depuis le disque local ou Azure Blob Storage.
    """

    if source == "local":
        outputs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
        meta_path = os.path.join(outputs_path, filename)

        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Fichier local introuvable : {meta_path}")

        if filename.endswith(".parquet"):
            return pd.read_parquet(meta_path)
        elif filename.endswith(".csv"):
            return pd.read_csv(meta_path)
        else:
            raise ValueError("Format de fichier non support pour les mtadonnes")

    elif source == "azure":
        try:
            conn_str = connection_string or os.getenv("AZURE_CONN_STR")
            if not conn_str:
                raise RuntimeError("Chane de connexion Azure manquante. Dfinir AZURE_CONN_STR.")

            blob_service_client = BlobServiceClient.from_connection_string(conn_str)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

            stream = blob_client.download_blob()
            df_bytes = BytesIO()
            stream.readinto(df_bytes)
            df_bytes.seek(0)

            if filename.endswith(".parquet"):
                return pd.read_parquet(df_bytes)
            elif filename.endswith(".csv"):
                return pd.read_csv(df_bytes)
            else:
                raise ValueError("Format de fichier non support pour les mtadonnes")

        except Exception as e:
            raise RuntimeError(f"Erreur chargement mtadonnes Azure : {str(e)}")

    else:
        raise ValueError("Paramtre 'source' invalide. Attendu : 'local' ou 'azure'")



def load_df(source: str = "local",
            filename: str = "df_light.parquet",
            container_name: str = "artefacts-fresh",
            connection_string: str = None) -> pd.DataFrame:
    """
    Charge le DataFrame principal contenant les utilisateurs.
    """
    if source == "local":
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs", filename))
        if not os.path.exists(path):
            raise FileNotFoundError(f" Fichier df.parquet introuvable : {path}")
        return pd.read_parquet(path)

    elif source == "azure":
        try:
            conn_str = connection_string or os.getenv("AZURE_CONN_STR")
            if not conn_str:
                raise RuntimeError("Chane de connexion Azure manquante.")

            blob_client = BlobServiceClient.from_connection_string(conn_str).get_blob_client(
                container=container_name,
                blob=filename
            )
            stream = blob_client.download_blob()
            buffer = BytesIO()
            stream.readinto(buffer)
            buffer.seek(0)
            return pd.read_parquet(buffer)

        except Exception as e:
            raise RuntimeError(f" Erreur chargement df.parquet Azure : {str(e)}")

    else:
        raise ValueError("Paramtre 'source' invalide. Attendu : 'local' ou 'azure'")


def load_embeddings(source: str = "local",
                    filename: str = "articles_embeddings_compressed.npz",
                    container_name: str = "artefacts-fresh",
                    connection_string: str = None) -> np.ndarray:
    """
    Charge la matrice des embeddings darticles (rduits) .npz
    """
    if source == "local":
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs", filename))
        if not os.path.exists(path):
            raise FileNotFoundError(f" Embeddings non trouvs : {path}")
        return np.load(path)["embeddings"]

    elif source == "azure":
        try:
            conn_str = connection_string or os.getenv("AZURE_CONN_STR")
            if not conn_str:
                raise RuntimeError("Chane de connexion Azure manquante.")

            blob_client = BlobServiceClient.from_connection_string(conn_str).get_blob_client(
                container=container_name,
                blob=filename
            )
            stream = blob_client.download_blob()
            buffer = BytesIO()
            stream.readinto(buffer)
            buffer.seek(0)
            return np.load(buffer)["embeddings"]

        except Exception as e:
            raise RuntimeError(f" Erreur chargement embeddings Azure : {str(e)}")

    else:
        raise ValueError("Paramtre 'source' invalide. Attendu : 'local' ou 'azure'")


def load_cf_model(source: str = "local",
                  filename: str = "model_cf.pkl",
                  container_name: str = "artefacts-fresh",
                  connection_string: str = None):
    """
    Charge un modle CF entran (format Surprise).
    """
    if source == "local":
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", filename))
        if not os.path.exists(path):
            raise FileNotFoundError(f" Modle CF non trouv : {path}")
        _, model = dump.load(path)
        return model

    elif source == "azure":
        try:
            conn_str = connection_string or os.getenv("AZURE_CONN_STR")
            if not conn_str:
                raise RuntimeError("Chane de connexion Azure manquante.")

            blob_client = BlobServiceClient.from_connection_string(conn_str).get_blob_client(
                container=container_name,
                blob=filename
            )
            blob_data = blob_client.download_blob().readall()
            model_obj = pickle.loads(blob_data)
            return model_obj["algo"]

        except Exception as e:
            raise RuntimeError(f" Erreur chargement modle CF Azure : {str(e)}")

    else:
        raise ValueError("Paramtre 'source' invalide. Attendu : 'local' ou 'azure'")



# Appels :
# En local              :           df = load_df(source="local")
    
# Depuis Azure Blob     :           df = load_df(source="azure")