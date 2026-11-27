
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class BorrowingCreate(BaseModel):
    student_id: str = Field(min_length=1)
    book_id: str = Field(min_length=1)


class BorrowingResponse(BaseModel):
    borrowing_id: str
    student_id: str
    book_id: str
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    borrowing_days: int
    status: Literal["active", "returned", "overdue"]
    fine_amount_paise: int = Field(default=0, ge=0)
    currency: Literal["INR"] = "INR"
