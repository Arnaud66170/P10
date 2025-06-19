# src/wrappers.py

import os
import sys
import pandas as pd
import numpy as np
from typing import List

# 🔧 Ajout dynamique du dossier src/ au sys.path si nécessaire
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
src_path = os.path.join(project_root, "src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# ✅ Imports internes (ne pas utiliser 'src.' ici)
from loaders import load_cf_model, load_metadata
from recommendation_engine import get_recommendations

# 📁 Définition des chemins vers les artefacts
outputs_path = os.path.join(project_root, "outputs")
models_path = os.path.join(project_root, "models")
cf_model_path = os.path.join(models_path, "model_cf.pkl")
articles_path = os.path.join(outputs_path, "df_articles.parquet")
interactions_path = os.path.join(outputs_path, "df.parquet")


def extract_embeddings_and_index(df_articles: pd.DataFrame) -> tuple[np.ndarray, dict]:
    """
    Extrait la matrice des embeddings + dictionnaire id → index
    """
    embeddings = np.stack(df_articles["embedding"].values)

    article_id_to_index = {
        article_id: idx for idx, article_id in enumerate(df_articles["article_id"])
    }

    return embeddings, article_id_to_index


def get_recommendations_from_user(user_id: int,
                                  mode: str = "auto",
                                  alpha: float = 0.5,
                                  user_clicks_threshold: int = 5,
                                  top_n: int = 5) -> List[int]:
    """
    Wrapper centralisé pour appeler get_recommendations(...) à partir d’un seul user_id.
    """
    # Chargement des artefacts
    df = pd.read_parquet(interactions_path)
    df_articles = pd.read_parquet(articles_path)
    model_cf = load_cf_model(cf_model_path)
    embeddings, article_id_to_index = extract_embeddings_and_index(df_articles)

    return get_recommendations(
        user_id=user_id,
        df=df,
        model_cf=model_cf,
        embeddings=embeddings,
        article_id_to_index=article_id_to_index,
        mode=mode,
        alpha=alpha,
        user_clicks_threshold=user_clicks_threshold,
        top_n=top_n
    )
