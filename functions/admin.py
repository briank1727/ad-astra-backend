import firebase_admin
from firebase_admin import credentials, firestore

# Initialize the Firebase Admin SDK
firebase_admin.initialize_app()

# Get Firestore database instance
db = firestore.client()

# Export the admin and db for use in other modules
__all__ = ["firebase_admin", "db"]
