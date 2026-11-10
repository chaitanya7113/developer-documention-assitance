
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

for result in results:
    payload = result.payload

    print("-" * 80)
    print("Chunk ID:", payload.get("chunk_id"))
    print("File:", payload.get("file"))
    print("Section:", payload.get("section"))
    print("Has Code:", payload.get("has_code"))
    print("Content:", payload.get("content"))
