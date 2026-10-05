from app.database.app_connection import app_engine
from app.database.models import Base


def initialize_database():
    Base.metadata.create_all(bind=app_engine)
    print("Application database tables created successfully.")


if __name__ == "__main__":
    initialize_database()