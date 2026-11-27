
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timezone
from app.core.firestore import db


# Reference to borrowing policies
policies_collection = db.collection("borrowing_policies")


# ---------------------------------------
# 1. GENERAL BOOK POLICY
# ---------------------------------------

general_policy = {
    "policy_id": "POLICY001",
    "policy_name": "General Books",
    "book_category": "General",

    "book_type": "physical",
    "borrowing_days": 14,

    "grace_period_days": 2,
    "fine_per_day_paise": 500,
    "currency": "INR",

    "is_active": True,
    "created_at": datetime.now(timezone.utc)
}


# ---------------------------------------
# 2. REFERENCE BOOK POLICY
# ---------------------------------------

reference_policy = {
    "policy_id": "POLICY002",
    "policy_name": "Reference Books",
    "book_category": "Reference",

    "book_type": "physical",
    "borrowing_days": 7,

    "grace_period_days": 2,
    "fine_per_day_paise": 500,
    "currency": "INR",

    "is_active": True,
    "created_at": datetime.now(timezone.utc)
}


# ---------------------------------------
# 3. SAVE POLICIES
# ---------------------------------------

policies_collection.document("POLICY001").set(general_policy)

policies_collection.document("POLICY002").set(reference_policy)

print("Borrowing policies added successfully!")


# ---------------------------------------
# 4. RETRIEVE POLICIES
# ---------------------------------------

print("\nLIBRARY360 BORROWING POLICIES")
print("=" * 45)

policies = policies_collection.stream()

for policy in policies:
    data = policy.to_dict()

    print("\nPolicy ID:", policy.id)
    print("Policy name:", data["policy_name"])
    print("Book category:", data["book_category"])
    print("Borrowing duration:", data["borrowing_days"], "days")
    print("Grace period:", data["grace_period_days"], "days")
    print(
        "Fine per day: ₹",
        data["fine_per_day_paise"] / 100
    )
    print("Active:", data["is_active"])
    print("-" * 45)
