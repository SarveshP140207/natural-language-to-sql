from sqlalchemy import inspect

from app.database.connection import engine


def get_database_schema():
    inspector = inspect(engine)

    schema = {
        "database": engine.url.database,
        "tables": []
    }

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        primary_key = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)

        table_info = {
            "name": table_name,
            "columns": [],
            "primary_key": primary_key.get("constrained_columns", []),
            "foreign_keys": []
        }

        for column in columns:
            table_info["columns"].append({
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"],
                "default": column["default"]
            })

        for foreign_key in foreign_keys:
            table_info["foreign_keys"].append({
                "columns": foreign_key["constrained_columns"],
                "referred_table": foreign_key["referred_table"],
                "referred_columns": foreign_key["referred_columns"]
            })

        schema["tables"].append(table_info)

    return schema