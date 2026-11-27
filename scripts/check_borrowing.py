import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.firestore import db

borrowing_id = "Fzo5ndx2HREf93OgSmJ2"

doc = db.collection("borrowings").document(borrowing_id).get()

if doc.exists:
    data = doc.to_dict()

    print("\nBORROWING RECORD:")
    for key, value in data.items():
        print(f"{key}: {value}")
else:
    print("Borrowing record not found.")