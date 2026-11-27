
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta, timezone
from app.core.firestore import db


borrowings_collection = db.collection("borrowings")

# Use UTC timestamps for consistent date storage
now = datetime.now(timezone.utc)


# ---------------------------------------
# 1. PHYSICAL BOOK BORROWING
# ---------------------------------------

physical_borrowing = {
    "borrowing_id": "BORROW001",
    "student_id": "STU001",
    "book_id": "BOOK001",
    "book_type": "physical",

    "issue_date": now,
    "due_date": now + timedelta(days=14),
    "return_date": None,

    "borrowing_days": 14,
    "status": "active",

    "fine_amount_paise": 0,
    "currency": "INR"
}


# ---------------------------------------
# 2. DIGITAL BOOK BORROWING
# ---------------------------------------

digital_borrowing = {
    "borrowing_id": "BORROW002",
    "student_id": "STU001",
    "book_id": "BOOK002",
    "book_type": "digital",

    "issue_date": now,
    "access_expiry_date": now + timedelta(days=30),

    "borrowing_days": 30,
    "status": "active",

    "return_date": None,
    "fine_amount_paise": 0,
    "currency": "INR"
}


# ---------------------------------------
# 3. SAVE BORROWING RECORDS
# ---------------------------------------

borrowings_collection.document("BORROW001").set(
    physical_borrowing
)

borrowings_collection.document("BORROW002").set(
    digital_borrowing
)

print("Both borrowing records added successfully!")


# ---------------------------------------
# 4. RETRIEVE BORROWING RECORDS
# ---------------------------------------

print("\nLIBRARY360 BORROWING RECORDS")
print("=" * 45)

records = borrowings_collection.stream()

for record in records:
    data = record.to_dict()

    print("\nBorrowing ID:", record.id)
    print("Student:", data["student_id"])
    print("Book:", data["book_id"])
    print("Type:", data["book_type"])
    print("Status:", data["status"])

    if data["book_type"] == "physical":
        print("Due date:", data["due_date"])

    else:
        print("Access expires:", data["access_expiry_date"])

    print("-" * 45)
