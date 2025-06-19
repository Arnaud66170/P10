import azure.functions as func
import json
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Function triggered")

    user_id = req.params.get("user_id", None)
    if not user_id:
        return func.HttpResponse("Missing 'user_id'", status_code=400)

    try:
        user_id = int(user_id)
        recommendations = [10001, 10002, 10003]  # réponse factice de test

        return func.HttpResponse(
            json.dumps({"user_id": user_id, "recommendations": recommendations}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )
