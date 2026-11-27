from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=8, max_length=128)


class StudentAccountCreate(BaseModel):
    student_id: str = Field(min_length=1)
    password: str = Field(min_length=8, max_length=128)


class LibrarianSetup(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=12, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
