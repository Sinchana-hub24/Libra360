
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.models.borrowing_policy import BorrowingPolicyCreate


# Test a valid general book policy
policy = BorrowingPolicyCreate(
    policy_name="General Books",
    book_category="Computer Science",
    borrowing_days=14,
    grace_period_days=2,
    fine_per_day_paise=500
)

print("BORROWING POLICY VALIDATION SUCCESSFUL!")
print("\nValidated policy:")
print(policy.model_dump())


# Test invalid borrowing duration
try:
    BorrowingPolicyCreate(
        policy_name="Reference Books",
        book_category="Reference",
        borrowing_days=0,
        grace_period_days=2,
        fine_per_day_paise=500
    )

except Exception as error:
    print("\nINVALID POLICY REJECTED!")
    print(error)
