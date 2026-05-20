from __future__ import annotations

def validate_evidence_contract(payload: dict[str, object], *, claim_requires_evidence: bool = False) -> dict[str, object]:
    refs = payload.get("evidence_refs")
    valid_refs = isinstance(refs, list) and len(refs) > 0 and all(isinstance(item, str) and item for item in refs)
    blocked = claim_requires_evidence and not valid_refs
    return {
        "valid": valid_refs,
        "blocked": blocked,
        "reason": "EVIDENCE_REQUIRED_BLOCK" if blocked else "EVIDENCE_CONTRACT_REVIEW",
    }
