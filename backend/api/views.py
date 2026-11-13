
import re

from rest_framework.decorators import api_view
from rest_framework.response import Response

from rag.embeddings import create_query_embedding

from services.qdrant_service import search_combined_chunks

from rag.reranker import rerank_results
from rag.context_builder import build_context
from rag.generator import generate_answer
from rag.citation_builder import build_citations
from rag.query_intent import detect_query_intent

RERANKER_THRESHOLD = 1.0


def extract_function_candidates(question):
    """Extract code-style identifiers such as createRoot or hydrateRoot."""
    pattern = r"\b[A-Za-z_$][A-Za-z0-9_$]*[A-Z][A-Za-z0-9_$]*\b"
    return list(dict.fromkeys(re.findall(pattern, question)))


def merge_results(*result_groups):
    """Merge Qdrant points and remove duplicate chunks."""
    merged = []
    seen = set()

    for group in result_groups:
        for point in group:
            payload = point.payload
            key = payload.get("chunk_id")

            if not key:
                key = (
                    payload.get("file", ""),
                    payload.get("content", ""),
                )

            if key in seen:
                continue

            seen.add(key)
            merged.append(point)

    return merged


@api_view(["POST"])
def chat(request):
    question = request.data.get("question")
    

    if not isinstance(question, str) or not question.strip():
        return Response(
            {"error": "Question is required."},
            status=400,
        )

    question = question.strip()
    # 1. Detect query intent
    query_intent = detect_query_intent(question)

    print("Question:", question)
    print("Detected Intent:", query_intent)

    
    allowed_filters = {
        "framework",
        "version",
        "documentation_source",
        "source_commit",
        "snapshot_date",
    }

    requested_filters = request.data.get("filters") or {}

    if not isinstance(requested_filters, dict):
        return Response(
            {"error": "Filters must be a JSON object."},
            status=400,
        )

    invalid_filters = set(requested_filters) - allowed_filters

    if invalid_filters:
        return Response(
            {
                "error": "Unsupported metadata filters.",
                "invalid_filters": sorted(invalid_filters),
            },
            status=400,
        )

    metadata_filters = {
        key: value
        for key, value in requested_filters.items()
        if value is not None and value != ""
    }


    # 1. Create query embedding
    query_vector = create_query_embedding(question)

        # 2. Extract function candidates
    function_names = extract_function_candidates(question)

    # 3. Decide whether code retrieval is required
    include_code = query_intent in [
        "code_example",
        "both",
    ]

    # 4. Combined retrieval
    candidate_results = search_combined_chunks(
        query_vector=query_vector,
        function_names=function_names,
        include_code=include_code,
        limit=20,
        metadata_filters=metadata_filters,
    )

    print("Function Names:", function_names)
    print("Include Code:", include_code)
    print("Total Retrieved Chunks:", len(candidate_results))

    # 5. Reranking
    final_results = rerank_results(
    question=question,
    results=candidate_results,
    top_k=5,
    prefer_code=include_code,
    function_names=function_names,
    )

    print("\n--- RERANKED RESULTS ---")

    for index, result in enumerate(final_results, start=1):
        payload = result["payload"]

        print(f"\nRank: {index}")
        print(f"File: {payload.get('file')}")
        print(f"Section: {payload.get('section')}")
        print(f"Has Code: {payload.get('has_code')}")
        print(f"Final Score: {result.get('score')}")
        print(f"Cross Encoder Score: {result.get('cross_encoder_score')}")

    # 6. Filter low-scoring results
    final_results = [
        result
        for result in final_results
        if result["score"] >= RERANKER_THRESHOLD
    ]

    citations = build_citations(final_results)

   

    # 7. If no results meet the threshold, return a default response
    if not final_results:
        return Response({
            "question": question,
            "answer": (
                "I couldn't find the answer in the provided documentation."
            ),
            "citations": [],
        })

    # 7. Build context
    context = build_context(final_results)

    print("CONTEXT LENGTH:", len(context))
    print("CONTEXT PREVIEW:", context[:1500])

    # 8. Generate answer
    answer = generate_answer(question, context)

   


    print("GENERATED ANSWER:", repr(answer))

    return Response({
        "question": question,
        "answer": answer,
        "citations": citations,
    })
