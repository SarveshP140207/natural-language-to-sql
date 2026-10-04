import sqlglot

from app.validation.schema_validator import validate_generated_sql


valid_sql = """
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    SUM(o.total_amount) AS total_order_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name
ORDER BY total_order_amount DESC
LIMIT 5;
"""


invalid_sql = """
SELECT
    c.customer_id,
    c.customer_name
FROM customers c;
"""


print("Testing valid SQL...")

valid_expression = sqlglot.parse_one(
    valid_sql,
    read="mysql"
)

validate_generated_sql(valid_expression)

print("VALID SQL PASSED")
print()


print("Testing invalid SQL...")

invalid_expression = sqlglot.parse_one(
    invalid_sql,
    read="mysql"
)

try:
    validate_generated_sql(invalid_expression)
    print("ERROR: Invalid SQL was accepted.")
except ValueError as error:
    print("INVALID SQL BLOCKED")
    print(f"Reason: {error}")