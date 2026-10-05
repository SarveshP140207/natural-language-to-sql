import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus


load_dotenv()


APP_DB_HOST = os.getenv("APP_DB_HOST", "localhost")
APP_DB_PORT = os.getenv("APP_DB_PORT", "3306")
APP_DB_USER = os.getenv("APP_DB_USER")
APP_DB_PASSWORD = os.getenv("APP_DB_PASSWORD")
APP_DB_NAME = os.getenv("APP_DB_NAME", "nl_sql_app")


if not APP_DB_USER:
    raise ValueError("APP_DB_USER is not configured.")

if not APP_DB_PASSWORD:
    raise ValueError("APP_DB_PASSWORD is not configured.")


encoded_password = quote_plus(APP_DB_PASSWORD)


APP_DATABASE_URL = (
    f"mysql+mysqlconnector://{APP_DB_USER}:{encoded_password}"
    f"@{APP_DB_HOST}:{APP_DB_PORT}/{APP_DB_NAME}"
)


app_engine = create_engine(
    APP_DATABASE_URL,
    pool_pre_ping=True,
)


AppSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=app_engine,
)


def get_app_db():
    db = AppSessionLocal()

    try:
        yield db
    finally:
        db.close()