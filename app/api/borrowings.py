
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status

from app.core.firestore import db
from app.models.borrowing import BorrowingCreate, BorrowingResponse


router = APIRouter(
    prefix="/borrowings",
    tags=["Borrowings"]
)



@router.post(
    "/",
    response_model=BorrowingResponse,
    status_code=status.HTTP_201_CREATED
)
def issue_book(borrowing: BorrowingCreate):

    student_ref = db.collection("students").document(borrowing.student_id)
    student = student_ref.get()

    if not student.exists:
        raise HTTPException(status_code=404, detail="Student not found.")

    student_data = student.to_dict()

    if student_data.get("status") != "active":
        raise HTTPException(status_code=400, detail="Student account is inactive.")

    book_ref = db.collection("books").document(borrowing.book_id)
    book = book_ref.get()

    if not book.exists:
        raise HTTPException(status_code=404, detail="Book not found.")

    book_data = book.to_dict()

    if book_data.get("status") != "active":
        raise HTTPException(status_code=400, detail="Book is inactive.")

    if book_data.get("book_type") != "physical":
        raise HTTPException(
            status_code=400,
            detail="Digital books do not require physical borrowing."
        )

    available_copies = book_data.get("available_copies", 0)

    if available_copies <= 0:
        raise HTTPException(
            status_code=400,
            detail="No copies of this book are currently available."
        )

    # Find the active policy matching the book category
    category = book_data.get("category")

    all_policies = db.collection("borrowing_policies").stream()

    policy_records = [
        record for record in all_policies
        if record.to_dict().get("book_category") == category
        and (
            record.to_dict().get("status") == "active"
            or (
                "status" not in record.to_dict()
                and record.to_dict().get("is_active") is True
            )
        )
    ]

    if not policy_records:
        raise HTTPException(
            status_code=400,
            detail=f"No active borrowing policy found for category: {category}"
        )

    if len(policy_records) > 1:
        raise HTTPException(
            status_code=409,
            detail="Multiple active borrowing policies found for this category."
        )

    policy = policy_records[0].to_dict()
    policy_id = policy_records[0].id

    borrowing_days = policy["borrowing_days"]
    grace_period_days = policy["grace_period_days"]
    fine_per_day_paise = policy["fine_per_day_paise"]

    issue_date = datetime.now(timezone.utc)
    due_date = issue_date + timedelta(days=borrowing_days)

    borrowing_ref = db.collection("borrowings").document()

    borrowing_data = {
        "borrowing_id": borrowing_ref.id,
        "student_id": borrowing.student_id,
        "book_id": borrowing.book_id,
        "issue_date": issue_date,
        "due_date": due_date,
        "return_date": None,
        "borrowing_days": borrowing_days,
        "grace_period_days": grace_period_days,
        "fine_per_day_paise": fine_per_day_paise,
        "policy_id": policy_id,
        "policy_name": policy.get("policy_name"),
        "status": "active",
        "fine_amount_paise": 0,
        "currency": "INR"
    }

    borrowing_ref.set(borrowing_data)

    book_ref.update({
        "available_copies": available_copies - 1
    })

    return borrowing_data


