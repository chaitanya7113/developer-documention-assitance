from rag.embeddings import create_query_embedding
from services.qdrant_service import search_combined_chunks

question = "Show me a useState code example in React"

query_vector = create_query_embedding(question)

results = search_combined_chunks(
    query_vector=query_vector,
    function_name="useState",
    limit=20,
)

print("Total unique results:", len(results))

chunk_ids = [
    result.payload.get("chunk_id")
    for result in results
]

print("Unique chunk IDs:", len(set(chunk_ids)))
print("Duplicate chunks:", len(chunk_ids) - len(set(chunk_ids)))

print("\nTop 10 retrieved chunks:")

for i, result in enumerate(results[:10], start=1):
    payload = result.payload

    print(f"\nRank: {i}")
    print("File:", payload.get("file"))
    print("Section:", payload.get("section"))
    print("Has Code:", payload.get("has_code"))
    print("Function Names:", payload.get("function_names"))
    print("Function Calls:", payload.get("function_calls"))