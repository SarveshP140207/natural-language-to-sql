from app.database.executor import execute_read_only_query


sql = """
SELECT
    customer_id,
    first_name,
    last_name,
    city
FROM customers
ORDER BY customer_id
LIMIT 5
"""


try:
    result = execute_read_only_query(sql)

    print("Query executed successfully!\n")
    print("Columns:")
    print(result["columns"])

    print("\nRows:")

    for row in result["rows"]:
        print(row)

    print(f"\nTotal rows returned: {result['row_count']}")

except Exception as e:
    print("Query execution failed!")
    print(f"Error: {e}")