from urllib.parse import quote_plus

from sqlalchemy import create_engine, text

from app.core.encryption import decrypt_password
from app.database.connection import engine
from app.database.models import DatabaseConnection


def create_connection_engine(
    database_connection: DatabaseConnection,
):
    password = decrypt_password(
        database_connection.password_encrypted
    )

    encoded_password = quote_plus(password)

    database_url = (
        f"mysql+mysqlconnector://"
        f"{database_connection.username}:{encoded_password}"
        f"@{database_connection.host}:{database_connection.port}"
        f"/{database_connection.database_name}"
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 5,
        },
    )


def execute_read_only_query(
    sql: str,
    database_connection: DatabaseConnection | None = None,
):
    if database_connection is None:
        query_engine = engine
        owns_engine = False
    else:
        query_engine = create_connection_engine(
            database_connection
        )
        owns_engine = True

    try:
        with query_engine.connect() as connection:
            result = connection.execute(text(sql))

            columns = list(result.keys())
            rows = [
                dict(row._mapping)
                for row in result
            ]

            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
            }

    finally:
        if owns_engine:
            query_engine.dispose()