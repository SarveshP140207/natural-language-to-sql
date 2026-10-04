from ollama import chat

response = chat(
    model="qwen2.5-coder:7b",
    messages=[
        {
            "role": "user",
            "content": "Write one simple MySQL SELECT query to display all customers."
        }
    ]
)

print("Ollama response:")
print(response.message.content)