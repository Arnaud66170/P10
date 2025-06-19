# azure/function_app/function_app.py

import azure.functions as func
import logging
import json
import sys
import os

# Setup chemin vers src/
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
src_path = os.path.join(project_root, "src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import fonction wrapper
from wrappers import get_recommendations_from_user

# Création de l'app Azure Function
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="getRecommendations")
@app.route(route="getRecommendations")
def run_get_recommendations(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.params.get("user_id")
        if not user_id:
            return func.HttpResponse("Paramètre user_id manquant.", status_code=400)

        recommendations = get_recommendations_from_user(int(user_id))

        return func.HttpResponse(
            json.dumps({"user_id": user_id, "recommendations": recommendations}, ensure_ascii=False),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Erreur dans Azure Function :")
        return func.HttpResponse(f"Erreur : {str(e)}", status_code=500)
