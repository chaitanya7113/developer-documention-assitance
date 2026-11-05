from pathlib import Path
from ingestion.url_mapper import get_documentation_url


DOCS_ROOT = Path("../docs/react")


test_cases = [
    (
        "../docs/react/learn/installation.md",
        "https://react.dev/learn/installation",
    ),
    (
        "../docs/react/learn/index.md",
        "https://react.dev/learn",
    ),
    (
        "../docs/react/learn/react-compiler/index.md",
        "https://react.dev/learn/react-compiler",
    ),
    (
        "../docs/react/reference/react/act.md",
        "https://react.dev/reference/react/act",
    ),
    (
        "../docs/react/reference/react/index.md",
        "https://react.dev/reference/react",
    ),
    (
        "../docs/react/reference/eslint-plugin-react-hooks/lints/rules-of-hooks.md",
        "https://react.dev/reference/eslint-plugin-react-hooks/lints/rules-of-hooks",
    ),
]


for file_path, expected_url in test_cases:
    actual_url = get_documentation_url(file_path, DOCS_ROOT)

    assert actual_url == expected_url, (
        f"\nExpected: {expected_url}"
        f"\nActual:   {actual_url}"
    )

    print("PASS:", actual_url)


print("\nAll URL mapping tests passed!")