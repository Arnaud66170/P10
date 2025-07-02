# example_usage.py

import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np

from src.loaders import (
    load_df,
    load_embeddings,
    load_cf_model
)

# Chargement des variables d’environnement (notamment la chaîne de connexion Azure)
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

AZURE_CONN_STR = os.getenv("AZURE_CONN_STR")

# === LOCAL ===
print("Chargement des artefacts en LOCAL")

df_local = load_df(source="local")
print(f"✔ df_local : {df_local.shape}")

embeddings_local, mapping_local = load_embeddings(source="local")
print(f"✔ embeddings_local : {embeddings_local.shape}, mapping : {len(mapping_local)} articles")

model_local = load_cf_model(source="local")
print("✔ Modèle CF local chargé")

# === AZURE ===
print("\nChargement des artefacts depuis AZURE Blob Storage")

df_blob = load_df(source="azure", connection_string=AZURE_CONN_STR)
print(f"✔ df_blob : {df_blob.shape}")

embeddings_blob, mapping_blob = load_embeddings(source="azure", connection_string=AZURE_CONN_STR)
print(f"✔ embeddings_blob : {embeddings_blob.shape}, mapping : {len(mapping_blob)} articles")

model_blob = load_cf_model(source="azure", connection_string=AZURE_CONN_STR)
print("✔ Modèle CF Azure chargé")
