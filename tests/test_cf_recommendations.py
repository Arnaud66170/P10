# ============================================================================
# TEST : Génération de recommandations CF avec modèle pré-entraîné (SVD)
# ============================================================================

import os
import sys
import pandas as pd
import joblib
from surprise import Dataset, Reader, SVD

# Ajout du chemin vers src/ pour les imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# Import des fonctions
from recommendation_engine import get_cf_recommendations
from utils.validators import check_column_presence

try:
    from surprise import SVD
except ImportError:
    raise ImportError("Le module 'surprise' est requis. Installe-le via 'pip install scikit-surprise'.")


# Chargement du DataFrame d’échantillon
sample_path = os.path.join(project_root, "outputs", "df_sample.pkl")
df_sample = pd.read_pickle(sample_path)

# Vérification des colonnes nécessaires
required_cols = ["user_id", "article_id"]
check_column_presence(df_sample, required_cols, "df_sample")

# Chargement du modèle CF déjà entraîné sur df_sample.pkl
model_path = os.path.join(project_root, "models", "model_cf_test_sample.pkl")

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Modèle CF non trouvé à l'emplacement : {model_path}")

model_cf = joblib.load(model_path)

# Sélection d’un utilisateur aléatoire avec au moins un clic
user_id_test = df_sample["user_id"].value_counts().index[0]

# Génération de recommandations
print(f">>> Recommandations CF pour l'utilisateur test : {user_id_test}")
reco_ids = get_cf_recommendations(user_id = user_id_test,
                                  df = df_sample,
                                  model = model_cf,
                                  top_n = 5)

# Vérification du type de sortie
assert isinstance(reco_ids, list), "La sortie de get_cf_recommendations doit être une liste"
assert all(isinstance(i, int) for i in reco_ids), "Chaque élément doit être un entier (article_id)"

print(">>> Résultat OK :", reco_ids)


# Exécution du test dans le terminal (racine du projet) :
# python tests/test_cf_recommendations.py