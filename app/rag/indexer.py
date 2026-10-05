from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.database.models import DatabaseConnection
from app.rag.documents import generate_schema_documents
from app.rag.embeddings import get_embedding_model


QDRANT_PATH = "qdrant_data"
COLLECTION_PREFIX = "schema_knowledge"
VECTOR_SIZE = 384


def get_qdrant_client():
    return QdrantClient(path=QDRANT_PATH)


def get_collection_name(
    database_connection: DatabaseConnection | None = None,
) -> str:
    if database_connection is None:
        return COLLECTION_PREFIX

    return f"{COLLECTION_PREFIX}_{database_connection.connection_id}"


def create_collection(
    client,
    collection_name: str,
):
    existing_collections = [
        collection.name
        for collection in client.get_collections().collections
    ]

    if collection_name not in existing_collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )


def index_schema(
    database_connection: DatabaseConnection | None = None,
):
    documents = generate_schema_documents(
        database_connection,
    )

    embedding_model = get_embedding_model()
    client = get_qdrant_client()

    collection_name = get_collection_name(
        database_connection,
    )

    create_collection(
        client,
        collection_name,
    )

    texts = [
        document["content"]
        for document in documents
    ]

    embeddings = embedding_model.encode(texts)

    points = []

    for index, (document, embedding) in enumerate(
        zip(documents, embeddings)
    ):
        points.append(
            PointStruct(
                id=index,
                vector=embedding.tolist(),
                payload=document,
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points,
    )

    return len(points)


if __name__ == "__main__":
    count = index_schema()

    print(
        f"Indexed documents: {count}"
    )