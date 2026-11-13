import re

from rag.embeddings import create_query_embedding
from rag.query_intent import detect_query_intent
from rag.reranker import model, rerank_results, inspect_reranker_input
from services.qdrant_service import (
    search_similar_chunks,
    search_code_chunks,
    search_chunks_by_function,
)


QUESTION = "Show me a useEffect cleanup function example."

TEST_CASES = [
    "Show me a useEffect cleanup function example.",
    "How do I clean up an event listener in React?",
    "Why does React run the useEffect cleanup function before unmounting?",
    "Show me an example of useState in React.",
    "How do I fetch data using useEffect in React?",
]

# Manually verified target documentation sections for this benchmark.
# Update a label if the exact section heading in your Qdrant payload differs.
GROUND_TRUTH = {
    "Show me a useEffect cleanup function example.": [
        "Step 3: Add cleanup if needed",
    ],

    "How do I clean up an event listener in React?": [
        "Adding event listeners without a wrapper element",
        "`removeEventListener(type, listener, options?)`",
        "Subscribing to events",
    ],

    "Why does React run the useEffect cleanup function before unmounting?": [
        "My cleanup logic runs even though my component didn't unmount",
    ],

    "Show me an example of useState in React.": [
        "Anatomy of `useState`",
    ],

    "How do I fetch data using useEffect in React?": [
        "Fetching data with Effects",
        "Fetching data with `useEffect`",
    ],
}

FORMATS = ["content_only", "section_content", "full_metadata", "code_aware"]


def extract_function_candidates(question):
    # Finds camelCase/PascalCase identifiers such as useEffect and useState.
    pattern = r"\b[A-Za-z_$][A-Za-z0-9_$]*[A-Z][A-Za-z0-9_$]*\b"
    return list(dict.fromkeys(re.findall(pattern, question)))



def get_chunk_ids(results):
    return {
        (result.payload or {}).get("chunk_id")
        for result in results
        if (result.payload or {}).get("chunk_id")
    }


def print_results(branch_name, results):
    print("\n" + "=" * 70)
    print(f"{branch_name} RESULTS: {len(results)}")
    print("=" * 70)
    for rank, result in enumerate(results, start=1):
        payload = result.payload or {}
        print(f"\nResult: {rank}")
        print("Qdrant ID:", result.id)
        print("Chunk ID:", payload.get("chunk_id"))
        print("File:", payload.get("file"))
        print("Section:", payload.get("section"))
        print("Has Code:", payload.get("has_code"))
        print("Function Names:", payload.get("function_names"))
        print("Function Calls:", payload.get("function_calls"))
        print("Qdrant Score:", round(float(result.score), 4))
        print("Content Preview:", (payload.get("content") or "")[:250])


def print_reranked_results(title, results):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    for rank, item in enumerate(results, start=1):
        payload = item["payload"] or {}
        print(f"\nRank: {rank}")
        print("File:", payload.get("file"))
        print("Section:", payload.get("section"))
        print("Chunk ID:", payload.get("chunk_id"))
        print("Reranker Score:", round(item["score"], 4))
        print("Qdrant Score:", item["qdrant_score"])
        print("Has Code:", payload.get("has_code"))


def inspect_chunk_payload(results):
    for result in results:
        payload = result.payload or {}
        section = payload.get("section", "")
        if "cleanup" in section.lower():
            print("\n" + "=" * 60)
            print("SECTION:", section)
            print("PAYLOAD KEYS:", list(payload.keys()))
            for key, value in payload.items():
                print(f"\n{key}:")
                print(str(value)[:1000])


def compare_reranker_formats(question, results):
    """Print the original three-format comparison without calculating metrics."""
    pairs = {"content_only": [], "section_content": [], "full_metadata": []}
    for result in results:
        payload = result.payload or {}
        content = payload.get("content", "")
        section = payload.get("section", "")
        file_name = payload.get("file", "")
        pairs["content_only"].append((question, content))
        pairs["section_content"].append((question, f"{section}\n\n{content}"))
        pairs["full_metadata"].append((
            question,
            f"Documentation file: {file_name}\n\n"
            f"Documentation section: {section}\n\n"
            f"Documentation content:\n{content}",
        ))

    for mode, model_pairs in pairs.items():
        scores = model.predict(model_pairs)
        ranked = sorted(zip(results, scores), key=lambda item: float(item[1]), reverse=True)
        print("\n" + "=" * 60)
        print("RERANKER FORMAT:", mode)
        print("=" * 60)
        for rank, (result, score) in enumerate(ranked[:5], start=1):
            payload = result.payload or {}
            print(f"{rank}. {payload.get('section')} | Score: {float(score):.4f} | Has Code: {payload.get('has_code')}")


