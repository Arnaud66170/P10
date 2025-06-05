# src/data_preprocessing.py

import numpy as np
import pandas as pd
import os

def preprocess_all_articles(metadata_path, embeddings_path):
    """
    Pipeline global de préparation du DataFrame des articles.
    """
    df = load_metadata(metadata_path)
    embeddings = load_embeddings(embeddings_path)
    df = attach_embeddings(df, embeddings)
    return df

def load_articles_with_embeddings(metadata_path, embeddings_path):
    # Chargement des métadonnées
    df_articles = pd.read_csv(metadata_path)
    
    # Chargement des embeddings
    # embeddings = np.load(embeddings_path) if embeddings_path.endswith(".npz") else pickle.load(open(embeddings_path, "rb"))
    embeddings = np.load("articles_embeddings_compressed.npz")["embeddings"]

    # Vérification de l'alignement
    assert len(df_articles) == embeddings.shape[0], "Le nombre d'articles ne correspond pas aux embeddings"

    # Ajout des embeddings comme colonne ou attribut externe
    df_articles["embedding"] = list(embeddings)

    return df_articles

def load_embeddings(embeddings_path):
    """
    Charge les embeddings depuis un fichier .npz compressé.
    """
    data = np.load(embeddings_path)
    return data["embeddings"]

def load_metadata(metadata_path):
    """
    Charge les métadonnées des articles.
    """
    return pd.read_csv(metadata_path)

def attach_embeddings(df_articles, embeddings_array):
    """
    Ajoute la colonne 'embedding' au DataFrame des articles.
    """
    assert len(df_articles) == len(embeddings_array), "Taille des embeddings incompatible"
    df_articles["embedding"] = list(embeddings_array)
    return df_articles


