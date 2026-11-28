
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.firestore import db


router = APIRouter(
    prefix="/digital-access",
    tags=["Digital Book Access"]
)


class DigitalAccessRequest(BaseModel):
    student_id: str
    book_id: str
    granted_by: str = "LIBRARIAN001"


@router.post("/grant")
def grant_access(request: DigitalAccessRequest):

    student_id = resolve_student_id(request.student_id)
    student = db.collection("students").document(student_id).get()

    if not student.exists:
        raise HTTPException(404, "Student not found.")

    if student.to_dict().get("status") != "active":
        raise HTTPException(400, "Student account is inactive.")

    book_ref = db.collection("books").document(
        request.book_id
    )
    book = book_ref.get()

    if not book.exists:
        raise HTTPException(404, "Book not found.")

    book_data = book.to_dict()

    if book_data.get("book_type") != "digital":
        raise HTTPException(
            400,
            "Access permission is only for digital books."
        )

    if book_data.get("status") != "active":
        raise HTTPException(400, "Book is inactive.")

    access_id = f"{student_id}_{request.book_id}"

    access_ref = db.collection("digital_access").document(
        access_id
    )

    access_ref.set({
        "access_id": access_id,
        "student_id": student_id,
        "book_id": request.book_id,
        "granted_by": request.granted_by,
        "status": "active",
        "granted_at": datetime.now(timezone.utc),
        "expires_at": None
    })

    return {
        "message": "Digital book access granted successfully.",
        "access_id": access_id,
        "student_id": student_id,
        "book_id": request.book_id,
        "status": "active",
        "expires_at": None
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


@router.get("/{student_id}")
def get_student_access(student_id: str):

    student_id = resolve_student_id(student_id)
    student = db.collection("students").document(student_id).get()

    if not student.exists:
        raise HTTPException(404, "Student not found.")

    records = db.collection("digital_access").where(
        "student_id", "==", student_id
    ).where(
        "status", "==", "active"
    ).stream()

    access_list = []

    for record in records:
        data = record.to_dict()

        book = db.collection("books").document(
            data["book_id"]
        ).get()

        if book.exists:
            book_data = book.to_dict()

            access_list.append({
                "access_id": record.id,
                "student_id": student_id,
                "book_id": data["book_id"],
                "title": book_data.get("title"),
                "author": book_data.get("author"),
                "status": data["status"],
                "expires_at": None
            })

    return {
        "student_id": student_id,
        "digital_books": access_list,
        "total": len(access_list)
    }


@router.get("/all")
def get_all_digital_access():

    records = db.collection("digital_access").where(
        "status", "==", "active"
    ).stream()

    access_list = []

    for record in records:
        data = record.to_dict()

        student = db.collection("students").document(
            data["student_id"]
        ).get()

        book = db.collection("books").document(
            data["book_id"]
        ).get()

        access_list.append({
            "access_id": record.id,
            "student_id": data["student_id"],
            "usn": student.to_dict().get("usn") if student.exists else None,
            "student_name": student.to_dict().get("full_name") if student.exists else None,
            "book_id": data["book_id"],
            "book_title": book.to_dict().get("title") if book.exists else None,
            "status": data["status"],
        })

    return {
        "digital_access": access_list,
        "total": len(access_list)
    }


@router.post("/{student_id}/{book_id}/revoke")
def revoke_access(student_id: str, book_id: str):

    student_id = resolve_student_id(student_id)
    access_id = f"{student_id}_{book_id}"

    access_ref = db.collection("digital_access").document(
        access_id
    )

    access = access_ref.get()

    if not access.exists:
        raise HTTPException(404, "Access record not found.")

    if access.to_dict().get("status") != "active":
        raise HTTPException(400, "Access is already revoked.")

    access_ref.update({
        "status": "revoked",
        "revoked_at": datetime.now(timezone.utc)
    })

    return {
        "message": "Digital book access revoked successfully.",
        "student_id": student_id,
        "book_id": book_id,
        "status": "revoked"
    }
