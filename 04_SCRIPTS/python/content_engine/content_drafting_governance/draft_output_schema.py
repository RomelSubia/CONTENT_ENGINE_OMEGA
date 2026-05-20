from __future__ import annotations

def make_governance_output(
    *,
    status: str,
    reason: str,
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "status": status,
        "reason": reason,
        "payload": payload or {},
        "human_review_required": True,
        "final_output_allowed": False,
        "draft_creation_performed": False,
        "content_generation_performed": False,
        "queue_write_performed": False,
        "publishing_performed": False,
        "automation_performed": False,
    }
