from pathlib import Path


def load_markdown_files(source_dir):
    source_path = Path(source_dir)

    if not source_path.exists():
        raise FileNotFoundError(
            f"Documentation directory not found: {source_path}"
        )

    documents = []

    for file_path in source_path.rglob("*.md"):
        content = file_path.read_text(encoding="utf-8")

        documents.append({
            "source": str(file_path),
            "content": content,
        })

    return documents