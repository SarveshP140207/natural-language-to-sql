import base64
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv


load_dotenv()


ALGORITHM = "sha256"
ITERATIONS = 600_000
SALT_LENGTH = 16

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60
JWT_SECRET = os.getenv("JWT_SECRET")


if not JWT_SECRET:
    raise ValueError("JWT_SECRET is not configured.")


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")

    salt = secrets.token_bytes(SALT_LENGTH)

    password_hash = hashlib.pbkdf2_hmac(
        ALGORITHM,
        password.encode("utf-8"),
        salt,
        ITERATIONS,
    )

    encoded_salt = base64.urlsafe_b64encode(salt).decode("ascii")
    encoded_hash = base64.urlsafe_b64encode(password_hash).decode("ascii")

    return (
        f"pbkdf2_{ALGORITHM}${ITERATIONS}"
        f"${encoded_salt}${encoded_hash}"
    )


def verify_password(password: str, stored_hash: str) -> bool:
    if not password or not stored_hash:
        return False

    try:
        algorithm, iterations, encoded_salt, encoded_hash = (
            stored_hash.split("$")
        )

        if algorithm != f"pbkdf2_{ALGORITHM}":
            return False

        salt = base64.urlsafe_b64decode(
            encoded_salt.encode("ascii")
        )

        expected_hash = base64.urlsafe_b64decode(
            encoded_hash.encode("ascii")
        )

        calculated_hash = hashlib.pbkdf2_hmac(
            ALGORITHM,
            password.encode("utf-8"),
            salt,
            int(iterations),
        )

        return secrets.compare_digest(
            calculated_hash,
            expected_hash,
        )

    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
    )