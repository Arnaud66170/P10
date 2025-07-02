# tests/test_recommendation_wrapper.py

import sys
import os
import random

# Détection et ajout du chemin du src/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

from wrappers import get_recommendations_from_user


def test_reco(user_id: int = None,
              mode: str = "auto",
              alpha: float = 0.5,
              top_n: int = 5):
    """
    Teste le wrapper avec un user_id donné (ou sélection aléatoire).
    """
    import pandas as pd

    # Chemin vers df.parquet
    df_path = os.path.join(project_root, "outputs", "df.parquet")
    df = pd.read_parquet(df_path)

    # Choix d’un user_id si non fourni
    if user_id is None:
        user_id = df["user_id"].sample(1).iloc[0]

    print(f"[INFO] Test avec user_id = {user_id}")
    print(f"[INFO] Mode = {mode}, alpha = {alpha}, top_n = {top_n}")

    reco_ids = get_recommendations_from_user(
        user_id = user_id,
        mode = mode,
        alpha = alpha,
        top_n = top_n
    )

    print(f"[RESULTAT] Articles recommandés : {reco_ids}")

    # Chargement facultatif des métadonnées pour affichage
    df_articles = pd.read_parquet(os.path.join(project_root, "outputs", "df_articles.parquet"))
    display_cols = ["article_id", "category_id", "publisher_id", "created_at_ts"]

    df_display = df_articles[df_articles["article_id"].isin(reco_ids)][display_cols]
    print("[DETAIL] Articles recommandés :")
    print(df_display.to_string(index = False))


if __name__ == "__main__":
    test_reco()


# Exécution du test dans le terminal (racine du projet) :
# python tests/test_recommendation_wrapper.py