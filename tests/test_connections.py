import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database.app_connection import AppSessionLocal
from app.database.models import User
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user(client):
    suffix = uuid.uuid4().hex[:8]

    credentials = {
        "username": f"pytest_connection_{suffix}",
        "email": f"pytest_connection_{suffix}@example.com",
        "password": "TestPassword123!",
    }

    response = client.post(
        "/auth/register",
        json=credentials,
    )

    assert response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "username": credentials["username"],
            "password": credentials["password"],
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    yield {
        "credentials": credentials,
        "token": token,
    }

    db = AppSessionLocal()

    try:
        db.execute(
            delete(User).where(
                User.username == credentials["username"]
            )
        )
        db.commit()

    finally:
        db.close()


def test_list_database_connections(client):
    login_response = client.post(
        "/auth/login",
        json={
            "username": "auth_test_001",
            "password": "TestPassword123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/database/connections",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    connections = response.json()

    assert isinstance(connections, list)
    assert any(
        connection["connection_id"] == 1
        for connection in connections
    )


def test_test_saved_database_connection(client):
    login_response = client.post(
        "/auth/login",
        json={
            "username": "auth_test_001",
            "password": "TestPassword123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/database/connections/1/test",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["connection_id"] == 1
    assert data["status"] == "success"
    assert data["message"] == (
        "Database connection successful."
    )


def test_connection_cannot_be_accessed_by_another_user(
    client,
    test_user,
):
    response = client.get(
        "/database/connections",
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        "/database/connections/1/test",
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Database connection not found."
    )


def test_non_mysql_connection_is_rejected(
    client,
    test_user,
):
    payload = {
        "name": f"pytest_invalid_{uuid.uuid4().hex[:8]}",
        "db_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database_name": "example",
        "username": "example",
        "password": "example",
    }

    response = client.post(
        "/database/connections",
        json=payload,
        headers={
            "Authorization": f"Bearer {test_user['token']}"
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Only MySQL connections are currently supported."
    )