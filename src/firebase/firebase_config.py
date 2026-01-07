import os
import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")

cred = credentials.Certificate(KEY_PATH)

# Initialize app ONLY ONCE
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Firestore client
firestore_db = firestore.client()