from __future__ import annotations

from typing import Dict, Tuple

from .constants import FORBIDDEN_EXECUTION_TERMS


def execution_boundary_guard(approval: Dict) -> Tuple[bool, str]:
    text = " ".join(
        [
            str(approval.get("approval_statement", "")),
            str(approval.get("approval_intent", "")),
            str(approval.get("approval_scope", "")),
        ]
    ).lower()

    if any(term in text for term in FORBIDDEN_EXECUTION_TERMS):
        return False, "EXECUTION_BOUNDARY_VIOLATION"

    return True, "NO_EXECUTION_TOKEN"
