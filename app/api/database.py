from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.database.connection_tester import test_mysql_connection
from app.database.models import User
from app.schemas.database import (
    DatabaseConnectionCreate,
    DatabaseConnectionResponse,
)
from app.services.connection_service import (
    create_database_connection,
    get_user_connection,
    get_user_connections,
)


router = APIRouter(
    prefix="/database",
    tags=["Database Connections"],
)


@router.post(
    "/connections",
    response_model=DatabaseConnectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_database_connection(
    request: DatabaseConnectionCreate,
    current_user: User = Depends(get_current_user),
):
    try:
        connection = create_database_connection(
            user_id=current_user.user_id,
            name=request.name,
            db_type=request.db_type,
            host=request.host,
            port=request.port,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )

        return DatabaseConnectionResponse(
            connection_id=connection.connection_id,
            name=connection.name,
            db_type=connection.db_type,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/connections",
    response_model=list[DatabaseConnectionResponse],
)
def list_database_connections(
    current_user: User = Depends(get_current_user),
):
    connections = get_user_connections(current_user.user_id)

    return [
        DatabaseConnectionResponse(
            connection_id=connection.connection_id,
            name=connection.name,
            db_type=connection.db_type,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
        )
        for connection in connections
    ]


@router.post(
    "/connections/{connection_id}/test",
)
def test_saved_database_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
):
    connection = get_user_connection(
        user_id=current_user.user_id,
        connection_id=connection_id,
    )

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found.",
        )

    try:
        success = test_mysql_connection(
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            encrypted_password=connection.password_encrypted,
        )

        return {
            "connection_id": connection.connection_id,
            "status": "success" if success else "failed",
            "message": "Database connection successful."
            if success
            else "Database connection failed.",
        }

    except Exception as error:
        return {
            "connection_id": connection.connection_id,
            "status": "failed",
            "message": f"Database connection failed: {error}",
        }