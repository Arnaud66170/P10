# azure/function_app/get_recommendations/__init__.py

import azure.functions as func
import json
import logging
import os
import sys
from dotenv import load_dotenv

# ================================
# 📦 Chargement dynamique .env
# ================================

def load_correct_env():
    """
    Charge .env.dev ou .env.prod dynamiquement si la variable ENV n’est pas encore définie.
    """
    if os.getenv("ENV"):
        logging.info(f"[ENV] Mode déjà défini via ENV = {os.getenv('ENV')}")
        return

    current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    env_dev = os.path.join(current_dir, ".env.dev")
    env_prod = os.path.join(current_dir, ".env.prod")

    if os.path.exists(env_dev):
        load_dotenv(dotenv_path=env_dev)
        logging.info("[ENV] ✅ .env.dev chargé")
    elif os.path.exists(env_prod):
        load_dotenv(dotenv_path=env_prod)
        logging.info("[ENV] ✅ .env.prod chargé")
    else:
        logging.warning("[ENV] ⚠️ Aucun fichier .env trouvé")

load_correct_env()

# ================================
# 🔍 Recherche dynamique de src/
# ================================

def find_src_path(start_path: str, max_depth: int = 5) -> str:
    current_path = start_path
    for _ in range(max_depth):
        candidate = os.path.join(current_path, "src")
        if os.path.isdir(candidate):
            return candidate
        current_path = os.path.dirname(current_path)
    raise FileNotFoundError("❌ Dossier 'src/' introuvable dans l'arborescence ascendante.")

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = find_src_path(current_dir)

    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        logging.info(f"[INIT] src/ détecté et ajouté au sys.path : {src_path}")

except Exception as e:
    logging.error(f"[INIT ERROR] Impossible d'ajouter src/ : {str(e)}")
    raise

# ================================
# ✅ Import du moteur de recommandation
# ================================

try:
    from wrappers import get_recommendations_from_user
except ImportError as e:
    logging.error(f"[IMPORT ERROR] wrappers.py introuvable ou cassé : {str(e)}")
    raise

# ================================
# 🚀 Azure Function principale
# ================================

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("✅ Function 'get_recommendations' triggered.")

    try:
        # ===== Paramètres requis =====
        user_id   = req.params.get("user_id")
        mode      = req.params.get("mode", "auto")
        alpha     = req.params.get("alpha", "0.5")
        threshold = req.params.get("threshold", "5")
        top_n     = req.params.get("top_n", "5")

        # ===== Paramètre optionnel 'source' =====
        source = req.params.get("source", "azure").lower()
        env    = os.getenv("ENV", "production").lower()

        # ===== Validation des paramètres =====
        if user_id is None:
            return func.HttpResponse(json.dumps({"error": "Missing 'user_id'"}), status_code=400)

        try:
            user_id   = int(user_id)
            alpha     = float(alpha)
            threshold = int(threshold)
            top_n     = int(top_n)
        except ValueError as ve:
            return func.HttpResponse(json.dumps({"error": f"Invalid parameter types: {str(ve)}"}), status_code=400)

        if source not in ["local", "azure"]:
            return func.HttpResponse(json.dumps({"error": f"Paramètre 'source' invalide. Attendu : 'local' ou 'azure'"}), status_code=400)

        if env == "production" and source == "local":
            return func.HttpResponse(json.dumps({"error": "⚠️ Source 'local' interdite en mode production"}), status_code=403)

        logging.info(f"[PARAMS] user_id={user_id}, mode={mode}, alpha={alpha}, threshold={threshold}, top_n={top_n}, source={source}, env={env}")

        # ===== Appel au moteur de recommandation =====
        recommendations = get_recommendations_from_user(
            user_id=user_id,
            mode=mode,
            alpha=alpha,
            user_clicks_threshold=threshold,
            top_n=top_n,
            source=source
        )

        return func.HttpResponse(
            json.dumps({"user_id": user_id, "recommendations": recommendations}, indent=2),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        import traceback
        logging.error(f"🔥 Erreur dans get_recommendations: {str(e)}")
        logging.error(traceback.format_exc())
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
