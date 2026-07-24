"""Small email-style query parser shared by filterable screens."""

import re
from dataclasses import dataclass
from typing import Optional


TOKEN_PATTERN = re.compile(
    r'(?:-?[A-Za-z][\w-]*:)?(?:"[^"]*"|\S+)'
)
NUMBER_COMPARISON = re.compile(r"^(>=|<=|>|<|=)?(\d+)$")


@dataclass(frozen=True)
class FilterTerm:
    field: Optional[str]
    value: str
    negated: bool = False


def parse_query(query):
    """Parse words, quoted phrases, fields, and leading negation."""
    terms = []
    for token in TOKEN_PATTERN.findall(query):
        negated = token.startswith("-") and len(token) > 1
        body = token[1:] if negated else token
        field = None
        value = body
        if ":" in body:
            field, value = body.split(":", 1)
            field = field.lower()
        value = _unquote(value).strip().lower()
        if value:
            terms.append(FilterTerm(field, value, negated))
    return terms


def compare_number(actual, expression):
    """Evaluate a compact numeric expression such as >=100."""
    match = NUMBER_COMPARISON.fullmatch(expression)
    if not match:
        return False
    operator, expected = match.groups()
    expected = int(expected)
    comparisons = {
        ">=": actual >= expected,
        "<=": actual <= expected,
        ">": actual > expected,
        "<": actual < expected,
        "=": actual == expected,
        None: actual == expected,
    }
    return comparisons[operator]


def _unquote(value):
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value.strip('"')
