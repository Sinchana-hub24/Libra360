from datetime import datetime, timezone
from app.core.firestore import db

borrowing_id = "ZbZ7GJ8ghrU48rPY6Vzc"

new_due_date = datetime(
    2026, 11, 22, 11, 33, 11,
    tzinfo=timezone.utc
)

ref = db.collection("borrowings").document(borrowing_id)

if not ref.get().exists:
    print("Borrowing record not found!")
else:
    ref.update({"due_date": new_due_date})
    print("Test due date updated successfully!")
    print("Due date:", new_due_date)