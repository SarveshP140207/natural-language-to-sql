from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.database.models import User
from app.schemas.conversation import (
    ConversationMessageResponse,
    ConversationResponse,
)
from app.services.connection_service import get_user_connection
from app.services.conversation_service import (
    create_conversation,
    delete_user_conversation,
    get_user_conversation,
    get_user_conversation_messages,
    list_user_conversations,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_conversation(
    connection_id: int,
    title: str = "New conversation",
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

    conversation = create_conversation(
        user_id=current_user.user_id,
        connection_id=connection_id,
        title=title,
    )

    return conversation


@router.get(
    "",
    response_model=list[ConversationResponse],
)
def list_conversations(
    current_user: User = Depends(get_current_user),
):
    return list_user_conversations(
        user_id=current_user.user_id,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
):
    conversation = get_user_conversation(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return conversation


@router.get(
    "/{conversation_id}/messages",
    response_model=list[ConversationMessageResponse],
)
def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
):
    try:
        return get_user_conversation_messages(
            user_id=current_user.user_id,
            conversation_id=conversation_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
):
    deleted = delete_user_conversation(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )