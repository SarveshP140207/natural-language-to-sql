from urllib.parse import quote_plus

from sqlalchemy import create_engine, text

from app.core.encryption import decrypt_password


def test_mysql_connection(
    host: str,
    port: int,
    database_name: str,
    username: str,
    encrypted_password: str,
) -> bool:
    password = decrypt_password(encrypted_password)
    encoded_password = quote_plus(password)

    database_url = (
        f"mysql+mysqlconnector://{username}:{encoded_password}"
        f"@{host}:{port}/{database_name}"
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 5,
        },
    )

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True

    finally:
        engine.dispose()