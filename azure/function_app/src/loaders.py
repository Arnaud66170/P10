# src/loaders.py

import os
import pickle
import numpy as np
import pandas as pd
from surprise import dump


def load_metadata(path: str) -> pd.DataFrame:
    """
    Charge les métadonnées articles (au format .parquet ou .csv)
    """
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    elif path.endswith(".csv"):
        return pd.read_csv(path)
    else:
        raise ValueError("Format de fichier non supporté pour les métadonnées")


def load_embeddings(path: str):
    """
    Charge les embeddings compressés + le mapping article_id_to_index (au format .npz et .pkl)
    """
    if path.endswith(".npz"):
        embeddings = np.load(path)["embeddings"]
    else:
        with open(path, "rb") as f:
            embeddings = pickle.load(f)

    # Chargement du mapping associé (même dossier, fichier .pkl)
    base_path = os.path.dirname(path)
    map_path = os.path.join(base_path, "article_id_to_index.pkl")
    with open(map_path, "rb") as f:
        article_id_to_index = pickle.load(f)

    return embeddings, article_id_to_index


def load_cf_model(path: str):
    """
    Charge le modèle CF enregistré avec surprise.dump
    """
    _, model = dump.load(path)
    return model
