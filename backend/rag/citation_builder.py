
from pathlib import Path


def build_citations(results):
    """
    Extract unique documentation citations
    from reranked Qdrant results.
    """

    citations = []
    seen_urls = set()

    for result in results:
        payload = result.get("payload", {})

        documentation_url = payload.get("documentation_url")

        # Skip chunks without a documentation URL
        if not documentation_url:
            continue

        # Avoid duplicate citations
        if documentation_url in seen_urls:
            continue

        seen_urls.add(documentation_url)

        file_name = payload.get("file", "Unknown file")
        section = payload.get("section", "Unknown section")

        title = Path(file_name).stem

        # Use section name for index.md
        if title == "index":
            title = section

        citations.append({
            "title": title,
            "file": file_name,
            "section": section,
            "url": documentation_url,
        })

    return citations
