# azure/function_app/src/wrappers.py

import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Optional, List
from dotenv import load_dotenv

# ================================
# Configuration des logs
# ================================
logging.basicConfig(level=logging.INFO)

# ================================
# Chargement de .env.prod (Azure uniquement)
# ================================
def load_prod_env():
    if os.getenv("ENV"):
        logging.info(f"[ENV] ENV déjà défini : {os.getenv('ENV')}")
        return

    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env.prod"))
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        logging.info("[ENV] .env.prod chargé (local)")
    else:
        logging.info("[ENV] Variables d'environnement Azure utilisées")

load_prod_env()

# ================================
# Import avec gestion d'erreur robuste
# ================================
def safe_import_loaders():
    """Import sécurisé du module loaders avec diagnostic"""
    try:
        # Méthode 1: Import relatif depuis le même dossier src/
        from . import loaders
        logging.info("[IMPORT] Import relatif réussi: from . import loaders")
        return loaders
    except ImportError as e1:
        logging.warning(f"[IMPORT] Échec import relatif: {e1}")
        
        try:
            # Méthode 2: Import absolu après ajout sys.path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            import loaders
            logging.info("[IMPORT] Import absolu réussi après sys.path")
            return loaders
        except ImportError as e2:
            logging.error(f"[IMPORT] Échec import absolu: {e2}")
            
            try:
                # Méthode 3: Import depuis src explicite
                src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
                if src_path not in sys.path:
                    sys.path.insert(0, src_path)
                
                import loaders
                logging.info("[IMPORT] Import src explicite réussi")
                return loaders
            except ImportError as e3:
                logging.error(f"[IMPORT] Toutes les méthodes d'import ont échoué: {e3}")
                raise RuntimeError(f"Impossible d'importer loaders: {e1}, {e2}, {e3}")

# Chargement du module loaders
loaders_module = safe_import_loaders()

# ================================
# Import des autres modules avec même stratégie
# ================================
def safe_import_recommendation_engine():
    """Import sécurisé du moteur de recommandation"""
    try:
        from . import recommendation_engine
        return recommendation_engine
    except ImportError:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            import recommendation_engine
            return recommendation_engine
        except ImportError as e:
            logging.error(f"[IMPORT] Échec import recommendation_engine: {e}")
            raise RuntimeError(f"Impossible d'importer recommendation_engine: {e}")

recommendation_engine_module = safe_import_recommendation_engine()

# ================================
# Import du diagnostic Blob
# ================================
try:
    from . import blob_diagnostic
    blob_diagnostic_module = blob_diagnostic
except ImportError:
    blob_diagnostic_module = None

