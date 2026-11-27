
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class FineCreate(BaseModel):

    borrowing_id: str = Field(min_length=1)

    student_id: str = Field(min_length=1)

    book_id: str = Field(min_length=1)

    overdue_days: int = Field(ge=0)

    grace_period_days: int = Field(ge=0)

    fine_per_day_paise: int = Field(ge=0)

    currency: Literal["INR"] = "INR"


class FineResponse(BaseModel):

    fine_id: str

    borrowing_id: str

    student_id: str

    book_id: str

    overdue_days: int

    grace_period_days: int

    fine_per_day_paise: int

    fine_amount_paise: int = Field(ge=0)

    currency: Literal["INR"]

    payment_status: Literal["pending", "paid", "waived"]

    created_at: datetime
