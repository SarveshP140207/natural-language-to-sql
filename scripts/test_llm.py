from app.ai.llm import generate_response


response = generate_response(
    "Write one simple MySQL SELECT query to display all customers."
)

print("LLM response:")
print(response)