import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database.app_connection import AppSessionLocal
from app.database.models import Conversation, ConversationMessage, User
from app.main import app
from app.services.conversation_service import add_conversation_message


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user(client):
    login_response = client.post(
        "/auth/login",
        json={
            "username": "auth_test_001",
            "password": "TestPassword123!",
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    return {
        "token": data["access_token"],
        "user_id": data["user"]["user_id"],
    }


def cleanup_conversation(conversation_id):
    db = AppSessionLocal()

    try:
        db.execute(
            delete(ConversationMessage).where(
                ConversationMessage.conversation_id
                == conversation_id
            )
        )

        db.execute(
            delete(Conversation).where(
                Conversation.conversation_id
                == conversation_id
            )
        )

        db.commit()

    finally:
        db.close()


def test_create_conversation(
    client,
    test_user,
):
    title = f"Pytest create {uuid.uuid4().hex[:8]}"

    response = client.post(
        "/conversations",
        params={
            "connection_id": 1,
            "title": title,
        },
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["connection_id"] == 1
    assert data["title"] == title

    cleanup_conversation(
        data["conversation_id"]
    )


def test_conversation_messages_are_persisted(
    client,
    test_user,
):
    title = f"Pytest messages {uuid.uuid4().hex[:8]}"

    response = client.post(
        "/conversations",
        params={
            "connection_id": 1,
            "title": title,
        },
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 201

    conversation_id = response.json()["conversation_id"]

    add_conversation_message(
        conversation_id=conversation_id,
        role="user",
        content="Which category has the most products?",
    )

    add_conversation_message(
        conversation_id=conversation_id,
        role="assistant",
        content=(
            '{"columns":["category_name","product_count"],'
            '"rows":[{"category_name":"Automotive",'
            '"product_count":5}],"row_count":1}'
        ),
        sql_query=(
            "SELECT category_name, COUNT(*) "
            "FROM products "
            "GROUP BY category_name "
            "ORDER BY COUNT(*) DESC LIMIT 1"
        ),
    )

    response = client.get(
        f"/conversations/{conversation_id}/messages",
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 200

    messages = response.json()

    assert len(messages) == 2

    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == (
        "Which category has the most products?"
    )

    assert messages[1]["role"] == "assistant"
    assert messages[1]["sql_query"] is not None

    cleanup_conversation(
        conversation_id
    )


def test_get_single_conversation(
    client,
    test_user,
):
    title = f"Pytest single {uuid.uuid4().hex[:8]}"

    response = client.post(
        "/conversations",
        params={
            "connection_id": 1,
            "title": title,
        },
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 201

    conversation_id = response.json()["conversation_id"]

    response = client.get(
        f"/conversations/{conversation_id}",
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["conversation_id"] == conversation_id
    assert data["connection_id"] == 1
    assert data["title"] == title

    cleanup_conversation(
        conversation_id
    )


def test_list_conversations(
    client,
    test_user,
):
    title_a = f"Pytest list A {uuid.uuid4().hex[:8]}"
    title_b = f"Pytest list B {uuid.uuid4().hex[:8]}"

    first = client.post(
        "/conversations",
        params={
            "connection_id": 1,
            "title": title_a,
        },
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    second = client.post(
        "/conversations",
        params={
            "connection_id": 1,
            "title": title_b,
        },
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201

    first_id = first.json()["conversation_id"]
    second_id = second.json()["conversation_id"]

    response = client.get(
        "/conversations",
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 200

    conversations = response.json()

    titles = [
        conversation["title"]
        for conversation in conversations
    ]

    assert title_a in titles
    assert title_b in titles

    cleanup_conversation(first_id)
    cleanup_conversation(second_id)


def test_conversation_is_user_scoped(
    client,
    test_user,
):
    title = f"Pytest private {uuid.uuid4().hex[:8]}"

    response = client.post(
        "/conversations",
        params={
            "connection_id": 1,
            "title": title,
        },
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 201

    conversation_id = response.json()["conversation_id"]

    suffix = uuid.uuid4().hex[:8]

    other_credentials = {
        "username": f"pytest_other_conversation_{suffix}",
        "email": f"pytest_other_conversation_{suffix}@example.com",
        "password": "TestPassword123!",
    }

    register_response = client.post(
        "/auth/register",
        json=other_credentials,
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "username": other_credentials["username"],
            "password": other_credentials["password"],
        },
    )

    assert login_response.status_code == 200

    other_token = login_response.json()["access_token"]

    response = client.get(
        f"/conversations/{conversation_id}",
        headers={
            "Authorization": f"Bearer {other_token}"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Conversation not found."
    )

    response = client.get(
        f"/conversations/{conversation_id}/messages",
        headers={
            "Authorization": f"Bearer {other_token}"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Conversation not found."
    )

    cleanup_conversation(
        conversation_id
    )

    db = AppSessionLocal()

    try:
        db.execute(
            delete(User).where(
                User.username
                == other_credentials["username"]
            )
        )
        db.commit()

    finally:
        db.close()


def test_delete_conversation(
    client,
    test_user,
):
    title = f"Pytest delete {uuid.uuid4().hex[:8]}"

    response = client.post(
        "/conversations",
        params={
            "connection_id": 1,
            "title": title,
        },
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 201

    conversation_id = response.json()["conversation_id"]

    response = client.delete(
        f"/conversations/{conversation_id}",
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 204

    response = client.get(
        f"/conversations/{conversation_id}",
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Conversation not found."
    )