# ================================
# Fonction principale de recommandation
# ================================
def get_recommendations_from_user(user_id: int, 
                                  mode: str = "auto",
                                  top_n: int = 5,
                                  alpha: float = 0.7,
                                  source: str = "azure") -> Optional[List[dict]]:
    """
    Génère des recommandations pour un utilisateur donné
    
    Args:
        user_id: ID de l'utilisateur
        mode: Mode de recommandation ("auto", "collaborative", "content_based")
        top_n: Nombre de recommandations à retourner
        alpha: Poids pour la recommandation hybride (0.0-1.0)
        source: Source des données ("local" ou "azure")
    
    Returns:
        Liste de dictionnaires contenant les recommandations
    """
    try:
        logging.info(f"[WRAPPER] Début recommandations - user_id={user_id}, mode={mode}, source={source}")
        
        # Chargement des données avec logs détaillés
        logging.info("[WRAPPER] Tentative de chargement df_light...")
        df_light = loaders_module.load_df(source=source, filename="df_light.parquet")
        logging.info(f"[WRAPPER] df_light chargé: {df_light.shape[0]} lignes, {df_light.shape[1]} colonnes")
        
        # Vérification du contenu du DataFrame
        logging.info(f"[WRAPPER] Colonnes disponibles: {list(df_light.columns)}")
        logging.info(f"[WRAPPER] Nombre d'utilisateurs uniques: {df_light['user_id'].nunique()}")
        logging.info(f"[WRAPPER] Premiers user_ids: {sorted(df_light['user_id'].unique())[:10]}")
        
        # Validation de l'utilisateur avec logs détaillés
        user_exists = user_id in df_light['user_id'].unique()
        logging.info(f"[WRAPPER] user_id {user_id} existe: {user_exists}")
        
        if not user_exists:
            available_users = df_light['user_id'].unique()[:10].tolist()
            logging.warning(f"[WRAPPER] user_id {user_id} inexistant. Exemples disponibles: {available_users}")
            return None
        
        # Si on arrive ici, l'utilisateur existe, on continue...
        logging.info(f"[WRAPPER] Génération des recommandations pour user_id {user_id}")
        
        # Chargement de tous les artefacts nécessaires
        logging.info("[WRAPPER] Chargement des artefacts supplémentaires...")
        
        # Chargement du modèle CF
        model_cf = loaders_module.load_cf_model(source=source, filename="model_cf_light.pkl")
        logging.info("[WRAPPER] Modèle CF chargé")
        
        # Chargement des embeddings
        embeddings = loaders_module.load_embeddings(source=source, filename="articles_embeddings_compressed.npz")
        logging.info(f"[WRAPPER] Embeddings chargés: shape {embeddings.shape}")
        
        # Chargement des métadonnées articles
        df_articles = loaders_module.load_metadata(source=source, filename="df_articles_light.parquet")
        logging.info(f"[WRAPPER] Métadonnées articles chargées: {df_articles.shape[0]} articles")
        
        # Création de l'index des articles (supposé nécessaire)
        article_id_to_index = {article_id: idx for idx, article_id in enumerate(df_articles['article_id'].unique())}
        logging.info(f"[WRAPPER] Index articles créé: {len(article_id_to_index)} articles")
        
        # Génération des recommandations avec tous les paramètres
        recommendations = recommendation_engine_module.get_recommendations(
            user_id=user_id,
            df=df_light,
            model_cf=model_cf,
            embeddings=embeddings,
            article_id_to_index=article_id_to_index,
            mode=mode,
            top_n=top_n,
            alpha=alpha
        )
        
        logging.info(f"[WRAPPER] {len(recommendations)} recommandations générées")
        return recommendations
        
    except Exception as e:
        logging.error(f"[WRAPPER] Erreur lors de la génération de recommandations: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return None

# ================================
# Fonction de diagnostic système
# ================================
def system_diagnostic():
    """Fonction de diagnostic complète pour Azure Functions"""
    diagnostics = {
        "python_version": sys.version,
        "current_file": __file__,
        "current_dir": os.path.dirname(os.path.abspath(__file__)),
        "sys_path": sys.path[:5],
        "environment_vars": {
            "ENV": os.getenv("ENV"),
            "AZURE_STORAGE_CONNECTION_STRING": "***" if os.getenv("AZURE_STORAGE_CONNECTION_STRING") else None,
            "AZURE_CONN_STR": "***" if os.getenv("AZURE_CONN_STR") else None,
            "AzureWebJobsAZURE_CONN_STR": "***" if os.getenv("AzureWebJobsAZURE_CONN_STR") else None,
            "AzureWebJobsStorage": "***" if os.getenv("AzureWebJobsStorage") else None,
        },
        "loaders_import_status": "SUCCESS" if 'loaders_module' in globals() else "FAILED",
        "recommendation_engine_import_status": "SUCCESS" if 'recommendation_engine_module' in globals() else "FAILED"
    }
    
    # Test des fichiers présents
    current_dir = os.path.dirname(os.path.abspath(__file__))
    diagnostics["files_in_src"] = [f for f in os.listdir(current_dir) if f.endswith('.py')]
    
    # Test Azure Blob Storage
    if blob_diagnostic_module:
        try:
            blob_test = blob_diagnostic_module.test_azure_blob_connection()
            diagnostics["azure_blob_test"] = blob_test
            
            download_test = blob_diagnostic_module.test_specific_file_download("df_light.parquet")
            diagnostics["blob_download_test"] = download_test
            
        except Exception as e:
            diagnostics["azure_blob_test"] = {"error": str(e)}
    else:
        diagnostics["azure_blob_test"] = {"error": "Module de diagnostic non disponible"}
    
    return diagnostics