# azure/function_app/get_recommendations/__init__.py

import os
import sys
import json
import logging
import traceback
import azure.functions as func

# ================================
# Configuration des logs
# ================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ================================
# Ajout robuste du dossier src/ au sys.path
# ================================
def setup_python_path():
    """Configuration robuste du chemin Python pour Azure Functions"""
    current_file_dir = os.path.dirname(os.path.abspath(__file__))  # get_recommendations/
    function_app_dir = os.path.dirname(current_file_dir)           # function_app/
    src_dir = os.path.join(function_app_dir, "src")                # function_app/src/
    
    paths_to_add = [src_dir, function_app_dir, current_file_dir]
    
    for path in paths_to_add:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
            logging.info(f"[PATH] Ajouté au sys.path: {path}")
    
    # Diagnostic des fichiers disponibles
    if os.path.exists(src_dir):
        py_files = [f for f in os.listdir(src_dir) if f.endswith('.py')]
        logging.info(f"[PATH] Fichiers Python dans src/: {py_files}")
    else:
        logging.error(f"[PATH] Dossier src/ introuvable: {src_dir}")
    
    return src_dir

# Configuration du chemin Python
src_path = setup_python_path()

# ================================
# Import avec gestion d'erreur et diagnostic
# ================================
def import_with_diagnostic():
    """Import du moteur de recommandation avec diagnostic détaillé"""
    try:
        # Test d'import direct depuis src
        from src.wrappers import get_recommendations_from_user, system_diagnostic
        logging.info("[IMPORT] SUCCESS: Import direct depuis src.wrappers")
        return get_recommendations_from_user, system_diagnostic
        
    except ImportError as e1:
        logging.warning(f"[IMPORT] Échec import src.wrappers: {e1}")
        
        try:
            # Test d'import sans préfixe src
            from wrappers import get_recommendations_from_user, system_diagnostic
            logging.info("[IMPORT] SUCCESS: Import sans préfixe src")
            return get_recommendations_from_user, system_diagnostic
            
        except ImportError as e2:
            logging.error(f"[IMPORT] Échec import wrappers: {e2}")
            
            # Diagnostic détaillé en cas d'échec
            logging.error(f"[DIAGNOSTIC] sys.path: {sys.path}")
            logging.error(f"[DIAGNOSTIC] Répertoire de travail: {os.getcwd()}")
            logging.error(f"[DIAGNOSTIC] Fichier courant: {__file__}")
            
            if os.path.exists(src_path):
                files_in_src = os.listdir(src_path)
                logging.error(f"[DIAGNOSTIC] Fichiers dans src/: {files_in_src}")
                
                # Test de l'existence des fichiers critiques
                critical_files = ['wrappers.py', 'loaders.py', 'recommendation_engine.py']
                for file in critical_files:
                    file_path = os.path.join(src_path, file)
                    exists = os.path.exists(file_path)
                    logging.error(f"[DIAGNOSTIC] {file}: {'EXISTS' if exists else 'MISSING'}")
            
            raise RuntimeError(f"Impossible d'importer le moteur de recommandation: {e1}, {e2}")

# Import du moteur de recommandation
try:
    get_recommendations_from_user, system_diagnostic = import_with_diagnostic()
    logging.info("[INIT] Module wrappers importé avec succès")
except Exception as e:
    logging.error(f"[INIT] Erreur critique lors de l'import: {e}")
    get_recommendations_from_user = None
    system_diagnostic = None

# ================================
# Fonction principale Azure Functions
# ================================
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Point d'entrée principal pour Azure Functions"""
    
    logging.info("[MAIN] Azure Function 'get_recommendations' déclenchée")
    
    # Vérification de l'import des modules
    if get_recommendations_from_user is None:
        logging.error("[MAIN] Module de recommandation non disponible")
        return func.HttpResponse(
            json.dumps({
                "error": "Module de recommandation non disponible",
                "status": "IMPORT_ERROR"
            }),
            status_code=500,
            mimetype="application/json"
        )
    
    try:
        # Gestion des paramètres (GET et POST)
        if req.method == "POST":
            try:
                req_body = req.get_json()
            except ValueError:
                req_body = {}
        else:
            req_body = dict(req.params)
        
        logging.info(f"[MAIN] Paramètres reçus: {req_body}")
        
        # Paramètre spécial pour diagnostic système
        if req_body.get("diagnostic") == "true":
            if system_diagnostic:
                diagnostics = system_diagnostic()
                return func.HttpResponse(
                    json.dumps(diagnostics, indent=2),
                    status_code=200,
                    mimetype="application/json"
                )
            else:
                return func.HttpResponse(
                    json.dumps({"error": "Fonction de diagnostic non disponible"}),
                    status_code=500,
                    mimetype="application/json"
                )
        
        # Validation et extraction des paramètres
        try:
            user_id = int(req_body.get("user_id", 0))
            if user_id <= 0:
                raise ValueError("user_id doit être un entier positif")
        except (TypeError, ValueError) as e:
            logging.warning(f"[MAIN] Paramètre user_id invalide: {e}")
            return func.HttpResponse(
                json.dumps({
                    "error": "Paramètre 'user_id' invalide ou manquant",
                    "example": "?user_id=8&mode=auto&top_n=5"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Paramètres optionnels avec valeurs par défaut
        mode = req_body.get("mode", "auto")
        top_n = int(req_body.get("top_n", 5))
        alpha = float(req_body.get("alpha", 0.7))
        source = req_body.get("source", "azure")
        
        logging.info(f"[MAIN] Appel recommandation: user_id={user_id}, mode={mode}, top_n={top_n}, source={source}")
        
        # Génération des recommandations
        recommendations = get_recommendations_from_user(
            user_id=user_id,
            mode=mode,
            top_n=top_n,
            alpha=alpha,
            source=source
        )
        
        if recommendations is None:
            return func.HttpResponse(
                json.dumps({
                    "error": "Impossible de générer des recommandations",
                    "user_id": user_id,
                    "suggestions": "Vérifiez que l'user_id existe dans la base de données"
                }),
                status_code=404,
                mimetype="application/json"
            )
        
        # Réponse de succès
        response_data = {
            "user_id": user_id,
            "mode": mode,
            "top_n": top_n,
            "alpha": alpha,
            "source": source,
            "recommendations": recommendations,
            "count": len(recommendations),
            "status": "SUCCESS"
        }
        
        logging.info(f"[MAIN] Recommandations générées avec succès: {len(recommendations)} articles")
        
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"[MAIN] Erreur lors du traitement de la requête: {str(e)}")
        logging.error(traceback.format_exc())
        
        return func.HttpResponse(
            json.dumps({
                "error": "Erreur interne du serveur",
                "message": str(e),
                "status": "INTERNAL_ERROR"
            }),
            status_code=500,
            mimetype="application/json"
        )