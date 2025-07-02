# Correction du fichier src/wrappers.py pour gérer les deux modes

import os
import sys
import pandas as pd
import numpy as np
from typing import List
from dotenv import load_dotenv
import logging

# Chargement dynamique .env
def load_correct_env():
    if os.getenv("ENV"):
        logging.info(f"[ENV] Mode '{os.getenv('ENV')}' déjà défini.")
        return

    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_prod = os.path.join(root, ".env.prod")
    env_dev = os.path.join(root, ".env.dev")

    if os.path.exists(env_dev):
        load_dotenv(dotenv_path=env_dev)
        logging.info("[ENV] .env.dev chargé (mode développement)")
    elif os.path.exists(env_prod):
        load_dotenv(dotenv_path=env_prod)
        logging.info("[ENV] .env.prod chargé (mode production)")
    else:
        logging.warning("[ENV] Aucun fichier .env trouvé")

load_correct_env()

# Imports
try:
    from utils.paths import get_project_root
except ModuleNotFoundError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.abspath(os.path.join(current_dir, "..")))
    from utils.paths import get_project_root

project_root = get_project_root()
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from loaders import load_cf_model, load_df, load_metadata, load_embeddings
from recommendation_engine import get_recommendations

def extract_embeddings_and_index(df_articles: pd.DataFrame) -> tuple[np.ndarray, dict]:
    """
    Extrait la matrice des embeddings et le mapping article_id → index.
    """
    if "embedding" not in df_articles.columns:
        raise ValueError("Colonne 'embedding' manquante dans df_articles")
    
    embeddings = np.array(df_articles["embedding"].tolist())
    article_id_to_index = {
        article_id: idx 
        for idx, article_id in enumerate(df_articles["article_id"].values)
    }
    
    return embeddings, article_id_to_index

def get_recommendations_from_user(user_id: int,
                                  mode: str = "hybrid",
                                  alpha: float = 0.7,
                                  user_clicks_threshold: int = 3,
                                  top_n: int = 5,
                                  source: str = "local",
                                  connection_string: str = None) -> List[dict]:
    """
    Fonction principale de recommandation avec gestion dual local/azure.
    
    Args:
        user_id: ID utilisateur
        mode: "cbf", "cf", "hybrid", "auto"
        alpha: Pondération hybride (0-1)
        user_clicks_threshold: Seuil minimum de clics
        top_n: Nombre de recommandations
        source: "local" (artefacts complets) ou "azure" (artefacts allégés)
        connection_string: Chaîne connexion Azure
    
    Returns:
        Liste de recommandations
    """
    
    logging.info(f"[WRAPPERS] Démarrage recommandations pour user_id={user_id}, source={source}")
    
    try:
        # Configuration des fichiers selon le mode
        if source == "local":
            # Mode développement : artefacts complets
            df_filename = "df.parquet"
            articles_filename = "df_articles.parquet"
            model_filename = "model_cf.pkl"
            embeddings_filename = "articles_embeddings_compressed.npz"
            container_name = None  # Non utilisé en local
            logging.info("[WRAPPERS] Mode LOCAL : artefacts complets")
            
        elif source == "azure":
            # Mode production : artefacts allégés
            df_filename = "df_light.parquet"
            articles_filename = "df_articles_light.parquet"
            model_filename = "model_cf_light.pkl"
            embeddings_filename = "articles_embeddings_compressed.npz"
            container_name = "artefacts-fresh"  # Conteneur actuel
            logging.info("[WRAPPERS] Mode AZURE : artefacts allégés")
            
        else:
            raise ValueError(f"Source invalide : {source}. Utiliser 'local' ou 'azure'")

        # Chargement des artefacts
        logging.info(f"[WRAPPERS] Chargement des artefacts...")

        # Chargement des clics utilisateurs
        df = load_df(source=source, 
                     filename=df_filename, 
                     container_name=container_name,
                     connection_string=connection_string)
        logging.info(f"[WRAPPERS] df chargé : {df.shape}")

        # Chargement des embeddings
        embeddings = load_embeddings(source=source, 
                                     filename=embeddings_filename,
                                     container_name=container_name,
                                     connection_string=connection_string)
        logging.info(f"[WRAPPERS] Embeddings chargés : {embeddings.shape}")

        # Chargement des métadonnées articles
        df_articles = load_metadata(source=source, 
                                    filename=articles_filename,
                                    container_name=container_name,
                                    connection_string=connection_string)
        logging.info(f"[WRAPPERS] Articles chargés : {df_articles.shape}")

        # Extraction des mappings
        embeddings_matrix, article_id_to_index = extract_embeddings_and_index(df_articles)
        
        # Chargement du modèle CF si nécessaire
        model_cf = None
        if mode in ["cf", "hybrid", "auto"]:
            model_cf = load_cf_model(source=source, 
                                     filename=model_filename,
                                     container_name=container_name,
                                     connection_string=connection_string)
            logging.info("[WRAPPERS] Modèle CF chargé")

        # Génération des recommandations
        recommendations = get_recommendations(
            user_id=user_id,
            df=df,
            model_cf=model_cf,
            embeddings=embeddings_matrix,
            article_id_to_index=article_id_to_index,
            mode=mode,
            alpha=alpha,
            user_clicks_threshold=user_clicks_threshold,
            top_n=top_n
        )

        logging.info(f"[WRAPPERS] {len(recommendations)} recommandations générées")
        return recommendations

    except Exception as e:
        logging.error(f"[WRAPPERS] Erreur : {str(e)}")
        raise RuntimeError(f"Erreur dans get_recommendations_from_user: {str(e)}")