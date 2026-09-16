import re


def clean_text(text):
    # Remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # Convert Markdown links to visible text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove React documentation anchor syntax
    text = re.sub(r"\s*\{\/[^}]+\/\}", "", text)

# Remove "title:" prefix when it appears at the beginning
    text = re.sub(r"^title:\s*", "", text, flags=re.IGNORECASE)

    # Remove bold and italic Markdown markers
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()