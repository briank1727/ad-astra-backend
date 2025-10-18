from admin import db
from firebase_functions import https_fn
import json
import traceback


@https_fn.on_request()
def generate_achievements(req: https_fn.Request):
    data = req.get_json()
    questions = data.get("questions", [])

    if not questions:
        return https_fn.Response(
            json.dumps({"error": "No questions provided"}),
            status=400,
        )
