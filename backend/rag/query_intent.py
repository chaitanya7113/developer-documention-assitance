
import re


def detect_query_intent(question):
    """
    Detect whether the user wants:
    - explanation
    - code_example
    - both
    """

    question = question.lower().strip()

    code_patterns = [
        r"\bcode\b",
        r"\bexample\b",
        r"\bsnippet\b",
        r"\bimplementation\b",
        r"\bprogram\b",
        r"\bshow me how\b",
        r"\bhow to implement\b",
        r"\bwrite\b",
    ]

    explanation_patterns = [
        r"\bexplain\b",
        r"\bwhat is\b",
        r"\bwhat are\b",
        r"\bwhy\b",
        r"\bhow does\b",
        r"\bdescribe\b",
        r"\bmeaning\b",
    ]

    wants_code = any(
        re.search(pattern, question)
        for pattern in code_patterns
    )

    wants_explanation = any(
        re.search(pattern, question)
        for pattern in explanation_patterns
    )

    if wants_code and wants_explanation:
        return "both"

    if wants_code:
        return "code_example"

    return "explanation"
