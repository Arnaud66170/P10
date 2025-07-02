# ============================================================================
# TEST : Entraînement du modèle CF (SVD via Surprise) sur échantillon
# ============================================================================

import os
import pandas as pd
import sys

# Ajout du chemin vers src/ pour les imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# Import des modules à tester
from model_training import train_cf_model
from utils.validators import check_column_presence

# Chargement du DataFrame d’échantillon
sample_path = os.path.join(project_root, "outputs", "df_sample.pkl")
df_sample = pd.read_pickle(sample_path)

# Vérification des colonnes nécessaires
required_cols = ["user_id", "article_id"]
check_column_presence(df_sample, required_cols, "df_sample")

# Entraînement ou chargement du modèle sur l’échantillon
model_output_path = os.path.join(project_root, "models", "model_cf_test_sample.pkl")

print(">>> Test d'entraînement CF sur df_sample.pkl (échantillon)")
model = train_cf_model(df = df_sample,
                       model_path = model_output_path,
                       force_retrain = True)

print(">>> Modèle CF entraîné avec succès sur l'échantillon.")


# Exécution du test dans le terminal (racine du projet) :
# python tests/test_model_cf.py
