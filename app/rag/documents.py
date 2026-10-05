from app.database.introspector import get_database_schema
from app.database.models import DatabaseConnection
from app.rag.business_rules import BUSINESS_RULES
from app.rag.sql_examples import SQL_EXAMPLES
from app.services.business_rule_service import (
    get_connection_business_rules,
    serialize_business_rule,
)


def generate_schema_documents(
    database_connection: DatabaseConnection | None = None,
):
    schema = get_database_schema(database_connection)

    documents = []

    # -------------------------
    # Schema documents
    # -------------------------

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

    # -------------------------
    # Business rules
    # -------------------------

    if database_connection is not None:
        rules = get_connection_business_rules(
            database_connection.connection_id
        )

        for rule in rules:
            rule_data = serialize_business_rule(rule)

            documents.append({
                "type": "business_rule",
                "table": ", ".join(
                    rule_data["table_names"]
                ),
                "content": (
                    f"BUSINESS RULE: {rule_data['title']}\n\n"
                    f"{rule_data['description']}\n\n"
                    f"RELATED TABLES: "
                    f"{', '.join(rule_data['table_names'])}\n"
                    f"RELATED COLUMNS: "
                    f"{', '.join(rule_data['column_names'])}"
                )
            })

    else:
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

    # -------------------------
    # SQL examples
    # -------------------------

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