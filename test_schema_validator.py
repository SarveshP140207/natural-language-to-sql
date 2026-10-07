import pytest
from sqlglot import parse_one

from app.validation.schema_validator import validate_generated_sql


def test_valid_customers_query():
    expression = parse_one(
        """
        SELECT
            c.customer_id,
            c.first_name,
            c.email
        FROM customers AS c
        """
    )

    assert validate_generated_sql(expression) is True


def test_valid_products_query():
    expression = parse_one(
        """
        SELECT
            p.product_id,
            p.product_name,
            p.price
        FROM products AS p
        """
    )

    assert validate_generated_sql(expression) is True


def test_invalid_table():
    expression = parse_one(
        """
        SELECT
            e.employee_id
        FROM employees AS e
        """
    )

    with pytest.raises(
        ValueError,
        match="Table 'employees' does not exist",
    ):
        validate_generated_sql(expression)


def test_invalid_column():
    expression = parse_one(
        """
        SELECT
            c.customer_id,
            c.customer_name
        FROM customers AS c
        """
    )

    with pytest.raises(
        ValueError,
        match="Column 'customer_name' does not exist",
    ):
        validate_generated_sql(expression)


def test_select_star_is_allowed():
    expression = parse_one(
        """
        SELECT *
        FROM customers
        """
    )

    assert validate_generated_sql(expression) is True


def test_table_alias_is_resolved():
    expression = parse_one(
        """
        SELECT
            c.customer_id,
            c.email
        FROM customers AS c
        """
    )

    assert validate_generated_sql(expression) is True