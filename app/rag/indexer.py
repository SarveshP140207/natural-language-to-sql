from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.rag.documents import generate_schema_documents
from app.rag.embeddings import get_embedding_model


QDRANT_PATH = "qdrant_data"
COLLECTION_NAME = "schema_knowledge"
VECTOR_SIZE = 384


def get_qdrant_client():
    return QdrantClient(path=QDRANT_PATH)


def create_collection(client):
    existing_collections = [
        collection.name
        for collection in client.get_collections().collections
    ]

    if COLLECTION_NAME not in existing_collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )


def index_schema():
    documents = generate_schema_documents()
    embedding_model = get_embedding_model()
    client = get_qdrant_client()

    create_collection(client)

    texts = [document["content"] for document in documents]
    embeddings = embedding_model.encode(texts)

    points = []

    for index, (document, embedding) in enumerate(
        zip(documents, embeddings)
    ):
        points.append(
            PointStruct(
                id=index,
                vector=embedding.tolist(),
                payload=document
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return len(points)


if __name__ == "__main__":
    count = index_schema()
    print(f"Indexed documents: {count}")