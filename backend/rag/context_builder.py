
import tiktoken


MODEL_NAME = "gpt-4o-mini"
DEFAULT_CONTEXT_TOKEN_BUDGET = 6000

encoding = tiktoken.encoding_for_model(MODEL_NAME)


def count_tokens(text):
    return len(encoding.encode(text))


def build_context(
    results,
    max_tokens=DEFAULT_CONTEXT_TOKEN_BUDGET,
):
    context_parts = []
    used_tokens = 0

    for result in results:
        payload = result.get("payload", {})

        content = payload.get("content", "")
        if not isinstance(content, str) or not content.strip():
            continue

        file_name = payload.get("file", "Unknown file")
        section = payload.get("section", "Unknown section")

        chunk_text = (
            f"File: {file_name}\n"
            f"Section: {section}\n"
            f"Content:\n{content}"
        )

        separator = "\n\n---\n\n" if context_parts else ""
        required_tokens = count_tokens(separator + chunk_text)

        # Keep the first ranked chunk even if it exceeds the budget.
        if not context_parts and required_tokens > max_tokens:
            context_parts.append(chunk_text)
            used_tokens += required_tokens
            continue

        # Skip this chunk, but consider later, smaller chunks.
        if used_tokens + required_tokens > max_tokens:
            continue

        context_parts.append(chunk_text)
        used_tokens += required_tokens

    return "\n\n---\n\n".join(context_parts)
