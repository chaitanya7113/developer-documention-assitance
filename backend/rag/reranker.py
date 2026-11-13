
from sentence_transformers import CrossEncoder


model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def build_reranker_document(payload):
    """
    Include documentation metadata with chunk content
    before sending it to the CrossEncoder.
    """

    # parts = []

    # file_name = payload.get("file")
    # section = payload.get("section")
    # content = payload.get("content", "")

    # if file_name:
    #     parts.append(f"Documentation file: {file_name}")

    # if section:
    #     parts.append(f"Documentation section: {section}")

    # parts.append(f"Documentation content:\n{content}")

    # return "\n\n".join(parts)

    content = payload.get("content","")
    return content

def inspect_reranker_input(question, payload):
    document = build_reranker_document(payload)

    encoded = model.tokenizer(
        question,
        document,
        truncation=True,
        max_length=model.max_length,
    )

    full_encoded = model.tokenizer(
        question,
        document,
        truncation=False,
    )

    print("\n" + "=" * 60)
    print("RERANKER TOKEN INSPECTION")
    print("=" * 60)

    print("Section:", payload.get("section"))
    print("Character Length:", len(document))
    print("Model Max Length:", model.max_length)
    print("Original Token Count:", len(full_encoded["input_ids"]))
    print("Tokens After Truncation:", len(encoded["input_ids"]))

    print("=" * 60)

    
def rerank_results(question, results, top_k=3, prefer_code=False, function_names=None):

    pairs = []

    for result in results:
        payload = result.payload or {}

        document_text = build_reranker_document(payload)

        pairs.append((question, document_text))

    if not pairs:
        return []

    scores = model.predict(pairs)

    reranked = []

    for result, score in zip(results, scores):

        reranked.append({
        "score": float(score),
        "cross_encoder_score": float(score),
        "qdrant_score": getattr(result, "score", None),
        "payload": result.payload,
        })

    reranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return reranked[:top_k]
