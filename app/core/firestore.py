
from google.cloud import firestore
from app.core.config import settings

db = firestore.Client(
    project=settings.GOOGLE_CLOUD_PROJECT
)

print("Firestore client initialized successfully!")
