from django.shortcuts import render


# Create your views here.


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import time

from rag.embeddings import create_query_embedding
from services.qdrant_service import search_similar_chunks, search_chunks_by_files
from rag.reranker import rerank_results
from rag.context_builder import build_context
from rag.generator import generate_answer


@api_view(["POST"])
def chat(request):

    question = request.data.get("question")

    if not question:
        return Response(
            {"error": "Question is required."},
            status=400
        )

    # 1. Embedding
    start = time.time()

    query_vector = create_query_embedding(question)

    print("Embedding time:", time.time() - start)

    # 2. Qdrant retrieval
    start = time.time()

    results = search_similar_chunks(query_vector)

    print("Qdrant time:", time.time() - start)

    # 3. First reranking
    start = time.time()

    first_reranked = rerank_results(
        question,
        results,
        top_k=3
    )

    print("First reranking time:", time.time() - start)

    # 4. Unique files
    files = set()

    for result in first_reranked:
        files.add(result["payload"]["file"])

    # 5. Retrieve file chunks
    start = time.time()

    candidate_chunks = search_chunks_by_files(
    query_vector,
    files,
    limit=15
    )

    print("File retrieval time:", time.time() - start)

    # 6. Second reranking
    start = time.time()

    final_results = rerank_results(
        question,
        candidate_chunks,
        top_k=5
    )

    print("Second reranking time:", time.time() - start)

    # 7. Context building
    start = time.time()

    context = build_context(final_results)

    print("Context building time:", time.time() - start)

    # 8. LLM
    start = time.time()

    answer = generate_answer(
        question,
        context
    )

    print("LLM time:", time.time() - start)

    print(f"Question: {question}")
    print(f"Answer: {answer}")

    return Response({
        "question": question,
        "answer": answer
    })