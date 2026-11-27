import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from google.cloud import firestore
from app.core.firestore import db

# Reference to the students collection
students_collection = db.collection("students")

# Sample student document
student_data = {
    "student_id": "STU001",
    "usn": "1RV21CS001",
    "full_name": "Aarav Sharma",
    "email": "aarav@example.com",
    "department": "Computer Science",
    "year": 2,
    "status": "active",
    "created_at": firestore.SERVER_TIMESTAMP
}

# Save the student
student_ref = students_collection.document("STU001")
student_ref.set(student_data)

print("Student added successfully!")

# Retrieve the student
student = student_ref.get()

print("Student details:")
print(student.to_dict())
