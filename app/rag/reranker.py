from functools import lru_cache

from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=1)
def get_reranker():
    return CrossEncoder(MODEL_NAME)


def rerank_results(
    question: str,
    results: list[dict],
    top_k: int = 5
) -> list[dict]:
    if not results:
        return []

    pairs = [
        (question, result["content"])
        for result in results
    ]

    model = get_reranker()
    scores = model.predict(pairs)

    reranked = []

    for result, score in zip(results, scores):
        reranked.append({
            **result,
            "reranker_score": float(score)
        })

    reranked.sort(
        key=lambda item: item["reranker_score"],
        reverse=True
    )

    return reranked[:top_k]