def compare_code_aware_format(question, results):
    pairs = []
    for result in results:
        payload = result.payload or {}
        functions = payload.get("function_names") or []
        document = (
            f"Documentation section: {payload.get('section', '')}\n\n"
            f"Contains code: {payload.get('has_code', False)}\n"
            f"Programming language: {payload.get('language') or ''}\n"
            f"Function names: {', '.join(functions)}\n\n"
            f"Documentation content:\n{payload.get('content', '')}"
        )
        pairs.append((question, document))

    scores = model.predict(pairs)
    ranked = sorted(zip(results, scores), key=lambda item: float(item[1]), reverse=True)
    print("\n" + "=" * 60)
    print("RERANKER FORMAT: code_aware")
    print("=" * 60)
    for rank, (result, score) in enumerate(ranked[:5], start=1):
        payload = result.payload or {}
        print(f"{rank}. {payload.get('section')} | Score: {float(score):.4f} | Has Code: {payload.get('has_code')} | Language: {payload.get('language')}")


def calculate_metrics(ranked_results, relevant_sections, k=3):
    """ranked_results is a list of (Qdrant result, CrossEncoder score) pairs."""
    relevant_sections = set(relevant_sections)
    first_relevant_rank = None

    for rank, (result, _score) in enumerate(ranked_results, start=1):
        payload = result.payload or {}
        if payload.get("section") in relevant_sections:
            first_relevant_rank = rank
            break

    return {
        "top_1": int(first_relevant_rank == 1),
        "top_k": int(first_relevant_rank is not None and first_relevant_rank <= k),
        "mrr": 1 / first_relevant_rank if first_relevant_rank else 0.0,
        "first_relevant_rank": first_relevant_rank,
    }


def print_metric_summary(metrics_summary):
    print("\n" + "=" * 94)
    print("FINAL AGGREGATE METRICS")
    print("=" * 94)
    print(
        f"{'Format':<20} {'Top-1':>9} {'Top-3':>9} {'MRR@5':>10} "
        f"{'Code Top-1':>13} {'Code Top-3':>13}"
    )
    print("-" * 94)

    for format_name in FORMATS:
        all_metrics = metrics_summary[format_name]["all"]
        code_metrics = metrics_summary[format_name]["code"]
        if not all_metrics:
            continue

        top1 = sum(item["top_1"] for item in all_metrics) / len(all_metrics)
        top3 = sum(item["top_k"] for item in all_metrics) / len(all_metrics)
        mrr = sum(item["mrr"] for item in all_metrics) / len(all_metrics)

        code_top1 = (
            sum(item["top_1"] for item in code_metrics) / len(code_metrics)
            if code_metrics else 0.0
        )
        code_top3 = (
            sum(item["top_k"] for item in code_metrics) / len(code_metrics)
            if code_metrics else 0.0
        )

        print(
            f"{format_name:<20} {top1:>8.1%} {top3:>8.1%} {mrr:>10.3f} "
            f"{code_top1:>12.1%} {code_top3:>12.1%}"
        )

    print("\nTop-1/Top-3/MRR@5 use all test queries.")
    print("Code Top-1/Code Top-3 use only code_example or both intent queries.")
    print("Metrics are based on the manually defined GROUND_TRUTH section labels.")


