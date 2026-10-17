
import re


IGNORED_NAMES = {
    "if", "for", "while", "switch", "catch",
    "function", "return", "typeof", "new", "async",
}

IDENTIFIER = r"[A-Za-z_$][A-Za-z0-9_$]*"

FUNCTION_CALL_PATTERN = re.compile(
    rf"\b({IDENTIFIER})\s*\("
)

FUNCTION_DECLARATION_PATTERN = re.compile(
    rf"\bfunction\s*\*?\s*({IDENTIFIER})\s*\("
)

ARROW_FUNCTION_PATTERN = re.compile(
    rf"\b(?:const|let|var)\s+({IDENTIFIER})\s*=\s*"
    rf"(?:async\s*)?(?:"
    rf"\([^)]*\)\s*=>|{IDENTIFIER}\s*=>"
    rf")"
)

FUNCTION_EXPRESSION_VARIABLE_PATTERN = re.compile(
    rf"\b(?:const|let|var)\s+({IDENTIFIER})\s*=\s*"
    rf"(?:async\s*)?function\b"
)

METHOD_DEFINITION_PATTERN = re.compile(
    rf"(?:^|[{{}},;]\s*)({IDENTIFIER})\s*"
    rf"\([^()]*\)\s*\{{"
)


def mask_strings_and_comments(code):
    pattern = re.compile(
        r"""//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`"""
    )

    def replace_match(match):
        return re.sub(r"[^\n]", " ", match.group())

    return pattern.sub(replace_match, code)


def _find_definition_matches(code):
    patterns = (
        FUNCTION_DECLARATION_PATTERN,
        ARROW_FUNCTION_PATTERN,
        FUNCTION_EXPRESSION_VARIABLE_PATTERN,
        METHOD_DEFINITION_PATTERN,
    )

    matches = []
    for pattern in patterns:
        matches.extend(pattern.finditer(code))

    return matches


def detect_function_names(code):
    cleaned_code = mask_strings_and_comments(code)

    names = []
    for match in _find_definition_matches(cleaned_code):
        name = match.group(1)
        if name not in IGNORED_NAMES:
            names.append(name)

    return list(dict.fromkeys(names))


def detect_function_calls(code):
    cleaned_code = mask_strings_and_comments(code)

    definition_spans = {
        (match.start(1), match.end(1))
        for match in _find_definition_matches(cleaned_code)
    }

    calls = []
    for match in FUNCTION_CALL_PATTERN.finditer(cleaned_code):
        name = match.group(1)
        span = (match.start(1), match.end(1))

        if name in IGNORED_NAMES or span in definition_spans:
            continue

        calls.append(name)

    return list(dict.fromkeys(calls))
