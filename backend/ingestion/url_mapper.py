from pathlib import Path
from urllib.parse import quote


BASE_DOCUMENTATION_URL = "https://react.dev"


def get_documentation_url(file_path, docs_root):
    file_path = Path(file_path).resolve()
    docs_root = Path(docs_root).resolve()

    try:
        relative_path = file_path.relative_to(docs_root)
    except ValueError:
        raise ValueError(
            f"File {file_path} is outside documentation directory {docs_root}"
        )

    # Remove .md extension
    relative_path = relative_path.with_suffix("")

    # Remove index from the final path
    if relative_path.name == "index":
        relative_path = relative_path.parent

    # Convert Windows paths to URL paths
    url_path = "/".join(
        quote(part) for part in relative_path.parts
    )

    return f"{BASE_DOCUMENTATION_URL}/{url_path}"