def evaluate_multiple_queries(test_cases):
    metrics_summary = {
        name: {"all": [], "code": []}
        for name in FORMATS
    }

    for question in test_cases:
        print("\n" + "=" * 78)
        print("QUESTION:", question)
        print("=" * 78)

        intent = detect_query_intent(question)
        function_names = extract_function_candidates(question)
        include_code = intent in ("code_example", "both")

        print("Intent:", intent)
        print("Function Names:", function_names)
        print("Include Code:", include_code)

        query_vector = create_query_embedding(question)
        metadata_filters = {}

        semantic_results = search_similar_chunks(
            query_vector=query_vector,
            metadata_filters=metadata_filters,
        )

        code_results = []
        if include_code:
            code_results = search_code_chunks(
                query_vector=query_vector,
                limit=20,
                metadata_filters=metadata_filters,
            )

        function_results = []
        for function_name in function_names:
            function_results.extend(
                search_chunks_by_function(
                    query_vector=query_vector,
                    function_name=function_name,
                    limit=20,
                    metadata_filters=metadata_filters,
                )
            )

        # Merge all retrieval branches and deduplicate by chunk_id.
        all_results = semantic_results + code_results + function_results
        unique_results = []
        seen_chunk_ids = set()

        for result in all_results:
            payload = result.payload or {}
            chunk_id = payload.get("chunk_id")
            if chunk_id and chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(chunk_id)
                unique_results.append(result)

        print("Semantic candidates:", len(semantic_results))
        print("Code candidates:", len(code_results))
        print("Function candidates:", len(function_results))
        print("Unique candidates:", len(unique_results))

        if not unique_results:
            print("No candidates retrieved for this query.")
            continue

        pairs_by_format = {name: [] for name in FORMATS}

        for result in unique_results:
            payload = result.payload or {}
            content = payload.get("content", "")
            section = payload.get("section", "")
            file_name = payload.get("file", "")
            has_code = payload.get("has_code", False)
            language = payload.get("language") or ""
            functions = payload.get("function_names") or []

            pairs_by_format["content_only"].append((question, content))
            pairs_by_format["section_content"].append(
                (question, f"{section}\n\n{content}")
            )
            pairs_by_format["full_metadata"].append(
                (
                    question,
                    f"Documentation file: {file_name}\n"
                    f"Documentation section: {section}\n"
                    f"Documentation content:\n{content}",
                )
            )
            pairs_by_format["code_aware"].append(
                (
                    question,
                    f"Documentation section: {section}\n"
                    f"Contains code: {has_code}\n"
                    f"Programming language: {language}\n"
                    f"Function names: {', '.join(functions)}\n"
                    f"Documentation content:\n{content}",
                )
            )

        relevant_sections = GROUND_TRUTH.get(question, [])
        if not relevant_sections:
            print("WARNING: No GROUND_TRUTH labels configured for this query.")

        for format_name in FORMATS:
            scores = model.predict(pairs_by_format[format_name])
            ranked = sorted(
                zip(unique_results, scores),
                key=lambda item: float(item[1]),
                reverse=True,
            )

            # Metrics are calculated on the same Top-5 cutoff used in the experiment.
            query_metrics = calculate_metrics(ranked[:5], relevant_sections, k=3)
            metrics_summary[format_name]["all"].append(query_metrics)
            if include_code:
                metrics_summary[format_name]["code"].append(query_metrics)

            print("\n" + "-" * 68)
            print("FORMAT:", format_name)
            print(
                f"Metrics: Top-1={query_metrics['top_1']} | "
                f"Top-3={query_metrics['top_k']} | "
                f"MRR@5={query_metrics['mrr']:.3f} | "
                f"First relevant rank={query_metrics['first_relevant_rank']}"
            )

            for rank, (result, score) in enumerate(ranked[:5], start=1):
                payload = result.payload or {}
                print(
                    f"{rank}. {payload.get('section')} "
                    f"| Score: {float(score):.4f} "
                    f"| Has Code: {payload.get('has_code')} "
                    f"| Chunk ID: {payload.get('chunk_id')}"
                )

    print_metric_summary(metrics_summary)
    return metrics_summary


def debug_retrieval():
    """Run the detailed multi-query benchmark for the current test set."""
    return evaluate_multiple_queries(TEST_CASES)

def test_production_reranker():

    question = "Show me a useEffect cleanup function example."

    query_vector = create_query_embedding(question)

    semantic_results = search_similar_chunks(
        query_vector=query_vector,
        metadata_filters={}
    )

    code_results = search_code_chunks(
        query_vector=query_vector,
        limit=20,
        metadata_filters={}
    )

    combined = semantic_results + code_results

    unique_results = []
    seen = set()

    for result in combined:
        payload = result.payload or {}
        chunk_id = payload.get("chunk_id")

        if chunk_id and chunk_id not in seen:
            seen.add(chunk_id)
            unique_results.append(result)

    print("\nPRODUCTION RERANKER TEST")

    ranked = rerank_results(
        question=question,
        results=unique_results,
        top_k=5
    )

    print_reranked_results(
        "PRODUCTION CONTENT-ONLY RERANKER",
        ranked
    )


if __name__ == "__main__":
    test_production_reranker()
