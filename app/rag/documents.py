from app.database.introspector import get_database_schema
from app.rag.business_rules import BUSINESS_RULES
from app.rag.sql_examples import SQL_EXAMPLES


def generate_schema_documents():
    schema = get_database_schema()

    documents = []

    for table in schema["tables"]:
        lines = [
            f"TABLE: {table['name']}",
            "",
            "COLUMNS:"
        ]

        for column in table["columns"]:
            nullable = "NULL" if column["nullable"] else "NOT NULL"

            lines.append(
                f"- {column['name']} "
                f"({column['type']}, {nullable})"
            )

        if table["primary_key"]:
            lines.extend([
                "",
                f"PRIMARY KEY: {', '.join(table['primary_key'])}"
            ])

        if table["foreign_keys"]:
            lines.extend([
                "",
                "FOREIGN KEY RELATIONSHIPS:"
            ])

            for foreign_key in table["foreign_keys"]:
                columns = ", ".join(foreign_key["columns"])
                referred_columns = ", ".join(
                    foreign_key["referred_columns"]
                )

                lines.append(
                    f"- {table['name']}.{columns} -> "
                    f"{foreign_key['referred_table']}."
                    f"{referred_columns}"
                )

        documents.append({
            "type": "schema",
            "table": table["name"],
            "content": "\n".join(lines)
        })

    for rule in BUSINESS_RULES:
        documents.append({
            "type": "business_rule",
            "table": ", ".join(rule["tables"]),
            "content": (
                f"BUSINESS RULE: {rule['title']}\n\n"
                f"{rule['description']}\n\n"
                f"RELATED TABLES: {', '.join(rule['tables'])}\n"
                f"RELATED COLUMNS: {', '.join(rule['columns'])}"
            )
        })

    for example in SQL_EXAMPLES:
        documents.append({
            "type": "sql_example",
            "table": ", ".join(example["tables"]),
            "content": (
                f"SQL EXAMPLE: {example['example_id']}\n\n"
                f"QUESTION: {example['question']}\n\n"
                f"SQL:\n{example['sql']}\n\n"
                f"DESCRIPTION: {example['description']}\n\n"
                f"RELATED TABLES: {', '.join(example['tables'])}"
            )
        })

    return documents