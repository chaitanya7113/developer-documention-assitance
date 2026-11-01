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


def build_metadata_filter(metadata_filters=None):
    """Build an optional Qdrant filter from metadata fields."""
    if not metadata_filters:
        return None

    conditions = [
        FieldCondition(
            key=key,
            match=MatchValue(value=value),
        )
        for key, value in metadata_filters.items()
        if value is not None and value != ""
    ]

    if not conditions:
        return None

    return Filter(must=conditions)


def search_similar_chunks(query_vector, metadata_filters=None):
    query_filter = build_metadata_filter(metadata_filters)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        limit=20,
    )


    for point in results.points:
        print({
            "file": point.payload.get("file"),
            "framework": point.payload.get("framework"),
            "documentation_source": point.payload.get("documentation_source"),
            "source_commit": point.payload.get("source_commit"),
            "version": point.payload.get("version"),
        })

    return results.points


# def search_with_filter(query_vector, file_name): 
#     results = client.query_points(
#         collection_name=COLLECTION_NAME,
#         query=query_vector,
#         query_filter=Filter(
#             must=[
#                 FieldCondition(
#                     key="file",
#                     match=MatchValue(value=file_name)
#                 )
#             ]
#         ),
#         limit=5,
#     )

#     return results.points



#temp function for debugging
# def get_all_chunks():
#     results = client.scroll(
#         collection_name=COLLECTION_NAME,
#         limit=10,
#         with_payload=True,
#         with_vectors=False,
#     )

#     return results[0]

def get_chunks_by_section(file_name, section_name):

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="file",
                    match=MatchValue(value=file_name)
                ),
                FieldCondition(
                    key="section",
                    match=MatchValue(value=section_name)
                ),
            ]
        ),
        limit=20,
        with_payload=True,
        with_vectors=False,
    )

    return results[0]

def get_chunks_by_file(file_name):
    results = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="file",
                    match=MatchValue(value=file_name)
                )
            ]
        ),
        limit=100,
        with_payload=True,
        with_vectors=False,
    )

    return results[0]

def search_chunks_by_files(query_vector, file_names, limit=15):
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            should=[
                FieldCondition(
                    key="file",
                    match=MatchValue(value=file_name)
                )
                for file_name in file_names
            ]
        ),
        limit=limit,
    )

    return results.points




from qdrant_client.models import Filter, FieldCondition, MatchValue





def search_chunks_by_function(
    query_vector,
    function_name,
    limit=10,
    metadata_filters=None,
):
    metadata_filter = build_metadata_filter(metadata_filters)

    metadata_conditions = (
        metadata_filter.must
        if metadata_filter is not None
        else []
    )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=metadata_conditions,
            should=[
                FieldCondition(
                    key="function_names",
                    match=MatchValue(value=function_name),
                ),
                FieldCondition(
                    key="function_calls",
                    match=MatchValue(value=function_name),
                ),
            ],
        ),
        limit=limit,
    )

    return results.points
