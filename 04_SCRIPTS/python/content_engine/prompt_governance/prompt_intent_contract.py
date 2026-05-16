from __future__ import annotations

from typing import Any

ALLOWED_INTENTS = {
    "DEFINE_STRUCTURE",
    "DEFINE_RULES",
    "DEFINE_REVIEW_CRITERIA",
    "DEFINE_CHANNEL_BOUNDARY",
    "DEFINE_QUALITY_CHECK",
    "DEFINE_CONCEPTUAL_TEMPLATE",
    "DEFINE_SAFETY_CONSTRAINTS",
    "DEFINE_VERSIONING_RULES",
}

BLOCKED_INTENTS = {
    "GENERATE_FINAL_SCRIPT",
    "GENERATE_READY_POST",
    "GENERATE_CAPTION_TO_PUBLISH",
    "GENERATE_METADATA_TO_UPLOAD",
    "GENERATE_VIDEO_ASSET",
    "SEND_TO_QUEUE",
    "WRITE_METRICS",
    "PUBLISH_NOW",
    "TRIGGER_WORKFLOW",
    "CALL_WEBHOOK",
    "ACTIVATE_CAPA9",
    "WRITE_MANUAL",
    "WRITE_BRAIN",
    "WRITE_REPORTS_BRAIN",
}


def validate_prompt_intent(intent: str) -> dict[str, Any]:
    if intent in BLOCKED_INTENTS:
        return {"status": "BLOCK", "reason": "PROMPT_INTENT_BLOCKED", "intent": intent}
    if intent not in ALLOWED_INTENTS:
        return {"status": "BLOCK", "reason": "UNKNOWN_PROMPT_INTENT", "intent": intent}
    return {"status": "PASS", "intent": intent}
