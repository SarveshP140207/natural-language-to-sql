from app.ai.sql_generator import generate_sql
from app.database.executor import execute_read_only_query
from app.validation.query_limits import apply_query_limit
from app.validation.schema_validator import validate_generated_sql
from app.validation.sql_parser import parse_sql


def process_query(question: str):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # 1. Generate SQL from natural language.
    sql = generate_sql(question)

    # 2. Parse the generated SQL.
    expression = parse_sql(sql)

    # 3. Validate tables and columns against the live database schema.
    validate_generated_sql(expression)

    # 4. Normalize the validated SQL.
    validated_sql = expression.sql(dialect="mysql")

    # 5. Apply a maximum result-row limit.
    limited_sql = apply_query_limit(validated_sql)

    # 6. Execute the validated read-only query.
    result = execute_read_only_query(limited_sql)

    return {
        "question": question,
        "sql": limited_sql,
        "result": result
    }