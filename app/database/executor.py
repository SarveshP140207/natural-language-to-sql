from sqlalchemy import text

from app.database.connection import engine


def execute_read_only_query(sql: str):
    with engine.connect() as connection:
        result = connection.execute(text(sql))

        columns = list(result.keys())
        rows = [dict(row._mapping) for row in result]

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows)
        }