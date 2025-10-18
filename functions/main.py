# Firebase Functions main.py - All functions consolidated with CORS support
from firebase_admin import initialize_app, firestore, auth
from firebase_functions import https_fn
import re
import time
import json
import traceback
import google.cloud.firestore

app = initialize_app()


# CORS helper function
def cors_response(body, status=200):
    """Create an HTTP response with CORS headers"""
    response = https_fn.Response(body, status=status)
    response.headers.set("Access-Control-Allow-Origin", "*")
    response.headers.set(
        "Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"
    )
    response.headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.set("Access-Control-Max-Age", "3600")
    response.headers.set("Content-Type", "application/json")
    return response


def handle_cors(req):
    """Handle CORS preflight requests"""
    if req.method == "OPTIONS":
        return cors_response("")
    return None


# Helper functions for validation
def is_valid_email(email):
    email_regex = r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$"
    return bool(re.match(email_regex, email, re.IGNORECASE))


min_password_length = 6
password_regex = r"^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+$"
name_regex = r"^[A-Za-z]+$"


# Test function
@https_fn.on_request()
def hello_world(req: https_fn.Request) -> https_fn.Response:
    cors_resp = handle_cors(req)
    if cors_resp:
        return cors_resp

    return cors_response("Hello World! All functions in main.py")


# User management functions
@https_fn.on_request()
def create_user(req: https_fn.Request):
    cors_resp = handle_cors(req)
    if cors_resp:
        return cors_resp

    try:
        data = req.get_json()
        missing_fields = []
        email = data.get("email")
        password = data.get("password")
        firstName = data.get("firstName")
        lastName = data.get("lastName")

        if not email:
            missing_fields.append("email")
        if not password:
            missing_fields.append("password")
        if not firstName:
            missing_fields.append("firstName")
        if not lastName:
            missing_fields.append("lastName")

        if len(missing_fields) > 0:
            return cors_response(
                json.dumps(
                    {"error": f"Missing required fields: {', '.join(missing_fields)}"}
                ),
                status=400,
            )

        # Validate input types
        if not isinstance(email, str):
            return cors_response(
                json.dumps({"error": "Invalid type for field: email"}), status=400
            )
        if not isinstance(password, str):
            return cors_response(
                json.dumps({"error": "Invalid type for field: password"}), status=400
            )
        if not isinstance(firstName, str):
            return cors_response(
                json.dumps({"error": "Invalid type for field: firstName"}), status=400
            )
        if not isinstance(lastName, str):
            return cors_response(
                json.dumps({"error": "Invalid type for field: lastName"}), status=400
            )

        # Validate email format
        if not is_valid_email(email):
            return cors_response(
                json.dumps({"error": "Invalid email format"}), status=400
            )

        # Validate password
        if len(password) < min_password_length:
            return cors_response(
                json.dumps(
                    {
                        "error": f"Password must be at least {min_password_length} characters long"
                    }
                ),
                status=400,
            )
        if not re.match(password_regex, password):
            return cors_response(
                json.dumps({"error": "Password contains invalid characters"}),
                status=400,
            )

        # Validate names
        if not re.match(name_regex, firstName):
            return cors_response(
                json.dumps({"error": "First name must only contain letters"}),
                status=400,
            )
        if not re.match(name_regex, lastName):
            return cors_response(
                json.dumps({"error": "Last name must only contain letters"}), status=400
            )

        # Create user in Firebase Auth
        userRecord = auth.create_user(
            email=email, password=password, display_name=f"{firstName} {lastName}"
        )

        # Store additional user data in Firestore
        db: google.cloud.firestore.Client = firestore.client()
        db.collection("users").document(userRecord.uid).set(
            {
                "firstName": firstName,
                "lastName": lastName,
                "email": email,
                "joined": int(time.time()),
                "money": 0,
            }
        )

        return cors_response(
            json.dumps({"message": "User created successfully", "uid": userRecord.uid}),
            status=201,
        )

    except Exception as e:
        print(f"Error creating user: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return cors_response(json.dumps({"error": "Internal server error"}), status=500)


@https_fn.on_request()
def fetch_user_data(req: https_fn.Request):
    cors_resp = handle_cors(req)
    if cors_resp:
        return cors_resp

    try:
        data = req.get_json()
        uid = data.get("uid")

        if not uid:
            return cors_response(
                json.dumps({"error": "Missing required field: uid"}), status=400
            )

        if not isinstance(uid, str):
            return cors_response(
                json.dumps({"error": "Invalid type for field: uid"}), status=400
            )

        db: google.cloud.firestore.Client = firestore.client()
        user_doc = db.collection("users").document(uid).get()
        if not user_doc.exists:
            return cors_response(json.dumps({"error": "User not found"}), status=404)

        user_data = user_doc.to_dict()
        return cors_response(json.dumps({"userData": user_data}), status=200)

    except Exception as e:
        print(f"Error fetching user data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return cors_response(json.dumps({"error": "Internal server error"}), status=500)


@https_fn.on_request()
def delete_user(req: https_fn.Request):
    cors_resp = handle_cors(req)
    if cors_resp:
        return cors_resp

    try:
        data = req.get_json()
        uid = data.get("uid")

        if not uid:
            return cors_response(
                json.dumps({"error": "Missing required field: uid"}), status=400
            )

        if not isinstance(uid, str):
            return cors_response(
                json.dumps({"error": "Invalid type for field: uid"}), status=400
            )

        db: google.cloud.firestore.Client = firestore.client()
        user_doc = db.collection("users").document(uid).get()
        if not user_doc.exists:
            return cors_response(
                json.dumps({"error": "User not found in Firestore"}), status=404
            )

        # Check if user exists in Firebase Auth
        try:
            auth.get_user(uid)
        except auth.UserNotFoundError:
            return cors_response(
                json.dumps({"error": "User not found in Firebase Auth"}), status=404
            )

        auth.delete_user(uid)
        db.collection("users").document(uid).delete()

        return cors_response(
            json.dumps({"message": "User deleted successfully"}), status=200
        )

    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return cors_response(json.dumps({"error": "Internal server error"}), status=500)


# Bank/Money management functions
@https_fn.on_request()
def add_money(req: https_fn.Request):
    cors_resp = handle_cors(req)
    if cors_resp:
        return cors_resp

    try:
        data = req.get_json()
        uid = data.get("uid")
        amount = data.get("amount")

        if not uid or amount is None:
            return cors_response(
                json.dumps({"error": "Missing required fields: uid and amount"}),
                status=400,
            )

        if not isinstance(amount, (int, float)) or amount <= 0:
            return cors_response(
                json.dumps({"error": "Amount must be a positive number"}),
                status=400,
            )

        db: google.cloud.firestore.Client = firestore.client()
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return cors_response(
                json.dumps({"error": "User not found"}),
                status=404,
            )

        user_data = user_doc.to_dict()
        current_money = user_data.get("money", 0)
        new_money = current_money + amount

        user_ref.update({"money": new_money})

        return cors_response(
            json.dumps(
                {
                    "message": "Money added successfully",
                    "previous_balance": current_money,
                    "amount_added": amount,
                    "new_balance": new_money,
                }
            ),
            status=200,
        )

    except Exception as e:
        print(f"Error adding money: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return cors_response(json.dumps({"error": "Internal server error"}), status=500)
