from decimal import Decimal
from datetime import date, datetime


def is_numeric(value):
    return isinstance(
        value,
        (int, float, Decimal)
    ) and not isinstance(value, bool)


def is_date_value(value):
    return isinstance(
        value,
        (date, datetime)
    )


def make_json_safe(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    return value


def is_identifier_column(column: str) -> bool:
    name = column.lower()

    return (
        name == "id"
        or name.endswith("_id")
        or name.endswith("id")
        or name.endswith("code")
        or name.endswith("number")
    )


def is_name_column(column: str) -> bool:
    name = column.lower()

    return (
        "name" in name
        or name in {
            "customer",
            "product",
            "category",
            "city",
            "state",
        }
    )


def is_measurement_column(column: str) -> bool:
    name = column.lower()

    measurement_terms = (
        "amount",
        "price",
        "quantity",
        "count",
        "total",
        "average",
        "avg",
        "sum",
        "revenue",
        "sales",
        "rating",
        "score",
        "value",
    )

    return any(
        term in name
        for term in measurement_terms
    )


def build_display_label(
    row: dict,
    columns: list[str],
    x_column: str
) -> str:
    if (
        "first_name" in columns
        and "last_name" in columns
    ):
        first_name = row.get("first_name")
        last_name = row.get("last_name")

        if first_name and last_name:
            return f"{first_name} {last_name}"

    return str(row.get(x_column, ""))


def build_chart_data(
    rows: list[dict],
    columns: list[str],
    x_column: str,
    y_column: str
) -> list[dict]:
    chart_data = []

    for row in rows:
        chart_data.append({
            "label": build_display_label(
                row,
                columns,
                x_column
            ),
            "value": make_json_safe(
                row.get(y_column)
            )
        })

    return chart_data


def analyze_visualization(
    question: str,
    result: dict
) -> dict:
    columns = result.get("columns", [])
    rows = result.get("rows", [])

    if not columns or not rows:
        return {
            "type": "table",
            "title": "Query Results",
            "x_column": None,
            "y_column": None,
            "data": []
        }

    sample_rows = rows[:20]

    numeric_columns = []
    categorical_columns = []
    date_columns = []

    for column in columns:
        values = [
            row.get(column)
            for row in sample_rows
            if row.get(column) is not None
        ]

        if not values:
            continue

        if all(is_numeric(value) for value in values):
            numeric_columns.append(column)

        elif all(is_date_value(value) for value in values):
            date_columns.append(column)

        else:
            categorical_columns.append(column)

    measurement_columns = [
        column
        for column in numeric_columns
        if not is_identifier_column(column)
    ]

    preferred_measurements = [
        column
        for column in measurement_columns
        if is_measurement_column(column)
    ]

    if preferred_measurements:
        measurement_columns = preferred_measurements

    if date_columns and measurement_columns:
        x_column = date_columns[0]
        y_column = measurement_columns[0]

        return {
            "type": "line",
            "title": question,
            "x_column": x_column,
            "y_column": y_column,
            "data": build_chart_data(
                rows,
                columns,
                x_column,
                y_column
            )
        }

    if categorical_columns and measurement_columns:
        name_columns = [
            column
            for column in categorical_columns
            if is_name_column(column)
        ]

        x_column = (
            name_columns[0]
            if name_columns
            else categorical_columns[0]
        )

        y_column = measurement_columns[0]

        return {
            "type": "bar",
            "title": question,
            "x_column": x_column,
            "y_column": y_column,
            "data": build_chart_data(
                rows,
                columns,
                x_column,
                y_column
            )
        }

    if len(rows) == 1 and len(measurement_columns) == 1:
        y_column = measurement_columns[0]

        return {
            "type": "kpi",
            "title": question,
            "x_column": None,
            "y_column": y_column,
            "data": [
                {
                    "value": make_json_safe(
                        rows[0].get(y_column)
                    )
                }
            ]
        }

    return {
        "type": "table",
        "title": question,
        "x_column": None,
        "y_column": None,
        "data": []
    }