
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.models.digital_access import DigitalAccessCreate


# Test granting digital access
access = DigitalAccessCreate(
    student_id="STU001",
    book_id="BOOK002",
    granted_by="LIBRARIAN001"
)

print("DIGITAL ACCESS MODEL VALIDATION SUCCESSFUL!")

print("\nValidated access information:")
print(access.model_dump())

print("\nDigital access rules:")
print("No expiry date")
print("No return deadline")
print("No overdue fines")
print("Access controlled by librarian")


# Test invalid access request
try:
    DigitalAccessCreate(
        student_id="",
        book_id="BOOK002",
        granted_by="LIBRARIAN001"
    )

except Exception as error:
    print("\nINVALID DIGITAL ACCESS REJECTED!")
    print(error)
