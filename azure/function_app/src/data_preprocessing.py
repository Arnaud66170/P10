# src/data_preprocessing.py

import os
import pandas as pd
import numpy as np
import pickle
from typing import Tuple
from sklearn.decomposition import PCA


def load_metadata(metadata_path: str) -> pd.DataFrame:
    """
    Charge les métadonnées des articles, que ce soit au format CSV ou Parquet.
    """
    if metadata_path.endswith(".csv"):
        return pd.read_csv(metadata_path)
    elif metadata_path.endswith(".parquet"):
        return pd.read_parquet(metadata_path)
    else:
        raise ValueError(f"Format non supporté : {metadata_path}")


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


def reduce_embeddings(embeddings_array: np.ndarray, n_components: int = 100) -> np.ndarray:
    """
    Réduit la dimension de la matrice d'embeddings via PCA.

    Args:
        embeddings_array (np.ndarray): matrice (nb_articles, dim_initiale)
        n_components (int): nombre de composantes principales à conserver

    Returns:
        np.ndarray: matrice réduite (nb_articles, n_components)
    """
    pca = PCA(n_components=n_components)
    # fit_transform sur l'ensemble des embeddings
    reduced = pca.fit_transform(embeddings_array)
    return reduced


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


def load_article_embeddings(df_articles_path : str, embedding_col : str = "embedding") -> Tuple[np.ndarray, dict]:
    """
    Charge les embeddings compressés des articles à partir d’un fichier parquet.
    
    Args:
        df_articles_path (str): chemin vers df_articles_light.parquet
        embedding_col (str): nom de la colonne contenant les vecteurs
        
    Returns:
        Tuple:
            - embeddings (np.ndarray) : matrice (n_articles, n_dims)
            - article_id_to_index (dict) : mapping {article_id: index}
    """
    df_articles = pd.read_parquet(df_articles_path)

    if embedding_col not in df_articles.columns:
        raise ValueError(f"Colonne '{embedding_col}' absente du fichier parquet.")

    embeddings = np.array(df_articles[embedding_col].tolist())
    article_id_to_index = {article_id: idx for idx, article_id in enumerate(df_articles["article_id"].values)}

    return embeddings, article_id_to_index
