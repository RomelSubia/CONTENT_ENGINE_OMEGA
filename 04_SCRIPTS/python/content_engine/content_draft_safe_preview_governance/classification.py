from __future__ import annotations

from enum import StrEnum


class SafePreviewClassification(StrEnum):
    SAFE_CONCEPTUAL_PREVIEW = "SAFE_CONCEPTUAL_PREVIEW"
    SAFE_INTERNAL_VARIATION = "SAFE_INTERNAL_VARIATION"
    SAFE_STRUCTURE_PREVIEW = "SAFE_STRUCTURE_PREVIEW"


ALLOWED_CLASSIFICATIONS: frozenset[str] = frozenset(item.value for item in SafePreviewClassification)

BLOCKED_CLASSIFICATIONS: frozenset[str] = frozenset(
    {
        "FINAL_DRAFT",
        "PLATFORM_READY_COPY",
        "HASHTAGS_FINAL",
        "CTA_FINAL",
        "PUBLISHABLE_ASSET",
        "QUEUE_READY_PAYLOAD",
        "PUBLICATION_PAYLOAD",
        "AUTOMATION_PAYLOAD",
        "N8N_PAYLOAD",
        "WEBHOOK_PAYLOAD",
        "CAPA9_PAYLOAD",
    }
)


def is_allowed_classification(value: str) -> bool:
    return value in ALLOWED_CLASSIFICATIONS


def is_blocked_classification(value: str) -> bool:
    return value in BLOCKED_CLASSIFICATIONS
