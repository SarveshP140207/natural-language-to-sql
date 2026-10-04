from fastapi import APIRouter

from app.database.introspector import get_database_schema


router = APIRouter()


@router.get("/schema")
def get_schema():
    return get_database_schema()