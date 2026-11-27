
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.models.borrowing import BorrowingCreate
from pydantic import ValidationError


# Test valid borrowing request
borrowing = BorrowingCreate(
    student_id="STU001",
    book_id="BOOK001",
    borrowing_days=14
)

print("BORROWING MODEL VALIDATION SUCCESSFUL!")
print("\nValidated borrowing information:")
print(borrowing.model_dump())


# Test invalid borrowing duration
try:
    BorrowingCreate(
        student_id="STU001",
        book_id="BOOK001",
        borrowing_days=0
    )

except ValidationError as error:
    print("\nINVALID BORROWING REJECTED!")
    print(error)


# Test excessive borrowing duration
try:
    BorrowingCreate(
        student_id="STU001",
        book_id="BOOK001",
        borrowing_days=500
    )

except ValidationError as error:
    print("\nEXCESSIVE BORROWING DURATION REJECTED!")
    print(error)
