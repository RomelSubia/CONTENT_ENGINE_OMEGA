from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import HumanReviewRequest, HumanReviewResult


def build_review_record(request: HumanReviewRequest, result: HumanReviewResult) -> dict[str, Any]:
    return {
        "request": asdict(request),
        "result": asdict(result),
        "productive_operations_blocked": {
            "finalization_allowed_now": result.finalization_allowed_now,
            "queue_write_allowed_now": result.queue_write_allowed_now,
            "publishing_allowed_now": result.publishing_allowed_now,
            "automation_allowed_now": result.automation_allowed_now,
            "runtime_execution_allowed_now": result.runtime_execution_allowed_now,
            "draft_creation_allowed_now": result.draft_creation_allowed_now,
            "content_generation_allowed_now": result.content_generation_allowed_now,
        },
    }
