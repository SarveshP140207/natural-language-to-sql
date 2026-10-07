import pytest
from sqlglot import parse_one
from sqlalchemy import select

from app.database.app_connection import AppSessionLocal
from app.database.models import DatabaseConnection
from app.services import query_service


CONNECTION_ID = 1


def get_test_connection():
    db = AppSessionLocal()

    try:
        connection = db.scalar(
            select(DatabaseConnection).where(
                DatabaseConnection.connection_id == CONNECTION_ID
            )
        )

        if not connection:
            pytest.fail(
                f"Database connection {CONNECTION_ID} was not found."
            )

        return connection

    finally:
        db.close()


def test_valid_sql_is_accepted_for_selected_database():
    database_connection = get_test_connection()

    sql = """
        SELECT
            customer_id,
            first_name,
            email
        FROM customers
    """

    prepared_sql = query_service.validate_and_prepare_sql(
        sql,
        database_connection,
    )

    assert "FROM customers" in prepared_sql
    assert "customer_id" in prepared_sql
    assert "first_name" in prepared_sql
    assert "email" in prepared_sql


def test_invalid_table_is_rejected_for_selected_database():
    database_connection = get_test_connection()

    sql = """
        SELECT
            employee_id
        FROM employees
    """

    with pytest.raises(
        ValueError,
        match="Table 'employees' does not exist",
    ):
        query_service.validate_and_prepare_sql(
            sql,
            database_connection,
        )


def test_invalid_column_is_rejected_for_selected_database():
    database_connection = get_test_connection()

    sql = """
        SELECT
            customer_id,
            customer_name
        FROM customers
    """

    with pytest.raises(
        ValueError,
        match="Column 'customer_name' does not exist",
    ):
        query_service.validate_and_prepare_sql(
            sql,
            database_connection,
        )


def test_schema_validation_receives_selected_database():
    database_connection = get_test_connection()

    captured_connection = None

    original_validator = query_service.validate_generated_sql

    def capture_validator(
        expression,
        database_connection=None,
    ):
        nonlocal captured_connection

        captured_connection = database_connection

        return original_validator(
            expression,
            database_connection,
        )

    query_service.validate_generated_sql = capture_validator

    try:
        query_service.validate_and_prepare_sql(
            """
            SELECT customer_id
            FROM customers
            """,
            database_connection,
        )
    finally:
        query_service.validate_generated_sql = original_validator

    assert captured_connection is database_connection


def test_invalid_generated_sql_is_repaired_and_executed(
    monkeypatch,
):
    database_connection = get_test_connection()

    generated_sql = [
        """
        SELECT
            customer_id,
            customer_name
        FROM customers
        """,
        """
        SELECT
            customer_id,
            first_name
        FROM customers
        """,
    ]

    repair_calls = []

    def fake_generate_sql(
        question,
        conversation_context,
        database_connection,
    ):
        return generated_sql[0]

    def fake_repair_sql(
        question,
        sql,
        error,
    ):
        repair_calls.append(
            {
                "question": question,
                "sql": sql,
                "error": error,
            }
        )

        return generated_sql[1]

    def fake_execute_read_only_query(
        sql,
        database_connection,
    ):
        assert "customer_name" not in sql
        assert "first_name" in sql
        assert database_connection is database_connection

        return {
            "columns": [
                "customer_id",
                "first_name",
            ],
            "rows": [
                {
                    "customer_id": 1,
                    "first_name": "John",
                }
            ],
            "row_count": 1,
        }

    monkeypatch.setattr(
        query_service,
        "generate_sql",
        fake_generate_sql,
    )

    monkeypatch.setattr(
        query_service,
        "repair_sql",
        fake_repair_sql,
    )

    monkeypatch.setattr(
        query_service,
        "execute_read_only_query",
        fake_execute_read_only_query,
    )

    monkeypatch.setattr(
        query_service,
        "analyze_result",
        lambda question, sql, result: {
            "summary": "Test result"
        },
    )

    monkeypatch.setattr(
        query_service,
        "analyze_visualization",
        lambda question, result: None,
    )

    result = query_service.process_query(
        question="Show customer IDs and first names.",
        database_connection=database_connection,
    )

    assert len(repair_calls) == 1
    assert "customer_name" in repair_calls[0]["error"]

    assert "customer_id" in result["sql"]
    assert "first_name" in result["sql"]
    assert "customer_name" not in result["sql"]

    assert result["result"]["row_count"] == 1