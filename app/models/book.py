
from pydantic import BaseModel, Field, model_validator
from typing import Literal, Optional


class BookCreate(BaseModel):

    title: str = Field(min_length=2, max_length=200)
    author: str = Field(min_length=2, max_length=150)
    isbn: str = Field(min_length=5, max_length=20)
    category: str = Field(min_length=2, max_length=100)

    book_type: Literal["physical", "digital"]

    description: str = Field(default="", max_length=1000)

    # Physical book details
    total_copies: Optional[int] = Field(default=None, ge=1)
    shelf_location: Optional[str] = None

    # Digital book details (filled after PDF upload)
    storage_bucket: Optional[str] = None
    storage_path: Optional[str] = None
    file_format: Optional[Literal["PDF"]] = None
    file_size_bytes: Optional[int] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_book_details(self):

        if self.book_type == "physical":

            if self.total_copies is None:
                raise ValueError(
                    "Physical books must have total_copies."
                )

            if not self.shelf_location:
                raise ValueError(
                    "Physical books must have a shelf_location."
                )

        return self


class BookResponse(BaseModel):

    book_id: str
    title: str
    author: str
    isbn: str
    category: str

    book_type: Literal["physical", "digital"]

    description: str = ""

    status: Literal["active", "inactive"]

    total_copies: Optional[int] = None
    available_copies: Optional[int] = None

    shelf_location: Optional[str] = None

    storage_bucket: Optional[str] = None
    storage_path: Optional[str] = None
    file_format: Optional[str] = None
    file_size_bytes: Optional[int] = None
