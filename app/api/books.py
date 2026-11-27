from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.core.firestore import db
from app.models.book import BookCreate, BookResponse


router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED
)
def add_book(book: BookCreate):

    # Prevent duplicate ISBN registrations
    existing_books = (
        db.collection("books")
        .where("isbn", "==", book.isbn)
        .limit(1)
        .stream()
    )

    if any(existing_books):
        raise HTTPException(
            status_code=409,
            detail="A book with this ISBN already exists."
        )

    # Generate a unique book ID
    book_ref = db.collection("books").document()

    book_data = book.model_dump()

    # Prepare common book information
    book_data.update({
        "book_id": book_ref.id,
        "status": "active"
    })

    # Physical books start with all copies available
    if book.book_type == "physical":
        book_data["available_copies"] = book.total_copies

    else:
        # Digital books do not have physical copy counts
        book_data["available_copies"] = None

    # Save book information in Firestore
    book_ref.set(book_data)

    # Return saved book information
    return book_ref.get().to_dict()

@router.get(
    "/search",
    response_model=list[BookResponse]
)
def search_books(
    title: Optional[str] = Query(default=None),
    author: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None)
):

    books = db.collection("books").stream()

    results = []

    for book in books:

        book_data = book.to_dict()

        if title and title.lower() not in book_data["title"].lower():
            continue

        if author and author.lower() not in book_data["author"].lower():
            continue

        if category and category.lower() not in book_data["category"].lower():
            continue

        results.append(book_data)

    return results

@router.get(
    "/{book_id}",
    response_model=BookResponse
)
def get_book(book_id: str):

    book_ref = db.collection("books").document(book_id)

    book = book_ref.get()

    if not book.exists:
        raise HTTPException(
            status_code=404,
            detail="Book not found."
        )

    return book.to_dict()

@router.get(
    "/",
    response_model=list[BookResponse]
)
def get_all_books():

    books = db.collection("books").stream()

    return [book.to_dict() for book in books]



