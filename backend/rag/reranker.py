from sentence_transformers import CrossEncoder


model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank_results(question, results, top_k=3):

    pairs = []

    for result in results:
        content = result.payload["content"]
        pairs.append((question, content))

    scores = model.predict(pairs)

    reranked = []

    for result, score in zip(results, scores):
        reranked.append({
            "score": float(score),
            "qdrant_score": getattr(result, "score", None),
            "payload": result.payload,
        })

    reranked.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return reranked[:top_k]