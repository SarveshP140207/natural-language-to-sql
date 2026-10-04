from sqlalchemy import text

from app.database.connection import engine


try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE(), VERSION()"))
        database, version = result.fetchone()

        print("MySQL connection successful!")
        print(f"Database: {database}")
        print(f"MySQL version: {version}")

except Exception as e:
    print("MySQL connection failed!")
    print(f"Error: {e}")