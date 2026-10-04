from app.ai.llm import generate_response
from app.validation.sql_cleaner import clean_sql_response


def build_repair_prompt(
    question: str,
    sql: str,
    error: str,
) -> str:
    return f"""
You are a MySQL SQL repair assistant.

The original natural-language question was:

{question}

The generated SQL was:

{sql}

MySQL returned this execution error:

{error}

Repair the SQL so that it correctly answers the original question.

IMPORTANT RULES:
1. Return ONLY the corrected SQL query.
2. Do not include markdown code fences.
3. Do not include explanations.
4. Generate only a read-only SELECT query.
5. Do not invent tables or columns.
6. Preserve the original intent of the question.
7. Use valid MySQL syntax.

CORRECTED SQL:
""".strip()


def repair_sql(
    question: str,
    sql: str,
    error: str,
) -> str:
    prompt = build_repair_prompt(
        question=question,
        sql=sql,
        error=error,
    )

    response = generate_response(prompt)

    return clean_sql_response(response)