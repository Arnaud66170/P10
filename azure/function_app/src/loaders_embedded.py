# azure/function_app/src/loaders_embedded.py
# Alternative: artefacts embarqués directement dans la Function App

import os
import pickle
import numpy as np
import pandas as pd
import logging
from typing import Optional

# Chemin vers les artefacts embarqués dans la Function App
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")

def load_df_embedded(filename: str = "df_light.parquet") -> pd.DataFrame:
    """Charge le DataFrame depuis les artefacts embarqués"""
    file_path = os.path.join(ARTIFACTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Artefact non trouvé: {file_path}")
    
    logging.info(f"[EMBEDDED] Chargement df depuis: {file_path}")
    return pd.read_parquet(file_path)

def load_model_embedded(filename: str = "model_cf_light.pkl"):
    """Charge le modèle depuis les artefacts embarqués"""
    file_path = os.path.join(ARTIFACTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Modèle non trouvé: {file_path}")
    
    logging.info(f"[EMBEDDED] Chargement modèle depuis: {file_path}")
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def load_embeddings_embedded(filename: str = "articles_embeddings_compressed.npz") -> np.ndarray:
    """Charge les embeddings depuis les artefacts embarqués"""
    file_path = os.path.join(ARTIFACTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Embeddings non trouvés: {file_path}")
    
    logging.info(f"[EMBEDDED] Chargement embeddings depuis: {file_path}")
    return np.load(file_path)["embeddings"]

# Fonctions principales avec fallback automatique
def load_df(source: str = "embedded", **kwargs) -> pd.DataFrame:
    """Charge le DataFrame avec fallback automatique"""
    if source == "embedded":
        return load_df_embedded(kwargs.get("filename", "df_light.parquet"))
    else:
        # Fallback vers la méthode Azure Blob si nécessaire
        from . import loaders
        return loaders.load_df(source, **kwargs)