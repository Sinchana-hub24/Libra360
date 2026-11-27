
import os
import hmac

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.cloud import firestore

from app.core.firestore import db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from app.models.auth import (
    LoginRequest,
    StudentAccountCreate,
    LibrarianSetup,
    TokenResponse
)


router = APIRouter(prefix="/auth", tags=["Authentication"])

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    try:
        payload = decode_access_token(credentials.credentials)

        account_id = payload.get("sub")
        role = payload.get("role")

        if not account_id or role not in ["student", "librarian"]:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token."
            )

        account_ref = db.collection("user_accounts").document(account_id)
        account = account_ref.get()

        if not account.exists:
            raise HTTPException(
                status_code=401,
                detail="Account not found."
            )

        account_data = account.to_dict()

        if account_data.get("status") != "active":
            raise HTTPException(
                status_code=403,
                detail="Account is inactive."
            )

        return account_data

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )


def require_librarian(
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "librarian":
        raise HTTPException(
            status_code=403,
            detail="Librarian permission required."
        )

    return current_user


@router.post("/setup-librarian", status_code=201)
def setup_librarian(
    librarian: LibrarianSetup,
    x_setup_secret: str = Header()
):
    setup_secret = os.getenv("LIBRARY360_SETUP_SECRET")

    if not setup_secret or not hmac.compare_digest(
        x_setup_secret,
        setup_secret
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid librarian setup secret."
        )

    existing_librarians = (
        db.collection("user_accounts")
        .where("role", "==", "librarian")
        .limit(1)
        .stream()
    )

    if any(existing_librarians):
        raise HTTPException(
            status_code=409,
            detail="Initial librarian has already been created."
        )

    existing_email = (
        db.collection("user_accounts")
        .where("email", "==", librarian.email.lower())
        .limit(1)
        .stream()
    )

    if any(existing_email):
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    account_ref = db.collection("user_accounts").document()

    account_ref.set({
        "account_id": account_ref.id,
        "full_name": librarian.full_name,
        "email": librarian.email.lower(),
        "password_hash": hash_password(librarian.password),
        "role": "librarian",
        "student_id": None,
        "status": "active",
        "created_at": firestore.SERVER_TIMESTAMP
    })

    return {
        "message": "Initial librarian account created successfully.",
        "account_id": account_ref.id,
        "email": librarian.email.lower(),
        "role": "librarian"
    }


@router.post("/librarian/login", response_model=TokenResponse)
def librarian_login(login: LoginRequest):
    email = login.identifier.lower()

    accounts = (
        db.collection("user_accounts")
        .where("email", "==", email)
        .where("role", "==", "librarian")
        .limit(1)
        .stream()
    )

    account = next(iter(accounts), None)

    if account is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    account_data = account.to_dict()

    if account_data.get("status") != "active" or not verify_password(
        login.password,
        account_data.get("password_hash", "")
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    token = create_access_token({
        "sub": account.id,
        "role": "librarian"
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "librarian"
    }


@router.post("/student/login", response_model=TokenResponse)
def student_login(login: LoginRequest):
    identifier = login.identifier.strip()

    if "@" in identifier:
        accounts = (
            db.collection("user_accounts")
            .where("email", "==", identifier.lower())
            .where("role", "==", "student")
            .limit(1)
            .stream()
        )
    else:
        accounts = (
            db.collection("user_accounts")
            .where("student_id", "==", identifier)
            .where("role", "==", "student")
            .limit(1)
            .stream()
        )

    account = next(iter(accounts), None)

    if account is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid student ID/email or password."
        )

    account_data = account.to_dict()

    if account_data.get("status") != "active" or not verify_password(
        login.password,
        account_data.get("password_hash", "")
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid student ID/email or password."
        )

    token = create_access_token({
        "sub": account.id,
        "role": "student",
        "student_id": account_data.get("student_id")
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "student"
    }


@router.post("/students", status_code=201)
def create_student_account(
    account: StudentAccountCreate,
    librarian: dict = Depends(require_librarian)
):
    student_ref = db.collection("students").document(account.student_id)
    student = student_ref.get()

    if not student.exists:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found."
        )

    student_data = student.to_dict()

    if student_data.get("status") != "active":
        raise HTTPException(
            status_code=400,
            detail="Cannot create an account for an inactive student."
        )

    email = student_data.get("email", "").lower()

    existing_email = (
        db.collection("user_accounts")
        .where("email", "==", email)
        .limit(1)
        .stream()
    )

    if any(existing_email):
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    existing_student_account = (
        db.collection("user_accounts")
        .where("student_id", "==", account.student_id)
        .limit(1)
        .stream()
    )

    if any(existing_student_account):
        raise HTTPException(
            status_code=409,
            detail="This student already has a login account."
        )

    account_ref = db.collection("user_accounts").document()

    account_ref.set({
        "account_id": account_ref.id,
        "full_name": student_data.get("full_name"),
        "email": email,
        "password_hash": hash_password(account.password),
        "role": "student",
        "student_id": account.student_id,
        "status": "active",
        "created_at": firestore.SERVER_TIMESTAMP
    })

    return {
        "message": "Student login account created successfully.",
        "account_id": account_ref.id,
        "student_id": account.student_id,
        "email": email,
        "role": "student"
    }


@router.get("/me")
def get_my_account(
    current_user: dict = Depends(get_current_user)
):
    return {
        "account_id": current_user.get("account_id"),
        "full_name": current_user.get("full_name"),
        "email": current_user.get("email"),
        "role": current_user.get("role"),
        "student_id": current_user.get("student_id")
    }
