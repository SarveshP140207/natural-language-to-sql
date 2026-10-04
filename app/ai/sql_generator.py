from app.ai.llm import generate_response
from app.ai.prompts import build_sql_prompt
from app.database.introspector import get_database_schema
from app.validation.sql_cleaner import clean_sql_response


def generate_sql(question: str) -> str:
    schema = get_database_schema()

    prompt = build_sql_prompt(
        schema=schema,
        question=question
    )

    response = generate_response(prompt)

    return clean_sql_response(response)