import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database.app_connection import AppSessionLocal
from app.database.models import QueryHistory, User
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user_with_history(client):
    suffix = uuid.uuid4().hex[:8]

    credentials = {
        "username": f"pytest_history_{suffix}",
        "email": f"pytest_history_{suffix}@example.com",
        "password": "TestPassword123!",
    }

    register_response = client.post(
        "/auth/register",
        json=credentials,
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "username": credentials["username"],
            "password": credentials["password"],
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    db = AppSessionLocal()

    try:
        user = db.query(User).filter(
            User.username == credentials["username"]
        ).first()

        history = QueryHistory(
            user_id=user.user_id,
            connection_id=1,
            question="Pytest history question",
            sql_query="SELECT 1",
            result_summary='{"row_count":1,"columns":["1"],"rows":[{"1":1}]}',
            execution_time_ms=5,
        )

        db.add(history)
        db.commit()
        db.refresh(history)

        history_id = history.history_id
        user_id = user.user_id

    finally:
        db.close()

    yield {
        "token": token,
        "history_id": history_id,
        "user_id": user_id,
        "credentials": credentials,
    }

    db = AppSessionLocal()

    try:
        db.execute(
            delete(QueryHistory).where(
                QueryHistory.history_id == history_id
            )
        )

        db.execute(
            delete(User).where(
                User.user_id == user_id
            )
        )

        db.commit()

    finally:
        db.close()


def test_list_history(
    client,
    test_user_with_history,
):
    response = client.get(
        "/history",
        headers={
            "Authorization":
                f"Bearer {test_user_with_history['token']}"
        },
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 1
    assert history[0]["history_id"] == (
        test_user_with_history["history_id"]
    )
    assert history[0]["question"] == (
        "Pytest history question"
    )


def test_get_history_item(
    client,
    test_user_with_history,
):
    history_id = test_user_with_history["history_id"]

    response = client.get(
        f"/history/{history_id}",
        headers={
            "Authorization":
                f"Bearer {test_user_with_history['token']}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["history_id"] == history_id
    assert data["connection_id"] == 1
    assert data["question"] == (
        "Pytest history question"
    )
    assert data["sql_query"] == "SELECT 1"
    assert data["execution_time_ms"] == 5


def test_missing_history_returns_404(
    client,
    test_user_with_history,
):
    response = client.get(
        "/history/999999999",
        headers={
            "Authorization":
                f"Bearer {test_user_with_history['token']}"
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Query history item not found."
    )


def test_history_is_user_scoped(
    client,
    test_user_with_history,
):
    suffix = uuid.uuid4().hex[:8]

    other_credentials = {
        "username": f"pytest_other_{suffix}",
        "email": f"pytest_other_{suffix}@example.com",
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

    history_id = test_user_with_history["history_id"]

    response = client.get(
        f"/history/{history_id}",
        headers={
            "Authorization":
                f"Bearer {other_token}"
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Query history item not found."
    )

    db = AppSessionLocal()

    try:
        db.execute(
            delete(User).where(
                User.username == other_credentials["username"]
            )
        )
        db.commit()

    finally:
        db.close()