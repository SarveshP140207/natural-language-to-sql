import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv


load_dotenv()


DB_ENCRYPTION_KEY = os.getenv("DB_ENCRYPTION_KEY")


if not DB_ENCRYPTION_KEY:
    raise ValueError("DB_ENCRYPTION_KEY is not configured.")


fernet = Fernet(DB_ENCRYPTION_KEY.encode())


def encrypt_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")

    return fernet.encrypt(
        password.encode("utf-8")
    ).decode("utf-8")


def decrypt_password(encrypted_password: str) -> str:
    if not encrypted_password:
        raise ValueError("Encrypted password cannot be empty.")

    return fernet.decrypt(
        encrypted_password.encode("utf-8")
    ).decode("utf-8")