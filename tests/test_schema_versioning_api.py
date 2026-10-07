import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

CONNECTION_ID = 1

OWNER_USERNAME = "auth_test_001"
OWNER_PASSWORD = "TestPassword123!"


def login(username, password):
    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "access_token" in data

    return data["access_token"]


def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def test_schema_sync_endpoint():
    token = login(
        OWNER_USERNAME,
        OWNER_PASSWORD,
    )

    response = client.post(
        f"/database/connections/{CONNECTION_ID}/schema/sync",
        headers=auth_headers(token),
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "connection_id" in data
    assert "changed" in data
    assert "schema_version_id" in data
    assert "version_hash" in data
    assert "message" in data

    assert data["connection_id"] == CONNECTION_ID
    assert isinstance(data["changed"], bool)
    assert isinstance(data["schema_version_id"], int)
    assert isinstance(data["version_hash"], str)
    assert len(data["version_hash"]) == 64
    assert isinstance(data["message"], str)

    if "table_count" in data:
        assert data["table_count"] == 7


def test_schema_sync_is_idempotent():
    token = login(
        OWNER_USERNAME,
        OWNER_PASSWORD,
    )

    first_response = client.post(
        f"/database/connections/{CONNECTION_ID}/schema/sync",
        headers=auth_headers(token),
    )

    assert first_response.status_code == 200, first_response.text

    first_data = first_response.json()

    second_response = client.post(
        f"/database/connections/{CONNECTION_ID}/schema/sync",
        headers=auth_headers(token),
    )

    assert second_response.status_code == 200, second_response.text

    second_data = second_response.json()

    assert second_data["changed"] is False

    assert (
        second_data["schema_version_id"]
        == first_data["schema_version_id"]
    )

    assert (
        second_data["version_hash"]
        == first_data["version_hash"]
    )

    if "table_count" in second_data:
        assert second_data["table_count"] == 7

    if "indexed_documents" in second_data:
        assert second_data["indexed_documents"] is None

    message = second_data["message"].lower()

    assert (
        "unchanged" in message
        or "current" in message
    )


def test_schema_sync_is_user_scoped():
    login(
        OWNER_USERNAME,
        OWNER_PASSWORD,
    )

    username = (
        f"pytest_schema_{uuid.uuid4().hex[:8]}"
    )

    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
        },
    )

    assert register_response.status_code in (
        200,
        201,
    ), register_response.text

    other_token = login(
        username,
        password,
    )

    response = client.post(
        f"/database/connections/{CONNECTION_ID}/schema/sync",
        headers=auth_headers(other_token),
    )

    assert response.status_code == 404