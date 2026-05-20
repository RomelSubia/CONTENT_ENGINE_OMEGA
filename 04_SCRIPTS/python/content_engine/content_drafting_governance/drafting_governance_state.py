from __future__ import annotations

def get_drafting_governance_state() -> dict[str, object]:
    return {
        "component": "CONTENT_DRAFTING_GOVERNANCE_CORE",
        "status": "BUILT_PENDING_POST_AUDIT",
        "layer_mode": "GOVERNANCE_ONLY",
        "maturity_level_current": 0,
        "draft_creation_allowed_now": False,
        "content_generation_allowed_now": False,
        "queue_write_allowed_now": False,
        "publishing_allowed_now": False,
        "automation_allowed_now": False,
        "final_output_allowed_now": False,
        "argos_bridge_allowed_now": False,
        "human_review_required": True,
        "next_safe_step": "CONTENT_ENGINE_CONTENT_DRAFTING_GOVERNANCE_CORE_POST_BUILD_AUDIT",
    }


def assert_hard_false_permissions(state: dict[str, object] | None = None) -> bool:
    current = state or get_drafting_governance_state()
    hard_false_keys = [
        "draft_creation_allowed_now",
        "content_generation_allowed_now",
        "queue_write_allowed_now",
        "publishing_allowed_now",
        "automation_allowed_now",
        "final_output_allowed_now",
        "argos_bridge_allowed_now",
    ]
    return all(current.get(key) is False for key in hard_false_keys)
