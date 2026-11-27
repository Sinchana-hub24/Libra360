import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.firestore import db

borrowing_id = "InFuZrqW2Mvp9GISPvjp"

test_due_date = datetime.now(timezone.utc) - timedelta(days=5)

db.collection("borrowings").document(borrowing_id).update({
    "due_date": test_due_date
})

print("Test due date updated successfully!")
print("Due date:", test_due_date)
print("Simulated overdue days: 5")