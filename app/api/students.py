
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

    email = student.email.strip().lower()
    usn = student.usn.strip().upper()

    existing_students = (
        db.collection("students")
        .where("email", "==", email)
        .limit(1)
        .stream()
    )

    if any(existing_students):
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists."
        )

    existing_usn = (
        db.collection("students")
        .where("usn", "==", usn)
        .limit(1)
        .stream()
    )

    if any(existing_usn):
        raise HTTPException(
            status_code=409,
            detail="A student with this USN already exists."
        )

    student_ref = db.collection("students").document()

    student_data = student.model_dump()

    student_data.update({
        "student_id": student_ref.id,
        "usn": usn,
        "email": email,
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
    "/usn/{usn}",
    response_model=StudentResponse
)
def get_student_by_usn(usn: str):

    normalized_usn = usn.strip().upper()

    students = (
        db.collection("students")
        .where("usn", "==", normalized_usn)
        .limit(1)
        .stream()
    )

    student = next(iter(students), None)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    return student.to_dict()


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
