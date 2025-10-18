from admin import db
from firebase_functions import https_fn
import json
import traceback


@https_fn.on_request()
def add_money(req: https_fn.Request):
    try:
        data = req.get_json()
        uid = data.get("uid")
        amount = data.get("amount")

        if not uid or amount is None:
            return https_fn.Response(
                json.dumps({"error": "Missing required fields: uid and amount"}),
                status=400,
            )

        if not isinstance(amount, (int, float)) or amount <= 0:
            return https_fn.Response(
                json.dumps({"error": "Amount must be a positive number"}),
                status=400,
            )

        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return https_fn.Response(
                json.dumps({"error": "User not found"}),
                status=404,
            )

        user_data = user_doc.to_dict()
        current_money = user_data.get("money", 0)
        new_money = current_money + amount

        user_ref.update({"money": new_money})

        return https_fn.Response(
            json.dumps(
                {"message": "Money added successfully", "new_balance": new_money}
            ),
            status=200,
        )

    except Exception as e:
        print(
            f"Error adding money: {e} (line {traceback.extract_tb(e.__traceback__)[-1].lineno})"
        )
        return https_fn.Response(
            json.dumps({"error": "Error adding money"}),
            status=500,
        )
