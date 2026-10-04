from app.validation.schema_validator import validate_tables_and_columns


tests = [
    {
        "name": "Valid customers table",
        "tables": {"customers"},
        "columns": {
            "customers": {"customer_id", "first_name", "email"}
        }
    },
    {
        "name": "Valid products table",
        "tables": {"products"},
        "columns": {
            "products": {"product_id", "product_name", "price"}
        }
    },
    {
        "name": "Invalid table",
        "tables": {"employees"},
        "columns": {
            "employees": {"employee_id"}
        }
    },
    {
        "name": "Invalid column",
        "tables": {"customers"},
        "columns": {
            "customers": {"customer_id", "customer_name"}
        }
    }
]


for test in tests:
    print(f"\nTest: {test['name']}")

    try:
        validate_tables_and_columns(
            test["tables"],
            test["columns"]
        )

        print("ALLOWED")

    except ValueError as e:
        print("BLOCKED")
        print("Reason:", e)