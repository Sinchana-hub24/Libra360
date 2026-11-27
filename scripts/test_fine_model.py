
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.models.fine import FineCreate


# Test a valid fine
fine = FineCreate(
    borrowing_id="BORROW001",
    student_id="STU001",
    book_id="BOOK001",
    overdue_days=5,
    grace_period_days=2,
    fine_per_day_paise=500
)

print("FINE MODEL VALIDATION SUCCESSFUL!")
print("\nValidated fine information:")
print(fine.model_dump())


# Calculate the fine
chargeable_days = max(
    0,
    fine.overdue_days - fine.grace_period_days
)

fine_amount = chargeable_days * fine.fine_per_day_paise

print("\nFINE CALCULATION:")
print("Overdue days:", fine.overdue_days)
print("Grace period:", fine.grace_period_days)
print("Chargeable days:", chargeable_days)
print("Fine amount in paise:", fine_amount)
print("Fine amount in rupees:", fine_amount / 100)


# Test invalid fine
try:
    FineCreate(
        borrowing_id="BORROW001",
        student_id="STU001",
        book_id="BOOK001",
        overdue_days=-2,
        grace_period_days=2,
        fine_per_day_paise=500
    )

except Exception as error:
    print("\nINVALID FINE REJECTED!")
    print(error)
