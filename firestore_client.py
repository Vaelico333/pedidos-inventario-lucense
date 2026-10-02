import os, json
from google.cloud import firestore

def get_db():
    creds = json.loads(os.environ["FIRESTORE_KEY"])
    return firestore.Client.from_service_account_info(creds)   