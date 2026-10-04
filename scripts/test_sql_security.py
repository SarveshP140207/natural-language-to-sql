from app.validation.sql_parser import parse_sql


test_queries = {
    "Safe SELECT": """
        SELECT customer_id, first_name
        FROM customers
        LIMIT 5;
    """,

    "Safe JOIN": """
        SELECT c.first_name, o.total_amount
        FROM customers c
        JOIN orders o
        ON c.customer_id = o.customer_id
        LIMIT 5;
    """,

    "Blocked DELETE": """
        DELETE FROM customers
        WHERE customer_id = 1;
    """,

    "Blocked UPDATE": """
        UPDATE customers
        SET first_name = 'Hacked'
        WHERE customer_id = 1;
    """,

    "Blocked DROP": """
        DROP TABLE customers;
    """,

    "Blocked INSERT": """
        INSERT INTO customers
        (first_name, last_name, email, registration_date)
        VALUES ('Test', 'User', 'test@example.com', '2026-10-04');
    """,

    "Blocked Multiple Statements": """
        SELECT * FROM customers;
        DELETE FROM customers;
    """
}


for name, sql in test_queries.items():
    print(f"\nTesting: {name}")

    try:
        expression = parse_sql(sql)
        print("PASSED - Query allowed")
        print("Parsed as:", type(expression).__name__)

    except ValueError as error:
        print("BLOCKED")
        print("Reason:", error)