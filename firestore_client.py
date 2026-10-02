import os
from google.cloud import firestore

def get_db():
    key_path = os.environ.get("FIRESTORE_KEY_PATH", "firestore-key.json")
    db = firestore.Client.from_service_account_json(key_path)
    return db   