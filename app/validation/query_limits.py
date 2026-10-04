import sqlglot
from sqlglot import exp


DEFAULT_MAX_ROWS = 100


def apply_query_limit(sql: str, max_rows: int = DEFAULT_MAX_ROWS) -> str:
    if not sql or not sql.strip():
        raise ValueError("SQL query cannot be empty.")

    if max_rows <= 0:
        raise ValueError("Maximum rows must be greater than zero.")

    try:
        expression = sqlglot.parse_one(
            sql,
            read="mysql"
        )
    except Exception as e:
        raise ValueError(f"Invalid SQL syntax: {e}")

    if not isinstance(expression, (exp.Select, exp.Union)):
        raise ValueError(
            "Query limits can only be applied to SELECT queries."
        )

    # UNION queries are handled separately for now.
    if isinstance(expression, exp.Union):
        return expression.sql(dialect="mysql")

    limit_expression = expression.args.get("limit")

    if limit_expression is None:
        expression.set(
            "limit",
            exp.Limit(
                expression=exp.Literal.number(max_rows)
            )
        )
    else:
        existing_limit = limit_expression.expression

        if isinstance(existing_limit, exp.Literal):
            try:
                existing_value = int(existing_limit.this)

                if existing_value > max_rows:
                    limit_expression.set(
                        "expression",
                        exp.Literal.number(max_rows)
                    )
            except (TypeError, ValueError):
                raise ValueError(
                    "LIMIT value must be a valid integer."
                )

    return expression.sql(dialect="mysql")