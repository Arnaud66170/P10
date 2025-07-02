# scripts/check_azure_artifacts.py
from dotenv import load_dotenv
load_dotenv(".env.prod")

import os
from azure.storage.blob import BlobServiceClient

def check_blobs():
    """
    Vérifie la présence des artefacts sur Azure Blob Storage
    """
    AZURE_CONN_STR = os.getenv("AZURE_CONN_STR")
    
    if not AZURE_CONN_STR:
        print("ERREUR: Variable AZURE_CONN_STR non trouvée dans .env.prod")
        print("Vérifiez que le fichier .env.prod existe et contient AZURE_CONN_STR")
        return
    
    try:
        client = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
        container_name = "artefacts-fresh"
        
        print(f"Connexion à Azure Storage Account...")
        print(f"Conteneur cible : {container_name}")
        print()
        
        # Liste des fichiers attendus
        expected_files = [
            "df_light.parquet",
            "df_articles_light.parquet", 
            "articles_embeddings_compressed.npz",
            "model_cf_light.pkl"
        ]
        
        container_client = client.get_container_client(container_name)
        blobs = list(container_client.list_blobs())
        
        print("Fichiers trouvés sur Azure :")
        for blob in blobs:
            size_mb = blob.size / (1024 * 1024)
            print(f"  - {blob.name} ({size_mb:.2f} MB)")
        
        print()
        print("Vérification des fichiers attendus :")
        for file in expected_files:
            found = any(blob.name == file for blob in blobs)
            status = "OK" if found else "MANQUANT"
            print(f"  - {file}: {status}")
        
        missing_files = [f for f in expected_files if not any(blob.name == f for blob in blobs)]
        
        if missing_files:
            print()
            print(f"ATTENTION: {len(missing_files)} fichier(s) manquant(s)")
            for f in missing_files:
                print(f"  - {f}")
        else:
            print()
            print("Tous les artefacts sont présents sur Azure!")
            
    except Exception as e:
        print(f"ERREUR lors de la vérification Azure : {e}")

if __name__ == "__main__":
    check_blobs()