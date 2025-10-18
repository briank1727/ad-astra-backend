from admin import db
from firebase_admin import auth
from firebase_functions import https_fn
import re
import time
import json
import traceback


def is_valid_email(email):
    email_regex = r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$"
    return bool(re.match(email_regex, email, re.IGNORECASE))


min_password_length = 6
password_regex = r"^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+$"
name_regex = r"^[A-Za-z]+$"


@https_fn.on_request()
def create_user(req: https_fn.Request):
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
            return https_fn.Response(
                json.dumps(
                    {"error": "Missing required fields: " + ", ".join(missing_fields)}
                ),
                status=400,
            )

        invalid_types = []
        if not isinstance(email, str):
            invalid_types.append("Email")
        if not isinstance(password, str):
            invalid_types.append("Password")
        if not isinstance(firstName, str):
            invalid_types.append("First Name")
        if not isinstance(lastName, str):
            invalid_types.append("Last Name")

        if len(invalid_types) > 0:
            return https_fn.Response(
                json.dumps(
                    {"error": "Invalid types for fields: " + ", ".join(invalid_types)}
                ),
                status=400,
            )

        email = email.strip().lower()
        if not is_valid_email(email):
            return https_fn.Response(
                json.dumps({"error": "Invalid email format"}), status=400
            )

        try:
            auth.get_user_by_email(email)

            return https_fn.Response(
                json.dumps({"error": "Email is already in use"}), status=400
            )
        except auth.UserNotFoundError:
            pass
        except Exception as error:
            if hasattr(error, "code") and error.code != "auth/user-not-found":
                return https_fn.Response(
                    json.dumps({"error": "Error checking user existence"}), status=500
                )

        if len(password) < min_password_length:
            return https_fn.Response(
                json.dumps(
                    {
                        "error": f"Password must be at least {min_password_length} characters long"
                    }
                ),
                status=400,
            )

        if not re.match(password_regex, password):
            return https_fn.Response(
                json.dumps({"error": "Password contains invalid characters."}),
                status=400,
            )

        firstName = firstName.strip()
        lastName = lastName.strip()

        if len(firstName) < 1:
            return https_fn.Response(
                json.dumps({"error": "First Name must be at least 1 character."}),
                status=400,
            )

        if len(lastName) < 1:
            return https_fn.Response(
                json.dumps({"error": "Last Name must be at least 1 character."}),
                status=400,
            )

        if not re.match(name_regex, firstName):
            return https_fn.Response(
                json.dumps({"error": "First Name contains invalid characters."}),
                status=400,
            )
        if not re.match(name_regex, lastName):
            return https_fn.Response(
                json.dumps({"error": "Last Name contains invalid characters."}),
                status=400,
            )

        firstName = firstName[0].upper() + firstName[1:].lower()
        lastName = lastName[0].upper() + lastName[1:].lower()

        userRecord = auth.create_user(
            email=email, password=password, display_name=f"{firstName} {lastName}"
        )
        db.collection("users").document(userRecord.uid).set(
            {
                "firstName": firstName,
                "lastName": lastName,
                "email": email,
                "joined": int(time.time()),
                "money": 0,
            }
        )

        return https_fn.Response(
            json.dumps({"message": "User created successfully", "uid": userRecord.uid}),
            status=201,
        )
    except Exception as e:
        print(
            f"Error creating user: {e} (line {traceback.extract_tb(e.__traceback__)[-1].lineno})"
        )
        return https_fn.Response(
            json.dumps({"error": "Error creating user"}), status=500
        )


@https_fn.on_request()
def fetch_user_data(req: https_fn.Request):
    try:
        data = req.get_json()
        uid = data.get("uid")

        if not uid:
            return https_fn.Response(
                json.dumps({"error": "Missing required field: uid"}), status=400
            )

        if not isinstance(uid, str):
            return https_fn.Response(
                json.dumps({"error": "Invalid type for field: uid"}), status=400
            )

        user_doc = db.collection("users").document(uid).get()
        if not user_doc.exists:
            return https_fn.Response(
                json.dumps({"error": "User not found"}), status=404
            )

        user_data = user_doc.to_dict()
        return https_fn.Response(json.dumps({"userData": user_data}), status=200)
    except Exception as e:
        print(f"Error fetching user data: {e.with_traceback()}")
        return https_fn.Response(
            json.dumps({"error": "Error fetching user data"}), status=500
        )


@https_fn.on_request()
def delete_user(req: https_fn.Request):
    try:
        data = req.get_json()
        uid = data.get("uid")

        if not uid:
            return https_fn.Response(
                json.dumps({"error": "Missing required field: uid"}), status=400
            )

        if not isinstance(uid, str):
            return https_fn.Response(
                json.dumps({"error": "Invalid type for field: uid"}), status=400
            )

        auth.delete_user(uid)
        db.collection("users").document(uid).delete()

        return https_fn.Response(
            json.dumps({"message": "User deleted successfully"}), status=200
        )
    except Exception as e:
        print(f"Error deleting user: {e.with_traceback()}")
        return https_fn.Response(
            json.dumps({"error": "Error deleting user"}), status=500
        )
