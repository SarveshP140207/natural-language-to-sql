from app.services.query_service import process_query


question = "Find the top 5 customers by total order amount."

response = process_query(question)

print("Question:")
print(response["question"])

print("\nGenerated SQL:")
print(response["sql"])

print("\nQuery Result:")
print(response["result"])

print("\nRows:")
for row in response["result"]["rows"]:
    print(row)