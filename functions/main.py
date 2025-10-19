# Firebase Functions main.py - All functions consolidated with CORS support
from firebase_admin import initialize_app, firestore, auth
from firebase_functions import https_fn
import re
import time
import json
import traceback
import google.cloud.firestore
from gemini import generate_gamified_structure

app = initialize_app()


# CORS helper function
def cors_response(body, status=200):
    """Create an HTTP response with CORS headers"""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "3600",
    }
    if body:
        headers["Content-Type"] = "application/json"
    return https_fn.Response(body, status=status, headers=headers)
    # return https_fn.Response(body, status=status)


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

    return cors_response("Hello World All functions in main.py")


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


@https_fn.on_request()
def fetch_questions(req: https_fn.Request):
    cors_resp = handle_cors(req)
    if cors_resp:
        return cors_resp

    try:
        db: google.cloud.firestore.Client = firestore.client()
        questions_ref = db.collection("questions")
        questions = []
        for doc in questions_ref.stream():
            question_data = doc.to_dict()
            question_data["id"] = doc.id  # Include document ID
            questions.append(question_data)

        return cors_response(
            json.dumps({"questions": questions}),
            status=200,
        )
    except Exception as e:
        print(f"Error fetching questions: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return cors_response(json.dumps({"error": "Internal server error"}), status=500)


def valid_questions(questions_answers):
    print(questions_answers)
    if not isinstance(questions_answers, list):
        print("Error: questions_answers is not a list.")
        return False
    for idx, item in enumerate(questions_answers):
        if not isinstance(item, dict):
            print(f"Error: Item at index {idx} is not a dictionary.")
            return False
        if "question" not in item or "answer" not in item:
            print(f"Error: Item at index {idx} missing 'question' or 'answer' key.")
            return False
        if not isinstance(item["question"], str) or not isinstance(item["answer"], str):
            print(
                f"Error: 'question' or 'answer' in item at index {idx} is not a string."
            )
            return False
        if len(item["question"].strip()) == 0 or len(item["answer"].strip()) == 0:
            print(
                f"Error: 'question' or 'answer' in item at index {idx} is empty or whitespace."
            )
            return False
    return True


def valid_achievements(achievements):
    print(achievements)
    print(type(achievements))
    if not isinstance(achievements, dict):
        print("Invalid: achievements is not a dictionary")
        return False
    if "planets" not in achievements:
        print("Invalid: 'planets' key missing in achievements")
        return False
    if not isinstance(achievements["planets"], list):
        print("Invalid: 'planets' is not a list")
        return False
    for planet in achievements["planets"]:
        if not isinstance(planet, dict):
            print("Invalid: planet entry is not a dictionary")
            return False
        if (
            "name" not in planet
            or "image" not in planet
            or "achievements" not in planet
        ):
            print("Invalid: planet missing 'name', 'image', or 'achievements' key")
            return False
        if not isinstance(planet["name"], str) or not isinstance(planet["image"], str):
            print("Invalid: planet 'name' or 'image' is not a string")
            return False
        if not isinstance(planet["achievements"], list):
            print("Invalid: planet 'achievements' is not a list")
            return False
        for achievement in planet["achievements"]:
            if not isinstance(achievement, dict):
                print("Invalid: achievement entry is not a dictionary")
                return False
            if (
                "name" not in achievement
                or "description" not in achievement
                or "type" not in achievement
            ):
                print(
                    "Invalid: achievement missing 'name', 'description', or 'type' key"
                )
                return False
            if not isinstance(achievement["name"], str) or not isinstance(
                achievement["description"], str
            ):
                print("Invalid: achievement 'name' or 'description' is not a string")
                return False
            if achievement["type"] not in ["progress", "game", "streak"]:
                print(
                    f"Invalid: achievement 'type' is not valid ({achievement.get('type')})"
                )
                return False
            if "data" not in achievement:
                print("Invalid: achievement missing 'data' key")
                return False
            if not isinstance(achievement["data"], dict):
                print("Invalid: achievement 'data' is not a dictionary")
                return False
            # Validate achievement["data"] based on achievement["type"]
            if achievement["type"] == "progress":
                if (
                    "startDate" not in achievement["data"]
                    or "endDate" not in achievement["data"]
                ):
                    print(
                        "Invalid: progress achievement missing 'startDate' or 'endDate'"
                    )
                    return False
                if not isinstance(
                    achievement["data"]["startDate"], str
                ) or not isinstance(achievement["data"]["endDate"], str):
                    print(
                        "Invalid: progress achievement 'startDate' or 'endDate' is not a string"
                    )
                    return False
                date_regex = r"^\d{4}-\d{2}-\d{2}$"
                if not re.match(
                    date_regex, achievement["data"]["startDate"]
                ) or not re.match(date_regex, achievement["data"]["endDate"]):
                    print(
                        "Invalid: progress achievement 'startDate' or 'endDate' does not match YYYY-MM-DD"
                    )
                    return False
                if "moneyToSave" not in achievement["data"] or not isinstance(
                    achievement["data"]["moneyToSave"], int
                ):
                    print(
                        "Invalid: progress achievement missing 'moneyToSave' or it is not an int"
                    )
                    return False
            elif achievement["type"] == "streak":
                if (
                    "startDate" not in achievement["data"]
                    or "endDate" not in achievement["data"]
                ):
                    print(
                        "Invalid: streak achievement missing 'startDate' or 'endDate'"
                    )
                    return False
                if not isinstance(
                    achievement["data"]["startDate"], str
                ) or not isinstance(achievement["data"]["endDate"], str):
                    print(
                        "Invalid: streak achievement 'startDate' or 'endDate' is not a string"
                    )
                    return False
                date_regex = r"^\d{4}-\d{2}-\d{2}$"
                if not re.match(
                    date_regex, achievement["data"]["startDate"]
                ) or not re.match(date_regex, achievement["data"]["endDate"]):
                    print(
                        "Invalid: streak achievement 'startDate' or 'endDate' does not match YYYY-MM-DD"
                    )
                    return False
                if "numConsecutiveDays" not in achievement["data"] or not isinstance(
                    achievement["data"]["numConsecutiveDays"], int
                ):
                    print(
                        "Invalid: streak achievement missing 'numConsecutiveDays' or it is not an int"
                    )
                    return False
                if "minimumStreakAmount" not in achievement["data"] or not isinstance(
                    achievement["data"]["minimumStreakAmount"], int
                ):
                    print(
                        "Invalid: streak achievement missing 'minimumStreakAmount' or it is not an int"
                    )
                    return False
                if "frequency" not in achievement["data"] or achievement["data"][
                    "frequency"
                ] not in ["daily", "weekly", "monthly"]:
                    print(
                        "Invalid: streak achievement missing 'frequency' or it is not valid"
                    )
                    return False
            elif achievement["type"] == "game":
                if (
                    "startDate" not in achievement["data"]
                    or "endDate" not in achievement["data"]
                ):
                    print("Invalid: game achievement missing 'startDate' or 'endDate'")
                    return False
                if not isinstance(
                    achievement["data"]["startDate"], str
                ) or not isinstance(achievement["data"]["endDate"], str):
                    print(
                        "Invalid: game achievement 'startDate' or 'endDate' is not a string"
                    )
                    return False
                date_regex = r"^\d{4}-\d{2}-\d{2}$"
                if not re.match(
                    date_regex, achievement["data"]["startDate"]
                ) or not re.match(date_regex, achievement["data"]["endDate"]):
                    print(
                        "Invalid: game achievement 'startDate' or 'endDate' does not match YYYY-MM-DD"
                    )
                    return False
    return True


@https_fn.on_request()
def generate_ai_achievements(req: https_fn.Request):
    cors_resp = handle_cors(req)
    if cors_resp:
        return cors_resp

    try:
        data = req.get_json()
        uid = data.get("uid")
        questions_answers = data.get("questions")

        if not uid:
            return cors_response(
                json.dumps({"error": "Missing required field: uid"}), status=400
            )
        if not questions_answers:
            return cors_response(
                json.dumps({"error": "Invalid questions format"}), status=400
            )

        try:
            time.sleep(10)
            raise Exception("Random")
            # result = generate_gamified_structure(questions_answers)
            # data = result
            # if not valid_achievements(data):
            # raise ValueError("Generated achievements structure is invalid")
        except Exception as e:
            print(f"Error generating gamified structure: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            # Fallback to default response if Gemini fails
            with open("default_response.json", "r") as f:
                data = json.load(f)

        db: google.cloud.firestore.Client = firestore.client()
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return cors_response(
                json.dumps({"error": "User not found"}),
                status=404,
            )

        user_ref.update({"achievements": data})

        return cors_response(
            json.dumps(
                {
                    "message": "Achievements generated and stored successfully",
                    "achievements": data,
                }
            ),
            status=200,
        )
    except Exception as e:
        print(f"Error generating AI achievements: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return cors_response(json.dumps({"error": "Internal server error"}), status=500)


@https_fn.on_request()
def fetch_achievements(req: https_fn.Request):
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
        achievements = user_data.get("achievements", {})

        return cors_response(json.dumps({"achievements": achievements}), status=200)

    except Exception as e:
        print(f"Error fetching achievements: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return cors_response(json.dumps({"error": "Internal server error"}), status=500)


@https_fn.on_request()
def store_game_data(req: https_fn.Request):
    cors_resp = handle_cors(req)
    if cors_resp:
        return cors_resp

    try:
        data = req.get_json()
        uid = data.get("uid")
        store_game_data = data.get("gameData")

        if not uid or store_game_data is None:
            return cors_response(
                json.dumps({"error": "Missing required fields: uid and gameData"}),
                status=400,
            )
        if not isinstance(store_game_data, dict):
            return cors_response(
                json.dumps({"error": "gameData must be a dictionary"}), status=400
            )
        db: google.cloud.firestore.Client = firestore.client()
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return cors_response(
                json.dumps({"error": "User not found"}),
                status=404,
            )

        user_ref.update({"gameData": store_game_data})
        return cors_response(
            json.dumps({"message": "Game data stored successfully"}),
            status=200,
        )
    except Exception as e:
        print(f"Error storing game data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return cors_response(json.dumps({"error": "Internal server error"}), status=500)


@https_fn.on_request()
def fetch_game_data(req: https_fn.Request):
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
        game_data = user_data.get("gameData", {})

        return cors_response(json.dumps({"gameData": game_data}), status=200)

    except Exception as e:
        print(f"Error fetching game data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return cors_response(json.dumps({"error": "Internal server error"}), status=500)
