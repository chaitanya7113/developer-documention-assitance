
import re

IGNORED_NAMES = {
    "if", "for", "while", "switch", "catch",
    "function", "return", "typeof", "new",
}

FUNCTION_CALL_PATTERN = re.compile(
    r"\b([A-Za-z_$][A-Za-z0-9_$]*)\s*\("
)

ARROW_FUNCTION_PATTERN = re.compile(
    r"\b(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)"
    r"\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][A-Za-z0-9_$]*)\s*=>"
)


def mask_strings_and_comments(code):
    pattern = re.compile(
        r"""//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`"""
    )

    def replace_match(match):
        # Preserve newlines so the code structure stays readable.
        return re.sub(r"[^\n]", " ", match.group())

    return pattern.sub(replace_match, code)


def detect_function_names(code):
    cleaned_code = mask_strings_and_comments(code)

    matches = FUNCTION_CALL_PATTERN.findall(cleaned_code)
    matches.extend(ARROW_FUNCTION_PATTERN.findall(cleaned_code))

    matches = [
        name for name in matches
        if name not in IGNORED_NAMES
    ]

    return list(dict.fromkeys(matches))
