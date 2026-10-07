import pytest

from app.services.schema_version_service import calculate_schema_hash


def test_schema_hash_is_stable():
    schema = {
        "database": "ecommerce_db",
        "tables": {
            "orders": {
                "columns": [
                    {
                        "name": "order_id",
                        "type": "INT",
                    },
                    {
                        "name": "total_amount",
                        "type": "DECIMAL",
                    },
                ]
            },
            "customers": {
                "columns": [
                    {
                        "name": "customer_id",
                        "type": "INT",
                    }
                ]
            },
        },
    }

    first_hash = calculate_schema_hash(schema)
    second_hash = calculate_schema_hash(schema)

    assert first_hash == second_hash
    assert len(first_hash) == 64


def test_schema_hash_changes_when_schema_changes():
    original = {
        "database": "ecommerce_db",
        "tables": {
            "orders": {
                "columns": [
                    {
                        "name": "order_id",
                        "type": "INT",
                    }
                ]
            }
        },
    }

    changed = {
        "database": "ecommerce_db",
        "tables": {
            "orders": {
                "columns": [
                    {
                        "name": "order_id",
                        "type": "INT",
                    },
                    {
                        "name": "discount_amount",
                        "type": "DECIMAL",
                    },
                ]
            }
        },
    }

    original_hash = calculate_schema_hash(original)
    changed_hash = calculate_schema_hash(changed)

    assert original_hash != changed_hash


def test_schema_hash_is_independent_of_dictionary_order():
    schema_a = {
        "database": "ecommerce_db",
        "tables": {
            "orders": {
                "columns": [
                    {
                        "name": "order_id",
                        "type": "INT",
                    }
                ]
            },
            "customers": {
                "columns": [
                    {
                        "name": "customer_id",
                        "type": "INT",
                    }
                ]
            },
        },
    }

    schema_b = {
        "tables": {
            "customers": {
                "columns": [
                    {
                        "type": "INT",
                        "name": "customer_id",
                    }
                ]
            },
            "orders": {
                "columns": [
                    {
                        "type": "INT",
                        "name": "order_id",
                    }
                ]
            },
        },
        "database": "ecommerce_db",
    }

    assert calculate_schema_hash(schema_a) == calculate_schema_hash(schema_b)


def test_empty_schema_produces_valid_hash():
    schema = {}

    result = calculate_schema_hash(schema)

    assert isinstance(result, str)
    assert len(result) == 64
    assert all(
        character in "0123456789abcdef"
        for character in result
    )