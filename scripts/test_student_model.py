
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.models.student import StudentCreate

# Sample student registration
student = StudentCreate(
    full_name="Aarav Sharma",
    email="aarav@example.com",
    department="Computer Science",
    year=2
)

print("STUDENT MODEL VALIDATION SUCCESSFUL!")
print("\nValidated student information:")
print(student.model_dump())


# Test invalid data
try:
    StudentCreate(
        full_name="A",
        email="aarav@example.com",
        department="Computer Science",
        year=2
    )

except Exception as error:
    print("\nInvalid student data rejected successfully!")
    print(error)
