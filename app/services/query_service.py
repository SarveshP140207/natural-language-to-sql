from app.ai.result_analyzer import analyze_result
from app.ai.sql_generator import generate_sql
from app.ai.sql_repair import repair_sql
from app.database.executor import execute_read_only_query
from app.services.conversation_service import conversation_state
from app.validation.query_limits import apply_query_limit
from app.validation.schema_validator import validate_generated_sql
from app.validation.sql_parser import parse_sql


MAX_REPAIR_ATTEMPTS = 2


def build_conversation_context() -> str:
    messages = conversation_state.get_recent_messages(limit=5)

    if not messages:
        return ""

    context_parts = []

    for index, message in enumerate(messages, start=1):
        result = message["result"]

        context_parts.append(
            f"""Conversation {index}:
Question: {message['question']}
SQL: {message['sql']}
Result row count: {result.get('row_count', 0)}
Result columns: {result.get('columns', [])}
Result rows:
{result.get('rows', [])}
"""
        )

    return "\n".join(context_parts)


def validate_and_prepare_sql(sql: str) -> str:
    expression = parse_sql(sql)

    validate_generated_sql(expression)

    validated_sql = expression.sql(dialect="mysql")

    return apply_query_limit(validated_sql)


def process_query(question: str):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    conversation_context = build_conversation_context()

    sql = generate_sql(
        question=question,
        conversation_context=conversation_context
    )

    prepared_sql = validate_and_prepare_sql(sql)

    for attempt in range(MAX_REPAIR_ATTEMPTS + 1):
        try:
            result = execute_read_only_query(prepared_sql)

            analysis = analyze_result(
                question=question,
                sql=prepared_sql,
                result=result
            )

            conversation_state.add_message(
                question=question,
                sql=prepared_sql,
                result=result
            )

            return {
                "question": question,
                "sql": prepared_sql,
                "result": result,
                "analysis": analysis
            }

        except Exception as error:
            if attempt >= MAX_REPAIR_ATTEMPTS:
                raise

            repaired_sql = repair_sql(
                question=question,
                sql=prepared_sql,
                error=str(error)
            )

            prepared_sql = validate_and_prepare_sql(
                repaired_sql
            )