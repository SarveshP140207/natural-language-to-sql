from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_current_user
from app.database.app_connection import AppSessionLocal
from app.database.models import QueryHistory, User
from app.schemas.history import QueryHistoryResponse


router = APIRouter(
    prefix="/history",
    tags=["Query History"],
)


@router.get(
    "",
    response_model=list[QueryHistoryResponse],
)
def list_history(
    current_user: User = Depends(get_current_user),
):
    db = AppSessionLocal()

    try:
        history = db.scalars(
            select(QueryHistory)
            .where(QueryHistory.user_id == current_user.user_id)
            .order_by(QueryHistory.created_at.desc())
        ).all()

        return history

    finally:
        db.close()


@router.get(
    "/{history_id}",
    response_model=QueryHistoryResponse,
)
def get_history_item(
    history_id: int,
    current_user: User = Depends(get_current_user),
):
    db = AppSessionLocal()

    try:
        history = db.scalar(
            select(QueryHistory).where(
                (QueryHistory.history_id == history_id)
                & (QueryHistory.user_id == current_user.user_id)
            )
        )

        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query history item not found.",
            )

        return history

    finally:
        db.close()