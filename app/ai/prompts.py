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
9. Treat the retrieved RAG context as additional database knowledge.
10. If RAG context conflicts with the actual database schema,
    trust the actual database schema.

DATABASE SCHEMA:
{schema_text}

RETRIEVED RAG CONTEXT:
{rag_context}

CONVERSATION CONTEXT:
{conversation_context}

FOLLOW-UP QUESTION RESOLUTION:
1. The conversation context contains previous questions, SQL queries,
   and actual result rows from the database.
2. The current question may depend on the immediately previous result.
3. Resolve pronouns and references such as:
   "it", "its", "they", "them", "their", "that", "those",
   "these", "the same", "the first one", "the second one",
   "the above", and similar phrases.
4. When the current question contains a reference to a previous result,
   first identify the exact entity or value referred to using the
   previous result rows.
5. Never silently replace a specific previous entity with the whole table.
6. If the previous result contains a category_name, product_name,
   customer_name, order_id, product_id, customer_id, or another
   identifying value, use that value to restrict the new query.
7. If the previous result contains a value such as:
       category_name = "Automotive"
   and the user asks:
       "How many products does it have?"
   then "it" means the Automotive category.
   The query MUST count products belonging to the Automotive category,
   rather than counting all products.
8. In that example, use an appropriate condition such as:
       WHERE c.category_name = 'Automotive'
9. If the previous result contains multiple entities and the user says
   "them", "those", or "their", restrict the query to those entities
   rather than querying unrelated rows.
10. If the previous result contains primary-key values, prefer those
    identifiers when they are available and appropriate.
11. If the previous result contains a descriptive identifying value
    instead of a primary key, that value may be used to filter the query.
12. When the current question is independent and contains no reference
    to the previous conversation, generate the query normally.
13. Do not blindly copy the previous SQL.
14. Generate a NEW SQL query that answers the current question.
15. The actual database schema is always the final authority.

MANDATORY FOLLOW-UP CHECK:
Before producing SQL, determine whether the current question refers
to the previous result.

If YES:
- Identify the exact referenced entity.
- Restrict the SQL to that entity.
- Do NOT query the entire table unless the question explicitly asks
  for the entire table.

If NO:
- Treat the question as a new independent question.

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