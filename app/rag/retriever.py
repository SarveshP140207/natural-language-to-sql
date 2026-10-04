from app.rag.embeddings import get_embedding_model
from app.rag.indexer import (
    COLLECTION_NAME,
    get_qdrant_client,
)


def retrieve_schema_context(
    question: str,
    top_k: int = 5
):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    embedding_model = get_embedding_model()
    client = get_qdrant_client()

    query_embedding = embedding_model.encode(
        [question]
    )[0].tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
    )

    documents = []

    for result in results.points:
        documents.append({
            "score": result.score,
            "content": result.payload["content"],
            "type": result.payload["type"],
            "table": result.payload["table"],
        })

    return documents