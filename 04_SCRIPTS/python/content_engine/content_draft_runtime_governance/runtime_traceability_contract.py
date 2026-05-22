from __future__ import annotations

from .runtime_contracts import PASS
from .runtime_failure_policy import fail_closed

def validate_traceability_refs(refs: list[str] | None) -> dict[str, object]:
    if not refs:
        return fail_closed("MISSING_TRACEABILITY")
    return {"status": PASS, "traceability_refs": list(refs), "traceability_required": True}
