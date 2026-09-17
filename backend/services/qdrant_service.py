from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


client = QdrantClient(
    url="http://localhost:6333"
)

COLLECTION_NAME = "developer_docs"


def create_collection():
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

def upsert_chunks(chunks):
    points = []

    for chunk in chunks:
        points.append({
            "id": chunk["id"],
            "vector": chunk["embedding"],
            "payload": {
                "content": chunk["content"],
                **chunk["metadata"],
            },
        })

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )