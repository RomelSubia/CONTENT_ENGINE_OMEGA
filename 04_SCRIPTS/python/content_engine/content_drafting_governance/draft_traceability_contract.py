from __future__ import annotations

def validate_traceability_contract(payload: dict[str, object]) -> dict[str, object]:
    required = ["channel_or_domain_id", "traceability_refs"]
    missing = [key for key in required if not payload.get(key)]
    trace_refs = payload.get("traceability_refs")
    trace_valid = isinstance(trace_refs, list) and all(isinstance(item, str) and item for item in trace_refs)
    if not trace_valid and "traceability_refs" not in missing:
        missing.append("traceability_refs")
    return {
        "valid": not missing,
        "missing": sorted(set(missing)),
        "reason": "TRACEABILITY_CONTRACT_BLOCK" if missing else "TRACEABILITY_CONTRACT_PASS",
    }
