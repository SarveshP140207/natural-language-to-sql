from sqlalchemy import select

from app.core.encryption import encrypt_password
from app.database.app_connection import AppSessionLocal
from app.database.models import DatabaseConnection


def create_database_connection(
    user_id: int,
    name: str,
    db_type: str,
    host: str,
    port: int,
    database_name: str,
    username: str,
    password: str,
):
    if db_type.lower() != "mysql":
        raise ValueError("Only MySQL connections are currently supported.")

    db = AppSessionLocal()

    try:
        existing = db.scalar(
            select(DatabaseConnection).where(
                (DatabaseConnection.user_id == user_id)
                & (DatabaseConnection.name == name)
            )
        )

        if existing:
            raise ValueError(
                "A connection with this name already exists."
            )

        encrypted_password = encrypt_password(password)

        connection = DatabaseConnection(
            user_id=user_id,
            name=name,
            db_type=db_type.lower(),
            host=host,
            port=port,
            database_name=database_name,
            username=username,
            password_encrypted=encrypted_password,
        )

        db.add(connection)
        db.commit()
        db.refresh(connection)

        return connection

    finally:
        db.close()


def get_user_connections(user_id: int):
    db = AppSessionLocal()

    try:
        return db.scalars(
            select(DatabaseConnection)
            .where(DatabaseConnection.user_id == user_id)
            .order_by(DatabaseConnection.created_at.desc())
        ).all()

    finally:
        db.close()


def get_user_connection(
    user_id: int,
    connection_id: int,
):
    db = AppSessionLocal()

    try:
        return db.scalar(
            select(DatabaseConnection).where(
                (DatabaseConnection.connection_id == connection_id)
                & (DatabaseConnection.user_id == user_id)
            )
        )

    finally:
        db.close()