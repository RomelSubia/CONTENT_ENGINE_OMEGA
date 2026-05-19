"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


HARD_FALSE_KEYS = (
    "content_generation_allowed_now",
    "draft_creation_allowed_now",
    "draft_materialization_allowed_now",
    "draft_persistence_allowed_now",
    "draft_export_allowed_now",
    "draft_preview_allowed_now",
    "content_preview_allowed_now",
    "creative_outline_allowed_now",
    "near_final_sample_allowed_now",
    "sample_content_allowed_now",
    "prompt_execution_allowed_now",
    "script_execution_allowed_now",
    "asset_generation_allowed_now",
    "publishing_allowed_now",
    "automation_allowed_now",
    "queue_write_allowed_now",
    "real_queue_mutation_allowed_now",
    "manual_write_allowed_now",
    "brain_write_allowed_now",
    "reports_brain_write_allowed_now",
    "external_call_allowed_now",
    "operational_literal_allowed_now",
    "real_history_read_allowed_now",
    "productive_operations_allowed_now",
    "generation_execution_layer_allowed_now",
)

def build_content_generation_governance_state() -> dict:
    state = {
        "status": "PASS",
        "layer_mode": "GOVERNANCE_ONLY",
        "module_runtime_status": "BUILT_PENDING_POST_AUDIT",
        "component_chain_status": "CONTENT_GENERATION_GOVERNANCE_CORE_BUILT_PENDING_POST_AUDIT",
        "human_review_required": True,
        "next_safe_step": "CONTENT_ENGINE_CONTENT_GENERATION_GOVERNANCE_CORE_POST_BUILD_AUDIT",
    }
    for key in HARD_FALSE_KEYS:
        state[key] = False
    return state

def validate_content_generation_governance_state(state: dict) -> dict:
    missing = [key for key in ("layer_mode", "module_runtime_status", "component_chain_status") if key not in state]
    false_violations = [key for key in HARD_FALSE_KEYS if state.get(key) is not False]
    if missing or false_violations or state.get("layer_mode") != "GOVERNANCE_ONLY":
        return {
            "status": "BLOCK",
            "reason": "CONTENT_GENERATION_GOVERNANCE_STATE_INVALID",
            "missing": missing,
            "false_violations": false_violations,
        }
    if state.get("human_review_required") is not True:
        return {"status": "BLOCK", "reason": "HUMAN_REVIEW_REQUIRED_MUST_BE_TRUE"}
    return {"status": "PASS", "reason": "CONTENT_GENERATION_GOVERNANCE_STATE_VALID"}
