
import os
import json
import urllib.request
from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("FIRESTORE_EMULATOR_HOST", "localhost:4588")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "floci-local")

from app.core.firestore import db

BASE_URL = "http://127.0.0.1:8000"
STUDENT_ID = "STU001"
BOOK_ID = "3zuV7rp8LVpz1Kbo8coe"


def api_post(path, data):
    request = urllib.request.Request(
        BASE_URL + path,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


print("\n1. Creating a new physical borrowing...")

borrowing = api_post("/borrowings/", {
    "student_id": STUDENT_ID,
    "book_id": BOOK_ID,
    "borrowing_days": 14
})

borrowing_id = borrowing["borrowing_id"]
print("Borrowing created:", borrowing_id)

print("\n2. Simulating five overdue days...")

test_due_date = datetime.now(timezone.utc) - timedelta(days=5)

db.collection("borrowings").document(borrowing_id).update({
    "due_date": test_due_date
})

print("Test due date:", test_due_date)

print("\n3. Returning the book...")

result = api_post(
    f"/borrowings/{borrowing_id}/return",
    {}
)

print(json.dumps(result, indent=4))

print("\n4. Checking the separate Firestore fine record...")

fine = db.collection("fines").document(borrowing_id).get()

if fine.exists:
    fine_data = fine.to_dict()

    print("\nFINE RECORD FOUND!")
    print(json.dumps({
        "fine_amount_paise": fine_data["fine_amount_paise"],
        "fine_amount_rupees": fine_data["fine_amount_paise"] / 100,
        "payment_status": fine_data["payment_status"],
        "overdue_days": fine_data["overdue_days"]
    }, indent=4))

    if fine_data["fine_amount_paise"] == 1500:
        print("\nSUCCESS: Complete fine workflow passed!")
    else:
        print("\nERROR: Fine amount is incorrect.")
else:
    print("\nERROR: Separate fine record was not created.")
