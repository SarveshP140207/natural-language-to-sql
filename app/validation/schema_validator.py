from sqlalchemy import inspect
from sqlglot import exp

from app.database.connection import engine
from app.database.models import DatabaseConnection
from app.database.executor import create_connection_engine


def get_database_schema_map(
    database_connection: DatabaseConnection | None = None,
):
    if database_connection is None:
        query_engine = engine
        owns_engine = False
    else:
        query_engine = create_connection_engine(
            database_connection
        )
        owns_engine = True

    try:
        inspector = inspect(query_engine)

        schema_map = {}

        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)

            schema_map[table_name] = {
                column["name"]
                for column in columns
            }

        return schema_map

    finally:
        if owns_engine:
            query_engine.dispose()


def extract_tables(expression):
    tables = set()

    for table in expression.find_all(exp.Table):
        tables.add(table.name)

    return tables


def extract_select_aliases(expression):
    aliases = set()

    for alias in expression.find_all(exp.Alias):
        alias_name = alias.alias

        if alias_name:
            aliases.add(alias_name)

    return aliases


def extract_table_aliases(expression):
    aliases = {}

    for table in expression.find_all(exp.Table):
        table_name = table.name
        alias = table.alias

        if alias:
            aliases[alias] = table_name

    return aliases


def extract_columns(expression):
    columns = {}

    select_aliases = extract_select_aliases(
        expression
    )

    table_aliases = extract_table_aliases(
        expression
    )

    unqualified_columns = set()

    for column in expression.find_all(exp.Column):
        table_name = column.table
        column_name = column.name

        if column_name == "*":
            continue

        if column_name in select_aliases:
            continue

        if table_name:
            real_table_name = table_aliases.get(
                table_name,
                table_name,
            )

            columns.setdefault(
                real_table_name,
                set(),
            ).add(column_name)

        else:
            unqualified_columns.add(
                column_name
            )

    if unqualified_columns:
        columns[None] = unqualified_columns

    return columns


def validate_generated_sql(
    expression,
    database_connection: DatabaseConnection | None = None,
):
    schema_map = get_database_schema_map(
        database_connection
    )

    tables = extract_tables(expression)
    columns = extract_columns(expression)

    for table in tables:
        if table not in schema_map:
            raise ValueError(
                f"Table '{table}' does not exist in the database."
            )

    for table, requested_columns in columns.items():

        if table is None:
            for column in requested_columns:
                matching_tables = [
                    table_name
                    for table_name in tables
                    if column in schema_map[table_name]
                ]

                if not matching_tables:
                    raise ValueError(
                        f"Column '{column}' does not exist "
                        f"in the referenced tables."
                    )

                if len(matching_tables) > 1:
                    raise ValueError(
                        f"Column '{column}' is ambiguous "
                        f"across the referenced tables."
                    )

            continue

        if table not in schema_map:
            raise ValueError(
                f"Table '{table}' does not exist in the database."
            )

        for column in requested_columns:
            if column == "*":
                continue

            if column not in schema_map[table]:
                raise ValueError(
                    f"Column '{column}' does not exist "
                    f"in table '{table}'."
                )

    return True