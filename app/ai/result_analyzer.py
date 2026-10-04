from app.ai.llm import generate_response


def build_result_analysis_prompt(
    question: str,
    sql: str,
    result: dict
) -> str:
    return f"""
You are a data analysis assistant.

The user asked:

{question}

The SQL query executed was:

{sql}

The actual database result is:

Columns:
{result.get("columns", [])}

Rows:
{result.get("rows", [])}

Row count:
{result.get("row_count", 0)}

Analyze the actual result and answer the user's question naturally.

IMPORTANT RULES:
1. Use ONLY information present in the actual result.
2. Do not invent values or facts.
3. Do not perform calculations unless they can be derived directly
   from the provided result.
4. If the result is empty, clearly say that no matching records were found.
5. If the result contains a ranking, identify the important highest
   or lowest values when relevant.
6. If the result contains multiple records, summarize the important
   pattern instead of listing every row unnecessarily.
7. Keep the response concise and useful.
8. Mention important names, values, counts, dates, or categories
   when they directly answer the question.
9. NEVER assume a currency.
10. NEVER add a currency symbol such as $, ₹, €, £, or any other
    currency symbol unless the currency is explicitly present in
    the database result or explicitly specified by the user's question.
11. A column such as price, amount, total, total_spent, revenue, or
    sales does NOT by itself indicate a currency.
12. If the result contains a numeric monetary-looking value but no
    currency is specified, report only the number.
13. Do not convert between currencies.
14. Do not add words such as dollars, rupees, euros, or pounds unless
    the currency is explicitly known.
15. Do not mention SQL, database internals, prompts, or AI.
16. Do not claim information that is not present in the result.

Return only the natural-language answer.

ANSWER:
""".strip()


def analyze_result(
    question: str,
    sql: str,
    result: dict
) -> str:
    prompt = build_result_analysis_prompt(
        question=question,
        sql=sql,
        result=result
    )

    return generate_response(prompt).strip()