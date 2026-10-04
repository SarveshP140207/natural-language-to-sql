from app.rag.retriever import retrieve_schema_context


results = retrieve_schema_context(
    "Which category has the most products?",
    top_k=3
)

print("Retrieved:", len(results))
print()

for index, result in enumerate(results, start=1):
    print(
        f"--- Result {index} | "
        f"score={result['score']:.4f} | "
        f"table={result['table']} ---"
    )

    print(result["content"])
    print()
