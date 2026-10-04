from app.validation.query_limits import apply_query_limit


tests = [
    "SELECT * FROM customers",
    "SELECT customer_id, first_name FROM customers LIMIT 5",
    "SELECT * FROM products ORDER BY price DESC",
    "SELECT * FROM customers LIMIT 100000"
]

for sql in tests:
    print("\nOriginal SQL:")
    print(sql)

    try:
        limited_sql = apply_query_limit(sql)
        print("Limited SQL:")
        print(limited_sql)
    except Exception as e:
        print("ERROR:", e)