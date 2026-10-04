from app.validation.sql_cleaner import clean_sql_response


llm_response = """```sql
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    SUM(o.total_amount) AS total_order_amount
FROM
    customers c
JOIN
    orders o ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name
ORDER BY
    total_order_amount DESC
LIMIT 5;
```"""


cleaned_sql = clean_sql_response(llm_response)

print("Cleaned SQL:")
print(cleaned_sql)