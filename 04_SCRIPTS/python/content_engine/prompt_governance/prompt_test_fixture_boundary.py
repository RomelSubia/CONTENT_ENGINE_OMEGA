from __future__ import annotations

from typing import Any

ALLOWED_CONTEXTS = {"negative_test_fixture", "blocked_prompt_example", "synthetic_security_case", "failure_injection_case"}
BLOCKED_CONTEXTS = {"operational_prompt", "production_template", "active_prompt", "ready_to_use_prompt"}


def validate_test_fixture_boundary(context: str, contains_dangerous_text: bool = False) -> dict[str, Any]:
    if context in BLOCKED_CONTEXTS and contains_dangerous_text:
        return {"status": "BLOCK", "reason": "DANGEROUS_FIXTURE_PROMOTED_TO_OPERATIONAL_PROMPT"}
    if context not in ALLOWED_CONTEXTS and contains_dangerous_text:
        return {"status": "BLOCK", "reason": "UNAPPROVED_DANGEROUS_FIXTURE_CONTEXT"}
    return {"status": "PASS", "context": context}
