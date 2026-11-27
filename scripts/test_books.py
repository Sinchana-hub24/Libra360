
import sys
from pathlib import Path

# Add the main project folder to Python's import path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.firestore import db

# Reference to the books collection
books_collection = db.collection("books")


# ---------------------------------
# 1. PHYSICAL BOOK
# ---------------------------------

physical_book = {
    "book_id": "BOOK001",
    "title": "Introduction to Algorithms",
    "author": "Thomas H. Cormen",
    "isbn": "9780262046305",
    "category": "Computer Science",
    "book_type": "physical",
    "description": "A textbook about computer algorithms.",
    "status": "active",

    "total_copies": 10,
    "available_copies": 10,
    "shelf_location": "CS-A1"
}


# ---------------------------------
# 2. DIGITAL BOOK
# ---------------------------------

digital_book = {
    "book_id": "BOOK002",
    "title": "Python Programming",
    "author": "John Smith",
    "isbn": "9781234567890",
    "category": "Programming",
    "book_type": "digital",
    "description": "An introductory guide to Python.",
    "status": "active",

    "storage_bucket": "library360-digital-books",
    "storage_path": "books/BOOK002/python-programming.pdf",
    "file_format": "PDF",
    "file_size_bytes": 2500000
}


# ---------------------------------
# 3. SAVE BOTH BOOKS
# ---------------------------------

books_collection.document("BOOK001").set(physical_book)

books_collection.document("BOOK002").set(digital_book)

print("Both books added successfully!")


# ---------------------------------
# 4. RETRIEVE AND DISPLAY BOOKS
# ---------------------------------

print("\nLIBRARY360 BOOK CATALOG")
print("=" * 40)

books = books_collection.stream()

for book in books:
    print("\nBook ID:", book.id)
    print("Details:", book.to_dict())
    print("-" * 40)
