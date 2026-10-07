import uuid

import pytest
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


def headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def get_schema(path, method):
    openapi = app.openapi()

    operation = openapi["paths"][path][method.lower()]

    request_body = operation.get("requestBody")

    if not request_body:
        return None

    schema = (
        request_body
        .get("content", {})
        .get("application/json", {})
        .get("schema")
    )

    if not schema:
        return None

    while "$ref" in schema:
        ref = schema["$ref"].split("/")
        resolved = openapi

        for part in ref[1:]:
            resolved = resolved[part]

        schema = resolved

    return schema


def build_create_payload():
    schema = get_schema(
        "/business-rules",
        "post",
    )

    assert schema is not None

    properties = schema.get("properties", {})
    required = schema.get("required", [])

    payload = {}

    for field in required:
        name = field.lower()

        if "connection" in name and "id" in name:
            payload[field] = CONNECTION_ID

        elif "table" in name:
            payload[field] = ["orders"]

        elif "column" in name:
            payload[field] = [
                "status",
                "total_amount",
            ]

        elif "rule" in name or "description" in name or "text" in name:
            payload[field] = (
                "Revenue excludes cancelled orders."
            )

        elif "name" in name or "title" in name:
            payload[field] = (
                f"pytest-rule-{uuid.uuid4().hex[:8]}"
            )

        elif properties.get(field, {}).get("type") == "array":
            payload[field] = []

        elif properties.get(field, {}).get("type") == "boolean":
            payload[field] = True

        elif properties.get(field, {}).get("type") == "integer":
            payload[field] = 1

        elif properties.get(field, {}).get("type") == "number":
            payload[field] = 1

        else:
            payload[field] = "pytest business rule"

    return payload


def build_update_payload():
    schema = get_schema(
        "/business-rules/{rule_id}",
        "put",
    )

    assert schema is not None

    properties = schema.get("properties", {})
    required = schema.get("required", [])

    payload = {}

    for field in required:
        name = field.lower()

        if "connection" in name and "id" in name:
            payload[field] = CONNECTION_ID

        elif "table" in name:
            payload[field] = ["orders"]

        elif "column" in name:
            payload[field] = [
                "status",
                "total_amount",
            ]

        elif "rule" in name or "description" in name or "text" in name:
            payload[field] = (
                "Updated pytest business rule."
            )

        elif "name" in name or "title" in name:
            payload[field] = (
                f"pytest-updated-{uuid.uuid4().hex[:8]}"
            )

        elif properties.get(field, {}).get("type") == "array":
            payload[field] = []

        elif properties.get(field, {}).get("type") == "boolean":
            payload[field] = True

        elif properties.get(field, {}).get("type") == "integer":
            payload[field] = 1

        elif properties.get(field, {}).get("type") == "number":
            payload[field] = 1

        else:
            payload[field] = "updated pytest value"

    return payload


def create_rule(token):
    response = client.post(
        "/business-rules",
        params={
            "connection_id": CONNECTION_ID
        },
        json=build_create_payload(),
        headers=headers(token),
    )

    assert response.status_code == 201, response.text

    data = response.json()

    for key in (
        "business_rule_id",
        "rule_id",
        "id",
    ):
        if key in data:
            return data[key]

    pytest.fail(
        f"Could not find business rule ID: {data}"
    )


def delete_rule(token, rule_id):
    return client.delete(
        f"/business-rules/{rule_id}",
        params={
            "connection_id": CONNECTION_ID
        },
        headers=headers(token),
    )


@pytest.fixture
def owner_token():
    return login(
        OWNER_USERNAME,
        OWNER_PASSWORD,
    )


def test_create_business_rule(owner_token):
    rule_id = create_rule(owner_token)

    assert rule_id is not None

    response = delete_rule(
        owner_token,
        rule_id,
    )

    assert response.status_code == 204


def test_list_business_rules(owner_token):
    rule_id = create_rule(owner_token)

    try:
        response = client.get(
            "/business-rules",
            params={
                "connection_id": CONNECTION_ID
            },
            headers=headers(owner_token),
        )

        assert response.status_code == 200, response.text

        data = response.json()

        assert isinstance(data, list)

        ids = []

        for item in data:
            for key in (
                "business_rule_id",
                "rule_id",
                "id",
            ):
                if key in item:
                    ids.append(item[key])
                    break

        assert rule_id in ids

    finally:
        delete_rule(
            owner_token,
            rule_id,
        )


def test_get_business_rule(owner_token):
    rule_id = create_rule(owner_token)

    try:
        response = client.get(
            f"/business-rules/{rule_id}",
            params={
                "connection_id": CONNECTION_ID
            },
            headers=headers(owner_token),
        )

        assert response.status_code == 200, response.text

        data = response.json()

        returned_id = None

        for key in (
            "business_rule_id",
            "rule_id",
            "id",
        ):
            if key in data:
                returned_id = data[key]
                break

        assert returned_id == rule_id

    finally:
        delete_rule(
            owner_token,
            rule_id,
        )


def test_update_business_rule(owner_token):
    rule_id = create_rule(owner_token)

    try:
        response = client.put(
            f"/business-rules/{rule_id}",
            params={
                "connection_id": CONNECTION_ID
            },
            json=build_update_payload(),
            headers=headers(owner_token),
        )

        assert response.status_code == 200, response.text

    finally:
        delete_rule(
            owner_token,
            rule_id,
        )


def test_delete_business_rule(owner_token):
    rule_id = create_rule(owner_token)

    response = delete_rule(
        owner_token,
        rule_id,
    )

    assert response.status_code == 204

    response = client.get(
        f"/business-rules/{rule_id}",
        params={
            "connection_id": CONNECTION_ID
        },
        headers=headers(owner_token),
    )

    assert response.status_code == 404


def test_business_rule_is_user_scoped(owner_token):
    rule_id = create_rule(owner_token)

    try:
        other_username = (
            f"pytest_other_rules_{uuid.uuid4().hex[:8]}"
        )

        register_response = client.post(
            "/auth/register",
            json={
                "username": other_username,
                "email": f"{other_username}@example.com",
                "password": "TestPassword123!",
            },
        )

        assert register_response.status_code in (
            200,
            201,
        ), register_response.text

        other_token = login(
            other_username,
            "TestPassword123!",
        )

        response = client.get(
            f"/business-rules/{rule_id}",
            params={
                "connection_id": CONNECTION_ID
            },
            headers=headers(other_token),
        )

        assert response.status_code == 404

    finally:
        delete_rule(
            owner_token,
            rule_id,
        )