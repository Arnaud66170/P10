# ============================================================================
# Module : model_training.py
# But : Fonctions de préparation et entraînement des modèles CBF et CF
# ============================================================================

import os
import numpy as np
import pandas as pd
import pickle
from surprise import Dataset, Reader, SVD
from sklearn.decomposition import PCA
import joblib



# pour lier df et embeddings
def create_article_index_mapping(df_articles : pd.DataFrame) -> dict:
    """
    Crée un mapping article_id → index utilisé dans les embeddings.
    - df_articles : DataFrame contenant 'article_id' (indexés de 0 à n)
    Retour : dictionnaire {article_id: index}
    """
    return {article_id: idx for idx, article_id in enumerate(df_articles["article_id"].values)}


def train_cf_model(df : pd.DataFrame,
                   model_path : str = "models/model_cf.pkl",
                   force_retrain : bool = False) -> SVD:
    """
    Entraîne un modèle CF avec SVD (lib Surprise), ou recharge s’il existe.

    Args:
        df (pd.DataFrame) : DataFrame contenant 'user_id' et 'article_id'
        model_path (str) : Chemin vers fichier .pkl du modèle CF
        force_retrain (bool) : Forcer un réentraînement

    Returns:
        SVD : modèle CF entraîné
    """
    from surprise import dump  # import local pour rester modulaire

    # Vérifie si un modèle déjà entraîné est disponible
    if os.path.exists(model_path) and not force_retrain:
        print("Chargement du modèle CF existant depuis :", model_path)
        _, model = dump.load(model_path)  # chargement compatible avec dump.load
        return model

    print("Entraînement du modèle CF via SVD ...")

    # Construction du dataset à partir des clics
    df_ratings = df[["user_id", "article_id"]].copy()
    df_ratings["click"] = 1.0  # chaque clic devient une "note" binaire

    reader = Reader(rating_scale = (0, 1))
    data = Dataset.load_from_df(df_ratings, reader)
    trainset = data.build_full_trainset()

    model = SVD()
    model.fit(trainset)

    # Création du dossier cible si besoin
    os.makedirs(os.path.dirname(model_path), exist_ok = True)

    # Sauvegarde avec surprise.dump
    dump.dump(model_path, algo = model)

    return model
