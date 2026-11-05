from services.qdrant_service import client, COLLECTION_NAME

results = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=10,
    with_payload=True,
    with_vectors=False,
)

points, next_offset = results

for point in points:
    payload = point.payload

    print({
        "chunk_id": payload.get("chunk_id"),
        "file": payload.get("file"),
        "documentation_url": payload.get("documentation_url"),
        "section": payload.get("section"),
    })