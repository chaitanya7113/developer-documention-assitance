def build_context(results):
    context_parts = []

    for result in results:
        payload = result["payload"]

        context_parts.append(
            f"File: {payload['file']}\n"
            f"Section: {payload['section']}\n"
            f"Content:\n{payload['content']}"
        )

    return "\n\n---\n\n".join(context_parts)