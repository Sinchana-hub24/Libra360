import os
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt


# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    """Securely hash a password using scrypt."""

    salt = secrets.token_bytes(16)

    password_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        dklen=64
    )

    return (
        f"scrypt${salt.hex()}${password_hash.hex()}"
    )


def verify_password(
    plain_password: str,
    stored_password: str
) -> bool:
    """Verify a password against its stored hash."""

    try:
        algorithm, salt_hex, hash_hex = stored_password.split("$")

        if algorithm != "scrypt":
            return False

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.scrypt(
            plain_password.encode("utf-8"),
            salt=salt,
            n=16384,
            r=8,
            p=1,
            dklen=64
        )

        return hmac.compare_digest(
            actual_hash,
            expected_hash
        )

    except (ValueError, TypeError):
        return False


def create_access_token(data: dict) -> str:
    """Create a signed JWT access token."""

    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY environment variable is not configured."
        )

    payload = data.copy()

    expiration = (
        datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload.update({
        "iat": datetime.now(timezone.utc),
        "exp": expiration
    })

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    """Verify and decode a JWT access token."""

    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY environment variable is not configured."
        )

    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM]
    )
