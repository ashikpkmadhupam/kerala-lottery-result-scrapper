import os
import firebase_admin
from firebase_admin import credentials, firestore, messaging

firebase_key = os.environ.get("FIREBASE_KEY")

if not firebase_key:
    raise ValueError("FIREBASE_KEY not found in environment variables")

cred_dict = json.loads(firebase_key)
cred = credentials.Certificate(cred_dict)

# Initialize app ONLY ONCE
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Firestore client
firestore_db = firestore.client()
