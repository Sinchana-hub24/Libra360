
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

    student_ref = db.collection("students").document()

    student_data = student.model_dump()

    student_data.update({
        "student_id": student_ref.id,
        "status": "active",
        "created_at": firestore.SERVER_TIMESTAMP
    })

    student_ref.set(student_data)

    saved_student = student_ref.get().to_dict()

    return saved_student


# NEW: Get all students
@router.get(
    "/",
    response_model=list[StudentResponse]
)
def get_all_students():

    students = db.collection("students").stream()

    return [
        student.to_dict()
        for student in students
    ]


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
