from rank_bm25 import BM25Okapi

from app.database.models import DatabaseConnection
from app.rag.documents import generate_schema_documents
from app.rag.embeddings import get_embedding_model
from app.rag.indexer import (
    get_collection_name,
    get_qdrant_client,
)
from app.rag.reranker import rerank_results


def reciprocal_rank_fusion(
    ranked_lists,
    k=60,
):
    scores = {}

    for ranked_list in ranked_lists:
        for rank, document_id in enumerate(ranked_list, start=1):
            scores[document_id] = (
                scores.get(document_id, 0)
                + 1 / (k + rank)
            )

    return sorted(
        scores,
        key=scores.get,
        reverse=True,
    )


def retrieve_schema_context(
    question: str,
    top_k: int = 5,
    database_connection: DatabaseConnection | None = None,
):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    documents = generate_schema_documents(
        database_connection,
    )

    candidate_k = max(top_k * 3, 10)

    # -------------------------
    # 1. Semantic retrieval
    # -------------------------

    embedding_model = get_embedding_model()
    client = get_qdrant_client()

    query_embedding = embedding_model.encode(
        [question]
    )[0].tolist()

    collection_name = get_collection_name(
        database_connection,
    )

    vector_results = client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=candidate_k,
    )

    vector_ranked = [
        result.id
        for result in vector_results.points
    ]

    # -------------------------
    # 2. BM25 keyword retrieval
    # -------------------------

    tokenized_documents = [
        document["content"].lower().split()
        for document in documents
    ]

    bm25 = BM25Okapi(tokenized_documents)

    tokenized_query = question.lower().split()

    bm25_scores = bm25.get_scores(
        tokenized_query
    )

    bm25_ranked_indexes = sorted(
        range(len(bm25_scores)),
        key=lambda index: bm25_scores[index],
        reverse=True,
    )[:candidate_k]

    bm25_ranked = [
        index
        for index in bm25_ranked_indexes
    ]

    # -------------------------
    # 3. Reciprocal Rank Fusion
    # -------------------------

    fused_indexes = reciprocal_rank_fusion(
        [
            vector_ranked,
            bm25_ranked,
        ]
    )

    # -------------------------
    # 4. Build fused documents
    # -------------------------

    fused_results = []

    for document_id in fused_indexes[:candidate_k]:
        if not isinstance(document_id, int):
            continue

        if document_id >= len(documents):
            continue

        document = documents[document_id]

        fused_results.append({
            "score": 0,
            "content": document["content"],
            "type": document["type"],
            "table": document["table"],
        })

    # -------------------------
    # 5. CrossEncoder reranking
    # -------------------------

    reranked_results = rerank_results(
        question,
        fused_results,
        top_k=top_k,
    )

    return reranked_results