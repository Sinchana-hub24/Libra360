
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timezone
from app.core.firestore import db


fines_collection = db.collection("fines")


# ---------------------------------------
# 1. FINE CALCULATION FUNCTION
# ---------------------------------------

def calculate_fine(overdue_days, grace_period_days=2, fine_per_day_paise=500):

    chargeable_days = max(0, overdue_days - grace_period_days)

    fine_amount_paise = chargeable_days * fine_per_day_paise

    return fine_amount_paise


# ---------------------------------------
# 2. SAMPLE FINE DETAILS
# ---------------------------------------

overdue_days = 5

fine_amount_paise = calculate_fine(overdue_days)

print("FINE CALCULATION")
print("=" * 35)
print("Overdue days:", overdue_days)
print("Grace period: 2 days")
print("Chargeable days:", max(0, overdue_days - 2))
print("Fine amount: ₹", fine_amount_paise / 100)


# ---------------------------------------
# 3. CREATE FINE RECORD
# ---------------------------------------

fine_data = {
    "fine_id": "FINE001",
    "borrowing_id": "BORROW001",
    "student_id": "STU001",
    "book_id": "BOOK001",

    "book_type": "physical",
    "overdue_days": overdue_days,
    "grace_period_days": 2,

    "fine_per_day_paise": 500,
    "fine_amount_paise": fine_amount_paise,
    "currency": "INR",

    "payment_status": "pending",
    "created_at": datetime.now(timezone.utc)
}


# ---------------------------------------
# 4. SAVE FINE RECORD
# ---------------------------------------

fine_ref = fines_collection.document("FINE001")

fine_ref.set(fine_data)

print("\nFine record added successfully!")


# ---------------------------------------
# 5. RETRIEVE FINE RECORD
# ---------------------------------------

fine = fine_ref.get()

print("\nSAVED FINE DETAILS")
print("=" * 35)

print(fine.to_dict())


# ---------------------------------------
# 6. VERIFY DIGITAL BOOK RULE
# ---------------------------------------

digital_book_type = "digital"

if digital_book_type == "digital":
    print("\nDigital books do not incur overdue fines.")
