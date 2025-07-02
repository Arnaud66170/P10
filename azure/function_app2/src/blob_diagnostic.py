# azure/function_app/src/blob_diagnostic.py
# Test de diagnostic Azure Blob Storage

import os
import logging
from azure.storage.blob import BlobServiceClient

def test_azure_blob_connection():
    """Test de connexion Azure Blob avec diagnostic détaillé"""
    results = {
        "connection_test": False,
        "container_access": False,
        "file_listing": [],
        "error_details": None,
        "environment_vars": {}
    }
    
    # Vérification des variables d'environnement
    conn_vars = [
        "AZURE_STORAGE_CONNECTION_STRING",
        "AZURE_CONN_STR", 
        "AzureWebJobsAZURE_CONN_STR",
        "AzureWebJobsStorage"
    ]
    
    for var in conn_vars:
        value = os.getenv(var)
        results["environment_vars"][var] = "***SET***" if value else "NOT_SET"
    
    # Test de connexion
    try:
        # Tentative avec différentes variables d'environnement
        conn_str = None
        for var in conn_vars:
            conn_str = os.getenv(var)
            if conn_str:
                logging.info(f"[BLOB_TEST] Utilisation de {var}")
                break
        
        if not conn_str:
            results["error_details"] = "Aucune chaîne de connexion trouvée"
            return results
        
        # Test de connexion au service
        blob_service = BlobServiceClient.from_connection_string(conn_str)
        results["connection_test"] = True
        logging.info("[BLOB_TEST] Connexion BlobServiceClient OK")
        
        # Test d'accès au conteneur
        container_name = "artefacts-fresh"
        container_client = blob_service.get_container_client(container_name)
        
        # Liste des blobs
        blob_list = []
        for blob in container_client.list_blobs():
            blob_list.append({
                "name": blob.name,
                "size": blob.size,
                "last_modified": blob.last_modified.isoformat() if blob.last_modified else None
            })
        
        results["container_access"] = True
        results["file_listing"] = blob_list
        logging.info(f"[BLOB_TEST] Accès conteneur OK, {len(blob_list)} fichiers trouvés")
        
    except Exception as e:
        results["error_details"] = str(e)
        logging.error(f"[BLOB_TEST] Erreur: {e}")
        import traceback
        logging.error(traceback.format_exc())
    
    return results

def test_specific_file_download(filename="df_light.parquet"):
    """Test de téléchargement d'un fichier spécifique"""
    try:
        from io import BytesIO
        
        # Récupération de la chaîne de connexion
        conn_str = (
            os.getenv("AZURE_STORAGE_CONNECTION_STRING") or
            os.getenv("AZURE_CONN_STR") or
            os.getenv("AzureWebJobsAZURE_CONN_STR") or
            os.getenv("AzureWebJobsStorage")
        )
        
        if not conn_str:
            return {"success": False, "error": "Pas de chaîne de connexion"}
        
        blob_service = BlobServiceClient.from_connection_string(conn_str)
        blob_client = blob_service.get_blob_client(container="artefacts-fresh", blob=filename)
        
        # Tentative de téléchargement
        buffer = BytesIO()
        download_stream = blob_client.download_blob()
        download_stream.readinto(buffer)
        buffer.seek(0)
        
        file_size = len(buffer.getvalue())
        logging.info(f"[BLOB_DOWNLOAD] {filename} téléchargé: {file_size} bytes")
        
        return {
            "success": True, 
            "file_size": file_size,
            "buffer_ready": True
        }
        
    except Exception as e:
        logging.error(f"[BLOB_DOWNLOAD] Erreur téléchargement {filename}: {e}")
        return {"success": False, "error": str(e)}