import json
from time import perf_counter

from sqlalchemy import select

from app.database.app_connection import AppSessionLocal
from app.database.models import QueryHistory


def build_result_summary(result: dict) -> str:
    summary = {
        "row_count": result.get("row_count", 0),
        "columns": result.get("columns", []),
        "rows": result.get("rows", []),
    }

    return json.dumps(
        summary,
        default=str,
    )


def save_query_history(
    user_id: int,
    connection_id: int,
    question: str,
    sql_query: str,
    result: dict,
    execution_time_ms: int,
):
    db = AppSessionLocal()

    try:
        history = QueryHistory(
            user_id=user_id,
            connection_id=connection_id,
            question=question,
            sql_query=sql_query,
            result_summary=build_result_summary(result),
            execution_time_ms=execution_time_ms,
        )

        db.add(history)
        db.commit()
        db.refresh(history)

        return history

    finally:
        db.close()


def get_user_query_history(
    user_id: int,
    connection_id: int | None = None,
):
    db = AppSessionLocal()

    try:
        statement = (
            select(QueryHistory)
            .where(QueryHistory.user_id == user_id)
            .order_by(QueryHistory.created_at.desc())
        )

        if connection_id is not None:
            statement = statement.where(
                QueryHistory.connection_id == connection_id
            )

        return db.scalars(statement).all()

    finally:
        db.close()