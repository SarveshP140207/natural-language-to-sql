def build_sql_prompt(
    schema: dict,
    question: str,
    rag_context: str = "",
    conversation_context: str = ""
) -> str:
    schema_text = format_schema(schema)

    return f"""
You are a MySQL SQL generation assistant.

Your task is to convert the user's natural-language question
into a valid MySQL SELECT query.

IMPORTANT RULES:
1. Use ONLY tables and columns that exist in the database schema.
2. Do not invent table names or column names.
3. Use foreign-key relationships when joining tables.
4. Return ONLY the SQL query.
5. Do not include markdown code fences.
6. Do not include explanations.
7. Generate only read-only SELECT queries.
8. Use MySQL syntax.
9. Treat the retrieved RAG context as additional schema knowledge.
10. If RAG context conflicts with the actual database schema,
    trust the actual database schema.

DATABASE SCHEMA:
{schema_text}

RETRIEVED RAG CONTEXT:
{rag_context}

CONVERSATION CONTEXT:
{conversation_context}

IMPORTANT CONVERSATION RULES:
1. The conversation context contains previous questions, SQL queries,
   and actual result rows.
2. Use previous result rows when the current question refers to
   entities from an earlier result.
3. Resolve references such as "them", "their", "those", "that",
   "these", "the same", and "the second one" using the previous
   result rows.
4. When a follow-up refers to specific entities from a previous
   result, DO NOT query the entire table and return unrelated rows.
5. Identify the primary key or other identifying column in the
   previous result and use it to restrict the new query.
6. For example, if the previous result contains customer_id values
   43, 41, 68, 45, and 82, and the user asks "Show their cities",
   query the customers table for ONLY those customer_id values.
7. When appropriate, use a WHERE ... IN (...) condition containing
   the identifiers from the previous result.
8. Preserve the meaning of the previous result when answering a
   follow-up question.
9. If the current question is independent, ignore the previous
   conversation context.
10. Do not blindly copy previous SQL. Generate a new query that
    answers the current question.
11. Use the actual database schema as the final authority.

USER QUESTION:
{question}

SQL:
""".strip()


def format_schema(schema: dict) -> str:
    lines = []

    lines.append(f"Database: {schema['database']}")
    lines.append("")

    for table in schema["tables"]:
        lines.append(f"TABLE: {table['name']}")

        lines.append("COLUMNS:")
        for column in table["columns"]:
            nullable = "NULL" if column["nullable"] else "NOT NULL"

            lines.append(
                f"  - {column['name']} "
                f"({column['type']}, {nullable})"
            )

        if table["primary_key"]:
            lines.append(
                f"PRIMARY KEY: {', '.join(table['primary_key'])}"
            )

        if table["foreign_keys"]:
            lines.append("FOREIGN KEYS:")

            for foreign_key in table["foreign_keys"]:
                columns = ", ".join(foreign_key["columns"])
                referred_columns = ", ".join(
                    foreign_key["referred_columns"]
                )

                lines.append(
                    f"  - {columns} -> "
                    f"{foreign_key['referred_table']}"
                    f"({referred_columns})"
                )

        lines.append("")

    return "\n".join(lines)