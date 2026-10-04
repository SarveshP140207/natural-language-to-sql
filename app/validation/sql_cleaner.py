import re


def clean_sql_response(response: str) -> str:
    if not response:
        raise ValueError("LLM returned an empty response.")

    sql = response.strip()

    # Remove markdown SQL code fences.
    sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql)

    sql = sql.strip()

    if not sql:
        raise ValueError("No SQL query found in LLM response.")

    return sql