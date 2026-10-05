from datetime import datetime

from pydantic import BaseModel


class ConversationResponse(BaseModel):
    conversation_id: int
    connection_id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationMessageResponse(BaseModel):
    message_id: int
    role: str
    content: str
    sql_query: str | None
    created_at: datetime