
from fastapi import APIRouter, HTTPException, status
from google.cloud import firestore

from app.core.firestore import db
from app.models.student import StudentCreate, StudentResponse


router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
def register_student(student: StudentCreate):

    # Check whether this email is already registered
    existing_students = (
        db.collection("students")
        .where("email", "==", student.email)
        .limit(1)
        .stream()
    )

    if any(existing_students):
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists."
        )

    # Generate a unique student document ID
    student_ref = db.collection("students").document()

    student_data = student.model_dump()

    student_data.update({
        "student_id": student_ref.id,
        "status": "active",
        "created_at": firestore.SERVER_TIMESTAMP
    })

    # Save student information in Firestore
    student_ref.set(student_data)

    # Retrieve the saved document
    saved_student = student_ref.get().to_dict()

    return saved_student


@router.get(
    "/{student_id}",
    response_model=StudentResponse
)
def get_student(student_id: str):

    student_ref = db.collection("students").document(student_id)

    student = student_ref.get()

    if not student.exists:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    return student.to_dict()
