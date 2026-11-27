
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class DigitalAccessCreate(BaseModel):

    student_id: str = Field(min_length=1)

    book_id: str = Field(min_length=1)

    granted_by: str = Field(min_length=1)


class DigitalAccessResponse(BaseModel):

    access_id: str

    student_id: str

    book_id: str

    access_status: Literal["active", "revoked"]

    granted_at: datetime

    granted_by: str

    revoked_at: Optional[datetime] = None
