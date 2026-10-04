from app.ai.sql_generator import generate_sql


question = "Find the top 5 customers by total order amount."

sql = generate_sql(question)

print("Generated SQL:")
print(sql)