from __future__ import annotations

def fail_closed_result(reason: str, *, extra: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "status": "FAILED_BLOCKED",
        "reason": reason,
        "extra": extra or {},
        "draft_creation_performed": False,
        "content_generation_performed": False,
        "queue_write_performed": False,
        "publishing_performed": False,
        "automation_performed": False,
        "human_review_required": True,
        "final_output_allowed": False,
    }


def require_or_fail(condition: bool, reason: str) -> dict[str, object]:
    if condition:
        return {"status": "PASS", "reason": "REQUIREMENT_MET"}
    return fail_closed_result(reason)
