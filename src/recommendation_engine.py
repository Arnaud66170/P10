# src/recommendation_engine.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os
import sys

# Ajout dynamique du dossier src/ si lancé hors package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))  # pour function_app.py
src_path = os.path.join(project_root, "src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Optionnel : affichage pour debug
print(f"src/ ajouté à sys.path : {src_path}")

from typing import List
from surprise import Dataset, Reader, SVD

# Imports des fonctions de recommandation
# from .recommendation_engine import get_cbf_recommendations, get_cf_recommendations, get_hybrid_recommendations
from model_training import train_cf_model
from data_preprocessing import load_article_embeddings

def get_cbf_recommendations(user_id,
                            df,
                            embeddings,
                            article_id_to_index,
                            top_n = 5):
    """
    Renvoie les recommandations CBF pour un utilisateur donné.
    - user_id : identifiant de l’utilisateur
    - df : DataFrame interactions (colonnes : user_id, article_id)
    - embeddings : matrice numpy (n_articles, n_dims)
    - article_id_to_index : dict {article_id: index dans la matrice}
    - top_n : nombre de recommandations à renvoyer
    Retour : liste d’IDs d’articles recommandés
    """
    user_clicks = df[df["user_id"] == user_id]["article_id"].unique()

    if len(user_clicks) == 0:
        return []  # Aucun historique → aucune recommandation

    # On récupère les indices correspondants dans la matrice d’embeddings
    valid_indices = [article_id_to_index[a] for a in user_clicks if a in article_id_to_index]

    if not valid_indices:
        return []  # Aucun article cliquable ne correspond aux embeddings

    user_profile = np.mean(embeddings[valid_indices], axis = 0).reshape(1, -1)

    # Calcul des similarités avec tous les articles
    similarities = cosine_similarity(user_profile, embeddings)[0]

    # On évite de recommander des articles déjà vus
    for a in user_clicks:
        if a in article_id_to_index:
            idx = article_id_to_index[a]
            similarities[idx] = -1

    top_indices = np.argsort(similarities)[::-1][:top_n]

    # Mapping inverse : index → article_id
    index_to_article_id = {v: k for k, v in article_id_to_index.items()}
    return [int(index_to_article_id[i]) for i in top_indices if i in index_to_article_id]



def get_cf_recommendations(user_id : int,
                           df : "pd.DataFrame",
                           model,
                           top_n : int = 5) -> list:
    """
    Recommandations CF : prédit les meilleurs articles pour un utilisateur.

    Args:
        user_id (int) : utilisateur ciblé
        df (pd.DataFrame) : historique clics
        model : modèle CF entraîné (SVD)
        top_n (int) : nombre de suggestions

    Returns:
        list : article_id des articles recommandés
    """
    # Articles déjà vus par l'utilisateur
    seen_articles = df[df["user_id"] == user_id]["article_id"].unique()

    # Tous les articles existants
    all_articles = df["article_id"].unique()

    # Articles jamais vus
    unseen_articles = [aid for aid in all_articles if aid not in seen_articles]

    # Prédictions pour chaque article non vu
    predictions = [(aid, model.predict(user_id, aid).est) for aid in unseen_articles]

    # Tri décroissant par score
    predictions.sort(key = lambda x: x[1], reverse = True)

    # Récupération des article_id les mieux notés
    return [aid for aid, _ in predictions[:top_n]]


def get_hybrid_recommendations(user_id : int,
                                df : pd.DataFrame,
                                embeddings : np.ndarray,
                                article_id_to_index : dict,
                                model_cf,
                                top_n : int = 5,
                                alpha : float = 0.5) -> list:
    """
    Renvoie des recommandations hybrides (CBF + CF), pondérées par alpha.
    
    Args:
        user_id (int): identifiant utilisateur
        df (pd.DataFrame): interactions
        embeddings (np.ndarray): matrice d’embeddings articles
        article_id_to_index (dict): mapping article_id → index
        model_cf : modèle collaboratif pré-entraîné
        top_n (int): nombre d’articles à retourner
        alpha (float): pondération CBF vs CF (0.0 = 100% CF, 1.0 = 100% CBF)

    Returns:
        list: liste des article_id recommandés (triés par score combiné)
    """
    # Articles vus par l’utilisateur
    seen_articles = df[df["user_id"] == user_id]["article_id"].unique()
    all_articles = df["article_id"].unique()
    unseen_articles = [aid for aid in all_articles if aid not in seen_articles]

    # CBF : profil utilisateur
    user_clicks = [aid for aid in seen_articles if aid in article_id_to_index]
    if not user_clicks:
        return get_cf_recommendations(user_id, df, model_cf, top_n)

    profile_vec = np.mean(embeddings[[article_id_to_index[aid] for aid in user_clicks]], axis = 0).reshape(1, -1)
    cbf_scores = cosine_similarity(profile_vec, embeddings)[0]

    # Mise à zéro des articles vus
    for aid in seen_articles:
        if aid in article_id_to_index:
            cbf_scores[article_id_to_index[aid]] = -1

    # CF : prédiction de scores
    cf_scores = {aid: model_cf.predict(user_id, aid).est for aid in unseen_articles}

    # Fusion des scores pondérés
    hybrid_scores = {}
    for aid in unseen_articles:
        cbf_score = cbf_scores[article_id_to_index[aid]] if aid in article_id_to_index else 0
        cf_score = cf_scores.get(aid, 0)
        hybrid_scores[aid] = alpha * cbf_score + (1 - alpha) * cf_score

    # Tri décroissant
    sorted_articles = sorted(hybrid_scores.items(), key = lambda x: x[1], reverse = True)

    return [int(aid) for aid, _ in sorted_articles[:top_n]]


def get_recommendations(user_id: int,
                        df: pd.DataFrame,
                        model_cf,  # modèle CF préentraîné ou chargé
                        embeddings,
                        article_id_to_index,
                        mode: str = "auto",
                        alpha: float = 0.5,
                        user_clicks_threshold: int = 5,
                        top_n: int = 5) -> List[int]:
    """
    Fonction centrale de recommandation.

    Paramètres :
        user_id : ID utilisateur cible
        df : DataFrame interactions (user_id, article_id)
        model_cf : modèle collaboratif filtré (ex : SVD)
        embeddings : matrice d'embeddings réduits des articles
        article_id_to_index : mapping article_id → index dans embeddings
        mode : "cbf", "cf", "hybrid" ou "auto"
        alpha : poids CBF/CF pour mode "hybrid"
        user_clicks_threshold : seuil de clics pour bascule logique
        top_n : nombre d’articles recommandés

    Retour :
        Liste des article_id recommandés (triée par score décroissant)
    """
    user_history = df[df["user_id"] == user_id]["article_id"].tolist()
    nb_clicks = len(user_history)

    if mode == "auto":
        if nb_clicks == 0:
            return []
        elif nb_clicks < user_clicks_threshold:
            return get_cbf_recommendations(user_id, df, embeddings, article_id_to_index, top_n)
        else:
            return get_hybrid_recommendations(user_id, df, embeddings, article_id_to_index, model_cf, top_n, alpha)

    elif mode == "cbf":
        return get_cbf_recommendations(user_id, df, embeddings, article_id_to_index, top_n)

    elif mode == "cf":
        return get_cf_recommendations(user_id, df, model_cf, top_n)

    elif mode == "hybrid":
        return get_hybrid_recommendations(user_id, df, embeddings, article_id_to_index, model_cf, top_n, alpha)

    else:
        raise ValueError(f"Mode de recommandation invalide : {mode}")
