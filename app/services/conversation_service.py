import json
from datetime import UTC, datetime

from sqlalchemy import delete, select

from app.database.app_connection import AppSessionLocal
from app.database.models import Conversation, ConversationMessage


MAX_RESULT_ROWS = 20


def create_conversation(
    user_id: int,
    connection_id: int,
    title: str,
):
    db = AppSessionLocal()

    try:
        conversation = Conversation(
            user_id=user_id,
            connection_id=connection_id,
            title=title[:255],
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    finally:
        db.close()


def get_user_conversation(
    user_id: int,
    conversation_id: int,
):
    db = AppSessionLocal()

    try:
        return db.scalar(
            select(Conversation).where(
                (Conversation.conversation_id == conversation_id)
                & (Conversation.user_id == user_id)
            )
        )

    finally:
        db.close()


def list_user_conversations(
    user_id: int,
):
    db = AppSessionLocal()

    try:
        return db.scalars(
            select(Conversation)
            .where(
                Conversation.user_id == user_id
            )
            .order_by(
                Conversation.updated_at.desc()
            )
        ).all()

    finally:
        db.close()


def get_user_conversation_messages(
    user_id: int,
    conversation_id: int,
):
    conversation = get_user_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise ValueError("Conversation not found.")

    db = AppSessionLocal()

    try:
        return db.scalars(
            select(ConversationMessage)
            .where(
                ConversationMessage.conversation_id
                == conversation_id
            )
            .order_by(
                ConversationMessage.message_id.asc()
            )
        ).all()

    finally:
        db.close()


def delete_user_conversation(
    user_id: int,
    conversation_id: int,
) -> bool:
    conversation = get_user_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not conversation:
        return False

    db = AppSessionLocal()

    try:
        db.delete(conversation)
        db.commit()

        return True

    finally:
        db.close()


def add_conversation_message(
    conversation_id: int,
    role: str,
    content: str,
    sql_query: str | None = None,
):
    db = AppSessionLocal()

    try:
        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sql_query=sql_query,
        )

        db.add(message)

        conversation = db.scalar(
            select(Conversation).where(
                Conversation.conversation_id == conversation_id
            )
        )

        if conversation:
            conversation.updated_at = datetime.now(UTC)

        db.commit()
        db.refresh(message)

        return message

    finally:
        db.close()


def add_query_exchange(
    conversation_id: int,
    question: str,
    sql: str,
    result: dict,
):
    result_snapshot = {
        "columns": result.get("columns", []),
        "rows": result.get("rows", [])[:MAX_RESULT_ROWS],
        "row_count": result.get("row_count", 0),
    }

    add_conversation_message(
        conversation_id=conversation_id,
        role="user",
        content=question,
    )

    add_conversation_message(
        conversation_id=conversation_id,
        role="assistant",
        content=json.dumps(
            result_snapshot,
            default=str,
        ),
        sql_query=sql,
    )


def build_conversation_context(
    user_id: int,
    conversation_id: int,
    limit: int = 5,
) -> str:
    conversation = get_user_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise ValueError("Conversation not found.")

    db = AppSessionLocal()

    try:
        messages = list(
            db.scalars(
                select(ConversationMessage)
                .where(
                    ConversationMessage.conversation_id
                    == conversation_id
                )
                .order_by(
                    ConversationMessage.message_id.desc()
                )
                .limit(limit * 2)
            ).all()
        )

        messages.reverse()

    finally:
        db.close()

    if not messages:
        return ""

    context_parts = []
    pending_question = None
    exchange_number = 0

    for message in messages:
        if message.role == "user":
            pending_question = message.content

        elif message.role == "assistant" and pending_question:
            exchange_number += 1

            try:
                result = json.loads(message.content)
            except (json.JSONDecodeError, TypeError):
                result = {}

            context_parts.append(
                f"""Conversation {exchange_number}:
Question: {pending_question}
SQL: {message.sql_query or ""}
Result row count: {result.get("row_count", 0)}
Result columns: {result.get("columns", [])}
Result rows:
{result.get("rows", [])}
"""
            )

            pending_question = None

    return "\n".join(context_parts)