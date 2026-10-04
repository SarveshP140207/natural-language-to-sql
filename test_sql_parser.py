from app.validation.sql_parser import validate_sql


test_queries = [
    "SELECT * FROM customers",
    "SELECT customer_id, first_name FROM customers WHERE city = 'Chennai'",
    "SELECT c.first_name, o.total_amount FROM customers c JOIN orders o ON c.customer_id = o.customer_id",
    "DROP TABLE customers",
    "DELETE FROM customers",
    "UPDATE customers SET city = 'Chennai'",
    "SELECT * FROM customers; SELECT * FROM orders"
]


for query in test_queries:
    print("\nSQL:", query)

    try:
        validated_sql = validate_sql(query)
        print("ALLOWED")
        print("Validated:", validated_sql)

    except ValueError as e:
        print("BLOCKED")
        print("Reason:", e)