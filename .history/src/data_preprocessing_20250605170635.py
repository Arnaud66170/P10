# Exemple à intégrer dans src/data_preprocessing.py

import numpy as np
import pandas as pd

def load_articles_with_embeddings(metadata_path, embeddings_path):
    # Chargement des métadonnées
    df_articles = pd.read_csv(metadata_path)
    
    # Chargement des embeddings
    embeddings = np.load(embeddings_path) if embeddings_path.endswith(".npz") else pickle.load(open(embeddings_path, "rb"))

    # Vérification de l'alignement
    assert len(df_articles) == embeddings.shape[0], "Le nombre d'articles ne correspond pas aux embeddings"

    # Ajout des embeddings comme colonne ou attribut externe
    df_articles["embedding"] = list(embeddings)

    return df_articles
