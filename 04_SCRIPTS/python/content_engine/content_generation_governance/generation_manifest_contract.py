"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


from .generation_governance_state import HARD_FALSE_KEYS

def build_generation_manifest_payload(produced_artifacts: list[str], hashed_artifacts: dict[str, str]) -> dict:
    return {
        "status": "BUILT_PENDING_POST_AUDIT",
        "layer_mode": "GOVERNANCE_ONLY",
        "produced_artifacts": produced_artifacts,
        "hashed_artifacts": hashed_artifacts,
        "canonical_json": True,
        "manifest_completeness": "PASS",
        "next_safe_step": "CONTENT_ENGINE_CONTENT_GENERATION_GOVERNANCE_CORE_POST_BUILD_AUDIT",
    }

def validate_generation_manifest_payload(payload: dict) -> dict:
    required = ["status", "layer_mode", "produced_artifacts", "hashed_artifacts", "canonical_json", "manifest_completeness", "next_safe_step"]
    missing = [field for field in required if field not in payload]
    if missing:
        return {"status": "BLOCK", "reason": "MANIFEST_PAYLOAD_MISSING_FIELDS", "missing": missing}
    if payload.get("layer_mode") != "GOVERNANCE_ONLY":
        return {"status": "BLOCK", "reason": "MANIFEST_LAYER_MODE_INVALID"}
    if payload.get("next_safe_step") != "CONTENT_ENGINE_CONTENT_GENERATION_GOVERNANCE_CORE_POST_BUILD_AUDIT":
        return {"status": "BLOCK", "reason": "MANIFEST_NEXT_SAFE_STEP_INVALID"}
    return {"status": "PASS", "reason": "MANIFEST_PAYLOAD_VALID"}

def seal_hard_false_fields() -> tuple[str, ...]:
    return HARD_FALSE_KEYS + (
        "generation_execution_allowed_now",
        "sample_content_allowed_now",
        "report_publishable_content_allowed_now",
    )
