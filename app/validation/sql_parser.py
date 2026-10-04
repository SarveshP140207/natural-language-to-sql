import sqlglot
from sqlglot import exp


ALLOWED_STATEMENTS = (exp.Select, exp.Union)

BLOCKED_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Create,
    exp.Drop,
    exp.Alter,
    exp.TruncateTable,
    exp.Grant,
    exp.Revoke,
)


def parse_sql(sql: str):
    if not sql or not sql.strip():
        raise ValueError("SQL query cannot be empty.")

    try:
        statements = sqlglot.parse(sql, read="mysql")
    except Exception as e:
        raise ValueError(f"Invalid SQL syntax: {e}")

    if len(statements) != 1:
        raise ValueError("Only one SQL statement is allowed.")

    expression = statements[0]

    for node in expression.walk():
        if isinstance(node, BLOCKED_EXPRESSIONS):
            raise ValueError(
                f"Blocked SQL operation: {type(node).__name__}"
            )

    if not isinstance(expression, ALLOWED_STATEMENTS):
        raise ValueError(
            "Only SELECT queries and safe SELECT-based "
            "UNION queries are allowed."
        )

    return expression


def validate_sql(sql: str) -> str:
    expression = parse_sql(sql)

    return expression.sql(dialect="mysql")