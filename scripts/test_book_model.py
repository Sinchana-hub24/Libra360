
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.models.book import BookCreate


# Test a physical book
physical_book = BookCreate(
    title="Introduction to Algorithms",
    author="Thomas H. Cormen",
    isbn="9780262046305",
    category="Computer Science",
    book_type="physical",
    total_copies=10,
    shelf_location="CS-A1"
)

print("PHYSICAL BOOK VALIDATED!")
print(physical_book.model_dump())


# Test a digital book
digital_book = BookCreate(
    title="Python Programming",
    author="John Smith",
    isbn="9781234567890",
    category="Programming",
    book_type="digital",
    storage_bucket="library360-digital-books",
    storage_path="books/BOOK002/python-programming.pdf",
    file_format="PDF",
    file_size_bytes=2500000
)

print("\nDIGITAL BOOK VALIDATED!")
print(digital_book.model_dump())


# Test invalid physical book
try:
    BookCreate(
        title="Database Systems",
        author="John Smith",
        isbn="123456789",
        category="Computer Science",
        book_type="physical"
    )

except Exception as error:
    print("\nINVALID PHYSICAL BOOK REJECTED!")
    print(error)
