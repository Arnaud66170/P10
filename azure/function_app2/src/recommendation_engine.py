# azure/function_app/src/recommendation_engine.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from typing import List

# ============================
# Fonction utilitaire de conversion
# ============================

def convert_numpy_types(obj):
    """Convertit récursivement les types NumPy en types Python natifs"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    return obj

# ============================
# Recommandation CBF
# ============================

def get_cbf_recommendations(user_id,
                            df,
                            embeddings,
                            article_id_to_index,
                            top_n=5):
    user_clicks = df[df["user_id"] == user_id]["article_id"].unique()
    if len(user_clicks) == 0:
        return []

    valid_indices = [article_id_to_index[a] for a in user_clicks if a in article_id_to_index]
    if not valid_indices:
        return []

    user_profile = np.mean(embeddings[valid_indices], axis=0).reshape(1, -1)
    similarities = cosine_similarity(user_profile, embeddings)[0]

    for a in user_clicks:
        if a in article_id_to_index:
            similarities[article_id_to_index[a]] = -1

    top_indices = np.argsort(similarities)[::-1][:top_n]
    index_to_article_id = {v: k for k, v in article_id_to_index.items()}
    
    # Conversion explicite en int Python
    recommendations = [int(index_to_article_id[i]) for i in top_indices if i in index_to_article_id]
    return convert_numpy_types(recommendations)


# ============================
# Recommandation CF
# ============================

def get_cf_recommendations(user_id: int,
                           df: pd.DataFrame,
                           model,
                           top_n: int = 5) -> list:
    seen_articles = df[df["user_id"] == user_id]["article_id"].unique()
    all_articles = df["article_id"].unique()
    unseen_articles = [aid for aid in all_articles if aid not in seen_articles]

    predictions = [(aid, model.predict(user_id, aid).est) for aid in unseen_articles]
    predictions.sort(key=lambda x: x[1], reverse=True)
    
    # Conversion explicite en int Python
    recommendations = [int(aid) for aid, _ in predictions[:top_n]]
    return convert_numpy_types(recommendations)


# ============================
# Recommandation Hybride
# ============================

def get_hybrid_recommendations(user_id: int,
                               df: pd.DataFrame,
                               embeddings: np.ndarray,
                               article_id_to_index: dict,
                               model_cf,
                               top_n: int = 5,
                               alpha: float = 0.5) -> list:
    seen_articles = df[df["user_id"] == user_id]["article_id"].unique()
    all_articles = df["article_id"].unique()
    unseen_articles = [aid for aid in all_articles if aid not in seen_articles]

    user_clicks = [aid for aid in seen_articles if aid in article_id_to_index]
    if not user_clicks:
        return get_cf_recommendations(user_id, df, model_cf, top_n)

    profile_vec = np.mean(embeddings[[article_id_to_index[aid] for aid in user_clicks]], axis=0).reshape(1, -1)
    cbf_scores = cosine_similarity(profile_vec, embeddings)[0]

    for aid in seen_articles:
        if aid in article_id_to_index:
            cbf_scores[article_id_to_index[aid]] = -1

    cf_scores = {aid: model_cf.predict(user_id, aid).est for aid in unseen_articles}

    hybrid_scores = {}
    for aid in unseen_articles:
        cbf_score = cbf_scores[article_id_to_index[aid]] if aid in article_id_to_index else 0
        cf_score = cf_scores.get(aid, 0)
        hybrid_scores[aid] = alpha * cbf_score + (1 - alpha) * cf_score

    sorted_articles = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Conversion explicite en int Python
    recommendations = [int(aid) for aid, _ in sorted_articles[:top_n]]
    return convert_numpy_types(recommendations)


# ============================
# Fonction centrale
# ============================

def get_recommendations(user_id: int,
                        df: pd.DataFrame,
                        model_cf,
                        embeddings,
                        article_id_to_index,
                        mode: str = "auto",
                        alpha: float = 0.5,
                        user_clicks_threshold: int = 5,
                        top_n: int = 5,
                        df_articles: pd.DataFrame = None) -> List[int]:
    """
    Fonction centrale de recommandation.
    Si df_articles est fourni, trie les articles recommandés selon leur fraîcheur (created_at_ts)
    """
    user_history = df[df["user_id"] == user_id]["article_id"].tolist()
    nb_clicks = len(user_history)

    if mode == "auto":
        if nb_clicks == 0:
            reco = []
        elif nb_clicks < user_clicks_threshold:
            reco = get_cbf_recommendations(user_id, df, embeddings, article_id_to_index, top_n)
        else:
            reco = get_hybrid_recommendations(user_id, df, embeddings, article_id_to_index, model_cf, top_n, alpha)

    elif mode == "cbf":
        reco = get_cbf_recommendations(user_id, df, embeddings, article_id_to_index, top_n)

    elif mode == "cf":
        reco = get_cf_recommendations(user_id, df, model_cf, top_n)

    elif mode == "hybrid":
        reco = get_hybrid_recommendations(user_id, df, embeddings, article_id_to_index, model_cf, top_n, alpha)

    else:
        raise ValueError(f"Mode de recommandation invalide : {mode}")

    if df_articles is not None and "created_at_ts" in df_articles.columns:
        articles_info = df_articles[df_articles["article_id"].isin(reco)].copy()
        articles_info = articles_info.sort_values("created_at_ts", ascending=False)
        reco_sorted = articles_info["article_id"].tolist()
        # Conversion finale pour s'assurer que tout est en int Python
        final_reco = [int(aid) for aid in reco_sorted[:top_n]]
        return convert_numpy_types(final_reco)

    # Conversion finale pour s'assurer que tout est en int Python
    final_reco = [int(aid) for aid in reco]
    return convert_numpy_types(final_reco)