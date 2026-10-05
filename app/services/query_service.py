from time import perf_counter

from app.ai.result_analyzer import analyze_result
from app.ai.sql_generator import generate_sql
from app.ai.sql_repair import repair_sql
from app.ai.visualization_analyzer import analyze_visualization
from app.database.executor import execute_read_only_query
from app.database.models import DatabaseConnection
from app.services.conversation_service import (
    add_query_exchange,
    build_conversation_context,
)
from app.validation.query_limits import apply_query_limit
from app.validation.schema_validator import validate_generated_sql
from app.validation.sql_parser import parse_sql


MAX_REPAIR_ATTEMPTS = 2


def validate_and_prepare_sql(sql: str) -> str:
    expression = parse_sql(sql)

    validate_generated_sql(expression)

    validated_sql = expression.sql(dialect="mysql")

    return apply_query_limit(validated_sql)


def process_query(
    question: str,
    database_connection: DatabaseConnection | None = None,
    user_id: int | None = None,
    conversation_id: int | None = None,
):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    conversation_context = ""

    if conversation_id is not None:
        if user_id is None:
            raise ValueError(
                "User ID is required when using a conversation."
            )

        conversation_context = build_conversation_context(
            user_id=user_id,
            conversation_id=conversation_id,
            limit=5,
        )

    sql = generate_sql(
        question=question,
        conversation_context=conversation_context,
        database_connection=database_connection,
    )

    prepared_sql = validate_and_prepare_sql(sql)

    for attempt in range(MAX_REPAIR_ATTEMPTS + 1):
        try:
            execution_start = perf_counter()

            result = execute_read_only_query(
                prepared_sql,
                database_connection,
            )

            execution_time_ms = round(
                (perf_counter() - execution_start) * 1000
            )

            analysis = analyze_result(
                question=question,
                sql=prepared_sql,
                result=result,
            )

            visualization = analyze_visualization(
                question=question,
                result=result,
            )

            if (
                user_id is not None
                and conversation_id is not None
                and database_connection is not None
            ):
                add_query_exchange(
                    conversation_id=conversation_id,
                    question=question,
                    sql=prepared_sql,
                    result=result,
                )

            return {
                "question": question,
                "sql": prepared_sql,
                "result": result,
                "analysis": analysis,
                "visualization": visualization,
                "execution_time_ms": execution_time_ms,
            }

        except Exception as error:
            if attempt >= MAX_REPAIR_ATTEMPTS:
                raise

            repaired_sql = repair_sql(
                question=question,
                sql=prepared_sql,
                error=str(error),
            )

            prepared_sql = validate_and_prepare_sql(
                repaired_sql,
            )