# src/data_preprocessing.py

import os
import pandas as pd
import numpy as np
import pickle
from typing import Tuple


def load_metadata(metadata_path: str) -> pd.DataFrame:
    """
    Charge les métadonnées des articles depuis un fichier CSV.

    Args:
        metadata_path (str): Chemin vers le fichier articles_metadata.csv

    Returns:
        pd.DataFrame: Table des métadonnées articles
    """
    return pd.read_csv(metadata_path)


def load_embeddings_pickle(embeddings_path: str) -> np.ndarray:
    """
    Charge les embeddings depuis un fichier .pickle.

    Args:
        embeddings_path (str): Chemin vers le fichier pickle

    Returns:
        np.ndarray: Matrice numpy (nb_articles, dim_embeddings)
    """
    with open(embeddings_path, "rb") as f:
        embeddings = pickle.load(f)
    return embeddings


def attach_embeddings(df_articles: pd.DataFrame, embeddings_array: np.ndarray) -> pd.DataFrame:
    """
    Ajoute une colonne 'embedding' au DataFrame d'articles.

    Args:
        df_articles (pd.DataFrame): Métadonnées articles
        embeddings_array (np.ndarray): Embeddings (nb_articles, dim)

    Returns:
        pd.DataFrame: df enrichi avec colonne 'embedding'
    """
    assert len(df_articles) == len(embeddings_array), \
        f"Erreur : {len(df_articles)} articles vs {len(embeddings_array)} embeddings"

    df_articles["embedding"] = list(embeddings_array)
    return df_articles


def preprocess_all_articles(metadata_path: str, embeddings_path: str) -> pd.DataFrame:
    """
    Pipeline global de préparation des articles (métadonnées + embeddings).

    Args:
        metadata_path (str): Chemin du fichier articles_metadata.csv
        embeddings_path (str): Chemin du fichier .pickle contenant les embeddings

    Returns:
        pd.DataFrame: df enrichi
    """
    df = load_metadata(metadata_path)
    embeddings = load_embeddings_pickle(embeddings_path)
    df = attach_embeddings(df, embeddings)
    return df


def load_all_data(data_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Charge tous les fichiers nécessaires à la constitution du DataFrame principal df.

    Args:
        data_path (str): Chemin vers le dossier contenant les données (doit contenir les sous-dossiers et fichiers attendus)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
            - df_clicks_full : concaténation de tous les clicks_hour_XXX.csv
            - df_clicks_sample : fichier clicks_sample.csv
            - df_articles : métadonnées des articles
    """
    clicks_dir = os.path.join(data_path, "clicks")
    
    # Détection automatique de tous les fichiers clicks_hour_*.csv
    clicks_files = sorted([
        os.path.join(clicks_dir, f) for f in os.listdir(clicks_dir)
        if f.startswith("clicks_hour_") and f.endswith(".csv")
    ])

    if not clicks_files:
        raise FileNotFoundError(f"Aucun fichier 'clicks_hour_XXX.csv' trouvé dans {clicks_dir}")

    # Concaténation des fichiers de clics
    df_clicks_full = pd.concat((pd.read_csv(f) for f in clicks_files), ignore_index=True)

    # Chargement des autres fichiers
    df_clicks_sample = pd.read_csv(os.path.join(data_path, "clicks_sample.csv"))
    df_articles = pd.read_csv(os.path.join(data_path, "articles_metadata.csv"))

    return df_clicks_full, df_clicks_sample, df_articles
