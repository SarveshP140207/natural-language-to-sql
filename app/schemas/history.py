from datetime import datetime

from pydantic import BaseModel


class QueryHistoryResponse(BaseModel):
    history_id: int
    connection_id: int
    question: str
    sql_query: str
    result_summary: str | None
    execution_time_ms: int | None
    created_at: datetime