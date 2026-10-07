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
def test_credentials():
    suffix = uuid.uuid4().hex[:8]

    return {
        "username": f"pytest_user_{suffix}",
        "email": f"pytest_{suffix}@example.com",
        "password": "TestPassword123!",
    }


@pytest.fixture
def registered_user(client, test_credentials):
    response = client.post(
        "/auth/register",
        json=test_credentials,
    )

    assert response.status_code == 201

    yield test_credentials

    db = AppSessionLocal()

    try:
        db.execute(
            delete(User).where(
                User.username == test_credentials["username"]
            )
        )
        db.commit()

    finally:
        db.close()


def test_register_user(client, test_credentials):
    response = client.post(
        "/auth/register",
        json=test_credentials,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == test_credentials["username"]
    assert data["email"] == test_credentials["email"]
    assert data["is_active"] is True

    db = AppSessionLocal()

    try:
        user = db.query(User).filter(
            User.username == test_credentials["username"]
        ).first()

        assert user is not None
        assert user.password_hash != test_credentials["password"]

    finally:
        db.execute(
            delete(User).where(
                User.username == test_credentials["username"]
            )
        )
        db.commit()
        db.close()


def test_login_user(
    client,
    registered_user,
):
    response = client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == registered_user["username"]


def test_get_current_user(
    client,
    registered_user,
):
    login_response = client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == registered_user["username"]
    assert data["email"] == registered_user["email"]
    assert data["is_active"] is True


def test_invalid_login(
    client,
    registered_user,
):
    response = client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid username or password."
    )


def test_protected_me_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401