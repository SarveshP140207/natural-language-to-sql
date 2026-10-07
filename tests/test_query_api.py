from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user
from app.main import app


CONNECTION_ID = 1
TEST_USER_ID = 1


def headers(token: str):
    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def authenticated_client():
    test_user = SimpleNamespace(
        user_id=TEST_USER_ID,
    )

    app.dependency_overrides[
        get_current_user
    ] = lambda: test_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(
        get_current_user,
        None,
    )


def test_query_requires_authentication(client):
    response = client.post(
        "/query",
        json={
            "question": "Which category has the most products?",
            "connection_id": CONNECTION_ID,
        },
    )

    assert response.status_code == 401


def test_query_rejects_missing_connection(
    authenticated_client,
):
    response = authenticated_client.post(
        "/query",
        json={
            "question": "Which category has the most products?",
            "connection_id": 999999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Database connection not found."
    )


def test_query_creates_conversation_and_saves_history(
    authenticated_client,
    monkeypatch,
):
    captured = {}

    def fake_process_query(
        question,
        database_connection,
        user_id,
        conversation_id,
    ):
        captured["question"] = question
        captured["connection_id"] = (
            database_connection.connection_id
        )
        captured["user_id"] = user_id
        captured["conversation_id"] = conversation_id

        return {
            "question": question,
            "sql": (
                "SELECT category_id, category_name "
                "FROM categories"
            ),
            "result": {
                "columns": [
                    "category_id",
                    "category_name",
                ],
                "rows": [
                    {
                        "category_id": 1,
                        "category_name": "Automotive",
                    }
                ],
                "row_count": 1,
            },
            "analysis": {
                "summary": "Test result"
            },
            "visualization": None,
            "execution_time_ms": 10,
        }

    def fake_save_query_history(
        user_id,
        connection_id,
        question,
        sql_query,
        result,
        execution_time_ms,
    ):
        captured["history_user_id"] = user_id
        captured["history_connection_id"] = connection_id
        captured["history_question"] = question
        captured["history_sql"] = sql_query

        return SimpleNamespace(
            history_id=999001
        )

    monkeypatch.setattr(
        "app.main.process_query",
        fake_process_query,
    )

    monkeypatch.setattr(
        "app.main.save_query_history",
        fake_save_query_history,
    )

    response = authenticated_client.post(
        "/query",
        json={
            "question": "Which category has the most products?",
            "connection_id": CONNECTION_ID,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "Which category has the most products?"
    )

    assert data["history_id"] == 999001
    assert data["conversation_id"] is not None

    assert captured["question"] == (
        "Which category has the most products?"
    )

    assert captured["connection_id"] == CONNECTION_ID
    assert captured["user_id"] == TEST_USER_ID
    assert captured["conversation_id"] == (
        data["conversation_id"]
    )

    assert captured["history_user_id"] == TEST_USER_ID
    assert captured["history_connection_id"] == (
        CONNECTION_ID
    )

    assert captured["history_question"] == (
        "Which category has the most products?"
    )


def test_query_uses_existing_conversation(
    authenticated_client,
    monkeypatch,
):
    conversation_response = authenticated_client.post(
        "/conversations",
        params={
            "connection_id": CONNECTION_ID,
            "title": "Query API integration test",
        },
    )

    assert conversation_response.status_code == 201

    conversation_id = (
        conversation_response.json()["conversation_id"]
    )

    captured = {}

    def fake_process_query(
        question,
        database_connection,
        user_id,
        conversation_id,
    ):
        captured["question"] = question
        captured["connection_id"] = (
            database_connection.connection_id
        )
        captured["user_id"] = user_id
        captured["conversation_id"] = conversation_id

        return {
            "question": question,
            "sql": (
                "SELECT COUNT(*) AS product_count "
                "FROM products"
            ),
            "result": {
                "columns": [
                    "product_count"
                ],
                "rows": [
                    {
                        "product_count": 75
                    }
                ],
                "row_count": 1,
            },
            "analysis": {
                "summary": "75 products"
            },
            "visualization": None,
            "execution_time_ms": 8,
        }

    def fake_save_query_history(
        user_id,
        connection_id,
        question,
        sql_query,
        result,
        execution_time_ms,
    ):
        return SimpleNamespace(
            history_id=999002
        )

    monkeypatch.setattr(
        "app.main.process_query",
        fake_process_query,
    )

    monkeypatch.setattr(
        "app.main.save_query_history",
        fake_save_query_history,
    )

    response = authenticated_client.post(
        "/query",
        json={
            "question": "How many products are there?",
            "connection_id": CONNECTION_ID,
            "conversation_id": conversation_id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["conversation_id"] == conversation_id
    assert captured["conversation_id"] == conversation_id
    assert captured["user_id"] == TEST_USER_ID
    assert captured["connection_id"] == CONNECTION_ID
    assert data["history_id"] == 999002


def test_query_rejects_unknown_conversation(
    authenticated_client,
):
    response = authenticated_client.post(
        "/query",
        json={
            "question": "How many products are there?",
            "connection_id": CONNECTION_ID,
            "conversation_id": 999999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Conversation not found."
    )