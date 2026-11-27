
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


# Data received when registering a student
class StudentCreate(BaseModel):

    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: str = Field(
        min_length=5,
        max_length=150
    )

    department: str = Field(
        min_length=2,
        max_length=100
    )

    year: int = Field(
        ge=1,
        le=10
    )


# Complete student information
class StudentResponse(BaseModel):

    student_id: str

    full_name: str

    email: str

    department: str

    year: int

    status: Literal["active", "inactive"]

    created_at: datetime
