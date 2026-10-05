SQL_EXAMPLES = [
    {
        "example_id": "sql_001",
        "question": "How many customers are there?",
        "sql": """
SELECT COUNT(*) AS customer_count
FROM customers;
""".strip(),
        "tables": ["customers"],
        "description": "Count the total number of customers."
    },
    {
        "example_id": "sql_002",
        "question": "Which category has the most products?",
        "sql": """
SELECT
    c.category_name,
    COUNT(p.product_id) AS product_count
FROM categories c
JOIN products p
    ON c.category_id = p.category_id
GROUP BY c.category_id, c.category_name
ORDER BY product_count DESC
LIMIT 1;
""".strip(),
        "tables": ["categories", "products"],
        "description": "Find the category containing the most products."
    },
    {
        "example_id": "sql_003",
        "question": "Show the top 5 customers by total spending.",
        "sql": """
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    SUM(o.total_amount) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
WHERE o.status <> 'Cancelled'
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spending DESC
LIMIT 5;
""".strip(),
        "tables": ["customers", "orders"],
        "description": "Rank customers by spending while excluding cancelled orders."
    },
    {
        "example_id": "sql_004",
        "question": "What is the average order value?",
        "sql": """
SELECT AVG(total_amount) AS average_order_value
FROM orders
WHERE status <> 'Cancelled';
""".strip(),
        "tables": ["orders"],
        "description": "Calculate the average value of non-cancelled orders."
    },
    {
        "example_id": "sql_005",
        "question": "Which products have an average rating above 4?",
        "sql": """
SELECT
    p.product_id,
    p.product_name,
    AVG(r.rating) AS average_rating
FROM products p
JOIN reviews r
    ON p.product_id = r.product_id
GROUP BY p.product_id, p.product_name
HAVING AVG(r.rating) > 4
ORDER BY average_rating DESC;
""".strip(),
        "tables": ["products", "reviews"],
        "description": "Find products whose average customer rating is above 4."
    },
    {
        "example_id": "sql_006",
        "question": "What is the total revenue excluding cancelled orders?",
        "sql": """
SELECT SUM(total_amount) AS total_revenue
FROM orders
WHERE status <> 'Cancelled';
""".strip(),
        "tables": ["orders"],
        "description": "Calculate revenue while excluding cancelled orders."
    },
]