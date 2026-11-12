
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
        # Explicit code requests
        r"\bcode\b",
        r"\bexample\b",
        r"\bsnippet\b",
        r"\bimplementation\b",
        r"\bprogram\b",

        # Direct implementation requests
        r"\bshow me how\b",
        r"\bshow me\b",
        r"\bhow to implement\b",
        r"\bwrite\b",
        r"\bhow can i use\b",
        r"\bhow do i use\b",
        r"\bhow to use\b",

        # Action-oriented questions
        r"\bhow do i (?:clean up|remove|add|create|build|"
        r"implement|write|handle|fix|update|configure|"
        r"connect|disconnect|subscribe|unsubscribe|"
        r"attach|fetch|call|pass|set)\b",

        r"\bhow to (?:clean up|remove|add|create|build|"
        r"implement|write|handle|fix|update|configure|"
        r"connect|disconnect|subscribe|unsubscribe|"
        r"attach|fetch|call|pass|set)\b",
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
