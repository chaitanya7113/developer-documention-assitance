from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from uuid import uuid5, NAMESPACE_DNS
from qdrant_client.models import Filter, FieldCondition, MatchValue

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
        point_id = str(uuid5(NAMESPACE_DNS, chunk["id"]))

        points.append({
            "id": point_id,
            "vector": chunk["embedding"],
            "payload": {
                "chunk_id": chunk["id"],
                "content": chunk["content"],
                **chunk["metadata"],
            },
        })

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

def search_with_filter(query_vector, file_name): 
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="file",
                    match=MatchValue(value=file_name)
                )
            ]
        ),
        limit=5,
    )

    return results.points