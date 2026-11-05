
from rag.citation_builder import build_citations


def test_build_citations():

    results = [
        {
            "score": 8.5,
            "payload": {
                "file": "useCallback.md",
                "section": "Optimizing a custom Hook",
                "documentation_url": (
                    "https://react.dev/reference/react/useCallback"
                ),
            },
        },
        {
            "score": 7.9,
            "payload": {
                "file": "useCallback.md",
                "section": "Preventing an Effect from firing too often",
                "documentation_url": (
                    "https://react.dev/reference/react/useCallback"
                ),
            },
        },
        {
            "score": 7.5,
            "payload": {
                "file": "useState.md",
                "section": "Resetting state with a key",
                "documentation_url": (
                    "https://react.dev/reference/react/useState"
                ),
            },
        },
        {
            "score": 6.5,
            "payload": {
                "file": "unknown.md",
                "section": "Unknown section",
            },
        },
    ]

    citations = build_citations(results)

    assert len(citations) == 2

    assert citations[0]["title"] == "useCallback"
    assert citations[0]["file"] == "useCallback.md"
    assert citations[0]["section"] == "Optimizing a custom Hook"
    assert citations[0]["url"] == (
        "https://react.dev/reference/react/useCallback"
    )

    assert citations[1]["title"] == "useState"

    print("Citations:", citations)
    print("All citation tests passed!")


if __name__ == "__main__":
    test_build_citations()
