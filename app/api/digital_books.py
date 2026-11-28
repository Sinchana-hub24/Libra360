import io
import os
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from google.cloud import storage
from google.auth.credentials import AnonymousCredentials

from app.core.firestore import db
from app.core.config import settings


os.environ.setdefault(
    "STORAGE_EMULATOR_HOST",
    settings.STORAGE_EMULATOR_HOST
)

storage_client = storage.Client(
    project=settings.GOOGLE_CLOUD_PROJECT,
    credentials=AnonymousCredentials()
)

router = APIRouter(
    prefix="/digital-books",
    tags=["Digital Books"]
)

# Storage limits (in bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024       # 50 MB per PDF
MAX_TOTAL_STORAGE = 500 * 1024 * 1024  # 500 MB total across all digital books


@router.post("/upload/{book_id}")
async def upload_digital_book(
    book_id: str,
    file: UploadFile = File(...)
):

    # Verify the book exists
    book_ref = db.collection("books").document(book_id)
    book = book_ref.get()

    if not book.exists:
        raise HTTPException(404, "Book not found.")

    book_data = book.to_dict()

    if book_data.get("book_type") != "digital":
        raise HTTPException(400, "Only digital books can be uploaded.")

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF file.")

    content = await file.read()

    if not content.startswith(b"%PDF-"):
        raise HTTPException(400, "The uploaded file is not a valid PDF.")

    # Per-file size limit
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            413,
            f"File too large. Maximum size per PDF is {MAX_FILE_SIZE // (1024 * 1024)} MB."
        )

    # Total storage limit check
    total_used = 0
    all_books = db.collection("books").where("book_type", "==", "digital").stream()
    for b in all_books:
        b_data = b.to_dict()
        total_used += b_data.get("file_size_bytes", 0) or 0

    if total_used + len(content) > MAX_TOTAL_STORAGE:
        remaining = MAX_TOTAL_STORAGE - total_used
        raise HTTPException(
            413,
            f"Storage limit exceeded. Only {remaining // (1024 * 1024)} MB remaining "
            f"of {MAX_TOTAL_STORAGE // (1024 * 1024)} MB total."
        )

    bucket_name = settings.GCS_BUCKET_NAME

    # Find or create the storage bucket
    bucket = storage_client.lookup_bucket(bucket_name)

    if bucket is None:
        bucket = storage_client.create_bucket(bucket_name)

    safe_filename = Path(file.filename).name
    object_path = f"books/{book_id}/{safe_filename}"

    # Upload PDF to Cloud Storage
    blob = bucket.blob(object_path)

    blob.upload_from_string(
        content,
        content_type="application/pdf"
    )

    # Save file metadata in Firestore
    book_ref.update({
        "storage_path": object_path,
        "file_name": safe_filename,
        "content_type": "application/pdf",
        "file_size_bytes": len(content)
    })

    return {
        "message": "Digital book uploaded successfully.",
        "book_id": book_id,
        "file_name": safe_filename,
        "storage_path": object_path
    }


@router.get("/{book_id}/read")
def read_digital_book(book_id: str, student_id: str):

    # Check the student's access permission
    access_id = f"{student_id}_{book_id}"

    access = db.collection("digital_access").document(
        access_id
    ).get()

    if not access.exists:
        raise HTTPException(403, "You do not have access to this book.")

    if access.to_dict().get("status") != "active":
        raise HTTPException(403, "Your access to this book has been revoked.")

    # Find the book
    book = db.collection("books").document(book_id).get()

    if not book.exists:
        raise HTTPException(404, "Book not found.")

    book_data = book.to_dict()

    if book_data.get("book_type") != "digital":
        raise HTTPException(400, "This is not a digital book.")

    object_path = book_data.get("storage_path")

    if not object_path:
        raise HTTPException(404, "No PDF has been uploaded for this book.")

    # Retrieve the PDF from Cloud Storage
    bucket = storage_client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(object_path)

    if not blob.exists():
        raise HTTPException(404, "PDF file not found in storage.")

    pdf_content = blob.download_as_bytes()

    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline; filename=\"digital-book.pdf\""
        }
    )
