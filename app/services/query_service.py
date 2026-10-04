from app.ai.sql_generator import generate_sql
from app.ai.sql_repair import repair_sql
from app.database.executor import execute_read_only_query
from app.validation.query_limits import apply_query_limit
from app.validation.schema_validator import validate_generated_sql
from app.validation.sql_parser import parse_sql


MAX_REPAIR_ATTEMPTS = 2


def validate_and_prepare_sql(sql: str) -> str:
    expression = parse_sql(sql)

    validate_generated_sql(expression)

    validated_sql = expression.sql(dialect="mysql")

    return apply_query_limit(validated_sql)


def process_query(question: str):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # 1. Generate SQL from natural language.
    sql = generate_sql(question)

    # 2. Validate and prepare the generated SQL.
    prepared_sql = validate_and_prepare_sql(sql)

    # 3. Execute with limited repair attempts.
    for attempt in range(MAX_REPAIR_ATTEMPTS + 1):
        try:
            result = execute_read_only_query(prepared_sql)

            return {
                "question": question,
                "sql": prepared_sql,
                "result": result
            }

        except Exception as error:
            if attempt >= MAX_REPAIR_ATTEMPTS:
                raise

            repaired_sql = repair_sql(
                question=question,
                sql=prepared_sql,
                error=str(error)
            )

            # Every repaired query goes through the
            # exact same validation pipeline.
            prepared_sql = validate_and_prepare_sql(
                repaired_sql
            )