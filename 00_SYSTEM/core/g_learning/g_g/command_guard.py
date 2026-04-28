from __future__ import annotations

from typing import Any

from .constants import FORBIDDEN_OUTPUT_TERMS


def contains_command_token(data: Any) -> bool:
    text = str(data).lower()
    return any(term in text for term in FORBIDDEN_OUTPUT_TERMS)