@router.post("/{borrowing_id}/return")
def return_book(borrowing_id: str):

    # Find the borrowing record
    borrowing_ref = db.collection("borrowings").document(
        borrowing_id
    )
    borrowing = borrowing_ref.get()

    if not borrowing.exists:
        raise HTTPException(
            status_code=404,
            detail="Borrowing record not found."
        )

    borrowing_data = borrowing.to_dict()

    # Prevent returning an already returned book
    if borrowing_data.get("status") == "returned":
        raise HTTPException(
            status_code=400,
            detail="This book has already been returned."
        )

    # Find the physical book
    book_ref = db.collection("books").document(
        borrowing_data["book_id"]
    )
    book = book_ref.get()

    if not book.exists:
        raise HTTPException(
            status_code=404,
            detail="Book not found."
        )

    book_data = book.to_dict()

    if book_data.get("book_type") != "physical":
        raise HTTPException(
            status_code=400,
            detail="Only physical books can be returned."
        )

    # Record return date
    return_date = datetime.now(timezone.utc)

    # Calculate overdue days
    due_date = borrowing_data["due_date"]

    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)

    overdue_days = max(
        0,
        (return_date.date() - due_date.date()).days
    )

    grace_period_days = borrowing_data.get("grace_period_days", 2)
    fine_per_day_paise = borrowing_data.get("fine_per_day_paise", 500)

    chargeable_days = max(
        0,
        overdue_days - grace_period_days
    )

    # Calculate fine
    fine_amount_paise = (
        chargeable_days * fine_per_day_paise
    )

    # Update borrowing record
    borrowing_ref.update({
        "return_date": return_date,
        "status": "returned",
        "fine_amount_paise": fine_amount_paise
    })

    # Create a separate fine record if a fine is applicable
    if fine_amount_paise > 0:

        fine_ref = db.collection("fines").document(
            borrowing_id
        )

        fine_ref.set({
            "borrowing_id": borrowing_id,
            "student_id": borrowing_data["student_id"],
            "book_id": borrowing_data["book_id"],
            "overdue_days": overdue_days,
            "grace_period_days": grace_period_days,
            "fine_per_day_paise": fine_per_day_paise,
            "fine_amount_paise": fine_amount_paise,
            "currency": "INR",
            "payment_status": "pending",
            "created_at": return_date
        })

    # Restore one available copy
    updated_available_copies = (
        book_data.get("available_copies", 0) + 1
    )

    book_ref.update({
        "available_copies": updated_available_copies
    })

    # Return response
    return {
        "message": "Book returned successfully.",
        "borrowing_id": borrowing_id,
        "return_date": return_date,
        "status": "returned",
        "overdue_days": overdue_days,
        "fine_amount_paise": fine_amount_paise,
        "fine_amount_rupees": fine_amount_paise / 100,
        "available_copies": updated_available_copies
    }


@router.get("/student/{student_id}")
def get_student_borrowings(student_id: str):
    student = db.collection("students").document(student_id).get()

    if not student.exists:
        raise HTTPException(status_code=404, detail="Student not found.")

    records = db.collection("borrowings").where(
        "student_id", "==", student_id
    ).stream()

    result = []

    for record in records:
        data = record.to_dict()
        data["borrowing_id"] = record.id

        book = db.collection("books").document(data["book_id"]).get()
        data["title"] = (
            book.to_dict().get("title", "Unknown book")
            if book.exists else "Book unavailable"
        )

        result.append(data)

    result.sort(
        key=lambda x: x.get("issue_date") or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )

    return {
        "student_id": student_id,
        "total": len(result),
        "borrowings": result
    }


def resolve_student_id(student_id: str) -> str:
    student_ref = db.collection("students").document(student_id)
    student = student_ref.get()

    if student.exists:
        return student.to_dict().get("student_id") or student.id

    student_snapshot = next(
        iter(
            db.collection("students")
            .where("usn", "==", student_id.strip().upper())
            .limit(1)
            .stream()
        ),
        None
    )

    if student_snapshot is None:
        raise HTTPException(status_code=404, detail="Student not found.")

    return student_snapshot.to_dict().get("student_id") or student_snapshot.id


@router.get("/fines/student/{student_id}")
def get_student_fines(student_id: str):

    student_id = resolve_student_id(student_id)
    student = db.collection("students").document(student_id).get()

    if not student.exists:
        raise HTTPException(status_code=404, detail="Student not found.")

    records = db.collection("fines").where(
        "student_id", "==", student_id
    ).stream()

    result = []

    for record in records:
        data = record.to_dict()
        data["fine_id"] = record.id
        result.append(data)

    pending = sum(
        item.get("fine_amount_paise", 0)
        for item in result
        if item.get("payment_status") == "pending"
    )

    paid = sum(
        item.get("fine_amount_paise", 0)
        for item in result
        if item.get("payment_status") == "paid"
    )

    waived = sum(item.get("fine_amount_paise", 0) for item in result if item.get("payment_status") == "waived")

    return {
        "student_id": student_id,
        "usn": student.to_dict().get("usn"),
        "full_name": student.to_dict().get("full_name"),
        "email": student.to_dict().get("email"),
        "department": student.to_dict().get("department"),
        "total_fines": len(result),
        "pending_fines_paise": pending,
        "pending_fines_rupees": pending / 100,
        "paid_fines_paise": paid,
        "paid_fines_rupees": paid / 100,
        "fines": result,
        "waived_fines_paise": waived,
        "waived_fines_rupees": waived / 100,
    }

