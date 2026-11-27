from typing import Optional

from pydantic import BaseModel, Field, model_validator


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=8, max_length=128)


class StudentAccountCreate(BaseModel):
    usn: Optional[str] = Field(default=None, min_length=1, max_length=30)
    student_id: Optional[str] = Field(default=None, min_length=1)
    password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def require_student_identifier(self):
        if not self.usn and not self.student_id:
            raise ValueError("Either usn or student_id is required.")
        return self


class LibrarianSetup(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=12, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
