# ============================================================================
# TEST : Génération de recommandations Content-Based Filtering (CBF)
# ============================================================================

import os
import sys
import pandas as pd
import numpy as np

# Ajout du chemin vers src/ pour les imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# Import des fonctions CBF
from data_preprocessing import load_article_embeddings
from recommendation_engine import get_cbf_recommendations
from utils.validators import check_column_presence

# Chargement du sample utilisateur-article
df_sample_path = os.path.join(project_root, "outputs", "df_sample.pkl")
df = pd.read_pickle(df_sample_path)

check_column_presence(df, ["user_id", "article_id"], "df_sample")

# Chargement des embeddings compressés
df_articles_path = os.path.join(project_root, "outputs", "df_articles.parquet")
embeddings, article_id_to_index = load_article_embeddings(df_articles_path)

# Sélection d’un user_id du sample
user_id_test = df["user_id"].value_counts().index[0]

# Recommandation CBF
top_n = 5
reco_ids = get_cbf_recommendations(user_id = user_id_test,
                                   df = df,
                                   embeddings = embeddings,
                                   article_id_to_index = article_id_to_index,
                                   top_n = top_n)

# Vérification des résultats
assert isinstance(reco_ids, list), "La sortie doit être une liste"
assert len(reco_ids) == top_n, f"Le résultat doit contenir {top_n} articles"
assert all(isinstance(i, int) for i in reco_ids), "Les article_id doivent être des entiers"

print(f">>> CBF OK pour user_id {user_id_test} → {reco_ids}")

# Exécution du test dans le terminal (racine du projet) :
# python tests/test_cbf_recommendations.py
