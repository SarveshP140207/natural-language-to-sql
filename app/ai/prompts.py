def build_sql_prompt(schema: dict, question: str) -> str:
    schema_text = format_schema(schema)

    return f"""
You are a MySQL SQL generation assistant.

Your task is to convert the user's natural-language question into
a valid MySQL SELECT query.

IMPORTANT RULES:
1. Use ONLY tables and columns that exist in the provided schema.
2. Do not invent table names or column names.
3. Use the foreign-key relationships when joining tables.
4. Return ONLY the SQL query.
5. Do not include markdown code fences.
6. Do not include explanations.
7. Generate only read-only SELECT queries.
8. Use MySQL syntax.

DATABASE SCHEMA:
{schema_text}

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