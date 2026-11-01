
import re

from rest_framework.decorators import api_view
from rest_framework.response import Response

from rag.embeddings import create_query_embedding

from services.qdrant_service import (
    search_similar_chunks,
    search_chunks_by_function,
)

from rag.reranker import rerank_results
from rag.context_builder import build_context
from rag.generator import generate_answer


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

    # 2. Semantic retrieval
    semantic_results = search_similar_chunks(
    query_vector,
    metadata_filters=metadata_filters,
)

   
    # 3. Function-based retrieval for code-style identifiers
    function_results = []

    for function_name in extract_function_candidates(question):
        function_results.extend(
            search_chunks_by_function(
                query_vector,
                function_name,
                limit=10,
                metadata_filters=metadata_filters,
            )
        )


    # 4. Merge results and remove duplicates
    candidate_results = merge_results(
        semantic_results,
        function_results,
    )

    # 5. Rerank combined results
    final_results = rerank_results(
        question,
        candidate_results,
        top_k=5,
    )

    print("Question:", question)
    print("Candidates before threshold:")

    for result in final_results:
        print(
            "Score:", result["score"],
            "File:", result["payload"].get("file"),
            "Function calls:", result["payload"].get("function_calls"),
            "Content:", result["payload"].get("content", "")[:200],
        )

    # 6. Filter low-scoring results
    final_results = [
        result
        for result in final_results
        if result["score"] >= RERANKER_THRESHOLD
    ]

    print("-"*100)
    print("Final results after threshold:")
    print("THRESHOLD:", RERANKER_THRESHOLD)
    print("-"*100)
    for result in final_results:
        print(
            "Score:", result["score"],
            "File:", result["payload"].get("file"),
            "Function calls:", result["payload"].get("function_calls"),
            "Content:", result["payload"].get("content", "")[:200],
        )

    # 7. If no results meet the threshold, return a default response
    if not final_results:
        return Response({
            "question": question,
            "answer": (
                "I couldn't find the answer in the provided documentation."
            ),
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
    })
